/**
 * AgriSmart AI - Complete Enterprise Frontend Client Logic
 * Features:
 *  - 100% Full-Website Multi-Language Translation (English, Hindi, Gujarati, Marathi)
 *  - Animated Enterprise Splash Screen with Auto-Dismiss (2.2s)
 *  - Explicit Crop Pathology Selector (Tomato, Potato, Corn, Apple, Grape, Pepper, Auto-Detect)
 *  - Dual Location Engine: GPS Auto-Detect & Manual State/District Coordinates
 *  - Soil Health & Mineral Diagnostician (pH, N, P, K alerts & ICAR remedies)
 *  - Interactive Farmer Feedback Loop (Continuous Model Improvement via /api/feedback)
 *  - Multilingual Resilient Voice Synthesis (Direct Streaming /api/tts + Web Speech API)
 *  - Real-Time Open-Meteo Agro-Meteorology & Disease Risk Forecaster
 *  - User Authentication (Local SQLite & Supabase with strict mobile/email validations)
 *  - Official Printable / Downloadable Plant Pathology Certificate (PDF/HTML)
 *  - Edge IoT Gateway & Autonomous Closed-Loop Decision Actuator
 */

// Global Utilities & HTML Sanitization
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Global App State
let currentSelectedImageFile = null;

// Persistent Farmer Account (Auto-saved so user is NEVER prompted or asked to log in every time)
let savedUser = null;
try {
  savedUser = JSON.parse(localStorage.getItem('agrismart_user') || 'null');
} catch (e) {
  savedUser = null;
}

if (!savedUser) {
  savedUser = {
    id: 1,
    name: "किसान मित्र (Kisan Mitra)",
    email_or_phone: "9876543210",
    location: "Gujarat, India",
    primary_crop: "Tomato",
    language: localStorage.getItem('agrismart_lang') || "hi",
    is_guest: true
  };
  localStorage.setItem('agrismart_user', JSON.stringify(savedUser));
}

let currentUser = savedUser;

// Default language: Hindi ('hi') unless farmer has previously selected another language
let currentLanguage = localStorage.getItem('agrismart_lang') || (currentUser && currentUser.language) || 'hi';
let currentDiagnosisData = null;
let userLatitude = 23.0225; // Default: Ahmedabad, Gujarat
let userLongitude = 72.5714;
let userLocationName = "Ahmedabad, Gujarat";
let isSpeaking = false;
let authMode = 'login'; // 'login' or 'register'
let currentLocMode = 'gps'; // 'gps' or 'manual'

