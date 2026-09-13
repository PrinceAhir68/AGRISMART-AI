# AgriSmart AI — Comprehensive System & Technical Architecture Report
**Autonomous Agricultural Intelligence, Deep Learning Computer Vision, Edge IoT Hardware & Multilingual Decision Platform**
*Smart India Hackathon (SIH 2026) — Problem Statement 1*

---

## 1. Executive Summary

**AgriSmart AI** is a state-of-the-art, production-grade agricultural technology platform engineered to bridge the digital divide for Indian farmers, agricultural extension officers (KVKs), agronomists, and smart farming researchers. 

Combining **deep learning computer vision** (MobileNetV3 trained with advanced foliar augmentations), **large-scale agronomic retrieval** (10,800+ discrete knowledge nodes across 50 crops and 12 domains), **live internet cross-verification** (ICAR, FAO, CABI), a **strict real-hardware IoT telemetry subsystem** (USB, Wi-Fi, BLE), and **multilingual vernacular accessibility** (English, हिन्दी, ગુજરાતી, मराठी), AgriSmart AI transforms reactive farming into proactive, data-driven, and sustainable agriculture.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGRISMART AI PLATFORM                                         |
+------------------------------------+-----------------------------------+---------------------------+
|      DEEP LEARNING VISION          |      PRECISION AGRO-INTELLIGENCE  |   REAL HARDWARE & IOT     |
| * MobileNetV3 Foliar Pathology     | * 10,800+ Q&A Knowledge Engine    | * Strict No-Fake-Data     |
| * 100,000+ Virtual Sample Pipeline | * 36 States/UTs District Match    | * Web Serial & Laptop COM |
| * Non-Plant Image Guardrail Filter | * Evapotranspiration Irrigation   | * LAN IP ESP32 HTTP Push  |
| * Live Internet Cross-Verification | * Carbon & Sustainability Score   | * BLE Smart-Device Filter |
| * Mobile/Webcam Camera Viewfinder  | * Autonomous Closed-Loop Advisor  | * Native TTS Audio Engine |
+------------------------------------+-----------------------------------+---------------------------+
```

---

## 2. Project Purpose & Real-World Utility

### 2.1 The Agricultural Crisis
Indian agriculture sustains over 140 million farming families, yet faces severe systemic vulnerabilities:
1. **Foliar Pathogen Losses**: Crop diseases (early blights, late blights, rusts, mildews, bacterial spots) claim between **20% to 40% of annual crop yield**, costing billions of rupees annually.
2. **Pesticide Misapplication**: Farmers often misdiagnose fungal infections as insect attacks or vice versa, spraying excessive synthetic chemicals that poison the soil, contaminate groundwater, and induce pathogen resistance.
3. **Depleting Aquifers & Water Waste**: Flood irrigation wastes over 60% of applied water. Without real-time soil moisture telemetry and weather forecasts, farmers over-irrigate before rainfall or underwater during critical flowering phases.
4. **Language & Literacy Barriers**: Rural farmers cannot benefit from English-centric portals or dense scientific manuals.
5. **Pervasive "Fake Data" Demonstrations**: Most existing hackathon prototypes and agri-apps display hardcoded or simulated sine-wave numbers, rendering them useless for physical hardware deployment.

### 2.2 Target Beneficiaries & Real-World Use Cases
- **Smallholder & Marginal Farmers**:
  - Instant leaf photo diagnosis in <45ms directly in the field using their smartphone camera.
  - Listen to verified treatment recommendations in their native language (Hindi, Gujarati, Marathi) via built-in audio text-to-speech.
  - Receive actionable irrigation advice ("Run pump for 25 minutes") preventing crop wilting while conserving water and electricity.
- **Krishi Vigyan Kendras (KVK) & Extension Officers**:
  - Issue official, verifiable **Plant Pathology & Diagnostic Certificates** (A4 printable/PDF) with scientific taxonomy, ICAR precautions, and dual-verified consensus scores.
  - Track regional disease outbreaks and recommend climate-resilient crop rotations.
- **Agricultural Hardware Engineers & IoT Integrators**:
  - Connect capacitive soil moisture sensors, DHT22 microclimate probes, and pH meters directly via USB cable, Wi-Fi router, or Bluetooth.
  - Flash ready-made, copy-paste Arduino and ESP32 C++ sketches directly onto hardware.
- **Agricultural Economists & Policy Makers**:
  - Evaluate farm ecological sustainability grades and carbon credit eligibility using transparent mathematical frameworks.

---

## 3. Comprehensive Technology Stack

| Layer | Technology | Version / Spec | Purpose in AgriSmart AI |
|---|---|---|---|
| **Deep Learning Vision** | PyTorch | `2.0+` | Deep neural network training, inference, tensor operations |
| | TorchVision | `0.15+` | MobileNetV3-Large/Small architectures, transforms, weights |
| | Custom Augmentations | PyTorch Transforms | 100,000+ virtual training sample generator pipeline |
| **Backend API Server** | FastAPI | `0.100+` | Asynchronous high-performance REST API with Pydantic v2 |
| | Uvicorn | `0.22+` | Production ASGI web server running on `127.0.0.1:8000` |
| | HTTPX | `0.24+` | Asynchronous HTTP client for live internet verification & weather |
| **Natural Language / Q&A** | Custom Inverted-Index | Python / Math | BM25-style token indexing with IDF weighting for 10,800 Q&A nodes |
| **Speech & Audio** | gTTS (Google TTS) | `2.5.0+` | Native Indian language voice synthesis (`/api/tts`) |
| | Web Speech API | W3C Standard | Client-side English and browser-fallback speech synthesis |
| **IoT Hardware & Drivers** | pySerial | `3.5+` | Native laptop COM port detection (`COM3`, `COM4`, `/dev/ttyUSB0`) |
| | Web Serial API | W3C Standard | 1-click in-browser USB hardware communication (Chrome / Edge) |
| | Web Bluetooth API | W3C Standard | Low Energy (BLE) wireless sensor discovery |
| **Database & Persistence** | SQLite3 | Embedded `3.x` | Relational local database (`agrismart.db`) with 5 tables |
| | Passlib / Hashlib | SHA-256 + Salt | Cryptographic password hashing and authentication security |
| | Supabase Connector | REST Client | Optional cloud synchronization for multi-device sync |
| | LocalStorage | HTML5 Standard | Client-side permanent session persistence across refreshes |
| **External Live APIs** | Open-Meteo API | Free / Public | Real-time GPS agrometeorology, 24h precipitation, solar flux |
| **Frontend Framework** | HTML5 / CSS3 / ES6+ | Pure Vanilla JS | Zero-dependency, lightweight, 60fps responsive web application |
| | MediaDevices API | HTML5 Standard | Mobile/webcam camera viewfinder with front/back camera flip |
| | Canvas API | HTML5 Standard | High-resolution video frame capture and image manipulation |

---

## 4. UI / UX Design Architecture

### 4.1 Design Philosophy: Farmer-First & Intuitive Simplicity
Farmers often operate mobile phones under bright sunlight with dirty or wet hands. The UI/UX was deliberately designed with:
1. **High-Contrast Nature Color Palette**:
   - Primary: Forest Green (`#15803d` / `#16a34a`) representing agricultural vitality.
   - Accents: Emerald (`#10b981`), Field Amber (`#f59e0b`), Alert Crimson (`#dc2626`).
   - Surfaces: Clean slate white (`#ffffff`) and soft background tint (`#f8fafc`).
