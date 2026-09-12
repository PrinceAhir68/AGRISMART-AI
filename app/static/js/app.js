/**
 * AgriSmart AI - Frontend Client Logic
 * Handles interactive tabs, Core Vision diagnosis, Bonus Modules A-G,
 * Web Speech synthesis, and IoT streaming.
 */

let currentSelectedImageFile = null;
let currentLanguage = 'en';
let currentDiagnosis = 'Tomato___Early_blight';

document.addEventListener('DOMContentLoaded', () => {
  // Load initial live weather & IoT telemetry
  fetchLiveWeather();
  fetchIoTTelemetry();
  setInterval(fetchIoTTelemetry, 4000); // 4-second refresh

  // Drag & drop support
  const dropZone = document.getElementById('drop-zone');
  if (dropZone) {
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = '#10b981'; });
    dropZone.addEventListener('dragleave', () => { dropZone.style.borderColor = '#94a3b8'; });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '#94a3b8';
      if (e.dataTransfer.files.length > 0) {
        processSelectedFile(e.dataTransfer.files[0]);
      }
    });
  }

  // Initial calculations
  submitCropRecommendation();
  calculateIrrigation();
  computeSustainability();
});

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

  const activeContent = document.getElementById(tabId);
  if (activeContent) activeContent.classList.add('active');

  const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
  if (activeBtn) activeBtn.classList.add('active');
}

// -----------------------------------------------------------------
// Core Task: Leaf Disease Detection
// -----------------------------------------------------------------
function handleFileUpload(event) {
  if (event.target.files && event.target.files[0]) {
    processSelectedFile(event.target.files[0]);
  }
}

function processSelectedFile(file) {
  currentSelectedImageFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('image-preview').src = e.target.result;
    document.getElementById('image-preview-container').style.display = 'block';
  };
  reader.readAsDataURL(file);
}

async function loadSample(filename) {
  try {
    const resp = await fetch(`/samples/${filename}`);
    if (!resp.ok) throw new Error('Sample not found');
    const blob = await resp.blob();
    const file = new File([blob], filename, { type: 'image/jpeg' });
    processSelectedFile(file);
    setTimeout(runAnalysis, 150);
  } catch (e) {
    console.error('Error loading sample:', e);
  }
}

async function runAnalysis() {
  if (!currentSelectedImageFile) {
    alert('Please select or upload a leaf photo first.');
    return;
  }

  const btn = document.getElementById('btn-analyze');
  btn.innerText = 'Analyzing Image with MobileNetV3...';
  btn.disabled = true;

  const formData = new FormData();
  formData.append('file', currentSelectedImageFile);

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    renderDiagnosis(data);
  } catch (err) {
    alert('Failed to connect to AI inference server: ' + err.message);
  } finally {
    btn.innerText = '🔍 Run AI Disease Diagnosis';
    btn.disabled = false;
  }
}

function renderDiagnosis(data) {
  currentDiagnosis = data.class_label;
  document.getElementById('diag-empty').style.display = 'none';
  document.getElementById('diag-results').style.display = 'block';

  document.getElementById('res-disease-name').innerText = data.display_name;
  document.getElementById('res-crop-name').innerText = data.crop;
  document.getElementById('res-confidence').innerText = `${Math.round(data.confidence * 100)}%`;

  const badge = document.getElementById('diag-badge');
  if (data.is_disease) {
    badge.className = 'badge badge-danger';
    badge.innerText = 'Pathogen Detected';
  } else {
    badge.className = 'badge badge-success';
    badge.innerText = 'Healthy Crop';
  }

  // Precautions list
  const precUl = document.getElementById('res-precautions');
  precUl.innerHTML = '';
  (data.precautions || []).forEach(p => {
    const li = document.createElement('li');
    li.innerText = p;
    precUl.appendChild(li);
  });

  document.getElementById('res-organic').innerText = data.organic_treatment || 'None needed.';
  document.getElementById('res-chemical').innerText = data.chemical_treatment || 'No chemical intervention needed.';

  // Regional Translation
  const transBox = document.getElementById('res-hi-action');
  if (data.translations && data.translations.hi) {
    transBox.innerText = `${data.translations.hi.title}: ${data.translations.hi.action}`;
  } else {
    transBox.innerText = 'सटीक सलाह के लिए स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें।';
  }
}

function speakText(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const text = el.innerText;
  if (!text) return;

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    // Prefer Hindi voice if available
    const voices = window.speechSynthesis.getVoices();
    const hiVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('HI'));
    if (hiVoice) utterance.voice = hiVoice;
    window.speechSynthesis.speak(utterance);
  } else {
    alert('Browser voice audio synthesis is not supported on this browser.');
  }
}