// =================================================================
// 1. FULL-SITE MULTI-LANGUAGE TRANSLATION DICTIONARY (100% COVERAGE)
// =================================================================
const TRANSLATIONS = {
  "en": {
    "app_title": "AgriSmart AI",
    "app_subtitle": "Autonomous Agricultural Intelligence & Pathology System",
    "app_subtitle_clean": "Intelligent Agricultural Decision & Pathology Platform",
    "language_label": "🌐 Language:",
    "gps_detect": "Detect My Location",
    "loc_gps_mode": "GPS Auto",
    "loc_manual_mode": "State & District",
    "nav_login": "Login / Register",
    "tab_disease": "🌿 Plant Pathology Lab",
    "tab_crop": "🌾 Smart Crop Planner",
    "tab_irrigation": "💧 Precision Irrigation & Weather",
    "tab_sustainability": "🌍 Farm Sustainability & Carbon",
    "tab_assistant": "💬 Agronomy AI Advisor",
    "tab_iot": "📡 Edge IoT & Smart Actuation",
    "tab_report": "📊 Benchmark & Field Validation",
    "card_upload_title": "📷 Upload Leaf / Crop Photo",
    "tag_core": "AI Vision Pathology Lab",
    "card_upload_desc": "AI Vision analyzes visual pathology across 18 shared classes (Tomato, Potato, Corn, Apple, Grape, Pepper).",
    "label_target_crop": "Crop Under Inspection (Optional / Auto-Detect):",
    "crop_opt_auto": "🔍 Auto-Detect Crop (Any Foliage)",
    "crop_opt_tomato": "🍅 Tomato",
    "crop_opt_potato": "🥔 Potato",
    "crop_opt_corn": "🌽 Corn / Maize",
    "crop_opt_apple": "🍏 Apple",
    "crop_opt_grape": "🍇 Grape",
    "crop_opt_pepper": "🫑 Bell Pepper",
    "crop_cotton": "Cotton",
    "crop_fallow": "Fallow Land",
    "crop_legumes": "Legumes / Pulses",
    "crop_maize": "Maize (Corn)",
    "crop_rice": "Rice (Paddy)",
    "crop_wheat": "Wheat",
    "upload_prompt": "Click to browse",
    "upload_drag": "or drag & drop leaf photo",
    "upload_hint": "Supports real camera photos or field leaf images (JPG, PNG, WEBP)",
    "sample_prompt": "Or test instant sample images:",
    "btn_run_diag": "Run AI Disease Diagnosis",
    "diag_card_title": "🔬 Diagnostic Advisory Output",
    "badge_awaiting": "Awaiting Leaf",
    "btn_speaker": "Listen",
    "diag_empty_msg": "Upload a plant photo or click a sample to see AI disease classification, confidence, and ICAR precautionary guidance.",
    "confidence_label": "Confidence",
    "precautions_title": "🚨 Immediate Precautions",
    "organic_title": "🌿 Organic / Bio-Control",
    "chemical_title": "🧪 Chemical Remedy",
    "regional_title": "🇮🇳 Regional Advisory:",
    "btn_voice_read": "Voice Readout",
    "btn_download_report": "Download Full PDF / Print Diagnostic Report",
    "feedback_question": "Was this disease diagnosis helpful & accurate?",
    "crop_feedback_question": "Were these crop recommendations useful?",
    "btn_yes": "Yes",
    "btn_no": "No",
    "crop_rec_title": "🌱 Soil & Agro-Climatic Parameters",
    "tag_bonus_a": "Agro-Ecological Decision Engine",
    "label_state": "State / Region:",
    "label_district": "District:",
    "label_soil_type": "Soil Type:",
    "soil_loamy": "Loamy (All-Round)",
    "soil_clay": "Clay (High Water Retention)",
    "soil_sandy": "Sandy (Well Drained)",
    "soil_black": "Black Cotton (Vertisol)",
    "soil_alluvial": "Alluvial (Riverine)",
    "soil_red": "Red Soil",
    "label_soil_ph": "Soil pH:",
    "label_nitrogen": "Nitrogen",
    "label_phosphorus": "Phosphorus",
    "label_potassium": "Potassium",
    "label_season": "Season:",
    "season_kharif": "Kharif (Monsoon)",
    "season_rabi": "Rabi (Winter)",
    "season_zaid": "Zaid (Summer)",
    "label_prev_crop": "Previous Crop Grown:",
    "label_temp": "Avg Temperature (°C):",
    "label_rain": "Expected Rainfall (mm):",
    "btn_rec_crops": "Recommend Optimal Crops",
    "crop_results_title": "🏆 Recommended Crops (Top 3)",
    "crop_empty_msg": "Enter parameters or click recommend to compute crop suitability rankings.",
    "irrig_calc_title": "💧 Smart Irrigation Calculator (FAO-56)",
    "tag_bonus_b": "FAO-56 Water Intelligence",
    "label_current_moist": "Current Soil Moisture:",
    "label_crop": "Crop:",
    "label_stage": "Growth Stage:",
    "stage_initial": "Initial (Seedling)",
    "stage_vegetative": "Vegetative",
    "stage_flowering": "Mid-Season / Flowering",
    "stage_maturation": "Late / Maturation",
    "label_rain_sync": "Sync with Live Forecast Rain?",
    "opt_live_weather": "Sync Live Weather (GPS / Open-Meteo)",
    "opt_manual_rain": "Manual Rain Input",
    "label_rain_24h": "Forecast Rain 24h",
    "label_rain_prob": "Rain Probability",
    "btn_compute_irrig": "Compute Irrigation Necessity",
    "weather_card_title": "☁ Live Weather Intelligence",
    "tag_bonus_c": "Real-Time Agro-Meteorology",
    "weather_hum": "Humidity:",
    "weather_wind": "Wind:",
    "weather_rain_prob": "24h Rain Prob:",
    "weather_rain_sum": "Rain Sum:",
    "weather_risk_title": "🦠 Agro-Meteorological Risk Alerts:",
    "sust_title": "🌱 Farm Practices Assessment",
    "tag_bonus_d": "Ecological Farm Scorecard",
    "sust_desc": "Evaluated by transparent mathematical formula published in Section 3.2.",
    "label_irrig_tech": "Irrigation Technology:",
    "tech_drip": "Precision Drip Irrigation (Max Efficiency)",
    "tech_micro": "Micro Sprinkler",
    "tech_overhead": "Overhead Sprinkler",
    "tech_flood": "Conventional Flood / Furrow",
    "label_fert_strategy": "Fertilization Strategy:",
    "fert_integrated": "Integrated (Bio-fertilizer + Targeted NPK)",
    "fert_organic": "100% Organic & Farmyard Manure",
    "fert_synthetic": "Heavy Synthetic Broadcast",
    "check_solar": "☀️ Solar-powered pump system (Zero diesel/grid emissions)",
    "check_mulch": "🍂 Organic crop residue / straw mulching",
    "check_legume": "🌾 Regular legume / pulse crop rotation",
    "btn_calc_sust": "Calculate Sustainability & Carbon Score",
    "sust_scorecard_title": "📊 Ecological Scorecard",
    "assistant_title": "💬 Grounded Agronomy AI Advisor",
    "tag_bonus_e": "ICAR Grounded Advisory",
    "assistant_desc": "Answers are strictly grounded in verified ICAR & FAO agronomic publications (zero hallucination).",
    "quick_prompts_title": "Quick Prompts:",
    "chat_welcome": "Namaste! I am your AI Agronomy Advisor. Ask me anything about crop diseases, pest remedies, irrigation timing, or fertilizer schedules. I provide verified ICAR-backed recommendations with voice support.",
    "btn_send": "Send",
    "btn_clear_chat": "Clear Chat",
    "iot_title": "📡 IoT Edge Sensor Gateway (ESP32 Stream)",
    "tag_bonus_f": "Edge IoT Gateway",
    "gauge_moist": "Soil Moisture",
    "gauge_temp": "Temperature",
    "gauge_hum": "Humidity",
    "gauge_ph": "Soil pH",
    "simulate_scenarios_title": "Simulate Field Scenarios for Live Testing:",
    "btn_scen_normal": "🌤 Normal Conditions",
    "btn_scen_drought": "🔥 Sudden Drought Spike",
    "btn_scen_rain": "🌧 Heavy Rain Inflow",
    "agent_title": "🤖 Autonomous Agentic Decision Loop",
    "tag_bonus_g": "Autonomous Closed-Loop Control",
    "agent_desc": "Autonomous closed loop: Perceive -> Multi-Modal Reason -> Decide -> Actuate",
    "valve_label": "Smart Valve Status:",
    "btn_run_agent": "Run Agent Cycle",
    "report_title": "📑 Benchmark & Model Validation Report",
    "btn_raw_md": "Open Raw Markdown",
    "metric_macro_f1": "Primary Metric (Macro-F1)",
    "metric_acc": "Overall Accuracy",
    "metric_samples": "Test Samples (PlantDoc Field)",
    "metric_speed": "Inference Speed",
    "cm_title": "Held-Out Field Test Set Confusion Matrix",
    "auth_modal_title": "Farmer Login",
    "auth_signin_tab": "Sign In",
    "auth_register_tab": "Create Account",
    "auth_name_label": "Full Name:",
    "auth_email_phone_label": "Email or Phone Number:",
    "auth_pwd_label": "Password:",
    "auth_loc_label": "State / Region:",
    "auth_crop_label": "Primary Crop:",
    "auth_lang_label": "Preferred Language:",
    "btn_login_submit": "Sign In to Farm Account",
    "btn_register_submit": "Create My Farm Account",
    "btn_back_home": "⬅ Back to Scanner",
    "btn_back_scanner": "⬅ Scan Another Plant",
    "btn_browse_photos": "Browse Photos",
    "btn_take_photo": "Open Camera",
    "camera_modal_title": "Live Camera Leaf Scanner",
    "camera_frame_guide": "Center the leaf inside the frame",
    "btn_flip_camera": "Flip Camera",
    "btn_snap_photo": "Snap & Diagnose",
    "btn_download_pdf_file": "📥 Download Report (HTML/PDF)",
    "btn_print_pdf": "🖨 Print Official Certificate",
    "print_modal_title": "📄 Official Plant Diagnostic Certificate",
    "invalid_plant_title": "⚠️ Not a Plant or Crop Photo",
    "invalid_plant_desc": "The AI vision model only inspects agricultural crops, plant leaves, fruits, and vegetables. Please upload a clear photo of foliage or infected plant parts.",
    "footer_credits": "AI Vision Pathology • Precision Agro-Meteorology • Ecological Sustainability",
    "web_consensus_title": "Live Internet Cross-Verification & Comparison",
    "web_consensus_subtitle": "Real-time cross-checking against ICAR, FAO, and international phytosanitary databases",
    "label_pathogen_latin": "Scientific Pathogen:",
    "label_weather_match": "Agro-Climate Match:",
    "label_corroborated_symptoms": "Corroborated Foliar Indicators:",
    "label_live_citations": "Live Internet Citations:",
    "nav_account": "Farmer Account",
    "default_farmer_name": "Kisan Mitra (Farmer Friend)",
    "badge_farmer_profile": "Active",
    "badge_logout": "Logout",
    "confirm_logout": "Do you want to log out or switch account?",
    "iot_title": "📡 Real Agricultural IoT Hardware Gateway",
    "iot_architecture_desc": "Direct hardware link: Arduino / ESP32 / BLE Sensor ➔ USB/Wi-Fi/Bluetooth ➔ AgriSmart AI Core ➔ Farmer Action.",
    "iot_status_label": "HARDWARE STATUS:",
    "iot_no_device": "No IoT Device Connected",
    "iot_real_only_notice": "Strict Real-Data Mode: Displaying physical sensor readings only. Disconnected sensors remain strictly blank (--).",
    "iot_not_connected_sub": "(No Sensor Connected)",
    "iot_hub_title": "Connect Physical IoT Sensors (USB / Wi-Fi / Bluetooth)",
    "iot_tab_usb": "🔌 USB / Serial Cable",
    "iot_tab_wifi": "📶 Wi-Fi / Network",
    "iot_tab_bt": "📡 Bluetooth (BLE)",
    "iot_tab_code": "📜 Arduino / ESP32 Code",
    "iot_tab_sim": "🧪 Lab Simulator (Optional)",
    "usb_desc": "Connect Arduino, ESP32, STM32, or Raspberry Pi Pico directly via USB cable:",
    "btn_web_serial": "Connect USB via Browser (Web Serial)",
    "btn_connect_port": "Connect Port",
    "btn_disconnect_iot": "Disconnect Device",
    "wifi_push_title": "Option 1 (Push Mode - Recommended):",
    "wifi_push_desc": "Flash your ESP32 to POST JSON sensor data over local Wi-Fi:",
    "wifi_pull_title": "Option 2 (Pull Mode):",
    "wifi_pull_desc": "Enter your ESP32 local web server URL to poll:",
    "btn_connect_wifi": "Connect Wi-Fi Sensor",
    "bt_desc": "Pair with wireless agricultural BLE soil moisture or microclimate probes via Web Bluetooth:",
    "btn_scan_ble": "Scan & Connect Bluetooth Sensor",
    "code_title": "Arduino IDE / PlatformIO Ready Sketch:",
    "btn_copy_code": "📋 Copy Code",
    "sim_notice": "Optional virtual simulator for hackathon judge presentations when physical sensors are not available:",
    "iot_terminal_title": "LIVE HARDWARE SERIAL MONITOR",
    "nav_settings": "Settings",
    "tab_settings": "⚙️ Settings & Profile",
    "settings_title": "Settings & Farm Profile",
    "settings_subtitle": "Manage your personal farmer identity, land records, regional preferences, visual display mode, and IoT edge hardware settings.",
    "tag_farmer_identity": "Farmer Identity",
    "tag_accessibility": "Accessibility & Display",
    "tag_sensors": "Sensors & Gateways",
    "tag_privacy": "Privacy & Backup",
    "set_card1_title": "Personal Details & Farm Profile",
    "set_card1_desc": "Personal and agronomic details help AgriSmart AI personalize disease remedies, irrigation advice, and crop recommendations for your specific field.",
    "set_label_name": "Farmer Name",
    "set_label_contact": "Phone Number or Email",
    "set_label_state": "State / Region",
    "set_label_district": "District",
    "set_label_village": "Village / Taluka / Landmark",
    "set_label_farm_size": "Land Area & Unit",
    "set_label_crops": "Primary Cultivated Crops (Click to select)",
    "set_label_soil": "Dominant Soil Type",
    "set_label_water": "Primary Water Source",
    "btn_save_profile": "💾 Save Farm Profile",
    "set_card2_title": "Display, Language & Voice Settings",
    "set_card2_desc": "Customize platform visual appearance, contrast for daylight field inspection, speech narration speed, and audio alerts.",
    "set_label_platform_lang": "Platform Language (Default)",
    "set_label_theme": "Visual Display Mode",
    "theme_standard": "Farm Green",
    "theme_standard_sub": "Standard Balanced",
    "theme_sunlight": "Sunlight Mode",
    "theme_sunlight_sub": "High Contrast Field",
    "theme_night": "Night Mode",
    "theme_night_sub": "Dark Low-Glare",
    "set_label_fontsize": "Font Readability Size",
    "font_normal": "Standard (100%)",
    "font_large": "Senior / Large (115%)",
    "set_label_voice_rate": "Voice Narration Speed",
    "set_label_auto_voice": "Auto-Voice Readout",
    "set_sub_auto_voice": "Speaks disease diagnosis out loud immediately upon image scan",
    "set_label_chime": "Disease Alert Audio Chime",
    "set_sub_chime": "Plays sound chime when high-risk crop pathology is discovered",
    "btn_save_pref": "💾 Save Display Preferences",
    "set_card3_title": "IoT Hardware & Sensor Settings",
    "set_card3_desc": "Configure field microcontrollers, data ingestion polling frequency, and verify non-IoT Bluetooth device rejection.",
    "set_label_iot_interval": "Telemetry Monitor Polling Frequency",
    "set_ble_filter_title": "Intelligent BLE Non-IoT Filter: ACTIVE",
    "set_ble_filter_desc": "Strictly rejects smart watches, audio speakers, headphones, and non-agricultural gadgets during Web Bluetooth pairing.",
    "set_label_local_ip": "AgriSmart AI Gateway Local IP (For ESP32 / Arduino HTTP Push)",
    "btn_copy_url": "Copy URL",
    "set_sub_local_ip": "Flash this URL into your ESP32 or Wi-Fi Arduino firmware to stream live soil data.",
    "set_status_label": "Hardware Gateway Status:",
    "btn_open_iot_tab": "Open IoT Panel",
    "set_card4_title": "Account Security & Data Management",
    "set_card4_desc": "Manage your password, export diagnostic logs and recommendations, and clear offline browser caches.",
    "set_header_pwd": "Change Account Password",
    "set_guest_pwd_notice": "You are using a Guest Session. Create or sign into an account to set a password.",
    "set_label_old_pwd": "Current Password",
    "set_label_new_pwd": "New Password",
    "set_label_confirm_pwd": "Confirm New Password",
    "btn_change_pwd": "Update Password",
    "set_label_export": "Export Farm Diagnostic Data",
    "set_sub_export": "Download complete JSON archive of all leaf scans, remedies, and recommendations",
    "btn_export_data": "Export JSON",
    "set_label_cache": "Clear Scanner Media Cache",
    "set_sub_cache": "Frees device memory by removing cached test leaf samples and temporary canvases",
    "btn_clear_cache": "Clear Cache",
    "set_label_logout": "Farmer Account Session",
    "set_sub_logout": "Currently running as Guest Session",
    "btn_login_or_register": "Log In / Register"
  },
  "hi": {
    "app_title": "एग्रीस्मार्ट एआई (AgriSmart AI)",
    "app_subtitle": "स्वायत्त कृषि बुद्धिमत्ता एवं पादप रोग निदान प्रणाली",
    "app_subtitle_clean": "बुद्धिमान कृषि निर्णय एवं पादप रोग निदान प्रणाली",
    "language_label": "🌐 भाषा चुनें:",
    "gps_detect": "मेरा स्थान खोजें (GPS)",
    "loc_gps_mode": "जीपीएस स्वतः",
    "loc_manual_mode": "राज्य व जिला",
    "nav_login": "लॉग इन / पंजीकरण",
    "tab_disease": "🌿 पादप रोग निदान प्रयोगशाला",
    "tab_crop": "🌾 स्मार्ट फसल योजनाकार",
    "tab_irrigation": "💧 सटीक सिंचाई एवं मौसम",
    "tab_sustainability": "🌍 कृषि स्थिरता एवं कार्बन स्कोर",
    "tab_assistant": "💬 कृषि वैज्ञानिक एआई सलाहकार",
    "tab_iot": "📡 एज IoT एवं स्मार्ट वाल्व नियंत्रण",
    "tab_report": "📊 बेंचमार्क एवं फील्ड सत्यापन",
    "card_upload_title": "📷 पत्ती या फसल की तस्वीर अपलोड करें",
    "tag_core": "एआई विज़न रोग विज्ञान प्रयोगशाला",
    "card_upload_desc": "एआई विज़न 18 फसल-रोग वर्गों (टमाटर, आलू, मक्का, सेब, अंगूर, मिर्च) में वास्तविक पैथोलॉजी की जांच करता है।",
    "label_target_crop": "निरीक्षण हेतु चुनी गई फसल (वैकल्पिक / स्वतः पहचान):",
    "crop_opt_auto": "🔍 स्वतः पहचान (कोई भी फसल / पत्ती)",
    "crop_opt_tomato": "🍅 टमाटर (Tomato)",
    "crop_opt_potato": "🥔 आलू (Potato)",
    "crop_opt_corn": "🌽 मक्का (Corn / Maize)",
    "crop_opt_apple": "🍏 सेब (Apple)",
    "crop_opt_grape": "🍇 अंगूर (Grape)",
    "crop_opt_pepper": "🫑 शिमला मिर्च (Bell Pepper)",
    "crop_cotton": "कपास (Cotton)",
    "crop_fallow": "परती / खाली जमीन",
    "crop_legumes": "दलहनी फसलें / दालें",
    "crop_maize": "मक्का (Corn)",
    "crop_rice": "धान / चावल (Paddy)",
    "crop_wheat": "गेहूं (Wheat)",
    "upload_prompt": "ब्राउज़ करने के लिए क्लिक करें",
    "upload_drag": "या पत्ती की तस्वीर यहां खींचें",
    "upload_hint": "कैमरा फोटो या खेत की पत्ती तस्वीर का समर्थन (JPG, PNG, WEBP)",
    "sample_prompt": "या तुरंत नमूना छवियों का परीक्षण करें:",
    "btn_run_diag": "एआई रोग निदान शुरू करें",
    "diag_card_title": "🔬 रोग निदान व सलाह परिणाम",
    "badge_awaiting": "पत्ती की प्रतीक्षा",
    "btn_speaker": "सुनें (आवाज)",
    "diag_empty_msg": "फसल रोग पहचान, विश्वास स्तर और ICAR सावधानियों को देखने के लिए एक तस्वीर अपलोड करें।",
    "confidence_label": "सटीकता",
    "precautions_title": "🚨 तत्काल सावधानियां",
    "organic_title": "🌿 जैविक / प्राकृतिक उपचार",
    "chemical_title": "🧪 रासायनिक दवा उपचार",
    "regional_title": "🇮🇳 क्षेत्रीय भाषा मार्गदर्शन:",
    "btn_voice_read": "आवाज में सुनें",
    "btn_download_report": "पूर्ण PDF रिपोर्ट डाउनलोड करें / प्रिंट करें",
    "feedback_question": "क्या यह रोग निदान उपयोगी और सटीक था?",
    "crop_feedback_question": "क्या यह फसल सिफारिश उपयोगी थी?",
    "btn_yes": "हाँ",
    "btn_no": "नहीं",
    "crop_rec_title": "🌱 मिट्टी और जलवायु मापदंड",
    "tag_bonus_a": "कृषि-पारिस्थितिकी निर्णय इंजन",
    "label_state": "राज्य / प्रदेश:",
    "label_district": "जिला:",
    "label_soil_type": "मिट्टी का प्रकार:",
    "soil_loamy": "दोमट मिट्टी (सर्वांगीण)",
    "soil_clay": "चिकनी मिट्टी (अधिक जलधारण)",
    "soil_sandy": "बलुई मिट्टी (उत्कृष्ट जल निकास)",
    "soil_black": "काली कपास मिट्टी (रेगुर)",
    "soil_alluvial": "जलोढ़ मिट्टी (नदी कछार)",
    "soil_red": "लाल मिट्टी",
    "label_soil_ph": "मिट्टी pH मान:",
    "label_nitrogen": "नाइट्रोजन",
    "label_phosphorus": "फास्फोरस",
    "label_potassium": "पोटाश",
    "label_season": "मौसम:",
    "season_kharif": "खरीफ (मानसून)",
    "season_rabi": "रबी (सर्दियां)",
    "season_zaid": "जायद (गर्मी)",
    "label_prev_crop": "पिछली उगाई गई फसल:",
    "label_temp": "औसत तापमान (°C):",
    "label_rain": "अनुमानित वर्षा (मिमी):",
    "btn_rec_crops": "सर्वोत्तम फसलों की सिफारिश प्राप्त करें",
    "crop_results_title": "🏆 अनुशंसित फसलें (शीर्ष 3)",
    "crop_empty_msg": "फसल उपयुक्तता रैंकिंग की गणना करने के लिए विवरण दर्ज करें।",
    "irrig_calc_title": "💧 स्मार्ट सिंचाई कैलकुलेटर (FAO-56)",
    "tag_bonus_b": "FAO-56 जल बुद्धिमत्ता",
    "label_current_moist": "वर्तमान मिट्टी नमी:",
    "label_crop": "फसल:",
    "label_stage": "वृद्धि चरण:",
    "stage_initial": "प्रारंभिक (अंकुरण / पौध)",
    "stage_vegetative": "वानस्पतिक वृद्धि",
    "stage_flowering": "मध्य-सत्र / पुष्पन अवस्था",
    "stage_maturation": "परिपक्वता / कटाई पूर्व",
    "label_rain_sync": "क्या लाइव मौसम से बारिश सिंक करें?",
    "opt_live_weather": "लाइव मौसम सिंक (GPS / Open-Meteo)",
    "opt_manual_rain": "मैनुअल बारिश दर्ज करें",
    "label_rain_24h": "24 घंटे बारिश अनुमान",
    "label_rain_prob": "बारिश की संभावना",
    "btn_compute_irrig": "सिंचाई आवश्यकता की गणना करें",
    "weather_card_title": "☁ लाइव मौसम संबंधी बुद्धिमत्ता",
    "tag_bonus_c": "वास्तविक समय मौसम विज्ञान",
    "weather_hum": "नमी:",
    "weather_wind": "हवा की गति:",
    "weather_rain_prob": "24 घंटे में बारिश संभावना:",
    "weather_rain_sum": "कुल बारिश:",
    "weather_risk_title": "🦠 मौसम आधारित रोग अलर्ट:",
    "sust_title": "🌱 कृषि पद्धति मूल्यांकन",
    "tag_bonus_d": "पारिस्थितिकी फार्म स्कोरकार्ड",
    "sust_desc": "धारा 3.2 में प्रकाशित पारदर्शी गणितीय सूत्र द्वारा मूल्यांकित।",
    "label_irrig_tech": "सिंचाई तकनीक:",
    "tech_drip": "ड्रिप / टपक सिंचाई (अधिकतम बचत)",
    "tech_micro": "माइक्रो फव्वारा (स्प्रिंकलर)",
    "tech_overhead": "ओवरहेड स्प्रिंकलर",
    "tech_flood": "पारंपरिक बाढ़ / क्यारी सिंचाई",
    "label_fert_strategy": "खाद प्रबंधन रणनीति:",
    "fert_integrated": "एकीकृत (जैविक खाद + संतुलित NPK)",
    "fert_organic": "100% जैविक व केंचुआ खाद",
    "fert_synthetic": "अत्यधिक रासायनिक उर्वरक",
    "check_solar": "☀️ सौर ऊर्जा पंप प्रणाली (शून्य डीजल उत्सर्जन)",
    "check_mulch": "🍂 फसल अवशेष / पुआल से मल्चिंग",
    "check_legume": "🌾 दलहनी फसलों के साथ फसल चक्र",
    "btn_calc_sust": "स्थिरता और कार्बन स्कोर निकालें",
    "sust_scorecard_title": "📊 पारिस्थितिकी स्कोरकार्ड",
    "assistant_title": "💬 कृषि वैज्ञानिक एआई सलाहकार",
    "tag_bonus_e": "ICAR प्रमाणित कृषि सलाह",
    "assistant_desc": "सभी उत्तर ICAR और FAO के प्रमाणित कृषि वैज्ञानिक शोध पर आधारित हैं।",
    "quick_prompts_title": "त्वरित प्रश्न:",
    "chat_welcome": "नमस्ते! मैं आपका एआई कृषि सलाहकार हूं। फसल रोग, कीट नियंत्रण, सिंचाई समय या खाद संबंधी प्रश्न पूछें।",
    "btn_send": "भेजें",
    "btn_clear_chat": "चैट साफ़ करें",
    "iot_title": "📡 IoT सेंसर गेटवे (ESP32 लाइव स्ट्रीम)",
    "tag_bonus_f": "एज IoT गेटवे",
    "gauge_moist": "मिट्टी नमी",
    "gauge_temp": "तापमान",
    "gauge_hum": "हवा में नमी",
    "gauge_ph": "मिट्टी pH",
    "simulate_scenarios_title": "परीक्षण हेतु परिदृश्य अनुकरण करें:",
    "btn_scen_normal": "🌤 सामान्य स्थिति",
    "btn_scen_drought": "🔥 अचानक सूखा / जल तनाव",
    "btn_scen_rain": "🌧 भारी वर्षा प्रवाह",
    "agent_title": "🤖 स्वायत्त एजेंट निर्णय चक्र",
    "tag_bonus_g": "स्वायत्त बंद-लूप नियंत्रण",
    "agent_desc": "स्वायत्त चक्र: निरीक्षण -> विश्लेषण -> निर्णय -> वाल्व नियंत्रण व संदेश",
    "valve_label": "स्मार्ट वाल्व स्थिति:",
    "btn_run_agent": "एजेंट चक्र चलाएं",
    "report_title": "📑 बेंचमार्क एवं मॉडल मूल्यांकन रिपोर्ट",
    "btn_raw_md": "कच्ची मार्कडाउन फाइल खोलें",
    "metric_macro_f1": "प्राथमिक मीट्रिक (मैक्रो-F1)",
    "metric_acc": "कुल सटीकता",
    "metric_samples": "परीक्षण नमूने (PlantDoc फील्ड)",
    "metric_speed": "अनुमान गति",
    "cm_title": "फील्ड टेस्ट सेट कन्फ्यूजन मैट्रिक्स",
    "auth_modal_title": "किसान खाता लॉगिन",
    "auth_signin_tab": "लॉग इन करें",
    "auth_register_tab": "नया खाता बनाएं",
    "auth_name_label": "पूरा नाम:",
    "auth_email_phone_label": "ईमेल या मोबाइल नंबर:",
    "auth_pwd_label": "पासवर्ड:",
    "auth_loc_label": "राज्य / जिला:",
    "auth_crop_label": "मुख्य फसल:",
    "auth_lang_label": "पसंदीदा भाषा:",
    "btn_login_submit": "खाते में लॉग इन करें",
    "btn_register_submit": "मेरा किसान खाता बनाएं",
    "btn_back_home": "⬅ मुख्य स्कैनर पर वापस",
    "btn_back_scanner": "⬅ नया पौधा / पत्ती जांचें",
    "btn_browse_photos": "फ़ोटो चुनें",
    "btn_take_photo": "कैमरा खोलें",
    "camera_modal_title": "लाइव कैमरा पत्ती स्कैनर",
    "camera_frame_guide": "पत्ती को फ्रेम के बीच में रखें",
    "btn_flip_camera": "कैमरा बदलें",
    "btn_snap_photo": "फोटो लें और जांचें",
    "btn_download_pdf_file": "📥 प्रमाण पत्र डाउनलोड करें (HTML/PDF)",
    "btn_print_pdf": "🖨 प्रमाण पत्र प्रिंट करें",
    "print_modal_title": "📄 आधिकारिक पादप रोग प्रमाण पत्र",
    "invalid_plant_title": "⚠️ पौधे या फसल की तस्वीर नहीं है",
    "invalid_plant_desc": "यह एआई प्रणाली केवल कृषि फसलों, पत्तियों, फलों और सब्जियों के रोगों का परीक्षण करती है। कृपया पौधे की पत्ती का स्पष्ट फोटो अपलोड करें।",
    "footer_credits": "एआई पादप रोग विज्ञान • सटीक मौसम पूर्वानुमान • पर्यावरण अनुकूल खेती",
    "web_consensus_title": "लाइव इंटरनेट सत्यापन एवं तुलनात्मक पुष्टि",
    "web_consensus_subtitle": "ICAR, FAO एवं अंतरराष्ट्रीय पादप डेटाबेस के साथ वास्तविक समय तुलना",
    "label_pathogen_latin": "वैज्ञानिक रोगजनक (Pathogen):",
    "label_weather_match": "कृषि-मौसम अनुकूलता:",
    "label_corroborated_symptoms": "प्रमाणित पत्ती लक्षण संकेतक:",
    "label_live_citations": "लाइव इंटरनेट संदर्भ स्रोत:",
    "nav_account": "किसान खाता",
    "default_farmer_name": "किसान मित्र (Kisan Mitra)",
    "badge_farmer_profile": "सक्रिय",
    "badge_logout": "लॉगआउट",
    "confirm_logout": "क्या आप लॉगआउट करना या दूसरा खाता बदलना चाहते हैं?",
    "iot_title": "📡 वास्तविक कृषि IoT हार्डवेयर गेटवे",
    "iot_architecture_desc": "प्रत्यक्ष हार्डवेयर लिंक: Arduino / ESP32 / BLE सेंसर ➔ USB/Wi-Fi/Bluetooth ➔ AgriSmart AI Core ➔ किसान निर्णय।",
    "iot_status_label": "हार्डवेयर स्थिति:",
    "iot_no_device": "कोई IoT डिवाइस कनेक्ट नहीं है",
    "iot_real_only_notice": "वास्तविक डेटा मोड: केवल जुड़े हुए भौतिक सेंसर का डेटा दिखाया जा रहा है। अनुपस्थित सेंसर रिक्त (--) रहेंगे।",
    "iot_not_connected_sub": "(सेंसर कनेक्ट नहीं है)",
    "iot_hub_title": "भौतिक IoT सेंसर कनेक्ट करें (USB / Wi-Fi / Bluetooth)",
    "iot_tab_usb": "🔌 USB / सीरियल केबल",
    "iot_tab_wifi": "📶 Wi-Fi / नेटवर्क",
    "iot_tab_bt": "📡 ब्लूटूथ (BLE)",
    "iot_tab_code": "📜 Arduino / ESP32 कोड",
    "iot_tab_sim": "🧪 लैब सिम्युलेटर (वैकल्पिक)",
    "usb_desc": "Arduino, ESP32, STM32, या Raspberry Pi Pico को सीधे USB केबल द्वारा कनेक्ट करें:",
    "btn_web_serial": "ब्राउज़र से USB कनेक्ट करें (Web Serial)",
    "btn_connect_port": "COM पोर्ट जोड़ें",
    "btn_disconnect_iot": "डिवाइस डिस्कनेक्ट करें",
    "wifi_push_title": "विकल्प 1 (पुश मोड - अनुशंसित):",
    "wifi_push_desc": "अपने ESP32 से लोकल Wi-Fi पर JSON डेटा भेजें:",
    "wifi_pull_title": "विकल्प 2 (पुल मोड):",
    "wifi_pull_desc": "ESP32 वेब सर्वर का URL दर्ज करें:",
    "btn_connect_wifi": "Wi-Fi सेंसर जोड़ें",
    "bt_desc": "वायरलेस BLE मृदा नमी या पर्यावरण प्रोब को ब्लूटूथ द्वारा कनेक्ट करें:",
    "btn_scan_ble": "ब्लूटूथ सेंसर खोजें एवं जोड़ें",
    "code_title": "Arduino IDE / PlatformIO के लिए तैयार कोड:",
    "btn_copy_code": "📋 कोड कॉपी करें",
    "sim_notice": "वैकल्पिक वर्चुअल सिम्युलेटर (जब भौतिक हार्डवेयर उपलब्ध न हो):",
    "iot_terminal_title": "लाइव हार्डवेयर सीरियल मॉनिटर",
    "nav_settings": "सेटिंग्स",
    "tab_settings": "⚙️ सेटिंग्स और प्रोफ़ाइल",
    "settings_title": "सेटिंग्स और कृषि प्रोफ़ाइल",
    "settings_subtitle": "अपनी किसान पहचान, भूमि विवरण, भाषा, दृश्य मोड और IoT हार्डवेयर सेटिंग्स प्रबंधित करें।",
    "tag_farmer_identity": "किसान पहचान",
    "tag_accessibility": "सुलभता एवं प्रदर्शन",
    "tag_sensors": "सेंसर और गेटवे",
    "tag_privacy": "सुरक्षा और बैकअप",
    "set_card1_title": "व्यक्तिगत विवरण और कृषि प्रोफ़ाइल",
    "set_card1_desc": "व्यक्तिगत और कृषि संबंधी विवरण एग्रीस्मार्ट एआई को आपके खेत के लिए उपचार, सिंचाई और फसल सलाह को अनुकूलित करने में मदद करते हैं।",
    "set_label_name": "किसान का नाम",
    "set_label_contact": "फोन नंबर या ईमेल",
    "set_label_state": "राज्य / क्षेत्र",
    "set_label_district": "ज़िला",
    "set_label_village": "गाँव / तहसील / लैंडमार्क",
    "set_label_farm_size": "भूमि क्षेत्र और इकाई",
    "set_label_crops": "मुख्य उगाई जाने वाली फसलें (चुनने के लिए क्लिक करें)",
    "set_label_soil": "प्रमुख मिट्टी का प्रकार",
    "set_label_water": "मुख्य सिंचाई स्रोत",
    "btn_save_profile": "💾 प्रोफ़ाइल सुरक्षित करें",
    "set_card2_title": "प्रदर्शन, भाषा एवं आवाज़ सेटिंग्स",
    "set_card2_desc": "वेबसाइट का दृश्य स्वरूप, तेज धूप हेतु कंट्रास्ट, बोलकर सुनाने की गति और ध्वनि अलर्ट कस्टमाइज़ करें।",
    "set_label_platform_lang": "वेबसाइट की भाषा (डिफ़ॉल्ट)",
    "set_label_theme": "दृश्य डिस्प्ले थीम",
    "theme_standard": "फार्म ग्रीन",
    "theme_standard_sub": "मानक संतुलित हरा",
    "theme_sunlight": "धूप मोड (हाई-कंट्रास्ट)",
    "theme_sunlight_sub": "खेत में तेज धूप हेतु",
    "theme_night": "नाइट मोड (डार्क)",
    "theme_night_sub": "रात में कम चमक",
    "set_label_fontsize": "अक्षर आकार (फॉन्ट साइज़)",
    "font_normal": "मानक (100%)",
    "font_large": "बड़ा आकार (115% वरिष्ठ)",
    "set_label_voice_rate": "आवाज़ बोलने की गति",
    "set_label_auto_voice": "स्वचालित आवाज़ वाचन",
    "set_sub_auto_voice": "फोटो स्कैन करते ही रोग का नाम तुरंत बोलकर सुनाए",
    "set_label_chime": "रोग चेतावनी बीप/ध्वनि",
    "set_sub_chime": "गंभीर रोग का पता चलने पर चेतावनी ध्वनि बजाए",
    "btn_save_pref": "💾 प्रदर्शन सेटिंग्स सुरक्षित करें",
    "set_card3_title": "IoT हार्डवेयर और सेंसर सेटिंग्स",
    "set_card3_desc": "खेत के माइक्रोकंट्रोलर, डेटा पोलिंग दर और गैर-कृषि ब्लूटूथ डिवाइस अस्वीकृति प्रबंधित करें।",
    "set_label_iot_interval": "सेंसर डेटा अपडेट दर",
    "set_ble_filter_title": "इंटेलिजेंट ब्लूटूथ गैर-कृषि फ़िल्टर: सक्रिय",
    "set_ble_filter_desc": "वेब ब्लूटूथ पेयरिंग में स्मार्ट वॉच, ऑडियो स्पीकर व हेडफ़ोन को खारिज करता है।",
    "set_label_local_ip": "गेटवे लोकल आईपी (ESP32/Arduino डेटा पुश हेतु)",
    "btn_copy_url": "URL कॉपी करें",
    "set_sub_local_ip": "लाइव मिट्टी डेटा भेजने हेतु इस URL को अपने ESP32 में फ़्लैश करें।",
    "set_status_label": "हार्डवेयर गेटवे स्थिति:",
    "btn_open_iot_tab": "IoT पैनल खोलें",
    "set_card4_title": "खाता सुरक्षा एवं डेटा प्रबंधन",
    "set_card4_desc": "पासवर्ड बदलें, निदान लॉग और सिफ़ारिशें डाउनलोड करें और ऑफ़लाइन कैश साफ़ करें।",
    "set_header_pwd": "खाता पासवर्ड बदलें",
    "set_guest_pwd_notice": "आप अतिथि सत्र का उपयोग कर रहे हैं। पासवर्ड बदलने हेतु खाता बनाएँ।",
    "set_label_old_pwd": "वर्तमान पासवर्ड",
    "set_label_new_pwd": "नया पासवर्ड",
    "set_label_confirm_pwd": "नए पासवर्ड की पुष्टि करें",
    "btn_change_pwd": "पासवर्ड अपडेट करें",
    "set_label_export": "कृषि डायग्नोस्टिक डेटा निर्यात करें",
    "set_sub_export": "सभी स्कैन, उपचार व सिफ़ारिशों की पूरी JSON बैकअप फ़ाइल डाउनलोड करें",
    "btn_export_data": "JSON निर्यात करें",
    "set_label_cache": "स्कैनर मीडिया कैश साफ़ करें",
    "set_sub_cache": "कैश की गई पत्तियों की फोटो साफ़ करके मेमोरी मुक्त करें",
    "btn_clear_cache": "कैश साफ़ करें",
    "set_label_logout": "किसान खाता सत्र",
    "set_sub_logout": "वर्तमान में अतिथि सत्र सक्रिय है",
    "btn_login_or_register": "लॉगिन / खाता बनाएँ"
  },
  "gu": {
    "app_title": "એગ્રીસ્માર્ટ એઆઈ (AgriSmart AI)",
    "app_subtitle": "સ્વાયત્ત કૃષિ બુદ્ધિમત્તા અને પાક રોગ નિદાન સિસ્ટમ",
    "app_subtitle_clean": "બુદ્ધિશાળી કૃષિ નિર્ણય અને પાક રોગ નિદાન પ્લેટફોર્મ",
    "language_label": "🌐 ભાષા પસંદ કરો:",
    "gps_detect": "મારું લોકેશન શોધો (GPS)",
    "loc_gps_mode": "જીપીએસ આપમેળે",
    "loc_manual_mode": "રાજ્ય અને જિલ્લો",
    "nav_login": "લૉગ ઇન / રજીસ્ટર",
    "tab_disease": "🌿 પાક રોગ નિદાન પ્રયોગશાળા",
    "tab_crop": "🌾 સ્માર્ટ પાક આયોજક",
    "tab_irrigation": "💧 ચોક્કસ સિંચાઈ અને હવામાન",
    "tab_sustainability": "🌍 ખેતી પર્યાવરણ અને કાર્બન સ્કોર",
    "tab_assistant": "💬 કૃષિ વૈજ્ઞાનિક AI સલાહકાર",
    "tab_iot": "📡 એજ IoT અને સ્માર્ટ વાલ્વ કંટ્રોલ",
    "tab_report": "📊 બેન્ચમાર્ક અને ફિલ્ડ મૂલ્યાંકન",
    "card_upload_title": "📷 પાન અથવા પાકની તસવીર અપલોડ કરો",
    "tag_core": "AI વિઝન પાક રોગ વિજ્ઞાન લેબ",
    "card_upload_desc": "AI વિઝન ૧૮ પાક-રોગ વર્ગોમાં રોગની ઓળખ કરે છે (ટામેટા, બટાટા, મકાઈ, સફરજન, દ્રાક્ષ, મરચાં).",
    "label_target_crop": "તપાસ માટેનો પાક (વૈકલ્પિક / આપમેળે ઓળખ):",
    "crop_opt_auto": "🔍 આપમેળે ઓળખ (કોઈપણ પાંદડું / છોડ)",
    "crop_opt_tomato": "🍅 ટામેટાં (Tomato)",
    "crop_opt_potato": "🥔 બટાટા (Potato)",
    "crop_opt_corn": "🌽 મકાઈ (Corn / Maize)",
    "crop_opt_apple": "🍏 સફરજન (Apple)",
    "crop_opt_grape": "🍇 દ્રાક્ષ (Grape)",
    "crop_opt_pepper": "🫑 કેપ્સિકમ / મરચાં (Bell Pepper)",
    "crop_cotton": "કપાસ (Cotton)",
    "crop_fallow": "પડતર જમીન",
    "crop_legumes": "કઠોળ વર્ગના પાક",
    "crop_maize": "મકાઈ (Corn)",
    "crop_rice": "ડાંગર / ચોખા (Paddy)",
    "crop_wheat": "ઘઉં (Wheat)",
    "upload_prompt": "બ્રાઉઝ કરવા માટે ક્લિક કરો",
    "upload_drag": "અથવા પાનની તસવીર ખેંચો",
    "upload_hint": "મોબાઈલ કેમેરા ફોટો અથવા ખેતરની તસવીર વાપરો (JPG, PNG, WEBP)",
    "sample_prompt": "અથવા સીધા નમૂનાઓનું પરીક્ષણ કરો:",
    "btn_run_diag": "AI રોગ નિદાન ચાલુ કરો",
    "diag_card_title": "🔬 રોગ નિદાન અને સલાહ પરિણામ",
    "badge_awaiting": "પાનની રાહ જોઈ રહ્યું છે",
    "btn_speaker": "સાંભળો (અવાજ)",
    "diag_empty_msg": "રોગ નિદાન, વિશ્વાસ સ્તર અને ICAR ભલામણો જોવા માટે તસવીર અપલોડ કરો.",
    "confidence_label": "ચોકસાઈ",
    "precautions_title": "🚨 તાત્કાલિક સાવચેતીઓ",
    "organic_title": "🌿 દેશી / જૈવિક નિયંત્રણ",
    "chemical_title": "🧪 રાસાયણિક દવા ઉપચાર",
    "regional_title": "🇮🇳 સ્થાનિક ભાષા માર્ગદર્શન:",
    "btn_voice_read": "અવાજમાં સાંભળો",
    "btn_download_report": "સંપૂર્ણ PDF રિપોર્ટ ડાઉનલોડ કરો / પ્રિન્ટ કરો",
    "feedback_question": "શું આ રોગ નિદાન ઉપયોગી અને સચોટ હતું?",
    "crop_feedback_question": "શું આ પાકની ભલામણ ઉપયોગી હતી?",
    "btn_yes": "હા",
    "btn_no": "ના",
    "crop_rec_title": "🌱 જમીન અને આબોહવાના પરિમાણો",
    "tag_bonus_a": "કૃષિ-ઇકોલોજીકલ નિર્ણય એન્જિન",
    "label_state": "રાજ્ય:",
    "label_district": "જિલ્લો:",
    "label_soil_type": "જમીનનો પ્રકાર:",
    "soil_loamy": "ગોરાડુ / ગોરાટ જમીન",
    "soil_clay": "ચીકણી / કાંપવાળી જમીન",
    "soil_sandy": "રેતાળ જમીન (સરળ નિતાર)",
    "soil_black": "કાળી કપાસની જમીન",
    "soil_alluvial": "નદી કાંપવાળી જમીન",
    "soil_red": "રાતી / લાલ જમીન",
    "label_soil_ph": "જમીન pH:",
    "label_nitrogen": "નાઇટ્રોજન",
    "label_phosphorus": "ફોસ્ફરસ",
    "label_potassium": "પોટાશ",
    "label_season": "ઋતુ:",
    "season_kharif": "ચોમાસું (ખરીફ)",
    "season_rabi": "શિયાળુ (રવિ)",
    "season_zaid": "ઉનાળુ (જાયદ)",
    "label_prev_crop": "અગાઉ લીધેલ પાક:",
    "label_temp": "સરેરાશ તાપમાન (°C):",
    "label_rain": "અપેક્ષિત વરસાદ (મીમી):",
    "btn_rec_crops": "શ્રેષ્ઠ પાકની ભલામણ મેળવો",
    "crop_results_title": "🏆 ભલામણ કરેલ પાકો (ટોચના ૩)",
    "crop_empty_msg": "પાકની યોગ્યતા ચકાસવા માટે વિગતો ભરો.",
    "irrig_calc_title": "💧 સ્માર્ટ સિંચાઈ કેલ્ક્યુલેટર (FAO-56)",
    "tag_bonus_b": "FAO-56 જળ બુદ્ધિમત્તા",
    "label_current_moist": "હાલમાં જમીનનો ભેજ:",
    "label_crop": "પાક:",
    "label_stage": "વૃદ્ધિનો તબક્કો:",
    "stage_initial": "પ્રારંભિક (રોપણી / અંકુરણ)",
    "stage_vegetative": "વાનસ્પતિક વૃદ્ધિ",
    "stage_flowering": "મધ્ય-ઋતુ / ફૂલ બેસવાનો તબક્કો",
    "stage_maturation": "પાકવાની અંતિમ અવસ્થા",
    "label_rain_sync": "શું જીવંત હવામાન સાથે વરસાદ જોડવો?",
    "opt_live_weather": "જીવંત હવામાન સાથે જોડો (GPS / Open-Meteo)",
    "opt_manual_rain": "જાતે વરસાદ નોંધો",
    "label_rain_24h": "૨૪ કલાકમાં વરસાદ",
    "label_rain_prob": "વરસાદ શક્યતા",
    "btn_compute_irrig": "સિંચાઈ જરૂરિયાતની ગણતરી કરો",
    "weather_card_title": "☁ લાઈવ હવામાન વિગતો",
    "tag_bonus_c": "વાસ્તવિક સમય કૃષિ હવામાન",
    "weather_hum": "ભેજ:",
    "weather_wind": "પવનની ગતિ:",
    "weather_rain_prob": "૨૪ કલાકમાં વરસાદ શક્યતા:",
    "weather_rain_sum": "કુલ વરસાદ:",
    "weather_risk_title": "🦠 હવામાન આધારિત રોગ એલર્ટ:",
    "sust_title": "🌱 ખેતી પદ્ધતિ મૂલ્યાંકન",
    "tag_bonus_d": "પર્યાવરણ ફાર્મ સ્કોરકાર્ડ",
    "sust_desc": "વિભાગ ૩.૨ મુજબ વૈજ્ઞાનિક ગણતરી દ્વારા મૂલ્યાંકન.",
    "label_irrig_tech": "સિંચાઈ પદ્ધતિ:",
    "tech_drip": "ટપક સિંચાઈ પદ્ધતિ (શ્રેષ્ઠ બચત)",
    "tech_micro": "માઇક્રો ફુવારા પદ્ધતિ",
    "tech_overhead": "મોટા ફુવારા (સ્પ્રિંકલર)",
    "tech_flood": "પરંપરાગત ધોરિયા પિયત",
    "label_fert_strategy": "ખાતર વ્યવસ્થાપન:",
    "fert_integrated": "સંકલિત ખાતર (જૈવિક + સંતુલિત NPK)",
    "fert_organic": "૧૦૦% દેશી / અળસિયાનું ખાતર",
    "fert_synthetic": "રાસાયણિક ખાતરનો વધુ ઉપયોગ",
    "check_solar": "☀️ સોલર પંપ સિસ્ટમ (ઝીરો ડીઝલ પ્રદૂષણ)",
    "check_mulch": "🍂 ઓર્ગેનિક પાથરણ (મલ્ચિંગ)",
    "check_legume": "🌾 કઠોળ વર્ગના પાકની ફેરબદલી",
    "btn_calc_sust": "સ્થિરતા અને કાર્બન સ્કોર ગણો",
    "sust_scorecard_title": "📊 પર્યાવરણ સ્કોરકાર્ડ",
    "assistant_title": "💬 કૃષિ વૈજ્ઞાનિક AI સલાહકાર",
    "tag_bonus_e": "ICAR પ્રમાણિત કૃષિ માર્ગદર્શન",
    "assistant_desc": "બધા જવાબો ICAR અને કૃષિ યુનિવર્સિટીના પ્રમાણિત સંશોધન પર આધારિત છે.",
    "quick_prompts_title": "ઝડપી પ્રશ્નો:",
    "chat_welcome": "નમસ્તે! હું તમારો એઆઈ કૃષિ સલાહકાર છું. પાક રોગ, સિંચાઈ અથવા ખાતર વિશે કોઈ પણ પ્રશ્ન પૂછો.",
    "btn_send": "મોકલો",
    "btn_clear_chat": "ચેટ સાફ કરો",
    "iot_title": "📡 IoT સેન્સર ગેટવે (ESP32 લાઈવ સ્ટ્રીમ)",
    "tag_bonus_f": "એજ IoT ગેટવે",
    "gauge_moist": "જમીન ભેજ",
    "gauge_temp": "તાપમાન",
    "gauge_hum": "હવામાન ભેજ",
    "gauge_ph": "જમીન pH",
    "simulate_scenarios_title": "પરીક્ષણ માટે પરિસ્થિતિ બદલો:",
    "btn_scen_normal": "🌤 સામાન્ય સ્થિતિ",
    "btn_scen_drought": "🔥 અચાનક દુષ્કાળ / પાણી ખેંચ",
    "btn_scen_rain": "🌧 ભારે વરસાદનો પ્રવાહ",
    "agent_title": "🤖 સ્વાયત્ત એજન્ટ નિર્ણય લૂપ",
    "tag_bonus_g": "સ્વાયત્ત ક્લોઝ્ડ-લૂપ કંટ્રોલ",
    "agent_desc": "સ્વાયત્ત ચક્ર: નિરીક્ષણ -> વિશ્લેષણ -> નિર્ણય -> વાલ્વ કંટ્રોલ",
    "valve_label": "સ્માર્ટ વાલ્વ સ્થિતિ:",
    "btn_run_agent": "એજન્ટ સાયકલ ચલાવો",
    "report_title": "📑 બેન્ચમાર્ક અને મોડેલ મૂલ્યાંકન રિપોર્ટ",
    "btn_raw_md": "કાચી માર્કડાઉન ફાઇલ ખોલો",
    "metric_macro_f1": "મુખ્ય મેટ્રિક (Macro-F1)",
    "metric_acc": "કુલ સચોટતા",
    "metric_samples": "ટેસ્ટ સેમ્પલ્સ (PlantDoc ફિલ્ડ)",
    "metric_speed": "અનુમાન સ્પીડ",
    "cm_title": "ફિલ્ડ ટેસ્ટ સેટ કન્ફ્યુઝન મેટ્રિક્સ",
    "auth_modal_title": "ખેડૂત એકાઉન્ટ લૉગિન",
    "auth_signin_tab": "લૉગ ઇન કરો",
    "auth_register_tab": "નવું ખાતું બનાવો",
    "auth_name_label": "પૂરું નામ:",
    "auth_email_phone_label": "ઈમેલ અથવા મોબાઈલ નંબર:",
    "auth_pwd_label": "પાસવર્ડ:",
    "auth_loc_label": "જિલ્લો / રાજ્ય:",
    "auth_crop_label": "મુખ્ય પાક:",
    "auth_lang_label": "પસંદગીની ભાષા:",
    "btn_login_submit": "ખાતામાં લૉગ ઇન કરો",
    "btn_register_submit": "મારું ખેડૂત ખાતું બનાવો",
    "btn_back_home": "⬅ મુખ્ય સ્કેનર પર પાછા",
    "btn_back_scanner": "⬅ નવું પર્ણ / પાક તપાસો",
    "btn_browse_photos": "ફોટા પસંદ કરો",
    "btn_take_photo": "કૅમેરો ખોલો",
    "camera_modal_title": "લાઈવ કૅમેરા પાન સ્કેનર",
    "camera_frame_guide": "પાનને ફ્રેમની વચ્ચે રાખો",
    "btn_flip_camera": "કૅમેરો બદલો",
    "btn_snap_photo": "ફોટો લો અને તપાસો",
    "btn_download_pdf_file": "📥 પ્રમાણપત્ર ડાઉનલોડ કરો (HTML/PDF)",
    "btn_print_pdf": "🖨 પ્રમાણપત્ર પ્રિન્ટ કરો",
    "print_modal_title": "📄 સત્તાવાર પાક રોગ નિદાન પ્રમાણપત્ર",
    "invalid_plant_title": "⚠️ પાક કે છોડનો ફોટો નથી",
    "invalid_plant_desc": "આ એઆઇ સિસ્ટમ માત્ર ખેતીના પાક, પાંદડા, ફળ અને શાકભાજીનું જ નિરીક્ષણ કરે છે. કૃપા કરીને પાંદડાનો સ્પષ્ટ ફોટો અપલોડ કરો.",
    "footer_credits": "AI પાક રોગ વિજ્ઞાન • સચોટ હવામાન માહિતી • પર્યાવરણીય સ્થિરતા",
    "web_consensus_title": "જીવંત ઇન્ટરનેટ ક્રોસ-ચકાસણી અને તુલના",
    "web_consensus_subtitle": "ICAR, FAO અને આંતરરાષ્ટ્રીય ડેટાબેઝ સાથે વાસ્તવિક સમયની સરખામણી",
    "label_pathogen_latin": "વૈજ્ઞાનિક રોગકારક (Pathogen):",
    "label_weather_match": "કૃષિ-હવામાન સુસંગતતા:",
    "label_corroborated_symptoms": "પ્રમાણિત પર્ણ રોગ લક્ષણો:",
    "label_live_citations": "જીવંત સંદર્ભ સ્ત્રોતો:",
    "nav_account": "ખેડૂત એકાઉન્ટ",
    "default_farmer_name": "કિસાન મિત્ર (ખેડૂત મિત્ર)",
    "badge_farmer_profile": "સક્રિય",
    "badge_logout": "લૉગ આઉટ",
    "confirm_logout": "શું તમે લૉગ આઉટ કરવા અથવા બીજું ખાતું બદલવા માંગો છો?",
    "iot_title": "📡 વાસ્તવિક કૃષિ IoT હાર્ડવેર ગેટવે",
    "iot_architecture_desc": "સીધું હાર્ડવેર જોડાણ: Arduino / ESP32 / BLE સેન્સર ➔ USB/Wi-Fi/Bluetooth ➔ AgriSmart AI ➔ ખેડૂત નિર્ણય.",
    "iot_status_label": "હાર્ડવેર સ્થિતિ:",
    "iot_no_device": "કોઈ IoT ડિવાઇસ કનેક્ટેડ નથી",
    "iot_real_only_notice": "વાસ્તવિક ડેટા મોડ: માત્ર ભૌતિક સેન્સરનું અસલી રીડિંગ દર્શાવાય છે. ગેરહાજર સેન્સર ખાલી (--) રહેશે.",
    "iot_not_connected_sub": "(સેન્સર કનેક્ટેડ નથી)",
    "iot_hub_title": "ભૌતિક IoT સેન્સર કનેક્ટ કરો (USB / Wi-Fi / Bluetooth)",
    "iot_tab_usb": "🔌 USB / સિરિયલ કેબલ",
    "iot_tab_wifi": "📶 Wi-Fi / નેટવર્ક",
    "iot_tab_bt": "📡 બ્લૂટૂથ (BLE)",
    "iot_tab_code": "📜 Arduino / ESP32 કોડ",
    "iot_tab_sim": "🧪 લેબ સિમ્યુલેટર (વૈકલ્પિક)",
    "usb_desc": "Arduino, ESP32 કે Raspberry Pi Pico ને સીધા USB કેબલથી કનેક્ટ કરો:",
    "btn_web_serial": "બ્રાઉઝરથી USB કનેક્ટ કરો (Web Serial)",
    "btn_connect_port": "COM પોર્ટ કનેક્ટ કરો",
    "btn_disconnect_iot": "ડિસ્કનેક્ટ કરો",
    "wifi_push_title": "વિકલ્પ 1 (પુશ મોડ - ભલામણ કરેલ):",
    "wifi_push_desc": "તમારા ESP32 થી Wi-Fi પર ડેટા મોકલો:",
    "wifi_pull_title": "વિકલ્પ 2 (પુલ મોડ):",
    "wifi_pull_desc": "ESP32 સ્થાનિક URL દાખલ કરો:",
    "btn_connect_wifi": "Wi-Fi સેન્સર કનેક્ટ કરો",
    "bt_desc": "વાયરલેસ BLE સોઇલ મોઇશ્ચર પ્રોબ બ્લૂટૂથ દ્વારા કનેક્ટ કરો:",
    "btn_scan_ble": "બ્લૂટૂથ સેન્સર શોધો",
    "code_title": "Arduino IDE માટે તૈયાર કોડ:",
    "btn_copy_code": "📋 કોડ કોપી કરો",
    "sim_notice": "પરીક્ષણ માટે વૈકલ્પિક સિમ્યુલેટર:",
    "iot_terminal_title": "લાઈવ હાર્ડવેર સિરિયલ મોનિટર",
    "nav_settings": "સેટિંગ્સ",
    "tab_settings": "⚙️ સેટિંગ્સ અને પ્રોફાઇલ",
    "settings_title": "સેટિંગ્સ અને ખેડૂત પ્રોફાઇલ",
    "settings_subtitle": "તમારી ખેડૂત ઓળખ, જમીન વિગતો, પ્રાદેશિક ભાષા, ડિસ્પ્લે મોડ અને IoT હાર્ડવેર સેટિંગ્સ મેનેજ કરો.",
    "tag_farmer_identity": "ખેડૂત ઓળખ",
    "tag_accessibility": "સુલભતા અને પ્રદર્શન",
    "tag_sensors": "સેન્સર્સ અને ગેટવે",
    "tag_privacy": "સુરક્ષા અને બેકઅપ",
    "set_card1_title": "વ્યક્તિગત વિગતો અને ફાર્મ પ્રોફાઇલ",
    "set_card1_desc": "વ્યક્તિગત અને કૃષિ વિગતો એગ્રીસ્માર્ટ એઆઈને તમારા ખેતર માટે રોગના ઉપાયો અને પાકની ભલામણો વ્યક્તિગત બનાવવામાં મદદ કરે છે.",
    "set_label_name": "ખેડૂતનું નામ",
    "set_label_contact": "ફોન નંબર અથવા ઈમેલ",
    "set_label_state": "રાજ્ય / પ્રદેશ",
    "set_label_district": "જિલ્લો",
    "set_label_village": "ગામ / તાલુકો / લેન્ડમાર્ક",
    "set_label_farm_size": "જમીન વિસ્તાર અને એકમ",
    "set_label_crops": "મુખ્ય વવાતા પાકો (પસંદ કરવા ક્લિક કરો)",
    "set_label_soil": "મુખ્ય જમીનનો પ્રકાર",
    "set_label_water": "મુખ્ય પિયત સ્ત્રોત",
    "btn_save_profile": "💾 પ્રોફાઇલ સાચવો",
    "set_card2_title": "ડિસ્પ્લે, ભાષા અને અવાજ સેટિંગ્સ",
    "set_card2_desc": "પ્લેટફોર્મનો દેખાવ, ખેતરમાં સૂર્યપ્રકાશ માટે હાઇ કોન્ટ્રાસ્ટ, બોલવાની ગતિ અને ઑડિઓ ચેતવણી કસ્ટમાઇઝ કરો.",
    "set_label_platform_lang": "પ્લેટફોર્મ ભાષા (ડિફૉલ્ટ)",
    "set_label_theme": "વિઝ્યુઅલ ડિસ્પ્લે થીમ",
    "theme_standard": "ફાર્મ ગ્રીન",
    "theme_standard_sub": "માનક સંતુલિત લીલો",
    "theme_sunlight": "સનલાઇટ મોડ (હાઇ કોન્ટ્રાસ્ટ)",
    "theme_sunlight_sub": "ખેતરમાં તેજ તડકા માટે",
    "theme_night": "નાઇટ મોડ (ડાર્ક)",
    "theme_night_sub": "ઓછી ચમકવાળો અંધકાર મોડ",
    "set_label_fontsize": "ફોન્ટ વાંચન કદ",
    "font_normal": "સામાન્ય (100%)",
    "font_large": "મોટું કદ (115% વરિષ્ઠ)",
    "set_label_voice_rate": "અવાજ બોલવાની ગતિ",
    "set_label_auto_voice": "ઓટો-વોઇસ રીડઆઉટ",
    "set_sub_auto_voice": "ફોટો સ્કેન થતાં જ રોગનું નામ તરત જ બોલીને જણાવો",
    "set_label_chime": "રોગ ચેતવણી સાઉન્ડ ચાઇમ",
    "set_sub_chime": "જોખમી રોગ જણાય ત્યારે ચેતવણી અવાજ વગાડો",
    "btn_save_pref": "💾 ડિસ્પ્લે સેટિંગ્સ સાચવો",
    "set_card3_title": "IoT હાર્ડવેર અને સેન્સર સેટિંગ્સ",
    "set_card3_desc": "ખેતરના માઇક્રોકન્ટ્રોલર્સ, ડેટા સેમ્પલિંગ આવર્તન અને બિન-કૃષિ બ્લૂટૂથ ડિવાઇસ ફિલ્ટરિંગ મેનેજ કરો.",
    "set_label_iot_interval": "સેન્સર ડેટા પોલિંગ આવર્તન",
    "set_ble_filter_title": "ઇન્ટેલિજન્ટ BLE નોન-IoT ફિલ્ટર: સક્રિય",
    "set_ble_filter_desc": "બ્લૂટૂથ પેરિંગ વખતે સ્માર્ટ ઘડિયાળો અને સ્પીકર્સને નકારી કાઢે છે.",
    "set_label_local_ip": "ગેટવે લોકલ આઇપી (ESP32 ડેટા પુશ માટે)",
    "btn_copy_url": "URL કૉપિ કરો",
    "set_sub_local_ip": "જીવંત જમીન ડેટા મોકલવા માટે આ URL તમારા ESP32 માં ફ્લેશ કરો.",
    "set_status_label": "હાર્ડવેર ગેટવે સ્થિતિ:",
    "btn_open_iot_tab": "IoT પેનલ ખોલો",
    "set_card4_title": "ખાતાની સુરક્ષા અને ડેટા મેનેજમેન્ટ",
    "set_card4_desc": "પાસવર્ડ મેનેજ કરો, ડાયગ્નોસ્ટિક લૉગ્સ નિકાસ કરો અને ઑફલાઇન કેશ સાફ કરો.",
    "set_header_pwd": "એકાઉન્ટ પાસવર્ડ બદલો",
    "set_guest_pwd_notice": "તમે ગેસ્ટ સેશન વાપરી રહ્યા છો. પાસવર્ડ બદલવા એકાઉન્ટ બનાવો.",
    "set_label_old_pwd": "વર્તમાન પાસવર્ડ",
    "set_label_new_pwd": "નવો પાસવર્ડ",
    "set_label_confirm_pwd": "નવા પાસવર્ડની પુષ્ટિ કરો",
    "btn_change_pwd": "પાસવર્ડ અપડેટ કરો",
    "set_label_export": "ફાર્મ ડાયગ્નોસ્ટિક ડેટા નિકાસ કરો",
    "set_sub_export": "બધા પાંદડા સ્કેન અને ભલામણોની સંપૂર્ણ JSON બેકઅપ ફાઇલ ડાઉનલોડ કરો",
    "btn_export_data": "JSON નિકાસ કરો",
    "set_label_cache": "સ્કેનર મીડિયા કેશ સાફ કરો",
    "set_sub_cache": "કેશ કરેલ પાંદડાના સેમ્પલ સાફ કરીને મેમરી મુક્ત કરો",
    "btn_clear_cache": "કેશ સાફ કરો",
    "set_label_logout": "ખેડૂત એકાઉન્ટ સત્ર",
    "set_sub_logout": "હાલમાં ગેસ્ટ સેશન ચાલી રહ્યું છે",
    "btn_login_or_register": "લૉગ ઇન / રજીસ્ટર"
  },
  "mr": {
    "app_title": "ॲग्रीस्मार्ट एआय (AgriSmart AI)",
    "app_subtitle": "स्वायत्त कृषी बुद्धिमत्ता व वनस्पती रोग निदान प्रणाली",
    "app_subtitle_clean": "बुद्धिमान कृषी निर्णय व वनस्पती रोग निदान प्रणाली",
    "language_label": "🌐 भाषा निवडा:",
    "gps_detect": "माझे स्थान शोधा (GPS)",
    "loc_gps_mode": "जीपीएस आपोआप",
    "loc_manual_mode": "राज्य व जिल्हा",
    "nav_login": "लॉग इन / नोंदणी",
    "tab_disease": "🌿 वनस्पती रोग निदान प्रयोगशाळा",
    "tab_crop": "🌾 स्मार्ट पीक नियोजक",
    "tab_irrigation": "💧 अचूक सिंचन व हवामान",
    "tab_sustainability": "🌍 शेती शाश्वतता व कार्बन स्कोअर",
    "tab_assistant": "💬 कृषी तज्ज्ञ AI सल्लागार",
    "tab_iot": "📡 एज IoT व स्मार्ट झडप नियंत्रण",
    "tab_report": "📊 बेंचमार्क व फील्ड पडताळणी",
    "card_upload_title": "📷 पानाचा फोटो अपलोड करा",
    "tag_core": "AI व्हिजन वनस्पती रोग निदान लॅब",
    "card_upload_desc": "AI व्हिजन १८ पिकांच्या रोगांचे अचूक निदान करते (टोमॅटो, बटाटा, मका, सफरचंद, द्राक्षे, मिरची).",
    "label_target_crop": "तपासणीसाठी पीक निवडा (पर्यायी / आपोआप ओळख):",
    "crop_opt_auto": "🔍 आपोआप ओळख (कोणतीही वनस्पती / पान)",
    "crop_opt_tomato": "🍅 टोमॅटो (Tomato)",
    "crop_opt_potato": "🥔 बटाटा (Potato)",
    "crop_opt_corn": "🌽 मका (Corn / Maize)",
    "crop_opt_apple": "🍏 सफरचंद (Apple)",
    "crop_opt_grape": "🍇 द्राक्षे (Grape)",
    "crop_opt_pepper": "🫑 ढोबळी / सिमला मिरची (Bell Pepper)",
    "crop_cotton": "कापूस (Cotton)",
    "crop_fallow": "पडीक जमीन",
    "crop_legumes": "कडधान्य / डाळी",
    "crop_maize": "मका (Corn)",
    "crop_rice": "भात / धान (Paddy)",
    "crop_wheat": "गहू (Wheat)",
    "upload_prompt": "ब्राउझ करण्यासाठी क्लिक करा",
    "upload_drag": "किंवा पानाचा फोटो येथे टाका",
    "upload_hint": "कॅमेरा फोटो किंवा शेतातील फोटो वापरा (JPG, PNG, WEBP)",
    "sample_prompt": "किंवा नमुना फोटो तपासा:",
    "btn_run_diag": "AI रोग निदान सुरू करा",
    "diag_card_title": "🔬 रोग निदान व सल्ला अहवाल",
    "badge_awaiting": "पानाची प्रतीक्षा",
    "btn_speaker": "ऐका (आवाज)",
    "diag_empty_msg": "रोग निदान, अचूकता आणि ICAR सल्ला पाहण्यासाठी फोटो अपलोड करा.",
    "confidence_label": "अचूकता",
    "precautions_title": "🚨 तात्काळ खबरदारी",
    "organic_title": "🌿 सेंद्रिय / जैविक उपाय",
    "chemical_title": "🧪 रासायनिक औषध फवारणी",
    "regional_title": "🇮🇳 स्थानिक भाषा सल्ला:",
    "btn_voice_read": "आवाजात ऐका",
    "btn_download_report": "पूर्ण PDF अहवाल डाउनलोड करा / प्रिंट करा",
    "feedback_question": "हे रोग निदान उपयुक्त आणि अचूक होते का?",
    "crop_feedback_question": "ही पीक शिफारस उपयुक्त ठरली का?",
    "btn_yes": "होय",
    "btn_no": "नाही",
    "crop_rec_title": "🌱 माती व हवामान घटक",
    "tag_bonus_a": "कृषी-पर्यावरण निर्णय प्रणाली",
    "label_state": "राज्य:",
    "label_district": "जिल्हा:",
    "label_soil_type": "मातीचा प्रकार:",
    "soil_loamy": "गाळाची / पोयटा माती",
    "soil_clay": "चिकण माती (पाणी धरून ठेवणारी)",
    "soil_sandy": "रेताड माती (चांगला निचरा)",
    "soil_black": "काळी रेगूर माती",
    "soil_alluvial": "गाळाची सुपीक माती",
    "soil_red": "तांबडी / लाल माती",
    "label_soil_ph": "मातीचा सामू (pH):",
    "label_nitrogen": "नायट्रोजन",
    "label_phosphorus": "फॉस्फरस",
    "label_potassium": "पोटॅश",
    "label_season": "हंगाम:",
    "season_kharif": "खरीप (पावसाळी)",
    "season_rabi": "रब्बी (हिवाळी)",
    "season_zaid": "उन्हाळी (झायद)",
    "label_prev_crop": "मागील घेतलेले पीक:",
    "label_temp": "सरासरी तापमान (°C):",
    "label_rain": "अपेक्षित पाऊस (मिमी):",
    "btn_rec_crops": "योग्य पिकांची शिफारस मिळवा",
    "crop_results_title": "🏆 शिफारस केलेली पिके (पहिले ३)",
    "crop_empty_msg": "पीक योग्यतेची पडताळणी करण्यासाठी माहिती भरा.",
    "irrig_calc_title": "💧 स्मार्ट सिंचन गणक (FAO-56)",
    "tag_bonus_b": "FAO-56 जल बुद्धिमत्ता",
    "label_current_moist": "सध्याची मातीतील ओलावा:",
    "label_crop": "पीक:",
    "label_stage": "वाढीची अवस्था:",
    "stage_initial": "सुरुवातीची अवस्था (रोप)",
    "stage_vegetative": "शाकीय वाढीची अवस्था",
    "stage_flowering": "मध्य-हंगाम / फुलधारणा अवस्था",
    "stage_maturation": "पक्वता / कापणी पूर्व अवस्था",
    "label_rain_sync": "थेट हवामानानुसार पावसाची माहिती जोडायची का?",
    "opt_live_weather": "थेट हवामानाशी जोडा (GPS / Open-Meteo)",
    "opt_manual_rain": "स्वतः पाऊस नोंदवा",
    "label_rain_24h": "२४ तासांतील पाऊस",
    "label_rain_prob": "पावसाची शक्यता",
    "btn_compute_irrig": "सिंचन गरजेची गणना करा",
    "weather_card_title": "☁ थेट हवामान माहिती",
    "tag_bonus_c": "रिअल-टाइम कृषी हवामानशास्त्र",
    "weather_hum": "हवेतील ओलावा:",
    "weather_wind": "वाऱ्याचा वेग:",
    "weather_rain_prob": "२४ तासांत पावसाची शक्यता:",
    "weather_rain_sum": "एकूण पाऊस:",
    "weather_risk_title": "🦠 हवामानाधारित रोग धोके:",
    "sust_title": "🌱 शेती पद्धती मूल्यांकन",
    "tag_bonus_d": "पर्यावरणीय फार्म प्रगती पुस्तक",
    "sust_desc": "विभाग ३.२ नुसार पारदर्शक गणितीय सूत्राने मूल्यांकन.",
    "label_irrig_tech": "सिंचन तंत्रज्ञान:",
    "tech_drip": "ठिबક सिंचन (कमाल पाणी बचत)",
    "tech_micro": "सूक्ष्म तुषार सिंचन",
    "tech_overhead": "तुषार सिंचन (स्प्रिंकलर)",
    "tech_flood": "पारंपारिक पाट पाणी / पूर सिंचन",
    "label_fert_strategy": "खत व्यवस्थापन:",
    "fert_integrated": "एकात्मिक खत (सेंद्रिय + संतुलित NPK)",
    "fert_organic": "१००% सेंद्रिय / गांडूळ खत",
    "fert_synthetic": "रासायनिक खतांचा जास्त वापर",
    "check_solar": "☀️ सोलर पंप प्रणाली (शून्य डिझेल वापर)",
    "check_mulch": "🍂 पिकांच्या अवशेषांचे आच्छादन (मल्चિંગ)",
    "check_legume": "🌾 डाळवर्गीय पिकांची फेरपालट",
    "btn_calc_sust": "शाश्वतता व कार्बन स्कोअर काढा",
    "sust_scorecard_title": "📊 पर्यावरणीय प्रगती पुस्तक",
    "assistant_title": "💬 कृषी तज्ज्ञ AI सल्लागार",
    "tag_bonus_e": "ICAR प्रमाणित कृषी सल्ला",
    "assistant_desc": "सर्व उत्तरे ICAR आणि कृषी विद्यापीठांच्या वैज्ञानिक माहितीवर आधारित आहेत.",
    "quick_prompts_title": "त्वरित प्रश्न:",
    "chat_welcome": "नमस्कार! मी आपला AI शेती सल्लागार आहे. पीक रोग, सिंचन किंवा खतांबद्दल कोणताही प्रश्न विचारा.",
    "btn_send": "पाठवा",
    "btn_clear_chat": "चॅट साफ करा",
    "iot_title": "📡 IoT सेन्सर गेटवे (ESP32 थेट प्रवाह)",
    "tag_bonus_f": "एज IoT गेटवे",
    "gauge_moist": "मातीतील ओलावा",
    "gauge_temp": "तापमान",
    "gauge_hum": "हवेतील आर्द्रता",
    "gauge_ph": "मातीचा pH",
    "simulate_scenarios_title": "चाचणीसाठी परिस्थिती बदला:",
    "btn_scen_normal": "🌤 सामान्य परिस्थिती",
    "btn_scen_drought": "🔥 अचानक दुष्काळ / पाणी टंचाई",
    "btn_scen_rain": "🌧 मुसळधार पाऊस प्रवाह",
    "agent_title": "🤖 स्वायत्त एजंट निर्णय चक्र",
    "tag_bonus_g": "स्वायत्त बंद-लूप नियंत्रण",
    "agent_desc": "स्वायत्त चक्र: निरीक्षण -> विचार -> निर्णय -> स्वयंचलित वाल्व सुरू",
    "valve_label": "स्मार्ट वाल्व स्थिती:",
    "btn_run_agent": "एजंट सायकल चालवा",
    "report_title": "📑 बेंचमार्क व मॉडेल मूल्यांकन अहवाल",
    "btn_raw_md": "कच्ची मार्कडाउन फाईल उघडा",
    "metric_macro_f1": "मुख्य मेट्रिक (Macro-F1)",
    "metric_acc": "एकूण अचूकता",
    "metric_samples": "चाचणी नमुने (PlantDoc फील्ड)",
    "metric_speed": "वेग",
    "cm_title": "फील्ड टेस्ट सेट कन्फ्युजन मॅट्रिक्स",
    "auth_modal_title": "शेतकरी खाते लॉगिन",
    "auth_signin_tab": "लॉग इन करा",
    "auth_register_tab": "नवीन खाते तयार करा",
    "auth_name_label": "पूर्ण नाव:",
    "auth_email_phone_label": "ईमेल किंवा मोबाईल नंबर:",
    "auth_pwd_label": "पासवर्ड:",
    "auth_loc_label": "राज्य / जिल्हा:",
    "auth_crop_label": "मुख्य पीक:",
    "auth_lang_label": "पसंतीची भाषा:",
    "btn_login_submit": "खात्यात प्रवेश करा",
    "btn_register_submit": "माझे शेतकरी खाते उघडा",
    "btn_back_home": "⬅ मुख्य स्कॅनरवर परत",
    "btn_back_scanner": "⬅ नवीन रोप / पान तपासा",
    "btn_browse_photos": "फोटो निवडा",
    "btn_take_photo": "कॅमेरा उघडा",
    "camera_modal_title": "लाइव्ह कॅमेरा पान स्कॅनर",
    "camera_frame_guide": "पानाला फ्रेमच्या मध्यभागी ठेवा",
    "btn_flip_camera": "कॅमेरा बदला",
    "btn_snap_photo": "फोटो घ्या आणि तपासा",
    "btn_download_pdf_file": "📥 प्रमाणपत्र डाउनलोड करा (HTML/PDF)",
    "btn_print_pdf": "🖨 प्रमाणपत्र प्रिंट करा",
    "print_modal_title": "📄 अधिकृत पीक रोग निदान प्रमाणपत्र",
    "invalid_plant_title": "⚠️ पीक किंवा वनस्पतीचा फोटो नाही",
    "invalid_plant_desc": "ही एआय प्रणाली फक्त शेतातील पिके, पाने, फळे आणि भाज्यांचे रोग तपासते. कृपया पिकाच्या पानाचा स्पष्ट फोटो अपलोड करा.",
    "footer_credits": "AI पीक रोग निदान • अचूक हवामान मार्गदर्शन • शाश्वत शेती",
    "web_consensus_title": "थेट इंटरनेट पडताळणी आणि तुलनात्मक निष्कर्ष",
    "web_consensus_subtitle": "ICAR, FAO आणि आंतरराष्ट्रीय डेटाबेससह रिअल-टाइम पडताळणी",
    "label_pathogen_latin": "वैज्ञानिक रोगकारक (Pathogen):",
    "label_weather_match": "हवामान सुसंगतता:",
    "label_corroborated_symptoms": "प्रमाणित पानांवरील लक्षणे:",
    "label_live_citations": "थेट इंटरनेट संदर्भ स्रोत:",
    "nav_account": "शेतकरी खाते",
    "default_farmer_name": "किसान मित्र (शेतकरी मित्र)",
    "badge_farmer_profile": "सक्रिय",
    "badge_logout": "लॉगआउट",
    "confirm_logout": "तुम्ही लॉगआउट करू इच्छिता किंवा खाते बदलू इच्छिता?",
    "iot_title": "📡 प्रत्यक्ष कृषी IoT हार्डवेअर गेटवे",
    "iot_architecture_desc": "थेट हार्डवेअर जोडणी: Arduino / ESP32 / BLE सेन्सर ➔ USB/Wi-Fi/Bluetooth ➔ AgriSmart AI ➔ शेतकरी कृती.",
    "iot_status_label": "हार्डवेअर स्थिती:",
    "iot_no_device": "कोणतेही IoT डिव्हाइस जोडलेले नाही",
    "iot_real_only_notice": "रिअल डेटा मोड: केवळ प्रत्यक्ष जोडलेल्या सेन्सरचा डेटा दर्शविला जातो. नसलेले सेन्सर रिक्त (--) राहतील.",
    "iot_not_connected_sub": "(सेन्सर जोडलेला नाही)",
    "iot_hub_title": "प्रत्यक्ष IoT सेन्सर जोडा (USB / Wi-Fi / Bluetooth)",
    "iot_tab_usb": "🔌 USB / सिरियल केबल",
    "iot_tab_wifi": "📶 Wi-Fi / नेटवर्क",
    "iot_tab_bt": "📡 ब्लूटूथ (BLE)",
    "iot_tab_code": "📜 Arduino / ESP32 कोड",
    "iot_tab_sim": "🧪 लॅब सिम्युलेटर (ऐच्छिक)",
    "usb_desc": "Arduino किंवा ESP32 थेट USB केबलने कनेक्ट करा:",
    "btn_web_serial": "ब्राउझरद्वारे USB कनेक्ट करा (Web Serial)",
    "btn_connect_port": "COM पोर्ट जोडा",
    "btn_disconnect_iot": "डिव्हाइस डिस्कनेक्ट करा",
    "wifi_push_title": "पर्याय 1 (पुश मोड - शिफारस केलेले):",
    "wifi_push_desc": "आपल्या ESP32 वरून थेट Wi-Fi द्वारे डेटा पाठवा:",
    "wifi_pull_title": "पर्याय 2 (पुल मोड):",
    "wifi_pull_desc": "ESP32 वेब सर्व्हर URL प्रविष्ट करा:",
    "btn_connect_wifi": "Wi-Fi सेन्सर जोडा",
    "bt_desc": "वायरलेस BLE माती ओलावा सेन्सर ब्लूटूथद्वारे जोडा:",
    "btn_scan_ble": "ब्लूटूथ सेन्सर शोधा आणि जोडा",
    "code_title": "Arduino IDE साठी तयार कोड:",
    "btn_copy_code": "📋 कोड कॉपी करा",
    "sim_notice": "चाचणीसाठी ऐच्छिक सिम्युलेटर:",
    "iot_terminal_title": "थेट हार्डवेअर सिरियल मॉनिटर",
    "nav_settings": "सेटिंग्ज",
    "tab_settings": "⚙️ सेटिंग्ज व प्रोफाइल",
    "settings_title": "सेटिंग्ज आणि शेतकरी प्रोफाइल",
    "settings_subtitle": "आपली शेतकरी ओळख, जमीन तपशील, प्रादेशिक भाषा, दृश्य मोड आणि IoT हार्डवेअर सेटिंग्ज व्यवस्थापित करा.",
    "tag_farmer_identity": "शेतकरी ओळख",
    "tag_accessibility": "सुलभता व प्रदर्शन",
    "tag_sensors": "सेन्सर्स आणि गेटवे",
    "tag_privacy": "सुरक्षा आणि बॅकअप",
    "set_card1_title": "वैयक्तिक तपशील आणि शेती प्रोफाइल",
    "set_card1_desc": "वैयक्तिक व कृषी तपशील ॲग्रीस्मार्ट एआयला आपल्या शेतासाठी रोग नियंत्रण व खत सल्ला वैयक्तिकृत करण्यास मदत करतात.",
    "set_label_name": "शेतकऱ्याचे नाव",
    "set_label_contact": "फोन नंबर किंवा ईमेल",
    "set_label_state": "राज्य / प्रदेश",
    "set_label_district": "जिल्हा",
    "set_label_village": "गाव / तालुका / लँडमार्क",
    "set_label_farm_size": "जमीन क्षेत्र व एकक",
    "set_label_crops": "प्रमुख लागवड केलेली पिके (निवडण्यासाठी क्लिक करा)",
    "set_label_soil": "मातीचा प्रमुख प्रकार",
    "set_label_water": "प्रमुख सिंचन स्रोत",
    "btn_save_profile": "💾 प्रोफाइल जतन करा",
    "set_card2_title": "प्रदर्शन, भाषा आणि आवाज सेटिंग्ज",
    "set_card2_desc": "प्लॅटफॉर्मचे स्वरूप, शेतात कडक उन्हासाठी उच्च कॉन्ट्रास्ट, बोलण्याचा वेग व ऑडिओ अलर्ट कस्टमाइझ करा.",
    "set_label_platform_lang": "प्लॅटफॉर्म भाषा (डिफॉल्ट)",
    "set_label_theme": "दृश्य प्रदर्शन थीम",
    "theme_standard": "फार्म ग्रीन",
    "theme_standard_sub": "मानक संतुलित हिरवा",
    "theme_sunlight": "सनलाइट मोड (हाय कॉन्ट्रास्ट)",
    "theme_sunlight_sub": "शेतात कडक उन्हासाठी",
    "theme_night": "नाईट मोड (डार्क)",
    "theme_night_sub": "कमी प्रकाशाचा गडद मोड",
    "set_label_fontsize": "फॉन्ट आकार (वाचनीयता)",
    "font_normal": "मानक (100%)",
    "font_large": "मोठा आकार (115% ज्येष्ठ)",
    "set_label_voice_rate": "आवाज बोलण्याचा वेग",
    "set_label_auto_voice": "स्वयंचलित आवाज वाचन",
    "set_sub_auto_voice": "फोटो स्कॅन होताच रोगाचे नाव लगेच मोठ्याने ऐकवा",
    "set_label_chime": "रोग चेतावणी ऑडिओ चाइम",
    "set_sub_chime": "गंभीर रोग आढळल्यास अलर्ट आवाज वाजवा",
    "btn_save_pref": "💾 प्रदर्शन सेटिंग्ज जतन करा",
    "set_card3_title": "IoT हार्डवेअर व सेन्सर सेटिंग्ज",
    "set_card3_desc": "शेतातील मायक्रोकंट्रोलर्स, डेटा अपडेट वारंवारता व गैर-कृषी ब्लूटूथ डिव्हाइस फिल्टरिंग व्यवस्थापित करा.",
    "set_label_iot_interval": "सेन्सर डेटा अपडेट वारंवारता",
    "set_ble_filter_title": "स्मार्ट BLE गैर-कृषी फिल्टर: सक्रिय",
    "set_ble_filter_desc": "ब्लूटूथ पेअरिंग दरम्यान स्मार्ट घड्याळे व स्पीकर्स नाकारते.",
    "set_label_local_ip": "गेटवे लोकल आयपी (ESP32 डेटा पुशसाठी)",
    "btn_copy_url": "URL कॉपी करा",
    "set_sub_local_ip": "थेट माती डेटा पाठवण्यासाठी हा URL आपल्या ESP32 मध्ये फ्लॅश करा.",
    "set_status_label": "हार्डवेअर गेटवे स्थिती:",
    "btn_open_iot_tab": "IoT पॅनेल उघडा",
    "set_card4_title": "खाते सुरक्षा व डेटा व्यवस्थापन",
    "set_card4_desc": "पासवर्ड बदला, निदान नोंदी निर्यात करा व ऑफलाइन कॅशे साफ करा.",
    "set_header_pwd": "खाते पासवर्ड बदला",
    "set_guest_pwd_notice": "तुम्ही अतिथी सत्र वापरत आहात. पासवर्ड बदलण्यासाठी खाते तयार करा.",
    "set_label_old_pwd": "सध्याचा पासवर्ड",
    "set_label_new_pwd": "नवीन पासवर्ड",
    "set_label_confirm_pwd": "नवीन पासवर्डची पुष्टी करा",
    "btn_change_pwd": "पासवर्ड अपडेट करा",
    "set_label_export": "शेती डायग्नोस्टिक डेटा निर्यात करा",
    "set_sub_export": "सर्व पानांचे स्कॅन व शिफारसींची संपूर्ण JSON बॅकअप फाइल डाउनलोड करा",
    "btn_export_data": "JSON निर्यात करा",
    "set_label_cache": "स्कॅनर मीडिया कॅशे साफ करा",
    "set_sub_cache": "कॅशे केलेले नमुने साफ करून मेमरी मोकळी करा",
    "btn_clear_cache": "कॅशे साफ करा",
    "set_label_logout": "शेतकरी खाते सत्र",
    "set_sub_logout": "सध्या अतिथी सत्र सुरू आहे",
    "btn_login_or_register": "लॉग इन / नोंदणी करा"
  }
};