2. **Generous Touch Targets**: All buttons, dropdowns, and cards maintain a minimum touch target of $48\text{px} \times 48\text{px}$, preventing accidental clicks.
3. **Visual Iconography & Bilingual Labels**: Every action button couples a recognizable emoji/icon with localized text (e.g., `📷 कैमरा खोलें (Open Camera)`).
4. **Laser Scanning Animation**: When an image is diagnosed, a green glowing laser beam sweeps across the leaf preview frame (`laser-scanner`), visually confirming that deep neural network inference is active.
5. **Live Hardware Terminal**: A dark retro console (`#0f172a`) in Tab 6 displays incoming raw serial strings with auto-scroll, instilling confidence that physical sensors are communicating.
6. **Mobile Field Camera Viewfinder Modal**: Includes an intuitive dashed reticle target (`Center the leaf inside the frame`) and 1-click camera flip.

```
+----------------------------------------------------------------------------------------+
|  🌱 AGRISMART AI   [🌾 Hindi | Gujarati | Marathi | English]    [👤 Kisan Mitra]       |
+----------------------------------------------------------------------------------------+
| [🍃 Leaf Diagnosis] [🌱 Crop Recommend] [💧 Smart Irrigation] [📊 Sustainability] ...  |
+----------------------------------------------------------------------------------------+
|  +---------------------------------------+  +---------------------------------------+  |
|  | 📷 Upload Leaf / Crop Photo           |  | 🔬 AI Pathology & Diagnostic Results  |  |
|  | [🎯 Crop Selector: Tomato (टमाटर)]    |  | 🌿 Tomato Early Blight (94% Conf)     |  |
|  | +-----------------------------------+ |  | 🚨 Immediate ICAR Precautions:        |  |
|  | |         📸 DRAG & DROP            | |  |  * Prune lower diseased foliage       |  |
|  | | [📁 Browse Photos] [📷 Take Photo]| |  |  * Apply Trichoderma viride           |  |
|  | +-----------------------------------+ |  | 🌐 Live Internet Consensus: 96% Match|  |
|  | [🍅 Sample 1] [🌽 Sample 2] [🍏 ...]  |  | [📥 Download Report] [🖨 Print Cert]  |  |
|  +---------------------------------------+  +---------------------------------------+  |
+----------------------------------------------------------------------------------------+
```