// -----------------------------------------------------------------
// Bonus A: Crop Recommendation
// -----------------------------------------------------------------
async function submitCropRecommendation() {
  const payload = {
    soil_type: document.getElementById('crop-soil').value,
    ph: parseFloat(document.getElementById('crop-ph').value),
    n: parseFloat(document.getElementById('crop-n').value),
    p: parseFloat(document.getElementById('crop-p').value),
    k: parseFloat(document.getElementById('crop-k').value),
    season: document.getElementById('crop-season').value,
    previous_crop: document.getElementById('crop-prev').value,
    temperature: parseFloat(document.getElementById('crop-temp').value),
    rainfall: parseFloat(document.getElementById('crop-rain').value),
    location: 'Western India'
  };

  try {
    const res = await fetch('/api/crop-recommendation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderCropRecommendations(data.recommendations);
  } catch (e) {
    console.error('Crop rec error:', e);
  }
}

function renderCropRecommendations(recs) {
  const container = document.getElementById('crop-rec-results');
  container.innerHTML = '';
  container.className = '';

  recs.forEach((rec, idx) => {
    const card = document.createElement('div');
    card.className = 'treatment-card';
    card.style.background = idx === 0 ? '#ecfdf5' : '#f8fafc';
    card.style.border = idx === 0 ? '2px solid var(--primary)' : '1px solid var(--border)';
    card.style.marginBottom = '12px';

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <h4 style="font-size:1.1rem; color:#064e3b;">#${idx+1} ${rec.crop}</h4>
        <span class="badge badge-success" style="font-size:0.85rem;">${rec.suitability_score}% Match</span>
      </div>
      <p style="font-size:0.85rem; color:#475569; margin-bottom:6px;">${rec.description}</p>
      <div style="font-size:0.82rem; color:#1e293b;">
        <strong>Expected Yield:</strong> ${rec.yield_potential} • <strong>Cycle:</strong> ~${rec.duration_days} days
      </div>
      <div style="font-size:0.8rem; color:#047857; margin-top:4px;">
        <em>${rec.rotation_rationale}</em>
      </div>
    `;
    container.appendChild(card);
  });
}

// -----------------------------------------------------------------
// Bonus B & C: Smart Irrigation & Live Weather
// -----------------------------------------------------------------
let cachedWeatherData = null;

async function fetchLiveWeather() {
  try {
    const res = await fetch('/api/weather');
    const data = await res.json();
    cachedWeatherData = data;

    document.getElementById('w-temp').innerText = data.current_weather.temperature_c;
    document.getElementById('w-location').innerText = data.location;
    document.getElementById('w-source').innerText = data.data_source;
    document.getElementById('w-humidity').innerText = `${data.current_weather.humidity_pct}%`;
    document.getElementById('w-wind').innerText = `${data.current_weather.wind_speed_kmh} km/h`;
    document.getElementById('w-rain-prob').innerText = `${data.current_weather.rain_24h_prob_pct}%`;
    document.getElementById('w-rain-sum').innerText = `${data.current_weather.rain_24h_sum_mm} mm`;

    document.getElementById('live-weather-badge').innerText = `☁ ${data.current_weather.temperature_c}°C | ${data.location.split(',')[0]}`;

    // Render weather alerts
    const alertBox = document.getElementById('weather-alerts');
    alertBox.innerHTML = '';
    (data.agronomic_actions || []).forEach(act => {
      const p = document.createElement('p');
      p.style.fontSize = '0.85rem';
      p.style.marginBottom = '6px';
      const badgeClass = act.priority === 'HIGH' ? 'badge-danger' : (act.priority === 'MEDIUM' ? 'badge-warning' : 'badge-info');
      p.innerHTML = `<span class="badge ${badgeClass}" style="padding:2px 6px; font-size:0.7rem;">${act.priority}</span> <strong>${act.title}:</strong> ${act.guidance}`;
      alertBox.appendChild(p);
    });
  } catch (e) {
    console.error('Weather fetch error:', e);
  }
}

function toggleRainSync() {
  const syncVal = document.getElementById('irr-rain-sync').value;
  document.getElementById('manual-rain-row').style.display = (syncVal === 'manual') ? 'flex' : 'none';
}

async function calculateIrrigation() {
  let rainMm = 0.0;
  let rainProb = 10.0;

  if (document.getElementById('irr-rain-sync').value === 'live' && cachedWeatherData) {
    rainMm = cachedWeatherData.current_weather.rain_24h_sum_mm;
    rainProb = cachedWeatherData.current_weather.rain_24h_prob_pct;
  } else {
    rainMm = parseFloat(document.getElementById('irr-rain-mm').value || 0);
    rainProb = parseFloat(document.getElementById('irr-rain-prob').value || 10);
  }

  const payload = {
    current_soil_moisture: parseFloat(document.getElementById('irr-moisture').value),
    soil_type: document.getElementById('irr-soil').value,
    crop_type: document.getElementById('irr-crop').value,
    growth_stage: document.getElementById('irr-stage').value,
    forecast_rain_mm: rainMm,
    rain_probability_pct: rainProb,
    ambient_temp_c: cachedWeatherData ? cachedWeatherData.current_weather.temperature_c : 30.0
  };

  try {
    const res = await fetch('/api/smart-irrigation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderIrrigationDecision(data);
  } catch (e) {
    console.error('Irrigation error:', e);
  }
}

function renderIrrigationDecision(data) {
  const box = document.getElementById('irrigation-decision-box');
  box.style.display = 'block';

  let badgeColor = 'badge-success';
  let cardBg = '#f0fdf4';
  if (data.decision.includes('IRRIGATE NOW') || data.decision.includes('EMERGENCY')) {
    badgeColor = 'badge-danger';
    cardBg = '#fee2e2';
  } else if (data.decision.includes('DELAY')) {
    badgeColor = 'badge-warning';
    cardBg = '#fef3c7';
  }

  box.innerHTML = `
    <div style="background:${cardBg}; border:1px solid var(--border); padding:16px; border-radius:12px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <h4 style="font-size:1.15rem; color:#0f172a;">${data.decision}</h4>
        <span class="badge ${badgeColor}">${data.urgency}</span>
      </div>
      <p style="font-size:0.85rem; color:#334155; margin-bottom:8px;">
        Current Moisture: <strong>${data.current_moisture_pct}%</strong> (Stress Point: ${data.stress_threshold_pct}%)
      </p>
      ${data.water_volume_liters_sqm > 0 ? `
        <div style="background:white; padding:10px; border-radius:8px; margin-bottom:8px; font-size:0.85rem;">
          💧 Recommended Delivery: <strong>${data.water_volume_liters_sqm} L/m²</strong> (${data.irrigation_depth_mm} mm depth)<br>
          ⏱ Drip Runtime: <strong>${data.estimated_drip_runtime_minutes} minutes</strong>
        </div>
      ` : ''}
      <ul style="padding-left:18px; font-size:0.82rem; color:#475569;">
        ${data.reasoning.map(r => `<li>${r}</li>`).join('')}
      </ul>
      <div style="font-size:0.75rem; color:#64748b; margin-top:10px;">
        <em>Validation: ${data.validation_model} (${data.validation_score})</em>
      </div>
    </div>
  `;
}

// -----------------------------------------------------------------
// Bonus D: Sustainability & Carbon Calculator
// -----------------------------------------------------------------
async function computeSustainability() {
  const payload = {
    irrigation_method: document.getElementById('sust-method').value,
    fertilizer_type: document.getElementById('sust-fert').value,
    solar_powered_pump: document.getElementById('sust-solar').checked,
    organic_mulching: document.getElementById('sust-mulch').checked,
    crop_rotation_with_legumes: document.getElementById('sust-legume').checked,
    water_applied_liters_sqm: 4.5,
    optimal_water_liters_sqm: 4.0,
    disease_severity_pct: 5.0
  };

  try {
    const res = await fetch('/api/sustainability', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderSustainabilityScore(data);
  } catch (e) {
    console.error('Sustainability error:', e);
  }
}

function renderSustainabilityScore(data) {
  document.getElementById('sust-badge').innerText = data.rating.split('(')[1].replace(')', '');
  const box = document.getElementById('sust-score-box');

  box.innerHTML = `
    <div style="text-align:center; padding:16px 0; border-bottom:1px solid var(--border); margin-bottom:16px;">
      <div style="font-size:3.5rem; font-weight:800; color:${data.badge_color};">${data.sustainability_score}</div>
      <div style="font-weight:700; color:#334155; font-size:1.1rem;">${data.rating}</div>
      <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Formula: <code>${data.formula}</code></div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
      <div style="background:#f0fdf4; padding:12px; border-radius:10px; border:1px solid #bbf7d0;">
        <span style="font-size:0.75rem; color:#166534; font-weight:700;">WATER CONSERVED</span>
        <div style="font-size:1.3rem; font-weight:800; color:#15803d;">${(data.quantified_impact.water_saved_liters_ha / 1000000).toFixed(1)}M Liters/ha</div>
        <small style="font-size:0.7rem; color:#166534;">vs traditional flood baseline</small>
      </div>
      <div style="background:#eff6ff; padding:12px; border-radius:10px; border:1px solid #bfdbfe;">
        <span style="font-size:0.75rem; color:#1e40af; font-weight:700;">AVOIDED CARBON</span>
        <div style="font-size:1.3rem; font-weight:800; color:#1d4ed8;">${data.quantified_impact.carbon_emissions_avoided_kg_co2e} kg CO₂e</div>
        <small style="font-size:0.7rem; color:#1e40af;">avoided diesel & synthetic N emissions</small>
      </div>
    </div>

    <div style="background:#f8fafc; padding:12px; border-radius:10px;">
      <h5 style="font-size:0.85rem; margin-bottom:6px;">Actionable Farm Enhancements:</h5>
      <ul style="padding-left:18px; font-size:0.82rem; color:#475569;">
        ${data.improvement_suggestions.map(s => `<li>${s}</li>`).join('')}
      </ul>
    </div>
  `;
}

// -----------------------------------------------------------------
// Bonus E: Grounded Farmer Assistant
// -----------------------------------------------------------------
function setLanguage(lang, btn) {
  currentLanguage = lang;
  document.querySelectorAll('.btn-lang').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

function askQuick(q) {
  document.getElementById('chat-input').value = q;
  sendChatMessage();
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';

  const windowEl = document.getElementById('chat-window');

  // Append user message
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg user';
  userDiv.innerText = text;
  windowEl.appendChild(userDiv);
  windowEl.scrollTop = windowEl.scrollHeight;

  try {
    const res = await fetch('/api/assistant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, language: currentLanguage })
    });
    const data = await res.json();

    const botDiv = document.createElement('div');
    botDiv.className = 'chat-msg bot';
    botDiv.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <strong>🌱 ${data.topic}</strong>
        <button class="btn-tts" onclick="speakRaw('${data.answer.replace(/'/g, "\\'")}')">🔊 Voice</button>
      </div>
      <p>${data.answer}</p>
      <div style="font-size:0.75rem; color:#64748b; margin-top:6px; border-top:1px dashed #cbd5e1; padding-top:4px;">
        <em>Verified Source: ${data.grounded_source}</em>
      </div>
    `;
    windowEl.appendChild(botDiv);
    windowEl.scrollTop = windowEl.scrollHeight;
  } catch (e) {
    console.error('Chat error:', e);
  }
}

function speakRaw(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95;
    window.speechSynthesis.speak(u);
  }
}

// -----------------------------------------------------------------
// Bonus F & G: IoT Stream & Agentic Loop
// -----------------------------------------------------------------
async function fetchIoTTelemetry() {
  try {
    const res = await fetch('/api/iot/telemetry');
    const data = await res.json();
    const t = data.telemetry;

    document.getElementById('iot-moist').innerText = `${t.soil_moisture_pct}%`;
    document.getElementById('iot-temp').innerText = `${t.ambient_temperature_c}°C`;
    document.getElementById('iot-hum').innerText = `${t.relative_humidity_pct}%`;
    document.getElementById('iot-ph').innerText = t.soil_ph;

    const mStatus = document.getElementById('iot-moist-status');
    if (t.soil_moisture_pct < 15) {
      mStatus.innerText = 'Water Stressed';
      mStatus.style.color = '#ef4444';
    } else {
      mStatus.innerText = 'Normal Field Capacity';
      mStatus.style.color = '#10b981';
    }
  } catch (e) {
    console.error('IoT error:', e);
  }
}

async function triggerScenario(mode) {
  try {
    await fetch('/api/iot/scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: mode })
    });
    fetchIoTTelemetry();
  } catch (e) {
    console.error('Scenario error:', e);
  }
}

