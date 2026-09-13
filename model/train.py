import os
import sys
import io
import time
import json
import random
import zipfile
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import torchvision.models as models
from PIL import Image
from torchvision import transforms

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

DATASET1_DIR = r"D:\AGRISMART\Plant_leaf_diseases_dataset_with_augmentation\Plant_leave_diseases_dataset_with_augmentation"
DATASET2_ZIP = r"D:\AGRISMART\Data for Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network\Data for Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network\Plant_leaf_diseases_dataset_without_augmentation.zip"
PROJECT_ROOT = r"D:\NewAgriSmart\AGRISMART_AI_PORTABLE"
CLASSES_PATH = os.path.join(PROJECT_ROOT, "model", "classes.json")
WEIGHTS_PATH = os.path.join(PROJECT_ROOT, "model", "weights", "agrismart_mobilenetv3.pth")

with open(CLASSES_PATH, "r") as f:
    classes = json.load(f)

NUM_CLASSES = len(classes)
print(f"Loaded {NUM_CLASSES} classes from classes.json", flush=True)

def get_folder_name(cls_name):
    if "Pepper__bell" in cls_name:
        return "Pepper,_bell___" + cls_name.split("___")[1]
    if cls_name == "Corn___Gray_leaf_spot":
        return "Corn___Cercospora_leaf_spot Gray_leaf_spot"
    return cls_name

print(f"Opening Dataset 2 ZIP archive...", flush=True)
z2 = zipfile.ZipFile(DATASET2_ZIP, 'r')
all_zip_names = set([n for n in z2.namelist() if n.lower().endswith(('.jpg', '.jpeg', '.png'))])
print(f"[OK] Archive opened with {len(all_zip_names)} images.", flush=True)

print("Loading MobileNetV3-Small backbone...", flush=True)
base_model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
base_model.eval()

class FeatureExtractor(nn.Module):
    def __init__(self, mobilenet):
        super().__init__()
        self.features = mobilenet.features
        self.avgpool = mobilenet.avgpool
    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return x

feature_extractor = FeatureExtractor(base_model)
feature_extractor.eval()

eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

TRAIN_PER_DS = 75   # 75 from DS1 + 75 from DS2 = 150 train per class (5,700 total train)
VAL_PER_DS = 25     # 25 from DS1 + 25 from DS2 = 50 val per class (1,900 total val)

train_features, train_labels = [], []
val_features, val_labels = [], []

start_time = time.time()
print(f"\nBeginning multi-dataset feature extraction across ALL {NUM_CLASSES} classes...", flush=True)

