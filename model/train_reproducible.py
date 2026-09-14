"""
AgriSmart AI - Complete Reproducible Model Training & Evaluation Pipeline
Compliant with Model Accuracy Improvement & Real-World Validation Standards
- Backbone: MobileNetV3-Small (Pretrained on ImageNet)
- Classes: 39 plant foliage & background classes
- Transfer Learning: 2-Phase (Head Training -> Fine-Tuning)
- Loss: Class-Weighted CrossEntropyLoss with Label Smoothing
- Evaluation: Macro-F1, Top-1, Top-3, Confusion Matrix, and Real-World Benchmark
"""

import os
import sys
import io
import json
import time
import zipfile
from collections import defaultdict
from typing import List, Tuple, Dict
from PIL import Image
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T

# Project paths
BASE_DIR = r"C:\Users\prins\AGRISMART_AI\model"
PROJECT_ROOT = r"C:\Users\prins\AGRISMART_AI"
SPLIT_PATH = os.path.join(BASE_DIR, "dataset_split.json")
CLASSES_PATH = os.path.join(BASE_DIR, "classes.json")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
WEIGHTS_OUT = os.path.join(WEIGHTS_DIR, "agrismart_mobilenetv3.pth")
BEST_WEIGHTS_OUT = os.path.join(WEIGHTS_DIR, "agrismart_mobilenetv3_v2_best.pth")
METRICS_OUT = os.path.join(BASE_DIR, "metrics.json")
REPORT_METRICS_OUT = os.path.join(PROJECT_ROOT, "report", "metrics.json")
REPORT_CM_PNG = os.path.join(PROJECT_ROOT, "report", "confusion_matrix.png")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.makedirs(WEIGHTS_DIR, exist_ok=True)
os.makedirs(os.path.join(PROJECT_ROOT, "report"), exist_ok=True)

from model.network import AgriSmartVisionModel, get_field_robust_train_transforms, get_eval_transforms

class ZipDataset(Dataset):
    """High-efficiency dataset streaming directly from the dataset ZIP in RAM."""
    def __init__(self, zip_path: str, samples: List[Tuple[str, int]], transform=None):
        self.zip_path = zip_path
        self.samples = samples
        self.transform = transform
        self._zf = None

    def _get_zip(self):
        if self._zf is None:
            self._zf = zipfile.ZipFile(self.zip_path, "r")
        return self._zf

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        entry_path, class_idx = self.samples[idx]
        zf = self._get_zip()
        raw_bytes = zf.read(entry_path)
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, class_idx


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * imgs.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_acc = (correct / total) * 100.0
    return epoch_loss, epoch_acc


def evaluate_model(model, loader, criterion, device, num_classes=39):
    model.eval()
    running_loss = 0.0
    correct_top1 = 0
    correct_top3 = 0
    total = 0

    all_preds = []
    all_labels = []
    cm = np.zeros((num_classes, num_classes), dtype=int)

    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * imgs.size(0)
            probs = torch.softmax(outputs, dim=1)

            # Top 1
            _, preds = torch.max(outputs, 1)
            correct_top1 += (preds == labels).sum().item()

            # Top 3
            _, top3_preds = torch.topk(outputs, k=min(3, num_classes), dim=1)
            for i in range(labels.size(0)):
                if labels[i] in top3_preds[i]:
                    correct_top3 += 1

            total += labels.size(0)

            # Confusion Matrix updates
            p_cpu = preds.cpu().numpy()
            l_cpu = labels.cpu().numpy()
            for p, l in zip(p_cpu, l_cpu):
                cm[l, p] += 1
                all_preds.append(int(p))
                all_labels.append(int(l))

    val_loss = running_loss / total
    top1_acc = (correct_top1 / total) * 100.0
    top3_acc = (correct_top3 / total) * 100.0

    # Compute Macro Precision, Recall, F1 per class
    precisions = []
    recalls = []
    f1s = []
    per_class_metrics = {}

    for c in range(num_classes):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        per_class_metrics[c] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "support": int(cm[c, :].sum())
        }

    macro_precision = float(np.mean(precisions)) * 100.0
    macro_recall = float(np.mean(recalls)) * 100.0
    macro_f1 = float(np.mean(f1s)) * 100.0

    return {
        "loss": round(val_loss, 4),
        "top1_acc": round(top1_acc, 2),
        "top3_acc": round(top3_acc, 2),
        "macro_precision": round(macro_precision, 2),
        "macro_recall": round(macro_recall, 2),
        "macro_f1": round(macro_f1, 2),
        "confusion_matrix": cm,
        "per_class": per_class_metrics,
        "total_evaluated": total
    }


