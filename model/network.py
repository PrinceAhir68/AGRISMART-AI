"""
AgriSmart AI - Computer Vision Architecture
Backbone: MobileNetV3-Small (Transfer Learning)
Designed for low-latency, high-accuracy leaf disease detection under both lab and real-world field conditions.
"""

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T


class AgriSmartVisionModel(nn.Module):
    """
    MobileNetV3-Small backbone with a custom multi-layer classification head,
    regularized with Dropout and Batch Normalization for domain robustness.
    """
    def __init__(self, num_classes=39, pretrained=False):
        super(AgriSmartVisionModel, self).__init__()
        # Load backbone
        self.backbone = models.mobilenet_v3_small(weights=None)
        
        # Replace classifier
        in_features = self.backbone.classifier[0].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.BatchNorm1d(512),
            nn.Hardswish(inplace=True),
            nn.Dropout(p=0.25),
            nn.Linear(512, 128),
            nn.Hardswish(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


def get_eval_transforms():
    """
    Standard preprocessing for validation and inference.
    Resizes image to 224x224 and normalizes using ImageNet mean & std.
    """
    return T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def get_field_robust_train_transforms():
    """
    Data augmentation pipeline designed specifically to close the domain gap
    between lab-condition training images (PlantVillage) and held-out real field images (PlantDoc).
    Includes:
    - Random horizontal & vertical flips
    - Random affine (rotation, translation, scaling)
    - Color jitter (simulating varied sunlight, cloud shadows)
    - Gaussian blur (simulating hand-held smartphone camera motion)
    """
    return T.Compose([
        T.Resize((256, 256)),
        T.RandomResizedCrop(224, scale=(0.75, 1.0)),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.2),
        T.RandomRotation(degrees=25),
        T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.25, hue=0.1),
        T.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 1.5)),
        T.ToTensor(),
        T.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