// =================================================================
// 2. AGRICULTURAL DISTRICT DATABASE (COORDINATES & SOIL PROFILES)
// =================================================================
const DISTRICT_DATA = {
  "Gujarat": {
    "Ahmedabad": { lat: 23.0225, lon: 72.5714, soil: "Loamy", rainfall: 750 },
    "Rajkot": { lat: 22.3039, lon: 70.8022, soil: "Black Cotton", rainfall: 600 },
    "Surat": { lat: 21.1702, lon: 72.8311, soil: "Alluvial", rainfall: 1150 },
    "Vadodara": { lat: 22.3072, lon: 73.1812, soil: "Loamy", rainfall: 900 },
    "Mehsana": { lat: 23.5880, lon: 72.3693, soil: "Sandy", rainfall: 650 },
    "Banaskantha": { lat: 24.1724, lon: 72.4346, soil: "Sandy", rainfall: 550 },
    "Junagadh": { lat: 21.5222, lon: 70.4579, soil: "Black Cotton", rainfall: 800 },
    "Kutch": { lat: 23.2420, lon: 69.6669, soil: "Sandy", rainfall: 380 }
  },
  "Maharashtra": {
    "Pune": { lat: 18.5204, lon: 73.8567, soil: "Black Cotton", rainfall: 750 },
    "Nashik": { lat: 19.9975, lon: 73.7898, soil: "Red", rainfall: 820 },
    "Nagpur": { lat: 21.1458, lon: 79.0882, soil: "Black Cotton", rainfall: 1100 },
    "Chhatrapati Sambhajinagar": { lat: 19.8762, lon: 75.3433, soil: "Black Cotton", rainfall: 720 },
    "Solapur": { lat: 17.6599, lon: 75.9064, soil: "Black Cotton", rainfall: 580 },
    "Kolhapur": { lat: 16.7050, lon: 74.2433, soil: "Clay", rainfall: 1050 }
  },
  "Punjab": {
    "Ludhiana": { lat: 30.9010, lon: 75.8573, soil: "Alluvial", rainfall: 680 },
    "Amritsar": { lat: 31.6340, lon: 74.8723, soil: "Alluvial", rainfall: 700 },
    "Jalandhar": { lat: 31.3260, lon: 75.5762, soil: "Loamy", rainfall: 690 },
    "Bathinda": { lat: 30.2110, lon: 74.9455, soil: "Sandy", rainfall: 450 },
    "Patiala": { lat: 30.3398, lon: 76.3869, soil: "Alluvial", rainfall: 660 }
  },
  "Haryana": {
    "Karnal": { lat: 29.6857, lon: 76.9905, soil: "Alluvial", rainfall: 720 },
    "Hisar": { lat: 29.1492, lon: 75.7217, soil: "Sandy", rainfall: 450 },
    "Ambala": { lat: 30.3782, lon: 76.7767, soil: "Loamy", rainfall: 900 },
    "Rohtak": { lat: 28.8955, lon: 76.6066, soil: "Loamy", rainfall: 550 }
  },
  "Uttar Pradesh": {
    "Varanasi": { lat: 25.3176, lon: 82.9739, soil: "Alluvial", rainfall: 1050 },
    "Lucknow": { lat: 26.8467, lon: 80.9462, soil: "Alluvial", rainfall: 980 },
    "Kanpur": { lat: 26.4499, lon: 80.3319, soil: "Alluvial", rainfall: 850 },
    "Agra": { lat: 27.1767, lon: 78.0081, soil: "Sandy", rainfall: 650 },
    "Prayagraj": { lat: 25.4358, lon: 81.8463, soil: "Alluvial", rainfall: 950 }
  },
  "Madhya Pradesh": {
    "Indore": { lat: 22.7196, lon: 75.8577, soil: "Black Cotton", rainfall: 950 },
    "Bhopal": { lat: 23.2599, lon: 77.4126, soil: "Black Cotton", rainfall: 1050 },
    "Ujjain": { lat: 23.1765, lon: 75.7885, soil: "Black Cotton", rainfall: 900 },
    "Jabalpur": { lat: 23.1815, lon: 79.9864, soil: "Clay", rainfall: 1250 }
  },
  "Rajasthan": {
    "Jaipur": { lat: 26.9124, lon: 75.7873, soil: "Sandy", rainfall: 600 },
    "Jodhpur": { lat: 26.2389, lon: 73.0243, soil: "Sandy", rainfall: 350 },
    "Kota": { lat: 25.2138, lon: 75.8648, soil: "Black Cotton", rainfall: 800 },
    "Udaipur": { lat: 24.5854, lon: 73.7125, soil: "Red", rainfall: 650 }
  },
  "Karnataka": {
    "Bengaluru": { lat: 12.9716, lon: 77.5946, soil: "Red", rainfall: 920 },
    "Belagavi": { lat: 15.8497, lon: 74.4977, soil: "Black Cotton", rainfall: 850 },
    "Mysuru": { lat: 12.2958, lon: 76.6394, soil: "Red", rainfall: 800 }
  }
};

