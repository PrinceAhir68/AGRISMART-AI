"""
AgriSmart AI - Model Training & Fine-Tuning Pipeline
SIH-2026 Problem Statement 1
Architecture: MobileNetV3-Small
Trains the neural network on multi-crop leaf dataset with field-condition augmentations.
"""

import os
import sys
import json
import time
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from model.network import AgriSmartVisionModel, get_field_robust_train_transforms, get_eval_transforms

CLASSES_PATH = os.path.join(BASE_DIR, "classes.json")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "agrismart_mobilenetv3.pth")
SAMPLES_DIR = os.path.join(BASE_DIR, "test_samples")

os.makedirs(WEIGHTS_DIR, exist_ok=True)

with open(CLASSES_PATH, "r") as f:
    CLASSES = json.load(f)
NUM_CLASSES = len(CLASSES)


class SyntheticFieldAgriDataset(Dataset):
    """
    Generates training batches combining real sample images and augmented
    synthetic field representations across all 18 classes to teach the network
    robust representations despite lab/field domain shifts.
    """
    def __init__(self, samples_per_class=40, transform=None):
        self.transform = transform
        self.data = []
        
        # Collect existing sample images
        sample_files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".jpg")] if os.path.exists(SAMPLES_DIR) else []
        
        for cls_idx, cls_name in enumerate(CLASSES):
            # Find matching sample file if any
            matched_file = None
            for sf in sample_files:
                parts = cls_name.lower().split("___")
                if parts[1].replace("__", "_") in sf:
                    matched_file = os.path.join(SAMPLES_DIR, sf)
                    break
            
            for _ in range(samples_per_class):
                self.data.append((cls_idx, cls_name, matched_file))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        cls_idx, cls_name, sample_path = self.data[idx]
        
        if sample_path and os.path.exists(sample_path) and np.random.rand() > 0.3:
            img = Image.open(sample_path).convert("RGB")
        else:
            # Generate synthetic training patch reflecting class pathology
            img = self._generate_synthetic_patch(cls_name)
            
        if self.transform:
            img = self.transform(img)
            
        return img, cls_idx

    def _generate_synthetic_patch(self, cls_name: str) -> Image.Image:
        """Creates an augmented 224x224 RGB image with characteristic leaf and disease color patterns."""
        arr = np.zeros((224, 224, 3), dtype=np.uint8)
        
        # Base leaf chlorophyll
        arr[:, :, 0] = np.random.randint(40, 80)
        arr[:, :, 1] = np.random.randint(110, 160)
        arr[:, :, 2] = np.random.randint(30, 70)
        
        if "healthy" in cls_name.lower():
            # Clean vibrant green
            arr[:, :, 1] = np.random.randint(130, 180)
        elif "rust" in cls_name.lower():
            # Cinnamon rust pustules
            mask = np.random.rand(224, 224) > 0.88
            arr[mask, 0] = 180
            arr[mask, 1] = 70
            arr[mask, 2] = 20
        elif "blight" in cls_name.lower():
            # Dark necrotic centers with yellow halos
            mask = np.random.rand(224, 224) > 0.85
            arr[mask, 0] = 40
            arr[mask, 1] = 30
            arr[mask, 2] = 20
        elif "spot" in cls_name.lower():
            # Tiny dark specks
            mask = np.random.rand(224, 224) > 0.92
            arr[mask, 0] = 30
            arr[mask, 1] = 25
            arr[mask, 2] = 20
            
        return Image.fromarray(arr)


def train_model(epochs: int = 5, batch_size: int = 16, lr: float = 0.001):
    print(f"Initializing AgriSmart AI MobileNetV3 Training Pipeline...")
    print(f"Classes: {NUM_CLASSES} | Epochs: {epochs} | Batch Size: {batch_size} | LR: {lr}")
    
    device = torch.device("cpu")
    print(f"Training on device: {device}")

    train_transform = get_field_robust_train_transforms()
    eval_transform = get_eval_transforms()

    train_dataset = SyntheticFieldAgriDataset(samples_per_class=30, transform=train_transform)
    val_dataset = SyntheticFieldAgriDataset(samples_per_class=10, transform=eval_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = AgriSmartVisionModel(num_classes=NUM_CLASSES, pretrained=False).to(device)

    # Load existing weights if available to resume / fine-tune
    if os.path.exists(WEIGHTS_PATH):
        try:
            state_dict = torch.load(WEIGHTS_PATH, map_location=device, weights_only=True)
            model.load_state_dict(state_dict)
            print("Loaded existing weights for transfer fine-tuning.")
        except Exception:
            pass

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    start_time = time.time()
    best_acc = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        scheduler.step()
        train_loss = running_loss / total
        train_acc = correct / total

        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, targets in val_loader:
                images, targets = images.to(device), targets.to(device)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += targets.size(0)
                val_correct += predicted.eq(targets).sum().item()

        val_acc = val_correct / val_total
        print(f"Epoch [{epoch}/{epochs}] - Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}% | Val Acc: {val_acc*100:.2f}%")

        if val_acc >= best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), WEIGHTS_PATH)

    elapsed = time.time() - start_time
    print(f"\nTraining Complete in {elapsed:.1f}s! Best Validation Accuracy: {best_acc*100:.2f}%")
    print(f"Updated weights saved to: {WEIGHTS_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train AgriSmart AI Vision Model")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    args = parser.parse_args()

    train_model(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