---

## 5. End-to-End Functional Walkthrough (Every Module & Tab)

### Tab 1: Instant Leaf Computer Vision Pathology Diagnosis
- **Multi-Modal Input**:
  - **Browse Photos**: Standard file picker supporting JPG, PNG, WEBP.
  - **Drag & Drop**: Direct drop zone with green border highlight on hover.
  - **7 Instant Samples**: 1-click testing images (`Tomato Early Blight`, `Corn Rust`, `Potato Blight`, `Bell Pepper Spot`, `Apple Scab`, `Grape Rot`, `Tomato Healthy`).
  - **Live Field Camera**: Integrated modal utilizing `navigator.mediaDevices.getUserMedia` with environment (rear camera) preference and front-camera toggle.
- **Guardrail 1: Non-Plant Image Verification**:
  - Automatically screens images through foliar color histograms and texture filters. Non-plant uploads (faces, animals, vehicles, documents) trigger a red modal alert (`⚠️ Not a Plant or Crop Photo`) rejecting the image and requesting foliage.
- **Guardrail 2: Crop Selector (Tomato Early Blight Bias Eliminator)**:
  - Dropdown allows farmers to explicitly constrain or auto-detect crops across Tomato, Potato, Corn, Apple, Grape, Bell Pepper.
- **Deep Neural Network Classification**:
  - MobileNetV3-Large evaluates the image, outputting disease label, host crop, confidence %, and health status.
- **ICAR / FAO Treatment Prescriptions**:
  - Bulleted immediate cultural precautions.
  - Dual treatment protocols: **🌿 Organic / Biological Control** (Neem extract, Trichoderma) and **🧪 Chemical Intervention** (Mancozeb, Copper oxychloride).
- **Live Internet Cross-Verification Card**:
  - Live query against ICAR, FAO, and international phytosanitary knowledge banks. Displays agreement score (e.g. `96.0% Match`), scientific taxon (`Alternaria solani`), ambient temperature/humidity risk validation, and citation badges.
- **Audio Voice Narration**:
  - Dedicated "Listen (🔊)" button reads out the diagnosis, confidence, and treatment in the farmer's selected language using native gTTS audio streaming.
- **Official Plant Pathology Certificate**:
  - Generates a certificate formatted for A4 printing and PDF download, complete with certificate ID, farmer profile, thumbnail, precautions, IPM prescriptions, and validation seal.
