#!/usr/bin/env python
"""
AgriSmart AI - Root Predict Entrypoint
SIH-2026 Problem Statement 1 (Mandatory Core Task)

Usage:
  python predict.py --image <path_to_leaf_image>
  python predict.py --image model/test_samples/tomato_early_blight.jpg
  python predict.py --image <path> --json
"""

import sys
import os

# Add repo root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.predict import main, predict, predict_class_label

if __name__ == "__main__":
    main()
