# AgriSmart AI — Autonomous Agricultural Intelligence & Pathology Platform

[![Live Website](https://img.shields.io/badge/Live_Website-GitHub_Pages-brightgreen.svg)](https://princeahir68.github.io/AGRISMART-AI/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/PrinceAhir68/AGRISMART-AI)
[![Held-Out Test Accuracy](https://img.shields.io/badge/Held--Out_Test_Accuracy-95.05%25-success.svg)](model/metrics.json)
[![Dataset](https://img.shields.io/badge/Dataset-PlantVillage_54K-orange.svg)](https://doi.org/10.17632/tywbtsjrjv.1)
[![License](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch%20%2F%20MobileNetV3-EE4C2C.svg)](https://pytorch.org)

> **Developed by Syntax squad**  
> **Source Code & Project Home**: [https://github.com/PrinceAhir68/AGRISMART-AI](https://github.com/PrinceAhir68/AGRISMART-AI)  
> **Live Web Application**: [https://princeahir68.github.io/AGRISMART-AI/](https://princeahir68.github.io/AGRISMART-AI/)  
> **Team Contact**: [princeahir688@gmail.com](mailto:princeahir688@gmail.com)  

---

## 📽️ Demo Video

The complete product walkthrough, live foliar scan, multilingual voice interaction, and hardware gateway demonstration is included in this repository:

* **Video File**: [`demo/agrismart_ai_demo.mp4`](demo/agrismart_ai_demo.mp4) (Tracked via Git LFS)
* **Direct Stream / Download**: Available directly from the GitHub repository release and `demo/` folder.
* **Key Demonstration Highlights**:
  1. Instant foliar pathology scanning with compulsory crop selection.
  2. 5-Stage progressive scan visualization and 7-level ICAR phytosanitary diagnosis.
  3. High-contrast sunlight readability mode for in-field daytime inspection.
  4. FAO-56 Penman-Monteith 4-state precision irrigation decision engine.
  5. Kisan Mitra multilingual voice assistant (English, Hindi, Gujarati, Marathi).
  6. Real physical IoT sensor hub with zero-fake-data policy.

---

## 📑 Table of Contents
1. [Platform Overview & Capabilities](#1-platform-overview--capabilities)
2. [Datasets, Source & Licensing](#2-datasets-source--licensing)
3. [Held-Out Model Architecture & Metrics](#3-held-out-model-architecture--metrics)
4. [Live Website & Deployment Guides](#4-live-website--deployment-guides)
5. [Quickstart & Reproducibility](#5-quickstart--reproducibility)
6. [Core Vision Predict CLI Contract](#6-core-vision-predict-cli-contract)
7. [Edge IoT Hardware Integration](#7-edge-iot-hardware-integration)
8. [About Us & Team Syntax squad](#8-about-us--team-syntax-squad)

---

## 1. Platform Overview & Capabilities

AgriSmart AI is a production-grade, autonomous agricultural intelligence platform designed specifically for real-world farming environments:

| Module | Purpose | Technology & Specification |
|---|---|---|
| **AI Plant Doctor** | Compulsory-crop foliar diagnosis across 39 classes & 14 crops | MobileNetV3-Small (1.34M params, 95.05% held-out test accuracy, 38ms CPU latency) |
| **Smart Crop Planner** | Agro-climatic crop suitability scoring | Multi-factor matrix (Soil NPK, pH, Rainfall, Season, Crop Rotation) |
| **Precision Irrigation** | Scientific water management & pump control | FAO-56 Penman-Monteith Evapotranspiration + Open-Meteo 24h precipitation forecast |
| **Sustainability Index** | Transparent farm environmental footprint score | Published index formula for water conservation, carbon sequestration, and chemical optimization |
| **Kisan Mitra AI** | Multilingual agronomy voice advisor | Grounded ICAR agronomic corpus with speech synthesis in English, Hindi, Gujarati, Marathi |
| **Edge IoT Center** | Physical agricultural sensor gateway | USB Serial / Wi-Fi / Bluetooth BLE bridge with strict zero-fake-data policy (`--` for unprobed channels) |

---

## 2. Datasets, Source & Licensing

AgriSmart AI is trained and evaluated on internationally recognized, peer-reviewed open agricultural datasets with complete provenance and legal licensing:

### A. Primary Foliar Disease Dataset
* **Dataset Name**: **PlantVillage Foliar Pathology Dataset**
* **Creators / Authors**: David P. Hughes & Marcel Salathé (Pennsylvania State University & EPFL)
* **Academic Citation**:  
  > Hughes, D. P., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics.* arXiv preprint [arXiv:1511.08060](https://arxiv.org/abs/1511.08060).
* **Official Data Sources & Persistent Identifiers**:
  * **Mendeley Data**: [doi:10.17632/tywbtsjrjv.1](https://doi.org/10.17632/tywbtsjrjv.1)
  * **Kaggle Official Mirror**: [https://www.kaggle.com/datasets/emmarex/plantdisease](https://www.kaggle.com/datasets/emmarex/plantdisease) & [https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset)
  * **CrowdAI Challenge**: PlantVillage Disease Classification Benchmark
* **Licensing**:
  * **Creative Commons Attribution-ShareAlike 4.0 International ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/))**
  * Portions released under **Creative Commons Zero ([CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/))** Public Domain Dedication.
* **Scale & Scope**:
  * 54,305 curated foliar disease images.
  * 39 fine-grained classes covering 14 crops: Tomato, Potato, Corn (Maize), Apple, Grape, Bell Pepper, Orange / Citrus, Blueberry, Cherry, Peach, Raspberry, Soybean, Squash, Strawberry.
  * Captures both healthy baseline foliar structures and 25 distinct phytopathogens (fungal, bacterial, oomycete, viral, and mite damage).

### B. Held-Out Evaluation Protocol & Zero-Fabrication Policy
* **Split Ratio**: Stratified **80% Training (43,444 images)**, **10% Validation (5,430 images)**, and **10% Held-Out Test (5,431 images)**.
* **Reproducibility**: Partitioned using a fixed pseudorandom seed (`seed=42`) with strict stratified sampling to ensure no patient/image leakage across splits.
* **Held-Out Test Accuracy**: **95.05%** across all 39 classes on MobileNetV3-Small (audited and verified in `model/metrics.json`).

### C. Agronomic Knowledge Base & Weather Sources
* **ICAR Extension Guidelines**: Indian Council of Agricultural Research (ICAR) — Central Potato Research Institute (CPRI) & Indian Institute of Horticultural Research (IIHR) phytosanitary handbooks.
* **FAO-56 Irrigation Standard**: Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop evapotranspiration - Guidelines for computing crop water requirements.* FAO Irrigation and drainage paper 56.
* **Weather Data**: Open-Meteo High-Resolution Agro Weather API ([CC-BY 4.0](https://open-meteo.com/en/license)).

---

## 3. Held-Out Model Architecture & Metrics

Detailed held-out test evaluation report available at [`report/MODEL_REPORT.md`](report/MODEL_REPORT.md).

| Specification | Metric Value | Architectural Context |
|---|---|---|
| **Backbone Architecture** | **MobileNetV3-Small** | Edge-optimized depthwise separable convolutions with hard-swish non-linearities |
| **Model Size / Checkpoint** | **5.06 MB** (`agrismart_mobilenetv3.pth`) | Compact edge footprint suitable for smartphone and micro-gateway deployment |
| **Total Parameters** | **1,340,000 (1.34M)** | Highly parameter-efficient transfer-learning classifier |
| **Held-Out Test Accuracy** | **95.05%** | Evaluated on 5,431 unseen held-out test images across all 39 classes |
| **Macro-Averaged F1 Score** | **0.9179 (91.79%)** | Balanced precision and recall across rare and dominant foliar pathologies |
| **Inference Latency** | **38 ms** (Intel CPU) / **12 ms** (Edge GPU) | Real-time immediate field classification |

---

## 4. Live Website & Deployment Guides

### Option A: Open Live Website Directly
The project is configured for automated hosting on GitHub Pages:
👉 **[https://princeahir68.github.io/AGRISMART-AI/](https://princeahir68.github.io/AGRISMART-AI/)**

### Option B: Local Full-Stack Deployment (FastAPI + PyTorch)
```bash
# 1. Clone repository
git clone https://github.com/PrinceAhir68/AGRISMART-AI.git
cd AGRISMART-AI

# 2. Install requirements
pip install -r requirements.txt

# 3. Launch full-stack platform
python app/main.py
```
Open **`http://127.0.0.1:8000`** in any web browser.

### Option C: GitHub Pages Configuration in Your Fork
1. Go to your repository **Settings** on GitHub.
2. In the left navigation, click **Pages**.
3. Under **Build and deployment**:
   * **Source**: Select `Deploy from a branch`.
   * **Branch**: Select `main` (or `master`) and directory `/docs`.
   * Click **Save**.
4. GitHub Pages will build and publish your live website URL in ~60 seconds!

---

## 5. Quickstart & Reproducibility

### Run Complete Test Suite (104 Tests)
```bash
python -m unittest discover tests
```
*All 104 unit, integration, and security tests pass with 100% success.*

### Run One-Click Windows Launcher
Double-click `START_AGRISMART.bat` in the project root to automatically launch dependencies and the server.

---

## 6. Core Vision Predict CLI Contract

Per standardized competition specifications, AgriSmart AI exposes both a command-line interface and a Python function API:

### Python Interface
```python
from model.predict import predict, predict_class_label

# 1. Predict class label string
class_label = predict_class_label("model/test_samples/tomato_early_blight.jpg", target_crop="Tomato")
print("Predicted Class:", class_label)
# Output: 'Tomato___Early_blight'

# 2. Rich structured advisory dictionary
result = predict("model/test_samples/tomato_early_blight.jpg", target_crop="Tomato")
print(result["display_name"], result["confidence"])
print("Chemical Remedy:", result["chemical_treatment"])
print("Organic Treatment:", result["organic_treatment"])
```

### CLI Command Interface
```bash
# Standard console output
python predict.py --image model/test_samples/tomato_early_blight.jpg --crop Tomato

# JSON machine-readable output
python predict.py --image model/test_samples/corn_common_rust.jpg --crop Corn --json
```

---

## 7. Edge IoT Hardware Integration

AgriSmart AI interfaces directly with agricultural sensor microcontrollers:
* **Microcontrollers**: Arduino Uno, ESP32-S3, Raspberry Pi Pico W.
* **Supported Physical Sensors**: Capacitive Soil Moisture Sensor v1.2 / v2.0, DHT22/SHT31 (Temp & Humidity), Analog pH probe, NPK Optical Probe.
* **Connection Modes**: USB Serial Cable (COM/ttyACM), Local Wi-Fi (HTTP POST Ingestion), Bluetooth Low Energy (Web Bluetooth BLE).
* **Zero-Fake-Data Policy**: Any disconnected physical sensor strictly reports `--` rather than fabricated mock readings.

---

## 8. About Us & Team Syntax squad

* **Team Name**: **Syntax squad**
* **Project Repository**: [https://github.com/PrinceAhir68/AGRISMART-AI](https://github.com/PrinceAhir68/AGRISMART-AI)
* **Live Deployment**: [https://princeahir68.github.io/AGRISMART-AI/](https://princeahir68.github.io/AGRISMART-AI/)
* **Contact Email**: [princeahir688@gmail.com](mailto:princeahir688@gmail.com)
* **Author / Maintainer**: Prince Ahir

*Built with passion for sustainable agriculture and empowering smallholder farmers worldwide.*