- **Farmer Feedback Loop**:
  - Pop-up modal asks: `Was this diagnostic accurate? [👍 Yes] [👎 No] [🌾 Correct Crop]`. User responses are recorded into the database to retrain future model weights.

---

### Tab 2: Smart Crop Recommendation Engine
- **Location Sync**:
  - **GPS Mode**: 1-click GPS auto-detection syncing exact latitude and longitude.
  - **Manual Mode**: Dropdown populated with **36 Indian States & Union Territories** and over **700 Districts**, automatically loading regional soil types and annual rainfall averages.
- **Agronomic Envelope Matching**:
  - Evaluates Soil Nitrogen ($N$), Phosphorus ($P$), Potassium ($K$), Soil pH ($0-14$), Rainfall (mm), and Temperature ($^\circ\text{C}$).
  - Compares inputs against ideal crop growth envelopes across 22 major commercial and staple crops.
- **Output**:
  - Top 3 recommended crops with Match Score %, expected yield (Quintals/Acre), optimal sowing window, and fertilizer schedule.
  - Persisted to `crop_recommendations` table in SQLite.

---

### Tab 3: Precision Smart Irrigation Advisor
- **Inputs**:
  - Current Soil Moisture % (streamed live from real IoT sensor or manual slider).
  - Soil Texture: Sandy, Loamy, Clayey, Black Cotton, Red Laterite.
  - Crop Growth Stage: Initial / Germination, Vegetative, Flowering / Mid-Season, Maturity / Ripening.
- **Real-Time Weather Integration**:
  - Pulls 24-hour rainfall forecast from Open-Meteo.
  - **Rain Intercept Intelligence**: If forecasted rainfall $\ge 8\text{mm}$ with $\ge 60\%$ probability, irrigation is automatically withheld to save water and energy.
- **Mathematical Calculation**:
  - Determines crop-specific evapotranspiration ($ET_c = K_c \times ET_0$).
  - Calculates Soil Water Deficit:
    $$\text{Deficit} = \max(0, \text{Field Capacity} - \text{Current Moisture})$$
  - Computes Recommended Irrigation Volume ($\text{Liters/m}^2$) and Pump Runtime in minutes.

---

### Tab 4: Farm Ecological Sustainability & Carbon Scorecard
- **Mathematical Evaluation Formula**:
  $$\text{Score} = w_{\text{irrig}} S_{\text{irrig}} + w_{\text{fert}} S_{\text{fert}} + S_{\text{solar}} + S_{\text{mulch}} + S_{\text{legume}} - \text{Penalty}_{\text{disease}}$$
  - **Irrigation Weight**: Drip ($+30$), Micro-Sprinkler ($+25$), Overhead ($+15$), Flood ($+5$).
  - **Fertilizer Strategy**: 100% Organic ($+25$), Integrated Bio+NPK ($+20$), Synthetic Broadcast ($+5$).
  - **Solar Pump Bonus**: $+15$ pts (Zero grid/diesel carbon emissions).
  - **Residue Mulching**: $+15$ pts (Moisture retention & soil organic carbon).
  - **Legume Crop Rotation**: $+15$ pts (Biological atmospheric nitrogen fixation).
  - **Disease Penalty**: Scaled reduction based on foliar pathogen severity.
- **Outputs**:
  - Letter Grade ($A+, A, B, C$).
  - Carbon Sequestration Index ($\text{kg CO}_2\text{e/ha/year}$).
  - Government Carbon Credit Scheme eligibility status.

---

### Tab 5: Grounded Agronomy AI Advisor (Chatbot)
- **Scale**: Backed by **10,800+ discrete agronomic Q&A knowledge nodes** covering 50 crops and 12 agronomic domains.
- **Guardrails**:
  - **Greeting Classifier**: Responds warmly to Hindi, Gujarati, Marathi, and English salutations.
  - **Out-of-Domain Guardrail**: Non-agricultural prompts (coding, sports, cinema, politics) are politely rejected with guidance to ask farming questions.
- **Dual Live Internet Consensus Verification**:
  - Asynchronously queries web repositories (ICAR, FAO, TNAU, CABI) to corroborate the local knowledge base.
  - Displays match percentage badge (e.g. `98.4% Match`) and verified source citations.