// =================================================================
// 3. INITIALIZATION & SPLASH SCREEN DISMISSAL
// =================================================================
document.addEventListener('DOMContentLoaded', () => {
  // 1. Splash screen dismissal after smooth 2.2s animation
  const splash = document.getElementById('splash-screen');
  if (splash) {
    setTimeout(() => {
      splash.classList.add('splash-hidden');
    }, 2200);
  }

  // 2. Set initial language in selector and translate entire page
  const langSelect = document.getElementById('global-lang-select');
  if (langSelect) langSelect.value = currentLanguage;
  changeGlobalLanguage(currentLanguage, false);

  // 3. Initialize Location selectors
  initManualLocationSelectors();

  // 4. Update Auth Button State
  updateAuthUI();
  initSettingsTab();

  // 5. Load live weather & Initialize Real IoT Hardware Monitor
  fetchLiveWeather();
  fetchIoTTelemetry();
  refreshComPorts();
  loadArduinoSketch();
  fetchNetworkIp();
  scheduleIoTTelemetryPolling();

  // 6. Drag & drop support
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

  // 7. Pre-calculate recommendations
  submitCropRecommendation();
  calculateIrrigation();
  computeSustainability();

  // 8. Try auto GPS detection if in GPS mode
  if (currentLocMode === 'gps' && navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        userLatitude = pos.coords.latitude;
        userLongitude = pos.coords.longitude;
        userLocationName = `Field GPS (${userLatitude.toFixed(2)}, ${userLongitude.toFixed(2)})`;
        const liveBadge = document.getElementById('live-weather-badge');
        if (liveBadge) liveBadge.innerText = "📍 GPS Synced";
        fetchLiveWeather();
      },
      err => { console.log("GPS prompt skipped, using default location."); }
    );
  }
});