async function triggerAgentCycle() {
  try {
    const res = await fetch('/api/agent/cycle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crop: 'Tomato',
        stage: 'Mid-Season / Flowering',
        diagnosis: currentDiagnosis
      })
    });
    const data = await res.json();

    const valveBadge = document.getElementById('valve-status');
    valveBadge.innerText = data.valve_state;
    valveBadge.className = data.valve_state === 'OPEN' ? 'badge badge-danger' : 'badge badge-info';

    // Animate timeline
    const timeline = document.getElementById('agent-timeline');
    timeline.innerHTML = '';
    data.trace_log.forEach((logLine, idx) => {
      const step = document.createElement('div');
      step.className = 'agent-step';
      step.innerHTML = `
        <div class="step-num">${idx + 1}</div>
        <div class="step-content">${logLine}</div>
      `;
      timeline.appendChild(step);
    });

    const alertBox = document.getElementById('agent-alert-box');
    alertBox.innerHTML = `
      <div style="background:#fef3c7; border:1px solid #fde68a; padding:12px; border-radius:10px;">
        <strong>📱 Dispatched Farmer SMS / Notification:</strong>
        <p style="font-size:0.88rem; color:#92400e; margin-top:4px;">${data.farmer_alert_message}</p>
      </div>
    `;
  } catch (e) {
    console.error('Agent cycle error:', e);
  }
}