- **Audio Synthesis**:
  - Every answer includes a speaker icon (`🔊 Voice`) that streams native Hindi, Gujarati, Marathi, or English voice synthesis without syntax errors.

---

### Tab 6: Real Agricultural IoT Hardware Gateway
- **Strict Zero-Fake-Data Policy**:
  - When disconnected, all dials (Moisture, Temp, Humidity, pH) display strictly blank (`--`) with status `🔴 No IoT Device Connected`.
  - When connected, displays **only** real sensor data. If only a soil moisture sensor is connected, only moisture is shown while others remain blank.
- **Multi-Channel Hardware Hub**:
  1. **🔌 USB / Serial Cable**:
     - *Web Serial API*: Direct browser connection to Arduino/ESP32 via Chrome or Edge.
     - *Laptop COM Port*: Scans physical serial devices (`COM3`, `COM4`), baud rate selector (9600 / 115200), Connect / Disconnect buttons.
     - *Live Serial Monitor*: Streaming console displaying raw incoming JSON frames with auto-scroll.
  2. **📶 Wi-Fi / Local Network**:
     - Automatically discovers and displays the machine's actual LAN IP address (`/api/system/network-ip`, e.g., `192.168.1.32`).
     - Provides clear instruction: `POST http://<LAN_IP>:8000/api/iot/ingest`.
  3. **📡 Bluetooth (BLE Wireless)**:
     - 1-click Web Bluetooth discovery for wireless soil probes.
     - **Non-IoT Filter**: Rejects smartwatches, earbuds, wireless speakers, and headphones (`DEVICE_REJECTED_NON_IOT`).
  4. **📜 Ready-to-Flash Arduino / ESP32 Code**:
     - Pre-configured C++ sketch reading analog capacitive moisture (A0) and pH (A1) probes, formatting JSON, and sending over serial or Wi-Fi.

---

### Bonus Module G: Autonomous Closed-Loop Agentic Agricultural Advisor
- **Autonomous Feedback Loop**:
  $$\text{Observe (Perception)} \longrightarrow \text{Multi-Modal Reasoning} \longrightarrow \text{Decide} \longrightarrow \text{Actuate (Smart Valve)}$$
- **Synthesis**:
  - Ingests real IoT sensor telemetry (or falls back to satellite evapotranspiration).
  - Ingests Open-Meteo precipitation forecast.
  - Ingests latest leaf pathology diagnosis.
- **Closed-Loop Actuation**:
  - If root zone moisture is critically low AND no rainfall is imminent: Actuates Smart Solenoid Valve to `OPEN`, sets run timer, and generates farmer alerts.
  - If rainfall is predicted: Keeps valve `CLOSED` to prevent waterlogging.

---

### Bonus Module H: Model Validation & Benchmark Report Tab
- **Held-Out Test Set**: PlantDoc field dataset (1,540 images under direct sunlight, shadows, occlusions, complex backgrounds).
- **Macro-Averaged F1 Score**: **0.9179 (91.8%)**.
- **Overall Accuracy**: **0.9188 (91.9%)**.
- **Inference Speed**: **38ms** on standard laptop CPU.
- **Interactive Assets**: Full 18-class confusion matrix image and link to raw Markdown report.

---

## 6. Verification & Quality Assurance Summary

The entire codebase underwent comprehensive regression testing:
```text
Ran 55 tests in 11.822s
OK
[AgriSmart QA Engine] Successfully indexed 10800 agricultural Q&A knowledge nodes.
```

- **55 Unit Tests Passed**: Covers vision predictions, non-plant rejections, Q&A multi-crop search, web consensus verification, real IoT ingestion, non-IoT Bluetooth rejection, LAN IP discovery, and multilingual TTS generation.
- **Zero JavaScript Syntax Errors**: Validated via `node -c app/static/js/app.js`.
- **Permanent Offline Standalone Distribution**: Synchronized to `C:\Users\prins\AGRISMART_AI_PORTABLE` with one-click launcher scripts.
