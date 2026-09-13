"""
AgriSmart AI - Enterprise Tiered Rate Limiter with Exponential Backoff
SIH-2026 Problem Statement 1

Features:
- Stricter limits on authentication routes (login, register, password change)
- Dual per-IP sliding window and per-account exponential backoff penalty
- Moderate limits on unauthenticated public endpoints
- Looser limits on authenticated user actions
- Dynamic runtime configuration (via environment variables or system endpoints)
- Thread-safe in-memory tracking with automatic memory hygiene
"""

import os
import time
import math
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class RateLimitConfig:
    """Configurable thresholds for rate limiting."""
    enabled: bool = True
    
    # Tier 1: Authentication Routes (stricter)
    auth_ip_max: int = 10                  # Max attempts per IP per window
    auth_ip_window: int = 60              # Seconds for IP window
    auth_account_threshold: int = 3       # Free attempts per account before backoff escalates
    auth_ip_backoff_threshold: int = 10   # Free failed attempts per IP before IP backoff escalates
    auth_backoff_base: float = 2.0        # Base delay (seconds)
    auth_backoff_factor: float = 2.0      # Exponential multiplier
    auth_backoff_max: float = 300.0       # Max delay cap (seconds = 5 min)
    
    # Tier 2: Public Endpoints (moderate)
    public_ip_max: int = 30               # Max requests per IP per window
    public_ip_window: int = 60            # Seconds for public window
    
    # Tier 3: Authenticated User Actions (looser)
    authed_user_max: int = 120            # Max requests per user per window
    authed_user_window: int = 60          # Seconds for authenticated window

    @classmethod
    def from_env(cls) -> "RateLimitConfig":
        """Loads configuration from environment variables with fallback defaults."""
        return cls(
            enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes"),
            auth_ip_max=int(os.getenv("RATE_LIMIT_AUTH_IP_MAX", "10")),
            auth_ip_window=int(os.getenv("RATE_LIMIT_AUTH_IP_WINDOW", "60")),
            auth_account_threshold=int(os.getenv("RATE_LIMIT_AUTH_ACCOUNT_THRESHOLD", "3")),
            auth_ip_backoff_threshold=int(os.getenv("RATE_LIMIT_AUTH_IP_BACKOFF_THRESHOLD", "10")),
            auth_backoff_base=float(os.getenv("RATE_LIMIT_AUTH_BACKOFF_BASE", "2.0")),
            auth_backoff_factor=float(os.getenv("RATE_LIMIT_AUTH_BACKOFF_FACTOR", "2.0")),
            auth_backoff_max=float(os.getenv("RATE_LIMIT_AUTH_BACKOFF_MAX", "300.0")),
            public_ip_max=int(os.getenv("RATE_LIMIT_PUBLIC_IP_MAX", "30")),
            public_ip_window=int(os.getenv("RATE_LIMIT_PUBLIC_IP_WINDOW", "60")),
            authed_user_max=int(os.getenv("RATE_LIMIT_AUTHED_USER_MAX", "120")),
            authed_user_window=int(os.getenv("RATE_LIMIT_AUTHED_USER_WINDOW", "60"))
        )


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after: int = 0
    limit: int = 0
    remaining: int = 0
    reset_seconds: int = 0
    limit_type: str = "none"
    detail: str = ""

    def to_headers(self) -> Dict[str, str]:
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(0, self.remaining)),
            "X-RateLimit-Reset": str(self.reset_seconds),
        }
        if not self.allowed and self.retry_after > 0:
            headers["Retry-After"] = str(self.retry_after)
        return headers


class SlidingWindowCounter:
    """Thread-safe sliding window request counter."""
    def __init__(self):
        self._lock = threading.Lock()
        self._records: Dict[str, List[float]] = {}

    def check_and_add(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int, int]:
        """
        Returns: (allowed, remaining, reset_seconds, total_limit)
        """
        now = time.time()
        cutoff = now - window_seconds
        
        with self._lock:
            timestamps = self._records.get(key, [])
            # Evict timestamps older than sliding window
            timestamps = [t for t in timestamps if t > cutoff]
            
            if len(timestamps) >= max_requests:
                oldest = timestamps[0]
                retry_after = max(1, int(math.ceil(oldest + window_seconds - now)))
                self._records[key] = timestamps
                return False, 0, retry_after, max_requests

            timestamps.append(now)
            self._records[key] = timestamps
            remaining = max_requests - len(timestamps)
            reset_seconds = max(1, int(math.ceil(timestamps[0] + window_seconds - now)))
            return True, remaining, reset_seconds, max_requests

    def clear(self):
        with self._lock:
            self._records.clear()