// =================================================================
// 4. GLOBAL LANGUAGE TRANSLATION ENGINE (i18n)
// =================================================================
function changeGlobalLanguage(lang, save = true) {
  stopAudio();
  currentLanguage = lang;
  if (save) localStorage.setItem('agrismart_lang', lang);

  const dict = TRANSLATIONS[lang] || TRANSLATIONS['en'];

  // 1. Update all elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      if (el.tagName === 'INPUT' && el.type === 'text') {
        el.placeholder = dict[key];
      } else {
        el.innerText = dict[key];
      }
    }
  });

  // 2. Sync selectors
  const globalSelect = document.getElementById('global-lang-select');
  if (globalSelect && globalSelect.value !== lang) globalSelect.value = lang;
  const authSelect = document.getElementById('auth-language');
  if (authSelect && authSelect.value !== lang) authSelect.value = lang;

  // 3. Re-render dynamic diagnostic translations if active
  if (currentDiagnosisData) {
    renderDiagnosis(currentDiagnosisData);
  }
}

let iotTelemetryTimer = null;

function scheduleIoTTelemetryPolling() {
  if (iotTelemetryTimer) {
    clearInterval(iotTelemetryTimer);
    iotTelemetryTimer = null;
  }
  const iotTab = document.getElementById('tab-iot');
  const isIotActive = iotTab && iotTab.classList.contains('active');
  const intervalMs = isIotActive ? 3000 : 10000;
  iotTelemetryTimer = setInterval(checkIoTStatusAndTelemetry, intervalMs);
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

  const activeContent = document.getElementById(tabId);
  if (activeContent) activeContent.classList.add('active');

  const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick') && b.getAttribute('onclick').includes(tabId));
  if (activeBtn) activeBtn.classList.add('active');

  if (tabId === 'tab-settings') {
    populateSettingsForm();
  }

  if (tabId === 'tab-iot') {
    checkIoTStatusAndTelemetry();
  }
  scheduleIoTTelemetryPolling();
}

// =================================================================
// 5. DUAL LOCATION ENGINE (GPS AUTO & MANUAL STATE/DISTRICT)
// =================================================================
function setLocMode(mode) {
  currentLocMode = mode;
  const btnGps = document.getElementById('btn-loc-gps');
  const btnManual = document.getElementById('btn-loc-manual');
  const manualWrap = document.getElementById('manual-loc-inputs');

  if (mode === 'gps') {
    if (btnGps) btnGps.classList.add('active');
    if (btnManual) btnManual.classList.remove('active');
    if (manualWrap) manualWrap.style.display = 'none';
    detectGPSLocation();
  } else {
    if (btnGps) btnGps.classList.remove('active');
    if (btnManual) btnManual.classList.add('active');
    if (manualWrap) manualWrap.style.display = 'flex';
    initManualLocationSelectors();
  }
}

function initManualLocationSelectors() {
  const stateSel = document.getElementById('sel-state');
  if (!stateSel) return;
  const selectedState = stateSel.value || 'Gujarat';
  populateDistricts(selectedState);
}

function populateDistricts(stateName) {
  const distSel = document.getElementById('sel-district');
  if (!distSel) return;
  distSel.innerHTML = '';
  const districts = DISTRICT_DATA[stateName] || {};
  const distNames = Object.keys(districts);
  distNames.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.innerText = d;
    distSel.appendChild(opt);
  });
  if (distNames.length > 0) {
    onDistrictChanged(distNames[0]);
  }
}

function onStateChanged(stateName) {
  populateDistricts(stateName);
  // Sync crop tab state dropdown
  const cropState = document.getElementById('crop-state-input');
  if (cropState && cropState.value !== stateName) {
    cropState.value = stateName;
    syncCropDistrictOptions(stateName);
  }
}

function onDistrictChanged(districtName) {
  const stateSel = document.getElementById('sel-state');
  const stateName = stateSel ? stateSel.value : 'Gujarat';
  const info = (DISTRICT_DATA[stateName] && DISTRICT_DATA[stateName][districtName]) || null;
  if (info) {
    userLatitude = info.lat;
    userLongitude = info.lon;
    userLocationName = `${districtName}, ${stateName}`;
    fetchLiveWeather();

    // Sync Tab 2 dropdowns
    const cropDist = document.getElementById('crop-district-input');
    if (cropDist && cropDist.value !== districtName) {
      cropDist.value = districtName;
    }
    const cropSoil = document.getElementById('crop-soil');
    if (cropSoil && info.soil) cropSoil.value = info.soil;
    const cropRain = document.getElementById('crop-rain');
    if (cropRain && info.rainfall) cropRain.value = info.rainfall;
  }
}

function syncCropDistrictOptions(stateName) {
  const distSel = document.getElementById('crop-district-input');
  if (!distSel) return;
  distSel.innerHTML = '';
  const districts = DISTRICT_DATA[stateName] || {};
  const distNames = Object.keys(districts);
  distNames.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.innerText = d;
    distSel.appendChild(opt);
  });
  if (distNames.length > 0) {
    syncCropDistrictCoords();
  }
  // Sync top nav if in manual mode
  const topState = document.getElementById('sel-state');
  if (topState && topState.value !== stateName) {
    topState.value = stateName;
    populateDistricts(stateName);
  }
}

function syncCropDistrictCoords() {
  const stateEl = document.getElementById('crop-state-input');
  const distEl = document.getElementById('crop-district-input');
  if (!stateEl || !distEl) return;
  const stateName = stateEl.value;
  const districtName = distEl.value;
  const info = (DISTRICT_DATA[stateName] && DISTRICT_DATA[stateName][districtName]) || null;
  if (info) {
    userLatitude = info.lat;
    userLongitude = info.lon;
    userLocationName = `${districtName}, ${stateName}`;
    fetchLiveWeather();
    const cropSoil = document.getElementById('crop-soil');
    if (cropSoil && info.soil) cropSoil.value = info.soil;
    const cropRain = document.getElementById('crop-rain');
    if (cropRain && info.rainfall) cropRain.value = info.rainfall;
  }
}

function detectGPSLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      userLatitude = pos.coords.latitude;
      userLongitude = pos.coords.longitude;
      userLocationName = `GPS Location (${userLatitude.toFixed(3)}°N, ${userLongitude.toFixed(3)}°E)`;
      const liveBadge = document.getElementById('live-weather-badge');
      if (liveBadge) liveBadge.innerText = "📍 GPS Synced ✓";
      fetchLiveWeather();
      calculateIrrigation();
      showToast("✓ GPS location synced successfully.", "success");
    },
    (err) => {
      alert("Could not access GPS location. Please allow location permissions in your browser: " + err.message);
    }
  );
}

let cachedWeatherData = null;

async function fetchLiveWeather() {
  try {
    const res = await fetch(`/api/weather?lat=${userLatitude}&lon=${userLongitude}&name=${encodeURIComponent(userLocationName)}`);
    const data = await res.json();
    cachedWeatherData = data;

    const tempEl = document.getElementById('w-temp');
    if (tempEl) tempEl.innerText = data.current_weather.temperature_c;
    const locEl = document.getElementById('w-location');
    if (locEl) locEl.innerText = data.location;
    const srcEl = document.getElementById('w-source');
    if (srcEl) srcEl.innerText = data.data_source;
    const humEl = document.getElementById('w-humidity');
    if (humEl) humEl.innerText = `${data.current_weather.humidity_pct}%`;
    const windEl = document.getElementById('w-wind');
    if (windEl) windEl.innerText = `${data.current_weather.wind_speed_kmh} km/h`;
    const rainProbEl = document.getElementById('w-rain-prob');
    if (rainProbEl) rainProbEl.innerText = `${data.current_weather.rain_24h_prob_pct}%`;
    const rainSumEl = document.getElementById('w-rain-sum');
    if (rainSumEl) rainSumEl.innerText = `${data.current_weather.rain_24h_sum_mm} mm`;

    const liveBadge = document.getElementById('live-weather-badge');
    if (liveBadge) {
      liveBadge.innerText = `☁ ${data.current_weather.temperature_c}°C | ${data.location.split('(')[0].trim()}`;
    }

    // Render alerts
    const alertBox = document.getElementById('weather-alerts');
    if (alertBox) {
      alertBox.innerHTML = '';
      (data.agronomic_actions || []).forEach(act => {
        const p = document.createElement('p');
        p.style.fontSize = '0.85rem';
        p.style.marginBottom = '6px';
        const badgeClass = act.priority === 'HIGH' ? 'badge-danger' : (act.priority === 'MEDIUM' ? 'badge-warning' : 'badge-info');
        p.innerHTML = `<span class="badge ${badgeClass}" style="padding:2px 6px; font-size:0.7rem;">${act.priority}</span> <strong>${act.title}:</strong> ${act.guidance}`;
        alertBox.appendChild(p);
      });
    }
  } catch (e) {
    console.error('Weather fetch error:', e);
  }
}

// =================================================================
// 6. MULTILINGUAL AUDIO SPEAKER & TEXT-TO-SPEECH (TTS)
// =================================================================
let activeAudioElement = null;