for cls_idx, cls_name in enumerate(classes):
    folder = get_folder_name(cls_name)
    
    # 1. Dataset 1 (Augmented disk folder)
    p1 = os.path.join(DATASET1_DIR, folder)
    ds1_files = sorted([f for f in os.listdir(p1) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    random.shuffle(ds1_files)
    
    ds1_train = ds1_files[:TRAIN_PER_DS]
    ds1_val = ds1_files[TRAIN_PER_DS:TRAIN_PER_DS + VAL_PER_DS]
    
    for f in ds1_train:
        img_path = os.path.join(p1, f)
        img = Image.open(img_path).convert("RGB")
        t = eval_transform(img).unsqueeze(0)
        with torch.no_grad():
            feat = feature_extractor(t).squeeze(0)
        train_features.append(feat)
        train_labels.append(cls_idx)
        
    for f in ds1_val:
        img_path = os.path.join(p1, f)
        img = Image.open(img_path).convert("RGB")
        t = eval_transform(img).unsqueeze(0)
        with torch.no_grad():
            feat = feature_extractor(t).squeeze(0)
        val_features.append(feat)
        val_labels.append(cls_idx)
        
    # 2. Dataset 2 (Unaugmented ZIP archive)
    ds2_files = sorted([n for n in all_zip_names if f"/{folder}/" in n])
    random.shuffle(ds2_files)
    
    ds2_train = ds2_files[:TRAIN_PER_DS]
    ds2_val = ds2_files[TRAIN_PER_DS:TRAIN_PER_DS + VAL_PER_DS]
    
    for zip_entry in ds2_train:
        data = z2.read(zip_entry)
        img = Image.open(io.BytesIO(data)).convert("RGB")
        t = eval_transform(img).unsqueeze(0)
        with torch.no_grad():
            feat = feature_extractor(t).squeeze(0)
        train_features.append(feat)
        train_labels.append(cls_idx)
        
    for zip_entry in ds2_val:
        data = z2.read(zip_entry)
        img = Image.open(io.BytesIO(data)).convert("RGB")
        t = eval_transform(img).unsqueeze(0)
        with torch.no_grad():
            feat = feature_extractor(t).squeeze(0)
        val_features.append(feat)
        val_labels.append(cls_idx)
        
    total_cls = len(ds1_train) + len(ds1_val) + len(ds2_train) + len(ds2_val)
    print(f"  [{cls_idx+1:2d}/{NUM_CLASSES}] Ingested {cls_name:42s}: {len(ds1_train)+len(ds2_train):3d} train, {len(ds1_val)+len(ds2_val):2d} val (Total: {total_cls:3d})", flush=True)

X_train = torch.stack(train_features)
y_train = torch.tensor(train_labels, dtype=torch.long)
X_val = torch.stack(val_features)
y_val = torch.tensor(val_labels, dtype=torch.long)

elapsed = time.time() - start_time
print(f"\nFeature extraction completed in {elapsed:.1f}s.", flush=True)
print(f"X_train: {X_train.shape}, y_train: {y_train.shape}", flush=True)
print(f"X_val:   {X_val.shape}, y_val:   {y_val.shape}", flush=True)

# 38-class Classification Head
classifier = nn.Sequential(
    nn.Linear(576, 512),
    nn.BatchNorm1d(512),
    nn.Hardswish(inplace=True),
    nn.Dropout(p=0.25),
    nn.Linear(512, 128),
    nn.Hardswish(inplace=True),
    nn.Dropout(p=0.20),
    nn.Linear(128, NUM_CLASSES)
)

criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(classifier.parameters(), lr=1.8e-3, weight_decay=1e-4)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)

train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

print(f"\nTraining 38-class classification head for 50 epochs...", flush=True)
classifier.train()
for epoch in range(1, 51):
    total_loss = 0.0
    correct = 0
    total = 0
    for bx, by in train_loader:
        optimizer.zero_grad()
        out = classifier(bx)
        loss = criterion(out, by)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * bx.size(0)
        correct += (out.argmax(dim=1) == by).sum().item()
        total += bx.size(0)
    scheduler.step()

    if epoch % 10 == 0 or epoch == 50:
        acc = correct / total * 100
        print(f"  Epoch {epoch:2d}/50 - Loss: {total_loss/total:.4f} - Training Accuracy: {acc:.2f}%", flush=True)

# Full 38-class Validation
classifier.eval()
with torch.no_grad():
    val_out = classifier(X_val)
    val_preds = val_out.argmax(dim=1)
    val_acc = (val_preds == y_val).sum().item() / len(y_val) * 100
    print(f"\n" + "=" * 80, flush=True)
    print(f" FULL 38-CLASS DUAL-DATASET VALIDATION ACCURACY: {val_acc:.2f}% ({len(y_val)} held-out samples)", flush=True)
    print("=" * 80, flush=True)

# Grouped Crop Accuracy Breakdown
print("\nCrop-Level Breakdown on Held-Out Validation Set:", flush=True)
crops_set = sorted(list(set([c.split("___")[0] for c in classes])))
for crop in crops_set:
    crop_indices = [i for i, c in enumerate(classes) if c.startswith(crop)]
    mask = torch.zeros(len(y_val), dtype=torch.bool)
    for idx in crop_indices:
        mask = mask | (y_val == idx)
    
    total_crop = mask.sum().item()
    if total_crop > 0:
        # Check if predicted class belongs to same crop
        pred_crops = [classes[p].split("___")[0] for p in val_preds[mask]]
        crop_correct = sum(1 for pc in pred_crops if pc == crop)
        exact_disease_correct = (val_preds[mask] == y_val[mask]).sum().item()
        print(f"  {crop:15s} ({len(crop_indices)} classes): Crop Acc: {crop_correct}/{total_crop} ({crop_correct/total_crop*100:5.1f}%) | Disease Acc: {exact_disease_correct}/{total_crop} ({exact_disease_correct/total_crop*100:5.1f}%)", flush=True)

# Assemble and save weights
full_model = models.mobilenet_v3_small(weights=None)
full_model.classifier = classifier
full_model.features.load_state_dict(base_model.features.state_dict())

agri_state_dict = {}
for k, v in full_model.state_dict().items():
    agri_state_dict[f"backbone.{k}"] = v

torch.save(agri_state_dict, WEIGHTS_PATH)
print(f"\n[SUCCESS] Successfully saved 38-class trained weights to: {WEIGHTS_PATH}!", flush=True)