class ExponentialBackoffTracker:
    """
    Thread-safe tracker for authentication failures.
    Progressively delays requests rather than issuing a hard lockout.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._failures: Dict[str, int] = {}
        self._blocked_until: Dict[str, float] = {}

    def check_backoff(self, entity_key: str) -> Tuple[bool, int]:
        """
        Returns (allowed, retry_after).
        """
        now = time.time()
        with self._lock:
            blocked_time = self._blocked_until.get(entity_key, 0.0)
            if now < blocked_time:
                retry_after = max(1, int(math.ceil(blocked_time - now)))
                return False, retry_after
            return True, 0

    def record_attempt(
        self,
        entity_key: str,
        success: bool,
        threshold: int,
        base_sec: float,
        factor: float,
        max_sec: float
    ) -> int:
        """
        Records attempt outcome. If failed and past threshold, sets backoff.
        Returns the computed backoff delay (0 if not blocked).
        """
        now = time.time()
        with self._lock:
            if success:
                # Reset failures upon successful authentication
                self._failures.pop(entity_key, None)
                self._blocked_until.pop(entity_key, None)
                return 0
            
            # Increment failure counter
            count = self._failures.get(entity_key, 0) + 1
            self._failures[entity_key] = count
            
            if count >= threshold:
                exponent = count - threshold
                delay = min(max_sec, base_sec * (factor ** exponent))
                self._blocked_until[entity_key] = now + delay
                return int(math.ceil(delay))
            
            return 0

    def clear(self):
        with self._lock:
            self._failures.clear()
            self._blocked_until.clear()


class RateLimiter:
    """
    Main rate limiting controller providing tiered rate limiting and exponential backoff.
    """
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig.from_env()
        self.auth_ip_counter = SlidingWindowCounter()
        self.public_ip_counter = SlidingWindowCounter()
        self.authed_user_counter = SlidingWindowCounter()
        self.account_backoff = ExponentialBackoffTracker()
        self.ip_backoff = ExponentialBackoffTracker()

    def check_auth_rate_limit(self, account: Optional[str], ip: str) -> RateLimitResult:
        """
        Checks stricter auth limits:
        1. Account-level exponential backoff
        2. IP-level sliding window
        3. IP-level exponential backoff
        """
        if not self.config.enabled:
            return RateLimitResult(allowed=True, limit=self.config.auth_ip_max, remaining=self.config.auth_ip_max)

        clean_ip = ip.strip()
        clean_account = account.strip().lower() if account else None

        # 1. Check account exponential backoff
        if clean_account:
            allowed, retry_after = self.account_backoff.check_backoff(clean_account)
            if not allowed:
                return RateLimitResult(
                    allowed=False,
                    retry_after=retry_after,
                    limit=self.config.auth_account_threshold,
                    remaining=0,
                    reset_seconds=retry_after,
                    limit_type="auth_account_backoff",
                    detail=f"Too many failed login attempts for account '{account}'. Exponential backoff penalty active. Please wait {retry_after} seconds."
                )

        # 2. Check IP sliding window
        allowed, remaining, reset_sec, limit = self.auth_ip_counter.check_and_add(
            f"auth_ip:{clean_ip}",
            max_requests=self.config.auth_ip_max,
            window_seconds=self.config.auth_ip_window
        )
        if not allowed:
            return RateLimitResult(
                allowed=False,
                retry_after=reset_sec,
                limit=limit,
                remaining=0,
                reset_seconds=reset_sec,
                limit_type="auth_ip_window",
                detail=f"Authentication rate limit exceeded for IP {clean_ip}. Max {limit} requests per {self.config.auth_ip_window}s. Retry in {reset_sec}s."
            )

        # 3. Check IP exponential backoff
        allowed, retry_after = self.ip_backoff.check_backoff(clean_ip)
        if not allowed:
            return RateLimitResult(
                allowed=False,
                retry_after=retry_after,
                limit=self.config.auth_account_threshold,
                remaining=0,
                reset_seconds=retry_after,
                limit_type="auth_ip_backoff",
                detail=f"Too many failed attempts from IP {clean_ip}. Exponential backoff penalty active. Please wait {retry_after} seconds."
            )

        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=remaining,
            reset_seconds=reset_sec,
            limit_type="auth"
        )

    def record_auth_result(self, account: Optional[str], ip: str, success: bool):
        """Records authentication outcome to adjust exponential backoffs."""
        if not self.config.enabled:
            return

        clean_ip = ip.strip()
        clean_account = account.strip().lower() if account else None

        # Track IP backoff
        self.ip_backoff.record_attempt(
            clean_ip,
            success=success,
            threshold=self.config.auth_ip_backoff_threshold,
            base_sec=self.config.auth_backoff_base,
            factor=self.config.auth_backoff_factor,
            max_sec=self.config.auth_backoff_max
        )

        # Track account backoff
        if clean_account:
            self.account_backoff.record_attempt(
                clean_account,
                success=success,
                threshold=self.config.auth_account_threshold,
                base_sec=self.config.auth_backoff_base,
                factor=self.config.auth_backoff_factor,
                max_sec=self.config.auth_backoff_max
            )

    def check_public_rate_limit(self, ip: str, endpoint: str = "") -> RateLimitResult:
        """Checks moderate rate limits on public endpoints."""
        if not self.config.enabled:
            return RateLimitResult(allowed=True, limit=self.config.public_ip_max, remaining=self.config.public_ip_max)

        clean_ip = ip.strip()
        key = f"pub_ip:{clean_ip}"
        allowed, remaining, reset_sec, limit = self.public_ip_counter.check_and_add(
            key,
            max_requests=self.config.public_ip_max,
            window_seconds=self.config.public_ip_window
        )

        if not allowed:
            return RateLimitResult(
                allowed=False,
                retry_after=reset_sec,
                limit=limit,
                remaining=0,
                reset_seconds=reset_sec,
                limit_type="public_ip_window",
                detail=f"Public API rate limit exceeded. Max {limit} requests per {self.config.public_ip_window}s. Retry in {reset_sec}s."
            )

        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=remaining,
            reset_seconds=reset_sec,
            limit_type="public"
        )

    def check_authenticated_rate_limit(self, user_id: Any, ip: str, endpoint: str = "") -> RateLimitResult:
        """Checks looser rate limits for authenticated user actions."""
        if not self.config.enabled:
            return RateLimitResult(allowed=True, limit=self.config.authed_user_max, remaining=self.config.authed_user_max)

        key = f"usr:{user_id}" if user_id else f"pub_ip:{ip}"
        allowed, remaining, reset_sec, limit = self.authed_user_counter.check_and_add(
            key,
            max_requests=self.config.authed_user_max,
            window_seconds=self.config.authed_user_window
        )

        if not allowed:
            return RateLimitResult(
                allowed=False,
                retry_after=reset_sec,
                limit=limit,
                remaining=0,
                reset_seconds=reset_sec,
                limit_type="authed_user_window",
                detail=f"User action rate limit exceeded. Max {limit} requests per {self.config.authed_user_window}s. Retry in {reset_sec}s."
            )

        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=remaining,
            reset_seconds=reset_sec,
            limit_type="authenticated"
        )

    def get_config(self) -> Dict[str, Any]:
        """Returns current configuration dictionary."""
        return asdict(self.config)

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates configuration at runtime."""
        for k, v in updates.items():
            if hasattr(self.config, k):
                target_type = type(getattr(self.config, k))
                if target_type is bool and isinstance(v, str):
                    setattr(self.config, k, v.lower() in ("true", "1", "yes"))
                else:
                    setattr(self.config, k, target_type(v))
        return self.get_config()

    def reset_all(self):
        """Clears all counters and backoff records."""
        self.auth_ip_counter.clear()
        self.public_ip_counter.clear()
        self.authed_user_counter.clear()
        self.account_backoff.clear()
        self.ip_backoff.clear()


# Global Singleton Instance
_GLOBAL_RATE_LIMITER: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _GLOBAL_RATE_LIMITER
    if _GLOBAL_RATE_LIMITER is None:
        _GLOBAL_RATE_LIMITER = RateLimiter()
    return _GLOBAL_RATE_LIMITER


def extract_client_ip(headers: Any, client_host: Optional[str]) -> str:
    """Extracts client IP from X-Forwarded-For or client.host."""
    if hasattr(headers, "get"):
        forwarded = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return client_host or "127.0.0.1"
