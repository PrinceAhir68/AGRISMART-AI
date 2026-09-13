# How to Run AgriSmart AI on Any Laptop

This folder contains the complete, self-contained **AgriSmart AI** platform.
You can copy this entire folder to any Windows, Mac, or Linux laptop (via USB pendrive, Google Drive, or ZIP) and run it without errors.

---

## 🚀 Quickest Way (Windows — 1-Click Startup)

1. Double-click **`START_AGRISMART.bat`**.
   - It will check your Python installation.
   - On the first run, if dependencies are missing, it will automatically install them (`pip install -r requirements.txt`).
   - It will automatically launch your default web browser to **`http://127.0.0.1:8000`**.
   - That's it! The website is live and fully functional.

---

## 🛠️ Prerequisites for the Laptop

- **Python 3.9, 3.10, 3.11, 3.12, 3.13, or 3.14** installed.
  - Download from: [python.org/downloads](https://www.python.org/downloads/)
  - **IMPORTANT**: During Python setup on Windows, check the box:
    ✅ **"Add python.exe to PATH"**

---

## 💻 Manual Way (Command Prompt / PowerShell / Terminal)

If you prefer using the command line:

### Step 1: Open Terminal in this folder
```powershell
cd path\to\AGRISMART_AI_PORTABLE
```

### Step 2: Install required packages (first time only)
```powershell
pip install -r requirements.txt
```

### Step 3: Start the AgriSmart AI server
```powershell
python app/main.py
```

### Step 4: Open your browser
Navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Verifying the Installation (Run Tests)

To verify that all 36 AI vision models, database tables, and API modules are functioning properly on the new laptop:
- Double-click **`RUN_TESTS.bat`** OR
- Run:
  ```powershell
  python -m unittest discover -s tests
  ```
All 36 unit tests should report `OK`.

---

## 📦 What is Included in this Folder

- **`app/`**: FastAPI backend server, SQLite database, ICAR knowledge base, and agronomy modules:
  - `modules/crop_recommender.py`: Crop recommendation & soil health diagnostician.
  - `modules/farmer_assistant.py`: Multilingual agronomic AI chatbot with guardrails.
  - `modules/smart_irrigation.py`: FAO-56 irrigation calculator.
  - `modules/weather_service.py`: Real-time weather intelligence.
  - `modules/sustainability.py`: Ecological carbon scorecard.
  - `modules/iot_simulator.py`: ESP32 edge telemetry simulator.
  - `modules/agentic_advisor.py`: Autonomous closed-loop control.
- **`app/static/`**:
  - `index.html`: Responsive single-page application with animated splash screen.
  - `css/style.css`: Professional UI styling, themes, animations.
  - `js/app.js`: 100% full-site translation (EN, HI, GU, MR), geolocation, audio speaker, feedback loop.
- **`model/`**:
  - `predict.py`: AI vision leaf pathology predictor with non-plant verification & crop selector constraint.
  - `weights/agrismart_mobilenetv3.pth`: Pre-trained MobileNetV3 deep learning weights.
  - `test_samples/`: Demonstration images for instant testing (Tomato, Potato, Corn, Apple, Grape, Pepper).
- **`agrismart.db`**: Local SQLite database for farmer accounts, diagnosis history, and ratings.
- **`requirements.txt`**: Minimal, robust dependency definitions.
- **`START_AGRISMART.bat`**: 1-click launcher for Windows.
- **`RUN_TESTS.bat`**: 1-click test runner.
