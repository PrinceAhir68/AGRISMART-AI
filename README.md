# AgriSmart AI — Intelligent Agriculture for a Sustainable Future

[![SIH 2026 Internal Hackathon](https://img.shields.io/badge/SIH--2026-Internal_Hackathon-green.svg)](https://github.com)
[![Challenge Level](https://img.shields.io/badge/Challenge-Advanced_Difficulty-orange.svg)](https://github.com)
[![Core Metric](https://img.shields.io/badge/Held--Out_Field_Macro--F1-91.79%25-brightgreen.svg)](report/MODEL_REPORT.md)
[![Baseline Delta](https://img.shields.io/badge/Delta_vs_Baseline-%2B10.79%25-blue.svg)](report/MODEL_REPORT.md)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch%20%2F%20MobileNetV3-EE4C2C.svg)](https://pytorch.org)

> **Submission for Problem Statement 1 (PS-1): AGRISMART AI**  
> **L. J. Institute of Engineering and Technology [C-433]**  
> **Domain**: AI / AgriTech / Sustainability  
> **Technology**: AI/ML • Computer Vision • GenAI • IoT • Predictive Analytics  

---

## Table of Contents
1. [Overview & Implemented Modules (Core + Bonus A–G)](#1-implemented-modules-core--bonus-ag)
2. [Quickstart & Reproducibility (<5 Minutes)](#2-quickstart--reproducibility-5-minutes)
3. [Core Task Predict Interface (Section 4.1 Contract)](#3-core-task-predict-interface-section-41-contract)
4. [Datasets & Provenance](#4-datasets--provenance)
5. [Reported Metrics & Benchmark Comparison](#5-reported-metrics--benchmark-comparison)
6. [Architecture Overview](#6-architecture-overview)
7. [Known Limitations & Failure Modes](#7-known-limitations--failure-modes)
8. [Demo Video & Live Application](#8-demo-video--live-application)
9. [Originality Declaration & Citations](#9-originality-declaration--citations)

---

## 1. Implemented Modules (Core + Bonus A–G)

AgriSmart AI delivers the **Mandatory Core Task** and **all 7 Optional Bonus Modules (A through G)**:

| Module | Status | Technology / Backbone | Key Capability |
|---|---|---|---|
| **Mandatory Core Task** | **COMPLETE** | MobileNetV3-Small (Transfer Learning) + Domain-Augmentation | Leaf disease classification across 18 shared classes on field-condition held-out test set with reproducible CLI. |
| **Bonus A: Crop Recommendation** | **COMPLETE** | Agro-Climatic Multi-Parameter Scoring Engine | Recommends Top-3 crops from Soil Type, pH, NPK, Rainfall, Temp, Season, & Previous Crop with rotation synergy. |
| **Bonus B: Smart Irrigation** | **COMPLETE** | FAO-56 Penman-Monteith Water Depletion (MAD) | Real-time irrigation requirement modeling factoring in root depth, crop stage $K_c$, and 24h precipitation forecast. |
| **Bonus C: Weather Intelligence** | **COMPLETE** | Open-Meteo High-Resolution Agro API | Real-time microclimate sync, fungal spore germination risk index (0–100), and spray drift safety warnings. |
| **Bonus D: Sustainability Score** | **COMPLETE** | Transparent Published Index Formula | Evaluates water efficiency, chemical optimization, and soil carbon; outputs kg $CO_2e$ avoided and liters saved. |
| **Bonus E: Farmer Assistant (GenAI)** | **COMPLETE** | Grounded ICAR/FAO Agronomic Corpus + Web Speech Audio | Multilingual voice & text assistance in English, Hindi (हिन्दी), Gujarati (ગુજરાતી), and Marathi (मराठी). |
| **Bonus F: IoT Telemetry Integration** | **COMPLETE** | ESP32-S3 Edge Gateway Simulator | Real-time telemetry feed (Moisture %, Temp, RH %, pH, NPK) with live drought/rain anomaly injection. |
| **Bonus G: Agentic Autonomous Advisor** | **COMPLETE** | 4-Stage Autonomous ReAct Loop | Continuous observe-reason-decide-act loop with automated solenoid valve actuation and farmer alert dispatch. |

---

## 2. Quickstart & Reproducibility (<5 Minutes)

Judges can reproduce predictions, run the full test suite, or launch the interactive web dashboard in under 5 minutes.

### Step 1: Clone and Enter Repository
```bash
git clone https://github.com/your-team/AGRISMART_AI.git
cd AGRISMART_AI
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Core Disease Prediction CLI (Under 5 Seconds)
```bash
# Test Tomato Early Blight sample
python predict.py --image model/test_samples/tomato_early_blight.jpg

# Test Corn Common Rust sample with JSON advisory
python predict.py --image model/test_samples/corn_common_rust.jpg --json
```

### Step 4: Run Automated Verification Suite
```bash
python -m unittest tests/test_core_predict.py tests/test_bonus_modules.py
```
*(All 10 unit tests pass with zero failures).*

### Step 5: Launch Interactive Web Dashboard
```bash
python app/main.py
```
Open your browser at: **`http://127.0.0.1:8000`**

---

## 3. Core Task Predict Interface (Section 4.1 Contract)

Per Section 4.1, AgriSmart AI exposes both a **Python function interface** and a **command-line CLI**:

### Python API Interface
```python
from model.predict import predict, predict_class_label

# 1. Exact Section 4.1 contract: predict(image_path) -> class_label
class_label = predict_class_label("path/to/leaf.jpg")
print("Predicted Class:", class_label)
# Output: 'Tomato___Early_blight'

# 2. Rich structured advisory dictionary
result = predict("path/to/leaf.jpg")
print(result["display_name"], result["confidence"])
print("Precautions:", result["precautions"])
print("Chemical Remedy:", result["chemical_treatment"])
print("Hindi Advisory:", result["translations"]["hi"]["action"])
```

### CLI Command Interface
```bash
python predict.py --image <image_path>
```
**Sample Terminal Output:**
```text
Predicted Class: Tomato___Early_blight
Disease Name:    Tomato Early Blight
Confidence:      94.0%
Status:          DISEASED

Immediate Precautions:
  * Prune and burn/dispose of lower infected leaves immediately to prevent upward spore splash.
  * Avoid overhead sprinkler irrigation; switch strictly to root drip irrigation to keep foliage dry.
  * Ensure adequate plant spacing (60cm x 45cm) to promote good air circulation.

Recommended Treatment:
  Apply Mancozeb 75% WP @ 2.5g/L or Chlorothalonil 75% WP @ 2g/L at 10-day intervals if disease incidence exceeds 10%.

हिंदी मार्गदर्शन (Hindi Advisory):
  निचली संक्रमित पत्तियों को तुरंत तोड़कर खेत से दूर नष्ट करें। पत्तों पर सीधे पानी का छिड़काव न करें, ड्रिप सिंचाई अपनाएं।
```

---

## 4. Datasets & Provenance

| Role | Dataset Source | Nature & Scale | License / Citation |
|---|---|---|---|
| **Training & Validation** | **PlantVillage** | ~54,000 lab-condition leaf images on uniform backgrounds. | Hughes & Salathé (2015), CC-BY 4.0 |
| **Held-Out Test Set** | **PlantDoc-Style Field Set** | 1,540 field-condition images with complex lighting, shadows, occlusions, and background soil clutter. | Singh et al. (2020), CoDS-COMAD |
| **Crop Recommendation** | **ICAR / NBSS&LUP Agro-Met Matrix** | 2,200 multi-location soil-crop-climate records across Western & Central India. | ICAR Krishi Repository (Public Agronomic Data) |
| **Disease Guidance** | **ICAR Extension & TNAU Agritech** | Standardized symptom profiles, organic bio-treatments, and chemical controls. | ICAR-IIHR / CPRI Agronomic Handbooks |

---

## 5. Reported Metrics & Benchmark Comparison

Detailed one-page report available at [`report/MODEL_REPORT.md`](report/MODEL_REPORT.md).

### Metric Comparison on Held-Out Field Test Set
| Metric | Organizers' Baseline | AgriSmart AI (Ours) | Delta / Improvement |
|---|---|---|---|
| **Macro-Averaged F1 (Primary Metric)** | **0.8100 (81.0%)** | **0.9179 (91.79%)** | **+10.79%** 🚀 |
| **Overall Accuracy** | 0.8250 (82.5%) | **0.9188 (91.88%)** | **+9.38%** |
| **Inference Latency** | ~120 ms (ResNet-50) | **38 ms** (MobileNetV3-Small) | **3.1x Faster** |
| **Model Size** | ~98 MB | **5.06 MB** | **94.8% Smaller** |

### Confusion Matrix
![Confusion Matrix Heatmap](report/confusion_matrix.png)

---

## 6. Architecture Overview

```
                          [FARMER USER INTERFACE]
             (Web Dashboard • Multilingual Voice • Camera Input)
                                    │
                                    ▼
                          [FastAPI BACKEND SERVER]
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
[CORE VISION ENGINE]       [AGRONOMY ENGINES]          [IOT & AUTONOMOUS AGENT]
- MobileNetV3 Backbone     - Bonus A: Crop Rec         - Bonus F: ESP32 Simulator
- 18 Disease/Health Cls    - Bonus B: FAO-56 Irrig       (Moisture, Temp, RH, pH)
- Field-Robust Augment     - Bonus C: Open-Meteo       - Bonus G: Agentic Advisor
- 38ms CPU Inference       - Bonus D: Sustainability     (Perceive -> Reason ->
- ICAR Grounded Advisory   - Bonus E: GenAI Voice        Decide -> Actuate Valve)
```

---

## 7. Known Limitations & Failure Modes

1. **Extreme Clutter & Sub-20% Frame Coverage**: When smartphone photos are taken from several meters away where weeds cover >80% of the frame, classification confidence drops. The UI coaches farmers with dynamic framing guides.
2. **Multiple Overlapping Diseases**: In rare cases where a leaf has both bacterial spot and early blight simultaneously, the model predicts the visually dominant pathology.
3. **Severe Lens Flare**: Direct midday sunlight reflecting off wet cuticles can create specular white spots. Diffused morning/evening photography is recommended.

---

## 8. Demo Video & Live Application

- **Recorded Walkthrough (3–5 mins)**: [Demo Video Link (YouTube Unlisted Placeholder)](https://youtu.be/agrismart-sih2026-demo)
- **Local Live App**: `http://127.0.0.1:8000`
- **Docker Deployment**: Supported via `Dockerfile` for single-command production launch.

---

## 9. Originality Declaration & Citations

### Originality Declaration
*In compliance with Section 8 of the SIH-2026 Problem Statement 1 rules:*
- All substantive application architecture, domain-adaptation preprocessing, FAO-56 irrigation logic, sustainability equations, multilingual farmer assistant, and autonomous agentic loop were uniquely engineered during the competition window.
- No third-party codebase or public competition notebook was copied wholesale.

### Open-Source Library & Framework Citations
1. **PyTorch & Torchvision**: Paszke et al., *PyTorch: An Imperative Style, High-Performance Deep Learning Library*, NeurIPS 2019.
2. **MobileNetV3**: Howard et al., *Searching for MobileNetV3*, ICCV 2019.
3. **Open-Meteo**: Zippenfenig, P., *Open-Meteo Weather API*, open-meteo.com.
4. **FAO Irrigation and Drainage Paper 56**: Allen, R. G. et al., *Crop Evapotranspiration - Guidelines for Computing Crop Water Requirements*, FAO Rome, 1998.
5. **ICAR Agronomic Guidelines**: Indian Council of Agricultural Research Technical Publications (2020–2025).

---

**Developed for SIH - 2026 Internal Hackathon | L. J. Institute of Engineering and Technology [C-433]**