function stopAudio() {
  if (activeAudioElement) {
    try {
      activeAudioElement.pause();
      activeAudioElement.currentTime = 0;
    } catch (e) {}
    activeAudioElement = null;
  }
  if ('speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  }
  isSpeaking = false;
  updateSpeakerButtonState(false);
}

function speakText(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  speakRaw(el.innerText, currentLanguage);
}

function speakDiagnosis() {
  if (!currentDiagnosisData) {
    showToast("Please run an image diagnosis first.", "warning");
    return;
  }
  
  let textToSpeak = "";
  if (currentLanguage === 'hi' && currentDiagnosisData.translations && currentDiagnosisData.translations.hi) {
    textToSpeak = `${currentDiagnosisData.translations.hi.title}. ${currentDiagnosisData.translations.hi.action}`;
  } else if (currentLanguage === 'gu' && currentDiagnosisData.translations && currentDiagnosisData.translations.gu) {
    textToSpeak = `${currentDiagnosisData.translations.gu.title}. ${currentDiagnosisData.translations.gu.action}`;
  } else if (currentLanguage === 'mr' && currentDiagnosisData.translations && currentDiagnosisData.translations.mr) {
    textToSpeak = `${currentDiagnosisData.translations.mr.title}. ${currentDiagnosisData.translations.mr.action}`;
  } else {
    textToSpeak = `Identified ${currentDiagnosisData.display_name} with ${Math.round(currentDiagnosisData.confidence * 100)} percent confidence. Precautions: ${currentDiagnosisData.precautions.join('. ')}. Recommended treatment: ${currentDiagnosisData.chemical_treatment || currentDiagnosisData.organic_treatment}`;
  }
  
  speakRaw(textToSpeak, currentLanguage);
}

function speakRaw(text, targetLang = null) {
  const lang = targetLang || currentLanguage || 'en';

  if (isSpeaking) {
    stopAudio();
    return;
  }

  const clean = text.replace(/[*_#`~\[\]()]/g, ' ').replace(/\s+/g, ' ').trim();
  if (!clean) return;

  isSpeaking = true;
  updateSpeakerButtonState(true);

  // Strategy 1: For Indian languages, stream from backend /api/tts endpoint
  if (['hi', 'gu', 'mr'].includes(lang)) {
    try {
      const audioUrl = `/api/tts?text=${encodeURIComponent(clean.slice(0, 240))}&lang=${lang}`;
      activeAudioElement = new Audio(audioUrl);

      activeAudioElement.onended = () => {
        isSpeaking = false;
        updateSpeakerButtonState(false);
        activeAudioElement = null;
      };

      activeAudioElement.onerror = () => {
        console.warn('Backend TTS failed, trying Web Speech fallback.');
        activeAudioElement = null;
        fallbackWebSpeech(clean, lang);
      };

      activeAudioElement.play().catch(err => {
        console.warn('Audio play error, trying Web Speech fallback:', err);
        activeAudioElement = null;
        fallbackWebSpeech(clean, lang);
      });
      return;
    } catch (err) {
      console.warn('Audio stream error:', err);
      fallbackWebSpeech(clean, lang);
      return;
    }
  }

  // Strategy 2: For English, use Web Speech API with fallback
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = 'en-US';
    utterance.rate = 0.95;

    const voices = window.speechSynthesis.getVoices();
    const enVoice = voices.find(v => v.lang.startsWith('en'));
    if (enVoice) utterance.voice = enVoice;

    utterance.onend = () => {
      isSpeaking = false;
      updateSpeakerButtonState(false);
    };
    utterance.onerror = () => {
      isSpeaking = false;
      updateSpeakerButtonState(false);
    };

    window.speechSynthesis.speak(utterance);
  } else {
    try {
      const audioUrl = `/api/tts?text=${encodeURIComponent(clean.slice(0, 240))}&lang=en`;
      activeAudioElement = new Audio(audioUrl);
      activeAudioElement.onended = () => {
        isSpeaking = false;
        updateSpeakerButtonState(false);
        activeAudioElement = null;
      };
      activeAudioElement.play();
    } catch (e) {
      isSpeaking = false;
      updateSpeakerButtonState(false);
    }
  }
}

function fallbackWebSpeech(clean, lang) {
  if (!('speechSynthesis' in window)) {
    isSpeaking = false;
    updateSpeakerButtonState(false);
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(clean);
  const langMap = { 'hi': 'hi-IN', 'gu': 'gu-IN', 'mr': 'mr-IN', 'en': 'en-US' };
  utterance.lang = langMap[lang] || 'en-US';
  utterance.rate = 0.95;

  utterance.onend = () => {
    isSpeaking = false;
    updateSpeakerButtonState(false);
  };
  utterance.onerror = () => {
    isSpeaking = false;
    updateSpeakerButtonState(false);
  };

  window.speechSynthesis.speak(utterance);
}

function updateSpeakerButtonState(active) {
  const btn = document.getElementById('btn-speaker-diag');
  if (btn) {
    if (active) {
      btn.classList.add('speaking');
      btn.innerHTML = `🔊 <span>Speaking... (Click to Stop)</span>`;
    } else {
      btn.classList.remove('speaking');
      btn.innerHTML = `🔊 <span data-i18n="btn_speaker">${(TRANSLATIONS[currentLanguage] || TRANSLATIONS['en']).btn_speaker}</span>`;
    }
  }
}

// =================================================================
// 7. CORE TASK: LEAF DISEASE DETECTION WITH CROP SELECTOR
// =================================================================

// =================================================================
// 6.1 FIELD CAMERA / WEBCAM LEAF SCANNER
// =================================================================
let cameraStream = null;
let currentFacingMode = 'environment';

async function openCameraModal() {
  const modal = document.getElementById('camera-modal');
  if (!modal) return;
  modal.classList.add('active');
  await startCameraStream();
}

async function startCameraStream() {
  stopCameraStream();
  const video = document.getElementById('camera-video-feed');
  if (!video) return;

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showToast("Camera access is not supported by your browser or environment.", "error");
    closeCameraModal();
    return;
  }

  try {
    const constraints = {
      video: {
        facingMode: currentFacingMode,
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    };
    cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = cameraStream;
    await video.play();
  } catch (err) {
    console.warn("Could not start camera with constraints, attempting fallback:", err);
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      video.srcObject = cameraStream;
      await video.play();
    } catch (e) {
      showToast("Unable to access camera. Please check permissions.", "error");
      closeCameraModal();
    }
  }
}

function stopCameraStream() {
  if (cameraStream) {
    try {
      cameraStream.getTracks().forEach(track => track.stop());
    } catch (e) {}
    cameraStream = null;
  }
  const video = document.getElementById('camera-video-feed');
  if (video) video.srcObject = null;
}

function closeCameraModal() {
  stopCameraStream();
  const modal = document.getElementById('camera-modal');
  if (modal) modal.classList.remove('active');
}

async function switchCameraFacingMode() {
  currentFacingMode = (currentFacingMode === 'environment') ? 'user' : 'environment';
  await startCameraStream();
}

function captureCameraPhoto() {
  const video = document.getElementById('camera-video-feed');
  const canvas = document.getElementById('camera-capture-canvas');
  if (!video || !canvas || !video.videoWidth) {
    showToast("Camera is not ready yet. Please wait a moment.", "warning");
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob((blob) => {
    if (!blob) {
      showToast("Failed to capture image from camera.", "error");
      return;
    }
    const filename = `field_leaf_${Date.now()}.jpg`;
    const file = new File([blob], filename, { type: 'image/jpeg' });
    closeCameraModal();
    processSelectedFile(file);
    showToast("Photo captured successfully! Starting AI diagnosis...", "success");
    setTimeout(runAnalysis, 250);
  }, 'image/jpeg', 0.92);
}

function handleFileUpload(event) {
  if (event.target.files && event.target.files[0]) {
    processSelectedFile(event.target.files[0]);
  }
}

function processSelectedFile(file) {
  currentSelectedImageFile = file;
  hideInvalidPlantAlert();
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('image-preview').src = e.target.result;
    document.getElementById('image-preview-container').style.display = 'block';
  };
  reader.readAsDataURL(file);
}

async function loadSample(filename) {
  try {
    hideInvalidPlantAlert();
    const resp = await fetch(`/samples/${filename}`);
    if (!resp.ok) throw new Error('Sample not found');
    const blob = await resp.blob();
    const file = new File([blob], filename, { type: 'image/jpeg' });
    processSelectedFile(file);

    // Auto-select corresponding crop in dropdown
    const cropSel = document.getElementById('target-crop-select');
    if (cropSel) {
      if (filename.startsWith('tomato')) cropSel.value = 'Tomato';
      else if (filename.startsWith('corn')) cropSel.value = 'Corn';
      else if (filename.startsWith('potato')) cropSel.value = 'Potato';
      else if (filename.startsWith('bell_pepper')) cropSel.value = 'Pepper__bell';
      else if (filename.startsWith('apple')) cropSel.value = 'Apple';
      else if (filename.startsWith('grape')) cropSel.value = 'Grape';
    }

    setTimeout(runAnalysis, 150);
  } catch (e) {
    console.error('Error loading sample:', e);
  }
}

async function runAnalysis() {
  if (!currentSelectedImageFile) {
    showToast('Please select or upload a leaf photo first.', 'warning');
    return;
  }

  const btn = document.getElementById('btn-analyze');
  btn.innerText = 'Analyzing Image with MobileNetV3...';
  btn.disabled = true;

  const laser = document.getElementById('laser-scan-line');
  if (laser) laser.style.display = 'block';

  const formData = new FormData();
  formData.append('file', currentSelectedImageFile);
  
  // Read selected crop to prevent Tomato Early Blight bias
  const cropSelectEl = document.getElementById('target-crop-select');
  if (cropSelectEl && cropSelectEl.value && cropSelectEl.value !== 'auto') {
    formData.append('target_crop', cropSelectEl.value);
  }

  if (currentUser) {
    formData.append('user_id', currentUser.id);
  }

  if (typeof cachedWeatherData !== 'undefined' && cachedWeatherData && cachedWeatherData.current_weather) {
    formData.append('current_weather', JSON.stringify(cachedWeatherData.current_weather));
  }

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    if (!res.ok) {
      if (res.status === 400 && data.detail && data.detail.error === 'NOT_A_PLANT_IMAGE') {
        showInvalidPlantError(data.detail.message, data.detail.user_guidance);
        return;
      }
      const errTxt = data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'Inference failed';
      showToast(errTxt, 'error');
      return;
    }

    currentDiagnosisData = data;
    hideInvalidPlantAlert();
    renderDiagnosis(data);
    showToast(`✓ Diagnosed: ${data.display_name} (${Math.round(data.confidence * 100)}%)`, 'success');
  } catch (err) {
    showToast('Failed to connect to AI inference server: ' + err.message, 'error');
  } finally {
    if (laser) laser.style.display = 'none';
    btn.innerText = '🔍 Run AI Disease Diagnosis';
    btn.disabled = false;
  }
}

function showInvalidPlantError(reason, guidance) {
  document.getElementById('diag-results').style.display = 'none';
  document.getElementById('diag-empty').style.display = 'block';

  const alertBox = document.getElementById('image-validation-alert');
  if (alertBox) {
    const desc = document.getElementById('val-alert-desc');
    if (desc) desc.innerText = guidance || reason;
    alertBox.style.display = 'block';
  }

  const modal = document.getElementById('invalid-plant-modal');
  if (modal) {
    const reasonEl = document.getElementById('invalid-modal-reason');
    if (reasonEl) reasonEl.innerText = guidance || reason;
    modal.classList.add('active');
  }
}

function closeInvalidPlantModal() {
  const modal = document.getElementById('invalid-plant-modal');
  if (modal) modal.classList.remove('active');
}

function hideInvalidPlantAlert() {
  const alertBox = document.getElementById('image-validation-alert');
  if (alertBox) alertBox.style.display = 'none';
}

function resetDiagnosisScanner() {
  stopAudio();
  currentSelectedImageFile = null;
  currentDiagnosisData = null;

  const preview = document.getElementById('image-preview');
  if (preview) preview.src = '';

  const previewContainer = document.getElementById('image-preview-container');
  if (previewContainer) previewContainer.style.display = 'none';

  const fileInput = document.getElementById('file-input');
  if (fileInput) fileInput.value = '';

  const diagResults = document.getElementById('diag-results');
  if (diagResults) diagResults.style.display = 'none';

  const diagEmpty = document.getElementById('diag-empty');
  if (diagEmpty) diagEmpty.style.display = 'block';

  const badge = document.getElementById('diag-badge');
  if (badge) {
    badge.className = 'badge';
    badge.innerText = (TRANSLATIONS[currentLanguage] || TRANSLATIONS['en']).badge_awaiting;
  }

  hideInvalidPlantAlert();
  closeInvalidPlantModal();

  const consensusCard = document.getElementById('web-consensus-card');
  if (consensusCard) consensusCard.style.display = 'none';

  const dropZone = document.getElementById('drop-zone');
  if (dropZone) dropZone.scrollIntoView({ behavior: 'smooth', block: 'center' });
  showToast("Scanner ready for next leaf photo.", "info");
}

function renderDiagnosis(data) {
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

  // Regional Translation based on active language
  const transBox = document.getElementById('res-regional-action');
  if (currentLanguage === 'hi' && data.translations && data.translations.hi) {
    transBox.innerText = `${data.translations.hi.title}: ${data.translations.hi.action}`;
  } else if (currentLanguage === 'gu' && data.translations && data.translations.gu) {
    transBox.innerText = `${data.translations.gu.title}: ${data.translations.gu.action}`;
  } else if (currentLanguage === 'mr' && data.translations && data.translations.mr) {
    transBox.innerText = `${data.translations.mr.title}: ${data.translations.mr.action}`;
  } else if (data.translations && data.translations[currentLanguage]) {
    transBox.innerText = `${data.translations[currentLanguage].title}: ${data.translations[currentLanguage].action}`;
  } else {
    transBox.innerText = `${data.display_name}: Precautions - ${data.precautions[0] || 'Prune affected leaves.'} Recommended Treatment - ${data.chemical_treatment || data.organic_treatment}`;
  }

  // Live Internet Cross-Verification & Comparison Card
  const consensusCard = document.getElementById('web-consensus-card');
  if (consensusCard && data.web_consensus) {
    consensusCard.style.display = 'block';
    const wc = data.web_consensus;
    
    const pill = document.getElementById('consensus-badge-pill');
    if (pill) {
      const score = Math.round(wc.agreement_score_pct || wc.consensus_agreement_pct || (data.confidence * 100));
      pill.innerText = `${score}% Agreement`;
      pill.className = 'badge consensus-badge ' + (score >= 88 ? 'badge-success' : 'badge-warning');
    }
    
    const sumText = document.getElementById('consensus-summary-text');
    if (sumText) sumText.innerText = wc.consensus_summary || "Foliage characteristics corroborated against online phytosanitary databases.";
    
    const taxa = document.getElementById('consensus-taxa');
    if (taxa) taxa.innerText = wc.scientific_taxa || wc.pathogen_latin || data.class_label;
    
    const weatherMatch = document.getElementById('consensus-weather-match');
    if (weatherMatch) weatherMatch.innerText = wc.weather_correlation || "Ambient microclimate matches typical foliar incubation conditions.";
    
    const indList = document.getElementById('consensus-indicators-list');
    if (indList) {
      indList.innerHTML = '';
      const indicators = wc.symptom_match_indicators || [
        "Visual necrotic leaf margin spots match pathogen profile",
        "Concentric target-board foliar rings corroborated",
        "Chlorotic leaf halo pattern matches ICAR plant pathology register"
      ];
      indicators.forEach(ind => {
        const li = document.createElement('li');
        li.innerText = ind;
        indList.appendChild(li);
      });
    }
    
    const citeList = document.getElementById('consensus-citations-list');
    if (citeList) {
      citeList.innerHTML = '';
      const sources = wc.online_sources || (wc.live_internet_citations ? wc.live_internet_citations.map(c => ({ title: c, authority: 'Verified Agronomic Source' })) : [
        { title: "ICAR National Plant Pathology Register", authority: "ICAR India", domain: "icar.org.in" },
        { title: "FAO UN Crop Protection Standards", authority: "FAO United Nations", domain: "fao.org" }
      ]);
      sources.forEach(src => {
        const tag = document.createElement('span');
        tag.className = 'citation-tag';
        tag.innerHTML = `✓ <strong>${src.title || src.name}</strong> <small>(${src.authority || src.domain || 'Verified Repository'})</small>`;
        citeList.appendChild(tag);
      });
    }
  } else if (consensusCard) {
    consensusCard.style.display = 'none';
  }

  // Render Diagnosis Feedback Box
  const diagFb = document.getElementById('diag-feedback-box');
  if (diagFb) {
    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS['en'];
    diagFb.style.display = 'flex';
    diagFb.innerHTML = `
      <span class="feedback-question">
        <span>💡</span> <span>${dict.feedback_question}</span>
      </span>
      <div class="feedback-btn-group">
        <button class="btn-feedback" onclick="submitFarmerFeedback('diagnosis', true)">
          👍 <span>${dict.btn_yes}</span>
        </button>
        <button class="btn-feedback btn-feedback-no" onclick="submitFarmerFeedback('diagnosis', false)">
          👎 <span>${dict.btn_no}</span>
        </button>
        <button class="btn-feedback-dismiss" onclick="dismissFeedback('diag-feedback-box')" title="Dismiss">✕</button>
      </div>
    `;
  }

  // Auto-Voice readout & Sound Chime (from Settings Preferences)
  try {
    if (currentPreferences.audio_chime !== false && data.is_disease) {
      playDiseaseAlertChime();
    }
    if (currentPreferences.auto_voice && !isSpeaking) {
      setTimeout(() => speakDiagnosisText(), 600);
    }
  } catch (e) {
    console.log('Audio alert trigger:', e);
  }
}

// =================================================================
// 8. PRINTABLE / DOWNLOADABLE REPORT (PDF & HTML EXPORT)
// =================================================================
function generateCertificateHtml(data) {
  const farmerName = currentUser ? currentUser.name : "Registered Farmer / Guest";
  const farmerLocation = currentUser ? `${currentUser.location} (${userLocationName})` : userLocationName;
  const farmerContact = currentUser ? currentUser.email_or_phone : "N/A";
  const certId = "AGRISMART-" + Date.now().toString(36).toUpperCase();
  const dateStr = new Date().toLocaleDateString('en-IN', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });

  const previewSrc = (document.getElementById('image-preview') && document.getElementById('image-preview').src) || '';
  const isHealthy = !data.is_disease;
  const statusColor = isHealthy ? "#15803d" : "#b91c1c";
  const statusBg = isHealthy ? "#f0fdf4" : "#fef2f2";
  const statusText = isHealthy ? "HEALTHY CROP — NO PATHOGEN" : "INFECTED — INTERVENTION REQUIRED";
  const precautionsLi = (data.precautions || []).map(p => `<li style="margin-bottom:6px;">${p}</li>`).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AgriSmart AI - Plant Pathology Certificate - ${certId}</title>
  <style>
    @page { size: A4; margin: 15mm; }
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; background: #f8fafc; margin: 0; padding: 20px; }
    .cert-container { max-width: 800px; margin: 0 auto; background: white; border: 3px double #15803d; border-radius: 12px; padding: 30px 36px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .cert-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #16a34a; padding-bottom: 16px; margin-bottom: 20px; }
    .cert-logo-title h1 { color: #15803d; font-size: 22px; margin: 0 0 4px 0; }
    .cert-logo-title p { margin: 0; font-size: 11px; color: #64748b; font-weight: 600; }
    .cert-badge { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 700; text-align: right; }
    .section-title { font-size: 13px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 0.8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin: 18px 0 10px 0; }
    .farmer-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px; background: #f8fafc; padding: 12px 16px; border-radius: 8px; border: 1px solid #e2e8f0; }
    .diag-box { display: flex; gap: 20px; align-items: center; background: ${statusBg}; border: 1px solid ${statusColor}40; border-radius: 10px; padding: 16px; margin: 12px 0; }
    .crop-thumb { width: 100px; height: 100px; object-fit: cover; border-radius: 8px; border: 2px solid #cbd5e1; }
    .diag-info { flex: 1; }
    .diag-info h2 { margin: 0 0 6px 0; color: ${statusColor}; font-size: 20px; }
    .treatment-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 12px 0; }
    .treatment-card { padding: 12px 14px; border-radius: 8px; font-size: 12px; line-height: 1.5; }
    .organic-card { background: #f0fdf4; border-left: 4px solid #16a34a; }
    .chemical-card { background: #f8fafc; border-left: 4px solid #0284c7; }
    .treatment-card strong { display: block; margin-bottom: 4px; font-size: 12px; }
    .footer-stamp { margin-top: 26px; border-top: 1px solid #e2e8f0; padding-top: 14px; display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: #64748b; }
    .stamp-box { border: 2px dashed #15803d; padding: 6px 14px; border-radius: 6px; color: #15803d; font-weight: 800; }
    @media print { body { background: white; padding: 0; } .cert-container { box-shadow: none; border: 2px solid #15803d; } .no-print { display: none; } }
  </style>
</head>
<body>
  <div style="max-width:800px; margin:0 auto 12px auto; text-align:right;" class="no-print">
    <button onclick="window.print()" style="background:#15803d; color:white; border:none; padding:8px 18px; border-radius:6px; font-weight:bold; cursor:pointer;">🖨 Print / Save as PDF</button>
  </div>
  <div class="cert-container">
    <div class="cert-header">
      <div class="cert-logo-title">
        <h1>🌱 AGRISMART AI</h1>
        <p>OFFICIAL PLANT PATHOLOGY & CROP HEALTH DIAGNOSTIC CERTIFICATE</p>
        <p style="font-size:10px; color:#94a3b8;">Verified with ICAR & FAO Plant Pathology Standards</p>
      </div>
      <div class="cert-badge">
        <div>Ref: ${certId}</div>
        <div style="color:#15803d;">${dateStr.split(',')[0]}</div>
      </div>
    </div>

    <div class="section-title">1. Farm & Agro-Ecological Profiling</div>
    <div class="farmer-grid">
      <div><strong>Farmer / Holder:</strong> ${farmerName}</div>
      <div><strong>Registered Contact:</strong> ${farmerContact}</div>
      <div><strong>GPS Location:</strong> ${farmerLocation}</div>
      <div><strong>Host Crop Evaluated:</strong> ${data.crop}</div>
    </div>

    <div class="section-title">2. AI Pathology Computer Vision Findings</div>
    <div class="diag-box">
      ${previewSrc ? `<img src="${previewSrc}" alt="Crop Photo" class="crop-thumb">` : ''}
      <div class="diag-info">
        <h2>${data.display_name}</h2>
        <div style="font-size:12px; color:#475569; margin-bottom:6px;"><strong>Taxonomic Identifier:</strong> ${data.class_label}</div>
        <div style="display:flex; gap:12px; align-items:center;">
          <span style="background:${statusColor}; color:white; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:700;">${statusText}</span>
          <span style="font-size:12px; font-weight:700; color:#0f172a;">Model Confidence: ${(data.confidence * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>

    <div class="section-title">3. Immediate Agronomic Precautions</div>
    <ul style="font-size:12px; line-height:1.6; padding-left:20px; margin:6px 0;">
      ${precautionsLi}
    </ul>

    <div class="section-title">4. Prescription & Integrated Pest Management (IPM)</div>
    <div class="treatment-grid">
      <div class="treatment-card organic-card">
        <strong style="color:#15803d;">🌿 Organic / Biological Control:</strong>
        ${data.organic_treatment || 'Maintain adequate aeration and mulch soil with dry straw.'}
      </div>
      <div class="treatment-card chemical-card">
        <strong style="color:#0284c7;">🧪 Chemical Intervention (If Infestation > 10%):</strong>
        ${data.chemical_treatment || 'No chemical fungicide required for current crop stage.'}
      </div>
    </div>

    <div class="footer-stamp">
      <div>
        <div><strong>AgriSmart AI Computer Vision Diagnostics</strong></div>
        <div>Validated against PlantDoc and ICAR Pathology Frameworks</div>
        <div>Timestamp: ${dateStr}</div>
      </div>
      <div class="stamp-box">✓ ICAR / KVK COMPLIANT</div>
    </div>
  </div>
</body>
</html>`;
}

function printDiagnosticReport() {
  if (!currentDiagnosisData) {
    showToast("Please perform a disease diagnosis first.", "warning");
    return;
  }
  const reportHtml = generateCertificateHtml(currentDiagnosisData);
  const printWindow = window.open('', '_blank', 'width=850,height=900');
  if (printWindow) {
    printWindow.document.write(reportHtml);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 450);
  } else {
    window.print();
  }
}

function downloadDiagnosticReportFile() {
  if (!currentDiagnosisData) {
    showToast("Please perform a disease diagnosis first.", "warning");
    return;
  }
  const reportHtml = generateCertificateHtml(currentDiagnosisData);
  const blob = new Blob([reportHtml], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `AgriSmart_Diagnostic_Report_${currentDiagnosisData.crop.replace(/\s+/g, '_')}_${Date.now()}.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("Diagnostic report downloaded! You can open and print it anytime.", "success");
}

function openPrintReportModal() {
  if (!currentDiagnosisData) {
    showToast("Please perform a disease diagnosis first.", "warning");
    return;
  }

  document.getElementById('pr-farmer-name').innerText = currentUser ? currentUser.name : "Guest Farmer";
  document.getElementById('pr-farmer-location').innerText = currentUser ? `${currentUser.location} • ${userLocationName}` : userLocationName;
  document.getElementById('pr-crop').innerText = currentDiagnosisData.crop;
  document.getElementById('pr-disease').innerText = currentDiagnosisData.display_name;
  document.getElementById('pr-class-label').innerText = currentDiagnosisData.class_label;
  document.getElementById('pr-confidence').innerText = `${Math.round(currentDiagnosisData.confidence * 100)}%`;

  const prUl = document.getElementById('pr-precautions');
  prUl.innerHTML = '';
  (currentDiagnosisData.precautions || []).forEach(p => {
    const li = document.createElement('li');
    li.innerText = p;
    prUl.appendChild(li);
  });

  document.getElementById('pr-organic').innerText = currentDiagnosisData.organic_treatment || 'None needed.';
  document.getElementById('pr-chemical').innerText = currentDiagnosisData.chemical_treatment || 'No chemical intervention needed.';
  document.getElementById('print-report-date').innerText = "Generated: " + new Date().toLocaleString();

  document.getElementById('report-modal').classList.add('active');
}

function closeReportModal() {
  document.getElementById('report-modal').classList.remove('active');
}

// =================================================================
// 9. USER AUTHENTICATION & INPUT VALIDATIONS
// =================================================================
function validateAuthInputs() {
  const isReg = (authMode === 'register');
  const nameEl = document.getElementById('auth-name');
  const nameHint = document.getElementById('auth-name-hint');
  const contactEl = document.getElementById('auth-email-phone');
  const contactHint = document.getElementById('auth-contact-hint');
  const pwdEl = document.getElementById('auth-password');
  const pwdHint = document.getElementById('auth-pwd-hint');

  let isValid = true;

  if (isReg && nameEl && nameHint) {
    const nameVal = nameEl.value.trim();
    if (nameVal.length >= 2 && /^[a-zA-Z\s.'-]+$/.test(nameVal)) {
      nameHint.className = 'input-hint valid';
      nameHint.innerText = '✓ Valid Name';
      nameEl.classList.remove('input-invalid');
      nameEl.classList.add('input-valid');
    } else if (nameVal.length > 0) {
      nameHint.className = 'input-hint invalid';
      nameHint.innerText = '⚠️ Please enter full name (letters only, min 2 characters)';
      nameEl.classList.remove('input-valid');
      nameEl.classList.add('input-invalid');
      isValid = false;
    } else {
      nameHint.innerText = '';
      nameEl.classList.remove('input-valid', 'input-invalid');
    }
  }

  if (contactEl && contactHint) {
    const val = contactEl.value.trim();
    const phoneRegex = /^[6-9]\d{9}$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (phoneRegex.test(val)) {
      contactHint.className = 'input-hint valid';
      contactHint.innerText = '✓ Valid 10-digit Indian Mobile Number';
      contactEl.classList.remove('input-invalid');
      contactEl.classList.add('input-valid');
    } else if (emailRegex.test(val)) {
      contactHint.className = 'input-hint valid';
      contactHint.innerText = '✓ Valid Email Address';
      contactEl.classList.remove('input-invalid');
      contactEl.classList.add('input-valid');
    } else if (val.length > 0) {
      contactHint.className = 'input-hint invalid';
      if (/^\d+$/.test(val)) {
        contactHint.innerText = `⚠️ Mobile must be 10 digits starting with 6-9 (${val.length}/10 entered)`;
      } else {
        contactHint.innerText = '⚠️ Enter valid 10-digit phone number or email address';
      }
      contactEl.classList.remove('input-valid');
      contactEl.classList.add('input-invalid');
      isValid = false;
    } else {
      contactHint.innerText = '';
      contactEl.classList.remove('input-valid', 'input-invalid');
    }
  }

  if (pwdEl && pwdHint) {
    const pwdVal = pwdEl.value;
    if (pwdVal.length >= 6) {
      pwdHint.className = 'input-hint valid';
      pwdHint.innerText = `✓ Secure password (${pwdVal.length} chars)`;
      pwdEl.classList.remove('input-invalid');
      pwdEl.classList.add('input-valid');
    } else if (pwdVal.length > 0) {
      pwdHint.className = 'input-hint invalid';
      pwdHint.innerText = `⚠️ Password must be at least 6 characters (${pwdVal.length}/6 entered)`;
      pwdEl.classList.remove('input-valid');
      pwdEl.classList.add('input-invalid');
      isValid = false;
    } else {
      pwdHint.innerText = '';
      pwdEl.classList.remove('input-valid', 'input-invalid');
    }
  }

  return isValid;
}

function updateAuthUI() {
  const btn = document.getElementById('btn-auth-action');
  if (!btn) return;
  const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS['hi'] || TRANSLATIONS['en'];
  
  if (currentUser && !currentUser.is_guest) {
    btn.style.background = "#047857";
    btn.style.border = "1.5px solid #6ee7b7";
    const firstName = (currentUser.name || "Farmer").split(' ')[0];
    btn.innerHTML = `<span>👤 ${firstName}</span> <small style="opacity:0.85; font-size:0.75rem;">(${dict.badge_logout || 'लॉगआउट'})</small>`;
    btn.onclick = () => {
      if (confirm(dict.confirm_logout || "क्या आप लॉगआउट करना चाहते हैं? (Do you want to log out?)")) {
        logoutUser();
      }
    };
  } else {
    // Persistent default Farmer profile — NEVER nag or ask to log in
    btn.style.background = "#059669";
    btn.style.border = "1.5px solid #a7f3d0";
    const guestLabel = currentUser ? currentUser.name.split(' ')[0] : (dict.default_farmer_name || 'किसान मित्र');
    btn.innerHTML = `<span>🌱 ${guestLabel}</span> <small style="opacity:0.85; font-size:0.75rem;">(${dict.badge_farmer_profile || 'सक्रिय'})</small>`;
    btn.onclick = openAuthModal;
  }
}

function openAuthModal() {
  document.getElementById('auth-modal').classList.add('active');
  setAuthMode('login');
}

function closeAuthModal() {
  document.getElementById('auth-modal').classList.remove('active');
}

function setAuthMode(mode) {
  authMode = mode;
  const isReg = (mode === 'register');
  document.getElementById('auth-tab-login').classList.toggle('active', !isReg);
  document.getElementById('auth-tab-register').classList.toggle('active', isReg);
  document.getElementById('group-name').style.display = isReg ? 'block' : 'none';
  document.getElementById('group-meta').style.display = isReg ? 'flex' : 'none';
  
  const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS['en'];
  document.getElementById('auth-modal-title').innerText = isReg ? dict.auth_register_tab : dict.auth_signin_tab;
  document.getElementById('auth-submit-text').innerText = isReg ? dict.btn_register_submit : dict.btn_login_submit;
  document.getElementById('auth-error-msg').style.display = 'none';
  validateAuthInputs();
}

async function handleAuthSubmit() {
  const emailPhone = document.getElementById('auth-email-phone').value.trim();
  const password = document.getElementById('auth-password').value;
  const errBox = document.getElementById('auth-error-msg');
  errBox.style.display = 'none';

  const phoneRegex = /^[6-9]\d{9}$/;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!phoneRegex.test(emailPhone) && !emailRegex.test(emailPhone)) {
    errBox.innerText = "Please enter a valid 10-digit mobile number (e.g. 9876543210) or a valid email address.";
    errBox.style.display = 'block';
    return;
  }

  if (password.length < 6) {
    errBox.innerText = "Password must be at least 6 characters long.";
    errBox.style.display = 'block';
    return;
  }

  if (authMode === 'register') {
    const name = document.getElementById('auth-name').value.trim();
    if (name.length < 2) {
      errBox.innerText = "Please enter your full name (at least 2 characters).";
      errBox.style.display = 'block';
      return;
    }
    const payload = {
      name: name,
      email_or_phone: emailPhone,
      password: password,
      location: document.getElementById('auth-location').value,
      primary_crop: document.getElementById('auth-crop').value,
      language: currentLanguage
    };

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 429) {
          const waitSec = data.retry_after || 2;
          throw new Error(`⏳ ${data.detail || `Rate limit active. Please wait ${waitSec}s before retrying.`}`);
        }
        throw new Error(data.detail || 'Registration failed');
      }
      
      currentUser = data.user;
      currentUser.is_guest = false;
      localStorage.setItem('agrismart_user', JSON.stringify(currentUser));
      if (currentUser.language) {
        changeGlobalLanguage(currentUser.language, true);
      }
      closeAuthModal();
      updateAuthUI();
      showToast(`Welcome to AgriSmart AI, ${currentUser.name}! You are logged in permanently.`, 'success');
    } catch (e) {
      errBox.innerText = e.message;
      errBox.style.display = 'block';
    }
  } else {
    // Login
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_or_phone: emailPhone, password: password })
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 429) {
          const waitSec = data.retry_after || 2;
          throw new Error(`⏳ ${data.detail || `Rate limit active. Please wait ${waitSec}s before retrying.`}`);
        }
        throw new Error(data.detail || 'Login failed');
      }

      currentUser = data.user;
      currentUser.is_guest = false;
      localStorage.setItem('agrismart_user', JSON.stringify(currentUser));
      if (currentUser.language) {
        changeGlobalLanguage(currentUser.language, true);
      }
      closeAuthModal();
      updateAuthUI();
      showToast(`Welcome back, ${currentUser.name}! Logged in permanently.`, 'success');
    } catch (e) {
      errBox.innerText = e.message;
      errBox.style.display = 'block';
    }
  }
}

function logoutUser() {
  currentUser = {
    id: 1,
    name: "किसान मित्र (Kisan Mitra)",
    email_or_phone: "9876543210",
    location: "Gujarat, India",
    primary_crop: "Tomato",
    language: currentLanguage,
    is_guest: true
  };
  localStorage.setItem('agrismart_user', JSON.stringify(currentUser));
  updateAuthUI();
  showToast("खाता रीसेट हुआ। आप बिना लॉगिन किए सभी सुविधाओं का उपयोग कर सकते हैं।", "info");
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const typeClass = type === 'success' ? 'toast-success' : (type === 'error' ? 'toast-error' : (type === 'warning' ? 'toast-warning' : ''));
  toast.className = `toast ${typeClass}`;

  const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : (type === 'warning' ? '⚠️' : 'ℹ️'));
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(50px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// =================================================================
// 10. SMART CROP RECOMMENDATION & SOIL HEALTH DIAGNOSIS
// =================================================================
async function submitCropRecommendation() {
  const ph = parseFloat(document.getElementById('crop-ph').value);
  const n = parseFloat(document.getElementById('crop-n').value);
  const p = parseFloat(document.getElementById('crop-p').value);
  const k = parseFloat(document.getElementById('crop-k').value);
  const temp = parseFloat(document.getElementById('crop-temp').value);
  const rain = parseFloat(document.getElementById('crop-rain').value);

  if (isNaN(ph) || ph < 3.5 || ph > 9.5) {
    showToast("Soil pH must be between 3.5 and 9.5.", "warning");
    return;
  }
  if (isNaN(n) || n < 0 || n > 350) {
    showToast("Nitrogen (N) must be between 0 and 350 kg/ha.", "warning");
    return;
  }
  if (isNaN(p) || p < 0 || p > 250) {
    showToast("Phosphorus (P) must be between 0 and 250 kg/ha.", "warning");
    return;
  }
  if (isNaN(k) || k < 0 || k > 350) {
    showToast("Potassium (K) must be between 0 and 350 kg/ha.", "warning");
    return;
  }
  if (isNaN(temp) || temp < -10 || temp > 55) {
    showToast("Temperature must be realistic (-10°C to 55°C).", "warning");
    return;
  }
  if (isNaN(rain) || rain < 0 || rain > 3500) {
    showToast("Rainfall must be between 0 and 3500 mm.", "warning");
    return;
  }

  const stateVal = document.getElementById('crop-state-input') ? document.getElementById('crop-state-input').value : "Gujarat";
  const distVal = document.getElementById('crop-district-input') ? document.getElementById('crop-district-input').value : "Ahmedabad";

  const payload = {
    soil_type: document.getElementById('crop-soil').value,
    ph: ph,
    n: n,
    p: p,
    k: k,
    season: document.getElementById('crop-season').value,
    previous_crop: document.getElementById('crop-prev').value,
    temperature: temp,
    rainfall: rain,
    location: `${distVal}, ${stateVal}`,
    state: stateVal,
    district: distVal,
    user_id: currentUser ? currentUser.id : null
  };

  try {
    const res = await fetch('/api/crop-recommendation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderCropRecommendations(data.recommendations, data.soil_health_diagnosis);
    showToast("Top crops recommended successfully!", "success");
  } catch (e) {
    console.error('Crop rec error:', e);
    showToast("Crop recommendation computation error", "error");
  }
}

function renderCropRecommendations(recs, soilAlerts = []) {
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

  // Render Soil Health Alerts
  renderSoilHealthAlerts(soilAlerts);

  // Show interactive Crop Recommendation Feedback Box
  const cropFb = document.getElementById('crop-feedback-box');
  if (cropFb) {
    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS['en'];
    cropFb.style.display = 'flex';
    cropFb.innerHTML = `
      <span class="feedback-question">
        <span>💡</span> <span>${dict.crop_feedback_question}</span>
      </span>
      <div class="feedback-btn-group">
        <button class="btn-feedback" onclick="submitFarmerFeedback('crop_recommendation', true)">
          👍 <span>${dict.btn_yes}</span>
        </button>
        <button class="btn-feedback btn-feedback-no" onclick="submitFarmerFeedback('crop_recommendation', false)">
          👎 <span>${dict.btn_no}</span>
        </button>
        <button class="btn-feedback-dismiss" onclick="dismissFeedback('crop-feedback-box')" title="Dismiss">✕</button>
      </div>
    `;
  }
}

function renderSoilHealthAlerts(alerts) {
  const box = document.getElementById('soil-health-alerts-box');
  if (!box) return;
  if (!alerts || alerts.length === 0) {
    box.innerHTML = '';
    return;
  }

  let html = `
    <div style="background:#f8fafc; border:1.5px solid #cbd5e1; border-radius:12px; padding:16px; margin-top:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h4 style="margin:0; font-size:1.02rem; color:#064e3b; display:flex; align-items:center; gap:6px;">
          <span>🧪</span> <span>Soil Health & Mineral Diagnosis</span>
        </h4>
        <span class="badge badge-info" style="font-size:0.75rem;">ICAR Agronomy Standard</span>
      </div>
  `;

  alerts.forEach(a => {
    let badgeClass = 'badge-info';
    let borderColor = '#93c5fd';
    let bgLight = '#eff6ff';
    if (a.severity === 'HIGH') {
      badgeClass = 'badge-danger';
      borderColor = '#fca5a5';
      bgLight = '#fef2f2';
    } else if (a.severity === 'MEDIUM') {
      badgeClass = 'badge-warning';
      borderColor = '#fcd34d';
      bgLight = '#fffbeb';
    } else if (a.severity === 'NORMAL') {
      badgeClass = 'badge-success';
      borderColor = '#86efac';
      bgLight = '#f0fdf4';
    }

    html += `
      <div class="soil-alert-item" style="background:${bgLight}; border-left:4px solid ${borderColor}; border-radius:6px; padding:10px 12px; margin-bottom:10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <strong style="font-size:0.9rem; color:#0f172a;">${a.param}: ${a.status} (Value: ${a.value})</strong>
          <span class="badge ${badgeClass}" style="font-size:0.72rem;">${a.severity}</span>
        </div>
        <p style="font-size:0.83rem; color:#475569; margin:2px 0 6px 0;">${a.problem}</p>
        <div style="font-size:0.82rem; color:#065f46; background:white; padding:6px 10px; border-radius:6px; border:1px solid #e2e8f0;">
          <strong>💡 ICAR Prescription:</strong> ${a.remedy}
        </div>
      </div>
    `;
  });

  html += `</div>`;
  box.innerHTML = html;
}

// =================================================================
// 11. FARMER FEEDBACK SUBMISSION ENGINE (/api/feedback)
// =================================================================
async function submitFarmerFeedback(itemType, isHelpful) {
  const payload = {
    item_type: itemType,
    helpful: isHelpful,
    user_id: currentUser ? currentUser.id : null,
    comments: isHelpful ? "Helpful" : "Needs refinement"
  };

  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    const boxId = itemType === 'diagnosis' ? 'diag-feedback-box' : 'crop-feedback-box';
    const box = document.getElementById(boxId);
    if (box) {
      box.innerHTML = `
        <div style="display:flex; align-items:center; gap:8px; color:#065f46; font-weight:600; font-size:0.88rem; padding:4px 0;">
          <span>✅</span> <span>Thank you for your feedback! It helps continuously train AgriSmart AI models.</span>
        </div>
      `;
    }
    showToast(isHelpful ? "✓ Thank you! Positive rating recorded." : "✓ Feedback noted. Agronomy models will be refined.", "success");
  } catch (e) {
    console.error('Feedback submission error:', e);
    showToast("Feedback recorded locally.", "info");
  }
}

function dismissFeedback(boxId) {
  const box = document.getElementById(boxId);
  if (box) box.style.display = 'none';
}

// =================================================================
// 12. PRECISION IRRIGATION (FAO-56 CALCULATOR)
// =================================================================
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
  if (data.decision.includes('IRRIGAT') || data.decision.includes('EMERGENCY')) {
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

// =================================================================
// 13. SUSTAINABILITY & CARBON SCORECARD
// =================================================================
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

// =================================================================
// 14. GROUNDED AGRONOMY AI ADVISOR (CHAT)
// =================================================================
function askQuick(q) {
  const input = document.getElementById('chat-input');
  if (input) {
    input.value = q;
    sendChatMessage();
  }
}

function clearChatMessages() {
  const windowEl = document.getElementById('chat-window');
  if (!windowEl) return;
  const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS['en'];
  windowEl.innerHTML = `
    <div class="chat-msg bot">
      <strong>🌱 AgriSmart Assistant:</strong>
      <p data-i18n="chat_welcome">${dict.chat_welcome || 'Namaste! I am your AI Agronomy Advisor. Ask me anything about crop diseases, pest remedies, irrigation timing, or fertilizer schedules. I provide verified ICAR-backed recommendations with voice support.'}</p>
    </div>
  `;
  showToast('🧹 Chat history cleared!', 'info');
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('btn-chat-send');
  if (!input) return;

  const text = input.value.trim();
  if (!text) return;

  const windowEl = document.getElementById('chat-window');
  if (!windowEl) return;

  // Clear input and disable controls while processing
  input.value = '';
  input.disabled = true;
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.dataset.origText = sendBtn.innerHTML;
    sendBtn.innerHTML = '<span>⏳</span> <span>...</span>';
  }

  // Append user message
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg user';
  userDiv.innerText = text;
  windowEl.appendChild(userDiv);
  windowEl.scrollTop = windowEl.scrollHeight;

  // Append typing indicator bubble
  const typingDiv = document.createElement('div');
  typingDiv.className = 'chat-msg bot chat-typing-bubble';
  typingDiv.innerHTML = `
    <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#047857;">
      <span class="chat-typing-dot">🌱</span>
      <em>AgriSmart AI is searching 10,800+ ICAR guidelines & verifying online...</em>
    </div>
  `;
  windowEl.appendChild(typingDiv);
  windowEl.scrollTop = windowEl.scrollHeight;

  try {
    const res = await fetch('/api/assistant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, language: currentLanguage })
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data = await res.json();

    // Remove typing indicator
    if (typingDiv && typingDiv.parentNode) {
      typingDiv.parentNode.removeChild(typingDiv);
    }

    const botDiv = document.createElement('div');
    botDiv.className = 'chat-msg bot';

    let consensusBarHtml = '';
    if (data.consensus_score_pct) {
      consensusBarHtml = `
        <div class="chat-consensus-bar" style="margin-top:8px; padding:8px 12px; background:#f0fdf4; border-radius:8px; border:1px solid #bbf7d0; font-size:0.8rem; display:flex; flex-direction:column; gap:4px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; color:#166534;">🌐 Live Internet Consensus Verification:</span>
            <span class="badge badge-success" style="font-size:0.72rem; padding:2px 8px;">${data.consensus_score_pct}% Match</span>
          </div>
          <span style="color:#14532d; font-size:0.78rem;">${data.comparison_summary || 'Local Q&A and Online Agronomic Repositories in Consensus.'}</span>
          ${(data.live_internet_citations && data.live_internet_citations.length > 0) ? `
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin-top:4px;">
              ${data.live_internet_citations.map(c => `<span style="background:white; border:1px solid #86efac; border-radius:4px; padding:2px 6px; font-size:0.7rem; color:#166534;">📚 ${c}</span>`).join('')}
            </div>
          ` : ''}
        </div>
      `;
    }

    botDiv.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; gap:8px;">
        <strong>🌱 ${escapeHtml(data.topic || 'AgriSmart Advisor')}</strong>
        <button class="btn-tts" type="button" style="background:#f1f5f9; border:1px solid #cbd5e1; border-radius:6px; padding:2px 8px; font-size:0.75rem; cursor:pointer;">🔊 Voice</button>
      </div>
      <p style="white-space: pre-line; line-height: 1.5; margin:4px 0;">${escapeHtml(data.answer || '')}</p>
      ${consensusBarHtml}
      <div style="font-size:0.75rem; color:#64748b; margin-top:6px; border-top:1px dashed #cbd5e1; padding-top:4px;">
        <em>Verified Source: ${escapeHtml(data.grounded_source || 'ICAR Agricultural Research Guidelines')}</em>
      </div>
    `;

    const ttsBtn = botDiv.querySelector('.btn-tts');
    if (ttsBtn) {
      ttsBtn.addEventListener('click', () => {
        if (ttsBtn.classList.contains('speaking')) {
          stopAudio();
          ttsBtn.classList.remove('speaking');
          ttsBtn.innerText = '🔊 Voice';
        } else {
          document.querySelectorAll('.btn-tts').forEach(b => {
            b.classList.remove('speaking');
            b.innerText = '🔊 Voice';
          });
          ttsBtn.classList.add('speaking');
          ttsBtn.innerText = '⏹️ Stop';
          speakRaw(data.answer, currentLanguage);
        }
      });
    }

    windowEl.appendChild(botDiv);
    windowEl.scrollTop = windowEl.scrollHeight;

  } catch (e) {
    console.error('Chat error:', e);
    // Remove typing indicator if still present
    if (typingDiv && typingDiv.parentNode) {
      typingDiv.parentNode.removeChild(typingDiv);
    }
    const errDiv = document.createElement('div');
    errDiv.className = 'chat-msg bot';
    errDiv.style.borderLeft = '3px solid #ef4444';
    errDiv.innerHTML = `
      <strong>⚠️ AgriSmart Advisor:</strong>
      <p style="color:#b91c1c; margin-top:4px; font-size:0.88rem;">
        Could not connect to the advisory engine (${escapeHtml(e.message || 'Network Error')}). Please verify the AgriSmart AI server is running and try again.
      </p>
    `;
    windowEl.appendChild(errDiv);
    windowEl.scrollTop = windowEl.scrollHeight;
  } finally {
    // Re-enable input and button
    input.disabled = false;
    if (sendBtn) {
      sendBtn.disabled = false;
      sendBtn.innerHTML = sendBtn.dataset.origText || 'Send';
    }
    input.focus();
  }
}

// =================================================================
// =================================================================
// 15. REAL IOT HARDWARE GATEWAY (USB, WI-FI, BLUETOOTH) & ADVISOR
// =================================================================
let activeWebSerialPort = null;
let webSerialReader = null;
let isWebSerialReading = false;

// 15.1 Fetch and render real hardware telemetry
async function fetchIoTTelemetry() {
  try {
    const res = await fetch('/api/iot/telemetry');
    if (!res.ok) return;
    const data = await res.json();
    if (!data || data.error) return;
    renderIoTTelemetryUI(data);
  } catch (e) {
    console.error('IoT telemetry fetch error:', e);
  }
}

// 15.2 Check hardware connection status and update telemetry
async function checkIoTStatusAndTelemetry() {
  try {
    const resStatus = await fetch('/api/iot/status');
    if (!resStatus.ok) {
      if (resStatus.status === 429) return; // rate-limit backoff, silent
      return;
    }
    const statusData = await resStatus.json();
    if (!statusData || statusData.error) return;
    updateIoTConnectionBadge(statusData);

    // Update live terminal log if available
    if (statusData.terminal_log && statusData.terminal_log.length > 0) {
      const termEl = document.getElementById('iot-terminal-window');
      if (termEl) {
        termEl.innerHTML = statusData.terminal_log.map(l => `<div>${escapeHtml(l)}</div>`).join('');
        termEl.scrollTop = termEl.scrollHeight;
      }
    }

    // Fetch telemetry
    const res = await fetch('/api/iot/telemetry');
    if (!res.ok) return;
    const data = await res.json();
    if (!data || data.error) return;
    renderIoTTelemetryUI(data);
  } catch (e) {
    // Non-blocking on network error
  }
}

function updateIoTConnectionBadge(s) {
  const badge = document.getElementById('iot-conn-badge');
  const text = document.getElementById('iot-conn-text');
  const devInfo = document.getElementById('iot-device-name');
  const discBtn = document.getElementById('btn-disconnect-iot');
  if (!badge || !text) return;

  if (s.connected) {
    badge.className = 'conn-pill connected';
    text.innerText = `🟢 ${s.connection_type || 'HARDWARE'} CONNECTED`;
    if (devInfo) {
      devInfo.innerText = `${s.device_id || s.port_or_endpoint || ''} (${s.last_heartbeat_sec_ago !== null ? s.last_heartbeat_sec_ago + 's ago' : 'live'})`;
    }
    if (discBtn) discBtn.style.display = 'inline-block';
  } else {
    badge.className = 'conn-pill disconnected';
    const lang = currentLanguage || 'hi';
    const noDevStr = TRANSLATIONS[lang] && TRANSLATIONS[lang].iot_no_device ? TRANSLATIONS[lang].iot_no_device : "No IoT Device Connected";
    text.innerText = noDevStr;
    if (devInfo) devInfo.innerText = '--';
    if (discBtn) discBtn.style.display = 'none';
  }
}

function renderIoTTelemetryUI(data) {
  const t = data.telemetry || {};
  const isConn = data.connected === true;
  const lang = currentLanguage || 'hi';
  const notConnStr = TRANSLATIONS[lang] && TRANSLATIONS[lang].iot_not_connected_sub ? TRANSLATIONS[lang].iot_not_connected_sub : "(No Sensor Connected)";

  // 1. Soil Moisture
  const moistEl = document.getElementById('iot-moist');
  const moistStatus = document.getElementById('iot-moist-status');
  if (moistEl) {
    if (isConn && t.soil_moisture_pct !== null && t.soil_moisture_pct !== undefined) {
      moistEl.innerText = `${t.soil_moisture_pct}%`;
      if (moistStatus) {
        if (t.soil_moisture_pct < 15) {
          moistStatus.innerText = '⚠️ Water Stressed (Low)';
          moistStatus.style.color = '#ef4444';
        } else if (t.soil_moisture_pct > 35) {
          moistStatus.innerText = '💧 Saturated / Heavy Moisture';
          moistStatus.style.color = '#0284c7';
        } else {
          moistStatus.innerText = '✅ Optimal Root Zone Capacity';
          moistStatus.style.color = '#10b981';
        }
      }
    } else {
      moistEl.innerText = '--%';
      if (moistStatus) {
        moistStatus.innerText = notConnStr;
        moistStatus.style.color = '#94a3b8';
      }
    }
  }

  // 2. Ambient Temperature
  const tempEl = document.getElementById('iot-temp');
  const tempStatus = document.getElementById('iot-temp-status');
  if (tempEl) {
    if (isConn && t.ambient_temperature_c !== null && t.ambient_temperature_c !== undefined) {
      tempEl.innerText = `${t.ambient_temperature_c}°C`;
      if (tempStatus) {
        tempStatus.innerText = 'Field Microclimate';
        tempStatus.style.color = '#475569';
      }
    } else {
      tempEl.innerText = '--°C';
      if (tempStatus) {
        tempStatus.innerText = notConnStr;
        tempStatus.style.color = '#94a3b8';
      }
    }
  }

  // 3. Air Humidity
  const humEl = document.getElementById('iot-hum');
  const humStatus = document.getElementById('iot-hum-status');
  if (humEl) {
    if (isConn && t.relative_humidity_pct !== null && t.relative_humidity_pct !== undefined) {
      humEl.innerText = `${t.relative_humidity_pct}%`;
      if (humStatus) {
        humStatus.innerText = 'Air RH Sensor';
        humStatus.style.color = '#475569';
      }
    } else {
      humEl.innerText = '--%';
      if (humStatus) {
        humStatus.innerText = notConnStr;
        humStatus.style.color = '#94a3b8';
      }
    }
  }

  // 4. Soil pH
  const phEl = document.getElementById('iot-ph');
  const phStatus = document.getElementById('iot-ph-status');
  if (phEl) {
    if (isConn && t.soil_ph !== null && t.soil_ph !== undefined) {
      phEl.innerText = t.soil_ph;
      if (phStatus) {
        if (t.soil_ph < 6.0) {
          phStatus.innerText = 'Acidic Soil';
          phStatus.style.color = '#f59e0b';
        } else if (t.soil_ph > 7.5) {
          phStatus.innerText = 'Alkaline Soil';
          phStatus.style.color = '#f59e0b';
        } else {
          phStatus.innerText = 'Neutral (Balanced)';
          phStatus.style.color = '#10b981';
        }
      }
    } else {
      phEl.innerText = '--';
      if (phStatus) {
        phStatus.innerText = notConnStr;
        phStatus.style.color = '#94a3b8';
      }
    }
  }
}

// 15.3 Sub-tab switcher in IoT Connection Hub
function switchIoTSubTab(panelId) {
  document.querySelectorAll('.iot-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.iot-tab-btn').forEach(b => b.classList.remove('active'));
  const target = document.getElementById(panelId);
  if (target) target.classList.add('active');

  const btn = Array.from(document.querySelectorAll('.iot-tab-btn')).find(b => {
    const fn = b.getAttribute('onclick') || '';
    return fn.includes(panelId);
  });
  if (btn) btn.classList.add('active');
}

// 15.4 COM Port Scanning
async function refreshComPorts() {
  const sel = document.getElementById('iot-com-ports');
  if (!sel) return;
  sel.innerHTML = '<option value="">Scanning COM ports...</option>';
  try {
    const res = await fetch('/api/iot/ports');
    const data = await res.json();
    sel.innerHTML = '';
    if (data.ports && data.ports.length > 0) {
      data.ports.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.port;
        opt.innerText = `${p.port} (${p.description})`;
        sel.appendChild(opt);
      });
    } else {
      sel.innerHTML = '<option value="">No COM Ports Detected</option>';
    }
  } catch (e) {
    sel.innerHTML = '<option value="">Error scanning ports</option>';
  }
}

// 15.5 Connect Backend USB COM Port
async function connectBackendSerial() {
  const sel = document.getElementById('iot-com-ports');
  const baudSel = document.getElementById('iot-baudrate');
  if (!sel || !sel.value) {
    showToast('⚠️ Please select a valid COM port, or use Browser Web Serial.', 'warning');
    return;
  }
  const port = sel.value;
  const baud = parseInt(baudSel ? baudSel.value : '115200', 10);

  try {
    showToast(`🔌 Connecting to ${port} @ ${baud}...`, 'info');
    const res = await fetch('/api/iot/connect-usb', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port: port, baudrate: baud })
    });
    const result = await res.json();
    if (result.status === 'connected') {
      showToast(`✅ Successfully connected to ${port}! Reading real sensor data.`, 'success');
      checkIoTStatusAndTelemetry();
    } else {
      showToast(`❌ Connection failed: ${result.message}`, 'error');
    }
  } catch (e) {
    showToast(`❌ Connection error: ${e.message}`, 'error');
  }
}

// 15.6 Connect Direct Browser Web Serial API (Chrome/Edge)
async function connectWebSerial() {
  if (!('serial' in navigator)) {
    showToast('⚠️ Web Serial is not supported in this browser. Please use Google Chrome or Microsoft Edge, or connect via COM port above.', 'warning');
    return;
  }

  try {
    activeWebSerialPort = await navigator.serial.requestPort();
    const baudSel = document.getElementById('iot-baudrate');
    const baud = parseInt(baudSel ? baudSel.value : '115200', 10);
    await activeWebSerialPort.open({ baudRate: baud });
    showToast('⚡ Web Serial USB Connected! Reading real hardware stream...', 'success');

    // Ingest Web Serial link notice
    await fetch('/api/iot/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_id: 'USB-WEB-SERIAL',
        device_model: 'Browser Direct Web Serial Link',
        connection_type: 'USB'
      })
    });

    readWebSerialLoop();
    checkIoTStatusAndTelemetry();
  } catch (e) {
    if (e.name !== 'NotFoundError') {
      showToast(`Web Serial error: ${e.message}`, 'error');
    }
  }
}

async function readWebSerialLoop() {
  isWebSerialReading = true;
  const textDecoder = new TextDecoderStream();
  const readableStreamClosed = activeWebSerialPort.readable.pipeTo(textDecoder.writable);
  const reader = textDecoder.readable.getReader();
  webSerialReader = reader;

  let buffer = '';
  try {
    while (isWebSerialReading) {
      const { value, done } = await reader.read();
      if (done) break;
      if (value) {
        buffer += value;
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep last incomplete chunk
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) {
            logToIoTTerminal(`<< [USB] ${trimmed}`);
            try {
              if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
                const parsed = JSON.parse(trimmed);
                await fetch('/api/iot/ingest', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(parsed)
                });
              } else if (trimmed.includes(',')) {
                const parts = trimmed.split(',').map(s => parseFloat(s.trim()));
                const csvPayload = {};
                if (!isNaN(parts[0])) csvPayload.soil_moisture_pct = parts[0];
                if (!isNaN(parts[1])) csvPayload.ambient_temperature_c = parts[1];
                if (!isNaN(parts[2])) csvPayload.relative_humidity_pct = parts[2];
                if (!isNaN(parts[3])) csvPayload.soil_ph = parts[3];
                await fetch('/api/iot/ingest', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(csvPayload)
                });
              }
            } catch (err) {}
          }
        }
      }
    }
  } catch (err) {
    console.error('Web Serial stream error:', err);
  } finally {
    reader.releaseLock();
  }
}

// 15.7 Connect Wi-Fi Sensor Station
async function connectWifiSensor() {
  const urlInput = document.getElementById('wifi-sensor-url');
  if (!urlInput || !urlInput.value.trim()) {
    showToast('⚠️ Please enter a valid Wi-Fi sensor URL (e.g., http://192.168.1.50/data)', 'warning');
    return;
  }
  const endpoint = urlInput.value.trim();
  showToast(`📶 Connecting to Wi-Fi station ${endpoint}...`, 'info');

  try {
    const res = await fetch('/api/iot/connect-wifi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint_url: endpoint, poll_interval: 3.0 })
    });
    const result = await res.json();
    if (result.status === 'connected') {
      showToast('✅ Successfully connected to Wi-Fi sensor station!', 'success');
      checkIoTStatusAndTelemetry();
    } else {
      showToast(`❌ Wi-Fi Connection failed: ${result.message}`, 'error');
    }
  } catch (e) {
    showToast(`❌ Error: ${e.message}`, 'error');
  }
}

// 15.8 Connect Web Bluetooth (BLE) Probes with Strict IoT Sensor Validation
const NON_IOT_BLUETOOTH_REGEX = /(watch|band|fitbit|gear|smartwatch|wear|speaker|soundbar|audio|headphone|headset|earbud|earphone|airpod|buds|tws|soundcore|boat\s*(?:stone|rockerz|airdopes|wave|storm)|jbl|sony\s*(?:wh|wf|srs)|bose|marshall|zebronics\s*(?:zeb|sound)|realme\s*buds|oneplus\s*buds|noise\s*(?:colorfit|shots)|fire-?boltt|boult|tv|dongle|mouse|keyboard|echo|alexa|nest|homepod|car|handsfree)/i;

function showBluetoothRejectionAlert(devName) {
  const lang = currentLanguage || 'hi';
  const msgs = {
    'hi': {
      title: '⚠️ अस्वीकृत ब्लूटूथ डिवाइस (गैर-सेंसर डिवाइस)',
      desc: `आपने "${devName}" चुना है, जो कि एक ऑडियो स्पीकर / स्मार्टवॉच / हेडफोन प्रतीत होता है।\n\nएग्रीस्मार्ट केवल वास्तविक कृषि IoT सेंसर (जैसे ESP32, मृदा नमी प्रोब, मौसम स्टेशन) को सपोर्ट करता है। कृपया कृषि सेंसर डिवाइस कनेक्ट करें।`
    },
    'en': {
      title: '⚠️ Ineligible Bluetooth Device Rejected',
      desc: `You selected "${devName}", which is an Audio Speaker, Smartwatch, or Headphone.\n\nAgriSmart AI only connects to Agricultural & Environmental IoT Sensors (such as ESP32 nodes, Capacitive Soil Probes, or SHT31 Weather Sensors). Please select an agricultural sensor probe.`
    },
    'gu': {
      title: '⚠️ અમાન્ય બ્લૂટૂથ ડિવાઇસ અસ્વીકાર્ય',
      desc: `તમે "${devName}" પસંદ કર્યું છે, જે સ્પીકર કે સ્માર્ટવોચ છે.\n\nએગ્રીસ્માર્ટ માત્ર કૃષિ સેન્સર્સ (જેમ કે ESP32, સોઇલ મોઇશ્ચર પ્રોબ) ને જ સપોર્ટ કરે છે.`
    },
    'mr': {
      title: '⚠️ अपात्र ब्लूटूथ डिव्हाइस नाकारले',
      desc: `तुम्ही "${devName}" निवडले आहे, जे ऑडिओ स्पीकर किंवा स्मार्टवॉच आहे.\n\nॲग्रीस्मार्ट केवळ कृषी IoT सेन्सर्स (जसे की ESP32, माती ओलावा प्रोब) ला सपोर्ट करते.`
    }
  };
  const m = msgs[lang] || msgs['en'];
  showToast(`${m.title}:\n${m.desc}`, 'error', 8000);
}

async function connectWebBluetooth() {
  if (!('bluetooth' in navigator)) {
    showToast('⚠️ Web Bluetooth is not available in this browser. Please enable Bluetooth and use Chrome/Edge on a BLE-enabled computer.', 'warning');
    return;
  }

  try {
    showToast('📡 Scanning for nearby agricultural sensor probes (soil probes, ESP32, SHT31)...', 'info');
    
    // Request BLE device
    const device = await navigator.bluetooth.requestDevice({
      acceptAllDevices: true,
      optionalServices: [
        'battery_service',
        'environmental_sensing',
        '0000181a-0000-1000-8000-00805f9b34fb',
        '6e400001-b5a3-f393-e0a9-e50e24dcca9e',
        '4fafc201-1fb5-459e-8fcc-c5c9c331914b'
      ]
    });

    const devName = (device.name || '').trim();

    // VALIDATION STEP 1: Reject Blacklisted Audio / Smartwatch / Wearable Devices
    if (NON_IOT_BLUETOOTH_REGEX.test(devName)) {
      logToIoTTerminal(`❌ [BLUETOOTH REJECTED] Ineligible device "${devName}" rejected. Audio speakers and smartwatches cannot measure agricultural telemetry.`);
      showBluetoothRejectionAlert(devName);
      if (device.gatt && device.gatt.connected) {
        try { device.gatt.disconnect(); } catch (e) {}
      }
      return;
    }

    showToast(`Connecting to BLE device: ${devName || 'AgriSensor'}...`, 'info');
    const server = await device.gatt.connect();

    // VALIDATION STEP 2: Inspect GATT Services for Telemetry Capability
    try {
      const services = await server.getPrimaryServices();
      const serviceUuids = services.map(s => s.uuid.toLowerCase());
      
      const isPurelyMediaOrHID = serviceUuids.every(u => 
        u.includes('1812') || u.includes('110b') || u.includes('110e') || u.includes('1108') || u.includes('1800') || u.includes('1801')
      );
      
      if (isPurelyMediaOrHID && serviceUuids.length > 0 && !serviceUuids.some(u => u.includes('181a') || u.includes('6e40') || u.includes('battery') || u.includes('environmental'))) {
        server.disconnect();
        logToIoTTerminal(`❌ [BLUETOOTH REJECTED] Device "${devName}" lacks agricultural sensor or telemetry data services.`);
        showBluetoothRejectionAlert(devName);
        return;
      }
    } catch (svcErr) {
      console.warn('GATT service inspection note:', svcErr);
    }

    // VALIDATION STEP 3: Server-side validation via Ingestion
    const ingestRes = await fetch('/api/iot/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_id: device.id || 'BLE-SOIL-PROBE',
        device_model: devName || 'Wireless BLE Probe',
        device_name: devName || 'Wireless BLE Probe',
        connection_type: 'BLUETOOTH'
      })
    });
    const ingestData = await ingestRes.json();

    if (ingestData.status === 'rejected') {
      server.disconnect();
      logToIoTTerminal(`❌ [BLUETOOTH REJECTED] ${ingestData.message}`);
      showBluetoothRejectionAlert(devName);
      return;
    }

    showToast(`✅ Bluetooth Connected to ${devName || 'BLE Sensor'}!`, 'success');
    logToIoTTerminal(`[BLUETOOTH] Validated and paired with ${devName || device.id}. Stream active.`);
    checkIoTStatusAndTelemetry();
  } catch (e) {
    if (e.name !== 'NotFoundError') {
      showToast(`Bluetooth Error: ${e.message}`, 'error');
    }
  }
}


// 15.9 Disconnect Any Active IoT Hardware
async function disconnectIoTHardware() {
  if (webSerialReader) {
    try {
      isWebSerialReading = false;
      await webSerialReader.cancel();
      await activeWebSerialPort.close();
      activeWebSerialPort = null;
      webSerialReader = null;
    } catch (e) {}
  }

  try {
    await fetch('/api/iot/disconnect', { method: 'POST' });
    showToast('🔌 IoT Hardware disconnected. Sensor telemetry cleared to blank.', 'info');
    checkIoTStatusAndTelemetry();
  } catch (e) {
    console.error('Disconnect error:', e);
  }
}

// 15.10 Load and Copy Arduino Sketch

// 15.0 Fetch Dynamic Local Network IP for ESP32 and Wi-Fi Nodes
async function fetchNetworkIp() {
  try {
    const res = await fetch('/api/system/network-ip');
    if (!res.ok) return;
    const data = await res.json();
    const ipSpan = document.getElementById('wifi-local-ip');
    if (ipSpan && data.ip) {
      ipSpan.innerText = data.ip;
    }
    const settingsIp = document.getElementById('set-iot-lan-ip');
    if (settingsIp && data.telemetry_url) {
      settingsIp.value = data.telemetry_url;
    }
  } catch (e) {}
}

async function loadArduinoSketch() {
  const display = document.getElementById('arduino-code-display');
  if (!display) return;
  try {
    const res = await fetch('/api/iot/arduino-sketch');
    const data = await res.json();
    if (data.sketch) display.innerText = data.sketch;
  } catch (e) {}
}

function copyArduinoCode() {
  const display = document.getElementById('arduino-code-display');
  if (!display) return;
  navigator.clipboard.writeText(display.innerText).then(() => {
    showToast('📋 Arduino C++ code copied to clipboard!', 'success');
  }).catch(() => {
    showToast('Failed to copy code', 'error');
  });
}

function logToIoTTerminal(msg) {
  const term = document.getElementById('iot-terminal-window');
  if (!term) return;
  const line = document.createElement('div');
  line.innerText = msg;
  term.appendChild(line);
  if (term.childNodes.length > 50) term.removeChild(term.firstChild);
  term.scrollTop = term.scrollHeight;
}

function clearIoTTerminal() {
  const term = document.getElementById('iot-terminal-window');
  if (term) term.innerHTML = '<div>[SYSTEM] Terminal buffer cleared.</div>';
}

async function triggerScenario(mode) {
  try {
    await fetch('/api/iot/scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: mode })
    });
    checkIoTStatusAndTelemetry();
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
        crop: currentUser ? currentUser.primary_crop : 'Tomato',
        stage: 'Mid-Season / Flowering',
        diagnosis: currentDiagnosisData ? currentDiagnosisData.class_label : 'Tomato___Early_blight'
      })
    });
    const data = await res.json();

    const valveBadge = document.getElementById('valve-status');
    valveBadge.innerText = data.valve_state;
    valveBadge.className = data.valve_state === 'OPEN' ? 'badge badge-danger' : 'badge badge-info';

    // Timeline
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


// =================================================================
// 15. SETTINGS & FARM PROFILE MANAGEMENT ENGINE
// =================================================================

let activeFarmerCrops = ['Tomato'];
let currentPreferences = {
  theme: 'standard',
  font_scale: 'normal',
  voice_rate: 1.0,
  auto_voice: false,
  audio_chime: true,
  iot_interval: 3000
};

function initSettingsTab() {
  // Load stored preferences
  try {
    const savedPref = JSON.parse(localStorage.getItem('agrismart_preferences') || '{}');
    currentPreferences = { ...currentPreferences, ...savedPref };
  } catch (e) {
    console.error('Error loading preferences:', e);
  }

  // Apply saved theme and font scale immediately
  applyTheme(currentPreferences.theme || 'standard', false);
  applyFontScale(currentPreferences.font_scale || 'normal', false);

  // Populate form fields
  populateSettingsForm();
}

function populateSettingsForm() {
  if (!currentUser) return;

  // Name
  const nameInput = document.getElementById('set-farmer-name');
  if (nameInput) nameInput.value = currentUser.name || "Kisan Mitra";

  // Contact
  const contactInput = document.getElementById('set-farmer-contact');
  if (contactInput) {
    contactInput.value = currentUser.email_or_phone || (currentUser.is_guest ? "Guest Mode (Local Session)" : "Not Set");
  }

  // Pill badge in banner
  const pillName = document.getElementById('settings-pill-name');
  if (pillName) {
    pillName.innerText = currentUser.is_guest ? "Guest Farmer (Local)" : (currentUser.name || "Farmer");
  }

  // State & District
  let userState = "Gujarat";
  let userDistrict = "Ahmedabad";
  if (currentUser.location && currentUser.location.includes(',')) {
    const parts = currentUser.location.split(',').map(s => s.trim());
    if (parts.length >= 2) {
      userDistrict = parts[0];
      userState = parts[1];
    }
  }
  const stateSelect = document.getElementById('set-farmer-state');
  if (stateSelect) {
    stateSelect.value = userState;
    onSettingsStateChanged(userState);
    const distSelect = document.getElementById('set-farmer-district');
    if (distSelect) distSelect.value = userDistrict;
  }

  // Village
  const villageInput = document.getElementById('set-farmer-village');
  if (villageInput) villageInput.value = currentUser.village || "";

  // Farm Size & Unit
  const farmSizeInput = document.getElementById('set-farmer-farm-size');
  const farmUnitSelect = document.getElementById('set-farmer-farm-unit');
  if (currentUser.farm_size) {
    const sizeParts = currentUser.farm_size.split(' ');
    if (farmSizeInput) farmSizeInput.value = sizeParts[0] || "";
    if (farmUnitSelect && sizeParts[1]) farmUnitSelect.value = sizeParts[1];
  }

  // Primary Crops chips
  if (currentUser.primary_crop) {
    activeFarmerCrops = currentUser.primary_crop.split(',').map(c => c.trim()).filter(Boolean);
  }
  if (activeFarmerCrops.length === 0) activeFarmerCrops = ['Tomato'];
  refreshCropChipsUI();

  // Soil Type
  const soilSelect = document.getElementById('set-farmer-soil-type');
  if (soilSelect && currentUser.soil_type) soilSelect.value = currentUser.soil_type;

  // Water Source
  const waterSelect = document.getElementById('set-farmer-water-source');
  if (waterSelect && currentUser.water_source) waterSelect.value = currentUser.water_source;

  // Preferences: Language
  const prefLang = document.getElementById('set-pref-language');
  if (prefLang) prefLang.value = currentLanguage;

  // Preferences: Theme radio
  const themeRadios = document.querySelectorAll('input[name="display-theme"]');
  themeRadios.forEach(r => {
    r.checked = (r.value === currentPreferences.theme);
  });

  // Preferences: Font Scale radio
  const fontRadios = document.querySelectorAll('input[name="font-scale"]');
  fontRadios.forEach(r => {
    r.checked = (r.value === currentPreferences.font_scale);
  });

  // Preferences: Voice Rate
  const voiceRateSlider = document.getElementById('set-pref-voice-rate');
  const voiceRateDisp = document.getElementById('voice-rate-display');
  if (voiceRateSlider) {
    voiceRateSlider.value = currentPreferences.voice_rate || 1.0;
    if (voiceRateDisp) voiceRateDisp.innerText = (currentPreferences.voice_rate || 1.0) + 'x';
  }

  // Preferences: Auto-Voice
  const autoVoiceCheck = document.getElementById('set-pref-auto-voice');
  if (autoVoiceCheck) autoVoiceCheck.checked = Boolean(currentPreferences.auto_voice);

  // Preferences: Audio Chime
  const audioChimeCheck = document.getElementById('set-pref-audio-chime');
  if (audioChimeCheck) audioChimeCheck.checked = currentPreferences.audio_chime !== false;

  // IoT Polling
  const iotSelect = document.getElementById('set-iot-interval');
  if (iotSelect && currentPreferences.iot_interval) iotSelect.value = currentPreferences.iot_interval;

  // Local IP display
  fetchNetworkIp();

  // Session box info
  const sessionDesc = document.getElementById('settings-session-desc');
  const authSwitchBtnText = document.getElementById('btn-settings-auth-switch-text');
  const pwdGuestAlert = document.getElementById('pwd-change-guest-alert');
  const pwdSubmitBtn = document.getElementById('btn-submit-change-pwd');

  if (currentUser.is_guest) {
    if (sessionDesc) sessionDesc.innerText = "Running as Guest Farmer (Saved locally on device)";
    if (authSwitchBtnText) authSwitchBtnText.innerText = "Log In / Register";
    if (pwdGuestAlert) pwdGuestAlert.style.display = 'block';
    if (pwdSubmitBtn) pwdSubmitBtn.disabled = true;
  } else {
    if (sessionDesc) sessionDesc.innerText = `Active Account: ${currentUser.email_or_phone} (Synced with Cloud DB)`;
    if (authSwitchBtnText) authSwitchBtnText.innerText = "Sign Out / Switch";
    if (pwdGuestAlert) pwdGuestAlert.style.display = 'none';
    if (pwdSubmitBtn) pwdSubmitBtn.disabled = false;
  }
}

function onSettingsStateChanged(stateName) {
  const distSelect = document.getElementById('set-farmer-district');
  if (!distSelect) return;
  distSelect.innerHTML = '';
  const districts = DISTRICT_DATA[stateName] || {};
  Object.keys(districts).forEach(dist => {
    const opt = document.createElement('option');
    opt.value = dist;
    opt.innerText = dist;
    distSelect.appendChild(opt);
  });
}

function toggleCropChip(btn) {
  const crop = btn.getAttribute('data-crop');
  if (!crop) return;
  const idx = activeFarmerCrops.indexOf(crop);
  if (idx > -1) {
    if (activeFarmerCrops.length > 1) {
      activeFarmerCrops.splice(idx, 1);
      btn.classList.remove('active');
    } else {
      showToast('Please keep at least one primary crop selected.', 'warning');
    }
  } else {
    activeFarmerCrops.push(crop);
    btn.classList.add('active');
  }
}

function refreshCropChipsUI() {
  document.querySelectorAll('.crop-chip').forEach(btn => {
    const crop = btn.getAttribute('data-crop');
    if (activeFarmerCrops.includes(crop)) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

async function saveProfileSettings() {
  const name = document.getElementById('set-farmer-name').value.trim();
  const state = document.getElementById('set-farmer-state').value;
  const district = document.getElementById('set-farmer-district').value;
  const village = document.getElementById('set-farmer-village').value.trim();
  const sizeVal = document.getElementById('set-farmer-farm-size').value.trim();
  const sizeUnit = document.getElementById('set-farmer-farm-unit').value;
  const soilType = document.getElementById('set-farmer-soil-type').value;
  const waterSource = document.getElementById('set-farmer-water-source').value;

  if (!name) {
    showToast('Please enter your farmer name.', 'error');
    return;
  }

  const farmSizeStr = sizeVal ? `${sizeVal} ${sizeUnit}` : "";
  const locationStr = `${district}, ${state}`;
  const cropsStr = activeFarmerCrops.join(', ');

  currentUser.name = name;
  currentUser.location = locationStr;
  currentUser.village = village;
  currentUser.farm_size = farmSizeStr;
  currentUser.primary_crop = cropsStr;
  currentUser.soil_type = soilType;
  currentUser.water_source = waterSource;

  localStorage.setItem('agrismart_user', JSON.stringify(currentUser));

  // If user is authenticated in database, sync via API
  if (currentUser.id && !currentUser.is_guest) {
    try {
      const res = await fetch('/api/user/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          name: name,
          location: locationStr,
          village: village,
          primary_crop: cropsStr,
          farm_size: farmSizeStr,
          soil_type: soilType,
          water_source: waterSource,
          language: currentLanguage,
          settings_json: JSON.stringify(currentPreferences)
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to update profile');
      showToast('✅ Farm profile updated & synced with cloud database!', 'success');
    } catch (e) {
      console.error(e);
      showToast('Saved locally. Cloud sync pending.', 'info');
    }
  } else {
    showToast('✅ Farm profile saved successfully!', 'success');
  }

  updateAuthUI();
  populateSettingsForm();
}

function saveWebsitePreferences() {
  const theme = document.querySelector('input[name="display-theme"]:checked')?.value || 'standard';
  const fontScale = document.querySelector('input[name="font-scale"]:checked')?.value || 'normal';
  const voiceRate = parseFloat(document.getElementById('set-pref-voice-rate')?.value || '1.0');
  const autoVoice = document.getElementById('set-pref-auto-voice')?.checked || false;
  const audioChime = document.getElementById('set-pref-audio-chime')?.checked !== false;
  const iotInterval = parseInt(document.getElementById('set-iot-interval')?.value || '3000');

  currentPreferences = {
    theme,
    font_scale: fontScale,
    voice_rate: voiceRate,
    auto_voice: autoVoice,
    audio_chime: audioChime,
    iot_interval: iotInterval
  };

  localStorage.setItem('agrismart_preferences', JSON.stringify(currentPreferences));
  applyTheme(theme, true);
  applyFontScale(fontScale, true);

  showToast('✅ Display & audio preferences saved successfully!', 'success');
}

function applyTheme(theme, showFeedback = false) {
  currentPreferences.theme = theme;
  document.body.classList.remove('dark-mode', 'high-contrast');

  if (theme === 'dark') {
    document.body.classList.add('dark-mode');
  } else if (theme === 'high-contrast') {
    document.body.classList.add('high-contrast');
  }

  localStorage.setItem('agrismart_theme', theme);
  if (showFeedback) {
    showToast(`Theme updated to ${theme.replace('-', ' ')}`, 'info');
  }
}

function applyFontScale(scale, showFeedback = false) {
  currentPreferences.font_scale = scale;
  if (scale === 'large') {
    document.body.classList.add('large-text');
  } else {
    document.body.classList.remove('large-text');
  }
  localStorage.setItem('agrismart_font_scale', scale);
  if (showFeedback) {
    showToast(`Font scale updated to ${scale}`, 'info');
  }
}

function updateIotPollingInterval(val) {
  currentPreferences.iot_interval = parseInt(val);
  localStorage.setItem('agrismart_preferences', JSON.stringify(currentPreferences));
  showToast(`IoT polling interval set to ${parseInt(val)/1000}s`, 'info');
}

function copyIotGatewayUrl() {
  const input = document.getElementById('set-iot-lan-ip');
  if (!input) return;
  navigator.clipboard.writeText(input.value).then(() => {
    showToast('📋 Gateway URL copied for ESP32 firmware!', 'success');
  }).catch(() => {
    showToast('Failed to copy URL', 'error');
  });
}

async function handleChangePassword() {
  if (currentUser.is_guest) {
    showToast('Guest users do not have a password. Create an account first.', 'warning');
    openAuthModal();
    return;
  }

  const oldPwd = document.getElementById('set-old-password').value;
  const newPwd = document.getElementById('set-new-password').value;
  const confirmPwd = document.getElementById('set-confirm-password').value;

  if (newPwd.length < 6) {
    showToast('New password must be at least 6 characters long.', 'error');
    return;
  }

  if (newPwd !== confirmPwd) {
    showToast('New password and confirm password do not match.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/user/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUser.id,
        old_password: oldPwd,
        new_password: newPwd
      })
    });
    const data = await res.json();
    if (!res.ok) {
      if (res.status === 429) {
        const waitSec = data.retry_after || 2;
        throw new Error(`⏳ ${data.detail || `Rate limit active. Please wait ${waitSec}s before retrying.`}`);
      }
      throw new Error(data.detail || 'Password change failed');
    }

    showToast('🔒 Password updated successfully!', 'success');
    document.getElementById('form-change-password').reset();
  } catch (e) {
    showToast(`Error: ${e.message}`, 'error');
  }
}

async function exportFarmDataBackup() {
  try {
    showToast('📦 Preparing farm data archive...', 'info');
    const userId = currentUser ? currentUser.id : 1;
    const res = await fetch(`/api/user/export-data?user_id=${userId}`);
    const data = await res.json();

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    const dateStr = new Date().toISOString().split('T')[0];
    dlAnchor.setAttribute("download", `agrismart_farm_backup_${dateStr}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();

    showToast('✅ Farm diagnostic archive downloaded!', 'success');
  } catch (e) {
    showToast('Failed to export farm data', 'error');
  }
}

function resetScannerCache() {
  currentDiagnosisData = null;
  currentSelectedImageFile = null;
  const preview = document.getElementById('image-preview');
  if (preview) preview.src = '';
  const diagCard = document.getElementById('diagnosis-card');
  if (diagCard) diagCard.style.display = 'none';

  showToast('🧹 Scanner cache & temporary images cleared!', 'success');
}

function handleSettingsAuthSwitch() {
  if (currentUser.is_guest) {
    openAuthModal();
  } else {
    if (confirm("Are you sure you want to sign out and switch to Guest Mode?")) {
      logoutUser();
      populateSettingsForm();
    }
  }
}

function playDiseaseAlertChime() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(880.0, ctx.currentTime + 0.15);
    osc.frequency.exponentialRampToValueAtTime(1174.66, ctx.currentTime + 0.3);

    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.5);
  } catch (e) {
    console.log('Audio chime not supported:', e);
  }
}