def main():
    print("=" * 70)
    print("AgriSmart AI - Model Accuracy Improvement Training Pipeline")
    print("=" * 70)

    # 1. Load classes & split definition
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        classes = json.load(f)
    num_classes = len(classes)

    with open(SPLIT_PATH, "r", encoding="utf-8") as f:
        split_data = json.load(f)

    zip_path = split_data["zip_path"]
    class_weights_raw = split_data["class_weights"]

    device = torch.device("cpu")
    print(f"Device: {device}")
    print(f"Number of classes: {num_classes}")
    print(f"Train samples: {len(split_data['train_samples'])}")
    print(f"Val samples:   {len(split_data['val_samples'])}")
    print(f"Test samples:  {len(split_data['test_samples'])}")

    # 2. Datasets & Loaders
    train_transforms = get_field_robust_train_transforms()
    eval_transforms = get_eval_transforms()

    train_ds = ZipDataset(zip_path, split_data["train_samples"], transform=train_transforms)
    val_ds = ZipDataset(zip_path, split_data["val_samples"], transform=eval_transforms)
    test_ds = ZipDataset(zip_path, split_data["test_samples"], transform=eval_transforms)

    batch_size = 32
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    # 3. Model with Pretrained ImageNet Weights
    print("\nInitializing MobileNetV3-Small with ImageNet pretrained backbone...")
    model = AgriSmartVisionModel(num_classes=num_classes, pretrained=True)
    model.to(device)

    # 4. Class-Weighted Loss with Label Smoothing
    weights_tensor = torch.tensor(class_weights_raw, dtype=torch.float32).to(device)
    # Clip extreme weights to avoid instability
    weights_tensor = torch.clamp(weights_tensor, 0.2, 5.0)
    weights_tensor = weights_tensor / weights_tensor.mean()
    criterion = nn.CrossEntropyLoss(weight=weights_tensor, label_smoothing=0.08)

    # =========================================================================
    # PHASE 1: Train Classification Head (Backbone Frozen)
    # =========================================================================
    print("\n--- PHASE 1: Training Classification Head (Backbone Frozen) ---")
    for param in model.backbone.features.parameters():
        param.requires_grad = False

    optimizer_head = optim.AdamW(
        model.backbone.classifier.parameters(),
        lr=1e-3,
        weight_decay=1e-4
    )

    epochs_phase1 = 4
    best_val_f1 = 0.0
    history = []

    for epoch in range(1, epochs_phase1 + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer_head, device)
        val_res = evaluate_model(model, val_loader, criterion, device, num_classes)
        dt = time.time() - t0

        print(f"[Phase 1 | Epoch {epoch}/{epochs_phase1}] "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.1f}% | "
              f"Val Loss: {val_res['loss']:.4f} | Val Top-1: {val_res['top1_acc']:.1f}% | "
              f"Val Top-3: {val_res['top3_acc']:.1f}% | Val Macro-F1: {val_res['macro_f1']:.1f}% | "
              f"Time: {dt:.1f}s")

        history.append({
            "phase": 1,
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 2),
            "val_loss": val_res["loss"],
            "val_top1": val_res["top1_acc"],
            "val_top3": val_res["top3_acc"],
            "val_f1": val_res["macro_f1"]
        })

        if val_res["macro_f1"] > best_val_f1:
            best_val_f1 = val_res["macro_f1"]
            torch.save(model.state_dict(), BEST_WEIGHTS_OUT)

    # =========================================================================
    # PHASE 2: Fine-Tuning Top Backbone Layers
    # =========================================================================
    print("\n--- PHASE 2: Fine-Tuning Deep Backbone Features ---")
    # Unfreeze upper residual bottleneck blocks (layers 8 to 12)
    for idx, block in enumerate(model.backbone.features):
        if idx >= 8:
            for param in block.parameters():
                param.requires_grad = True

    optimizer_fine = optim.AdamW([
        {"params": [p for i, b in enumerate(model.backbone.features) if i >= 8 for p in b.parameters()], "lr": 1.5e-4},
        {"params": model.backbone.classifier.parameters(), "lr": 4e-4}
    ], weight_decay=1e-4)

    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer_fine, T_max=3, eta_min=5e-5)

    epochs_phase2 = 3
    for epoch in range(1, epochs_phase2 + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer_fine, device)
        scheduler.step()
        val_res = evaluate_model(model, val_loader, criterion, device, num_classes)
        dt = time.time() - t0

        print(f"[Phase 2 | Epoch {epoch}/{epochs_phase2}] "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.1f}% | "
              f"Val Loss: {val_res['loss']:.4f} | Val Top-1: {val_res['top1_acc']:.1f}% | "
              f"Val Top-3: {val_res['top3_acc']:.1f}% | Val Macro-F1: {val_res['macro_f1']:.1f}% | "
              f"Time: {dt:.1f}s")

        history.append({
            "phase": 2,
            "epoch": epoch + epochs_phase1,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 2),
            "val_loss": val_res["loss"],
            "val_top1": val_res["top1_acc"],
            "val_top3": val_res["top3_acc"],
            "val_f1": val_res["macro_f1"]
        })

        if val_res["macro_f1"] > best_val_f1:
            best_val_f1 = val_res["macro_f1"]
            torch.save(model.state_dict(), BEST_WEIGHTS_OUT)

    # Save final production weights
    torch.save(model.state_dict(), WEIGHTS_OUT)
    print(f"\nSaved production weights to: {WEIGHTS_OUT}")
    print(f"Saved best checkpoint to:    {BEST_WEIGHTS_OUT}")

    # =========================================================================
    # PHASE 3: Independent Held-Out Test Set Evaluation
    # =========================================================================
    print("\n" + "=" * 70)
    print("PHASE 3: Independent Held-Out Test Set Evaluation (Never seen in training)")
    print("=" * 70)

    # Load best checkpoint for test evaluation
    if os.path.exists(BEST_WEIGHTS_OUT):
        model.load_state_dict(torch.load(BEST_WEIGHTS_OUT, map_location=device))

    test_res = evaluate_model(model, test_loader, criterion, device, num_classes)

    print(f"Held-Out Test Set Results ({test_res['total_evaluated']} samples):")
    print(f"  Top-1 Accuracy:   {test_res['top1_acc']}%")
    print(f"  Top-3 Accuracy:   {test_res['top3_acc']}%")
    print(f"  Macro-Precision:  {test_res['macro_precision']}%")
    print(f"  Macro-Recall:     {test_res['macro_recall']}%")
    print(f"  Macro-F1 Score:   {test_res['macro_f1']}%")

    # Save Confusion Matrix & Class Breakdown
    cm_list = test_res["confusion_matrix"].tolist()
    per_class_summary = {}
    for idx, cname in enumerate(classes):
        m = test_res["per_class"][idx]
        per_class_summary[cname] = m

    evaluation_report = {
        "model_architecture": "MobileNetV3-Small (Transfer Learning)",
        "pretrained_weights": "ImageNet (MobileNet_V3_Small_Weights.DEFAULT)",
        "num_classes": num_classes,
        "classes": classes,
        "dataset_split": {
            "train": len(split_data["train_samples"]),
            "validation": len(split_data["val_samples"]),
            "held_out_test": len(split_data["test_samples"])
        },
        "held_out_test_metrics": {
            "top1_accuracy_pct": test_res["top1_acc"],
            "top3_accuracy_pct": test_res["top3_acc"],
            "macro_precision_pct": test_res["macro_precision"],
            "macro_recall_pct": test_res["macro_recall"],
            "macro_f1_pct": test_res["macro_f1"],
            "test_loss": test_res["loss"]
        },
        "training_history": history,
        "per_class_metrics": per_class_summary,
        "confusion_matrix": cm_list,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(METRICS_OUT, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2)

    with open(REPORT_METRICS_OUT, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2)

    # Plot Confusion Matrix
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(16, 14))
        im = ax.imshow(test_res["confusion_matrix"], interpolation='nearest', cmap=plt.cm.Greens)
        ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        ax.set(
            title=f"AgriSmart AI — 39-Class Held-Out Test Confusion Matrix (Accuracy: {test_res['top1_acc']}%)",
            ylabel="True Class",
            xlabel="Predicted Class"
        )
        plt.tight_layout()
        plt.savefig(REPORT_CM_PNG, dpi=180)
        plt.close()
        print(f"Generated confusion matrix plot at: {REPORT_CM_PNG}")
    except Exception as e:
        print(f"Warning plotting confusion matrix: {e}")

    print("\nTraining and Evaluation Pipeline COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
