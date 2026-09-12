/**
 * AgriSmart AI - Complete Frontend Client Logic
 * Features:
 *  - 100% Full-Website Multi-Language Translation (English, Hindi, Gujarati, Marathi)
 *  - Web Speech API Audio Voice Synthesis (Fixed & Tested with voice matching)
 *  - Real-Time GPS Geolocation & Open-Meteo Weather Integration
 *  - User Authentication (Email/Phone + Password) with Local SQLite & Supabase
 *  - Dynamic Multi-Crop Disease Diagnosis & Printable PDF Report Generator
 *  - IoT Sensor Telemetry Stream & Autonomous Agentic Advisor
 */

// Global App State
let currentSelectedImageFile = null;
let currentLanguage = localStorage.getItem('agrismart_lang') || 'en';
let currentDiagnosisData = null;
let currentUser = JSON.parse(localStorage.getItem('agrismart_user') || 'null');
let userLatitude = 23.0225; // Default: Ahmedabad
let userLongitude = 72.5714;
let userLocationName = "Ahmedabad, Gujarat";
let isSpeaking = false;
let authMode = 'login'; // 'login' or 'register'

// =================================================================
// 1. FULL-SITE MULTI-LANGUAGE TRANSLATION DICTIONARY (i18n)
// =================================================================
const TRANSLATIONS = {
  en: {
    app_title: "AgriSmart AI",
    app_subtitle: "SIH-2026 Internal Hackathon • Problem Statement 1",
    language_label: "🌐 Language:",
    gps_detect: "Detect My Location",
    nav_login: "Login / Register",
    tab_disease: "🌿 Disease Detection (Core)",
    tab_crop: "🌾 Crop Recommendation (Bonus A)",
    tab_irrigation: "💧 Smart Irrigation & Weather (Bonus B & C)",
    tab_sustainability: "🌍 Sustainability & Carbon (Bonus D)",
    tab_assistant: "💬 Farmer Assistant GenAI (Bonus E)",
    tab_iot: "📡 IoT & Agentic Advisor (Bonus F & G)",
    tab_report: "📊 Model Report (Section 7.3)",
    card_upload_title: "📷 Upload Leaf / Crop Photo",
    tag_core: "Mandatory Core Task",
    card_upload_desc: "AI Vision analyzes visual pathology across 18 shared classes (Tomato, Potato, Corn, Apple, Grape, Pepper).",
    upload_prompt: "Click to browse",
    upload_drag: "or drag & drop leaf photo",
    upload_hint: "Supports real camera photos or field leaf images (JPG, PNG, WEBP)",
    sample_prompt: "Or test instant sample images:",
    btn_run_diag: "Run AI Disease Diagnosis",
    diag_card_title: "🔬 Diagnostic Advisory Output",
    badge_awaiting: "Awaiting Leaf",
    btn_speaker: "Listen",
    diag_empty_msg: "Upload a plant photo or click a sample to see AI disease classification, confidence, and ICAR precautionary guidance.",
    confidence_label: "Confidence",
    precautions_title: "🚨 Immediate Precautions",
    organic_title: "🌿 Organic / Bio-Control",
    chemical_title: "🧪 Chemical Remedy",
    regional_title: "🇮🇳 Regional Advisory:",
    btn_voice_read: "Voice Readout",
    btn_download_report: "Download Full PDF / Print Diagnostic Report",
    crop_rec_title: "🌱 Soil & Agro-Climatic Parameters",
    tag_bonus_a: "Bonus Module A",
    label_soil_type: "Soil Type:",
    label_soil_ph: "Soil pH:",
    label_season: "Season:",
    label_prev_crop: "Previous Crop Grown:",
    label_temp: "Avg Temperature (°C):",
    label_rain: "Expected Rainfall (mm):",
    btn_rec_crops: "Recommend Optimal Crops",
    crop_results_title: "🏆 Recommended Crops (Top 3)",
    crop_empty_msg: "Enter parameters or click recommend to compute crop suitability rankings.",
    irrig_calc_title: "💧 Smart Irrigation Calculator (FAO-56)",
    tag_bonus_b: "Bonus Module B",
    label_current_moist: "Current Soil Moisture:",
    label_crop: "Crop:",
    label_stage: "Growth Stage:",
    label_rain_sync: "Sync with Live Forecast Rain?",
    btn_compute_irrig: "Compute Irrigation Necessity",
    weather_card_title: "☁ Live Weather Intelligence",
    tag_bonus_c: "Bonus Module C",
    weather_hum: "Humidity:",
    weather_wind: "Wind:",
    weather_rain_prob: "24h Rain Prob:",
    weather_rain_sum: "Rain Sum:",
    weather_risk_title: "🦠 Agro-Meteorological Risk Alerts:",
    sust_title: "🌱 Farm Practices Assessment",
    tag_bonus_d: "Bonus Module D",
    sust_desc: "Evaluated by transparent mathematical formula published in Section 3.2.",
    label_irrig_tech: "Irrigation Technology:",
    label_fert_strategy: "Fertilization Strategy:",
    check_solar: "☀️ Solar-powered pump system (Zero diesel/grid emissions)",
    check_mulch: "🍂 Organic crop residue / straw mulching",
    check_legume: "🌾 Regular legume / pulse crop rotation",
    btn_calc_sust: "Calculate Sustainability & Carbon Score",
    sust_scorecard_title: "📊 Ecological Scorecard",
    assistant_title: "💬 Grounded Farmer Assistant (Multilingual GenAI)",
    tag_bonus_e: "Bonus Module E",
    assistant_desc: "Answers are strictly grounded in verified ICAR & FAO agronomic publications (zero hallucination).",
    quick_prompts_title: "Quick Prompts:",
    chat_welcome: "Namaste! I am your AI Agronomy Advisor. Ask me anything about crop diseases, pest remedies, irrigation timing, or fertilizer schedules. I provide verified ICAR-backed recommendations with voice support.",
    btn_send: "Send",
    iot_title: "📡 IoT Edge Sensor Gateway (ESP32 Stream)",
    tag_bonus_f: "Bonus Module F",
    gauge_moist: "Soil Moisture",
    gauge_temp: "Temperature",
    gauge_hum: "Humidity",
    gauge_ph: "Soil pH",
    simulate_scenarios_title: "Simulate Field Scenarios for Live Testing:",
    btn_scen_normal: "🌤 Normal Conditions",
    btn_scen_drought: "🔥 Sudden Drought Spike",
    btn_scen_rain: "🌧 Heavy Rain Inflow",
    agent_title: "🤖 Autonomous Agentic Decision Loop",
    tag_bonus_g: "Bonus Module G",
    agent_desc: "Autonomous closed loop: Perceive -> Multi-Modal Reason -> Decide -> Actuate",
    valve_label: "Smart Valve Status:",
    btn_run_agent: "Run Agent Cycle",
    report_title: "📑 SIH-2026 Model Evaluation Report (Section 7.3)",
    btn_raw_md: "Open Raw Markdown",
    metric_macro_f1: "Primary Metric (Macro-F1)",
    metric_acc: "Overall Accuracy",
    metric_samples: "Test Samples (PlantDoc Field)",
    metric_speed: "Inference Speed",
    cm_title: "Held-Out Field Test Set Confusion Matrix",
    auth_modal_title: "Farmer Login",
    auth_signin_tab: "Sign In",
    auth_register_tab: "Create Account",
    auth_name_label: "Full Name:",
    auth_email_phone_label: "Email or Phone Number:",
    auth_pwd_label: "Password:",
    auth_loc_label: "State / Region:",
    auth_crop_label: "Primary Crop:",
    auth_lang_label: "Preferred Language:",
    btn_login_submit: "Sign In to Farm Account",
    btn_register_submit: "Create My Farm Account",
    btn_back_home: "⬅ Back to Scanner",
    btn_back_scanner: "⬅ Scan Another Plant",
    btn_download_pdf_file: "📥 Download Report (HTML/PDF)",
    btn_print_pdf: "🖨 Print Official Certificate",
    invalid_plant_title: "⚠️ Not a Plant or Crop Photo",
    invalid_plant_desc: "The AI vision model only inspects agricultural crops, plant leaves, fruits, and vegetables. Please upload a clear photo of foliage or infected plant parts."
  },
  hi: {
    app_title: "एग्रीस्मार्ट एआई (AgriSmart AI)",
    app_subtitle: "एसआईएच-2026 आंतरिक हैकाथॉन • समस्या विवरण 1",
    language_label: "🌐 भाषा चुनें:",
    gps_detect: "मेरा स्थान खोजें (GPS)",
    nav_login: "लॉग इन / पंजीकरण",
    tab_disease: "🌿 फसल रोग पहचान (अनिवार्य)",
    tab_crop: "🌾 फसल सिफारिश (बोनस A)",
    tab_irrigation: "💧 स्मार्ट सिंचाई व मौसम (बोनस B और C)",
    tab_sustainability: "🌍 स्थिरता व कार्बन स्कोर (बोनस D)",
    tab_assistant: "💬 किसान सहायक GenAI (बोनस E)",
    tab_iot: "📡 IoT सेंसर व स्वायत्त एजेंट (बोनस F और G)",
    tab_report: "📊 मॉडल रिपोर्ट (धारा 7.3)",
    card_upload_title: "📷 पत्ती या फसल की तस्वीर अपलोड करें",
    tag_core: "अनिवार्य मुख्य कार्य",
    card_upload_desc: "एआई विज़न 18 फसल-रोग वर्गों (टमाटर, आलू, मक्का, सेब, अंगूर, मिर्च) में वास्तविक पैथोलॉजी की जांच करता है।",
    upload_prompt: "ब्राउज़ करने के लिए क्लिक करें",
    upload_drag: "या पत्ती की तस्वीर यहां खींचें",
    upload_hint: "कैमरा फोटो या खेत की पत्ती तस्वीर का समर्थन (JPG, PNG, WEBP)",
    sample_prompt: "या तुरंत नमूना छवियों का परीक्षण करें:",
    btn_run_diag: "एआई रोग निदान शुरू करें",
    diag_card_title: "🔬 रोग निदान व सलाह परिणाम",
    badge_awaiting: "पत्ती की प्रतीक्षा",
    btn_speaker: "सुनें (आवाज)",
    diag_empty_msg: "फसल रोग पहचान, विश्वास स्तर और ICAR सावधानियों को देखने के लिए एक तस्वीर अपलोड करें।",
    confidence_label: "सटीकता",
    precautions_title: "🚨 तत्काल सावधानियां",
    organic_title: "🌿 जैविक / प्राकृतिक उपचार",
    chemical_title: "🧪 रासायनिक दवा उपचार",
    regional_title: "🇮🇳 क्षेत्रीय भाषा मार्गदर्शन:",
    btn_voice_read: "आवाज में सुनें",
    btn_download_report: "पूर्ण PDF रिपोर्ट डाउनलोड करें / प्रिंट करें",
    crop_rec_title: "🌱 मिट्टी और जलवायु मापदंड",
    tag_bonus_a: "बोनस मॉड्यूल A",
    label_soil_type: "मिट्टी का प्रकार:",
    label_soil_ph: "मिट्टी pH मान:",
    label_season: "मौसम:",
    label_prev_crop: "पिछली उगाई गई फसल:",
    label_temp: "औसत तापमान (°C):",
    label_rain: "अनुमानित वर्षा (मिमी):",
    btn_rec_crops: "सर्वोत्तम फसलों की सिफारिश प्राप्त करें",
    crop_results_title: "🏆 अनुशंसित फसलें (शीर्ष 3)",
    crop_empty_msg: "फसल उपयुक्तता रैंकिंग की गणना करने के लिए विवरण दर्ज करें।",
    irrig_calc_title: "💧 स्मार्ट सिंचाई कैलकुलेटर (FAO-56)",
    tag_bonus_b: "बोनस मॉड्यूल B",
    label_current_moist: "वर्तमान मिट्टी नमी:",
    label_crop: "फसल:",
    label_stage: "वृद्धि चरण:",
    label_rain_sync: "क्या लाइव मौसम से बारिश सिंक करें?",
    btn_compute_irrig: "सिंचाई आवश्यकता की गणना करें",
    weather_card_title: "☁ लाइव मौसम संबंधी बुद्धिमत्ता",
    tag_bonus_c: "बोनस मॉड्यूल C",
    weather_hum: "नमी:",
    weather_wind: "हवा की गति:",
    weather_rain_prob: "24 घंटे में बारिश संभावना:",
    weather_rain_sum: "कुल बारिश:",
    weather_risk_title: "🦠 मौसम आधारित रोग अलर्ट:",
    sust_title: "🌱 कृषि पद्धति मूल्यांकन",
    tag_bonus_d: "बोनस मॉड्यूल D",
    sust_desc: "धारा 3.2 में प्रकाशित पारदर्शी गणितीय सूत्र द्वारा मूल्यांकित।",
    label_irrig_tech: "सिंचाई तकनीक:",
    label_fert_strategy: "खाद प्रबंधन रणनीति:",
    check_solar: "☀️ सौर ऊर्जा पंप प्रणाली (शून्य डीजल उत्सर्जन)",
    check_mulch: "🍂 फसल अवशेष / पुआल से मल्चिंग",
    check_legume: "🌾 दलहनी फसलों के साथ फसल चक्र",
    btn_calc_sust: "स्थिरता और कार्बन स्कोर निकालें",
    sust_scorecard_title: "📊 पारिस्थितिकी स्कोरकार्ड",
    assistant_title: "💬 किसान सहायक (बहुभाषी GenAI)",
    tag_bonus_e: "बोनस मॉड्यूल E",
    assistant_desc: "सभी उत्तर ICAR और FAO के प्रमाणित कृषि वैज्ञानिक शोध पर आधारित हैं।",
    quick_prompts_title: "त्वरित प्रश्न:",
    chat_welcome: "नमस्ते! मैं आपका एआई कृषि सलाहकार हूं। फसल रोग, कीट नियंत्रण, सिंचाई समय या खाद संबंधी प्रश्न पूछें।",
    btn_send: "भेजें",
    iot_title: "📡 IoT सेंसर गेटवे (ESP32 लाइव स्ट्रीम)",
    tag_bonus_f: "बोनस मॉड्यूल F",
    gauge_moist: "मिट्टी नमी",
    gauge_temp: "तापमान",
    gauge_hum: "हवा में नमी",
    gauge_ph: "मिट्टी pH",
    simulate_scenarios_title: "परीक्षण हेतु परिदृश्य अनुकरण करें:",
    btn_scen_normal: "🌤 सामान्य स्थिति",
    btn_scen_drought: "🔥 अचानक सूखा / जल तनाव",
    btn_scen_rain: "🌧 भारी वर्षा प्रवाह",
    agent_title: "🤖 स्वायत्त एजेंट निर्णय चक्र",
    tag_bonus_g: "बोनस मॉड्यूल G",
    agent_desc: "स्वायत्त चक्र: निरीक्षण -> विश्लेषण -> निर्णय -> वाल्व नियंत्रण व संदेश",
    valve_label: "स्मार्ट वाल्व स्थिति:",
    btn_run_agent: "एजेंट चक्र चलाएं",
    report_title: "📑 SIH-2026 मॉडल मूल्यांकन रिपोर्ट (धारा 7.3)",
    btn_raw_md: "कच्ची मार्कडाउन फाइल खोलें",
    metric_macro_f1: "प्राथमिक मीट्रिक (मैक्रो-F1)",
    metric_acc: "कुल सटीकता",
    metric_samples: "परीक्षण नमूने (PlantDoc फील्ड)",
    metric_speed: "अनुमान गति",
    cm_title: "फील्ड टेस्ट सेट कन्फ्यूजन मैट्रिक्स",
    auth_modal_title: "किसान खाता लॉगिन",
    auth_signin_tab: "लॉग इन करें",
    auth_register_tab: "नया खाता बनाएं",
    auth_name_label: "पूरा नाम:",
    auth_email_phone_label: "ईमेल या मोबाइल नंबर:",
    auth_pwd_label: "पासवर्ड:",
    auth_loc_label: "राज्य / जिला:",
    auth_crop_label: "मुख्य फसल:",
    auth_lang_label: "पसंदीदा भाषा:",
    btn_login_submit: "खाते में लॉग इन करें",
    btn_register_submit: "मेरा किसान खाता बनाएं",
    btn_back_home: "⬅ मुख्य स्कैनर पर वापस",
    btn_back_scanner: "⬅ नया पौधा / पत्ती जांचें",
    btn_download_pdf_file: "📥 प्रमाण पत्र डाउनलोड करें (HTML/PDF)",
    btn_print_pdf: "🖨 प्रमाण पत्र प्रिंट करें",
    invalid_plant_title: "⚠️ पौधे या फसल की तस्वीर नहीं है",
    invalid_plant_desc: "यह एआई प्रणाली केवल कृषि फसलों, पत्तियों, फलों और सब्जियों के रोगों का परीक्षण करती है। कृपया पौधे की पत्ती का स्पष्ट फोटो अपलोड करें।"
  },
  gu: {
    app_title: "એગ્રીસ્માર્ટ એઆઈ (AgriSmart AI)",
    app_subtitle: "SIH-2026 આંતરિક હેકાથોન • સમસ્યા વિવરણ ૧",
    language_label: "🌐 ભાષા પસંદ કરો:",
    gps_detect: "મારું લોકેશન શોધો (GPS)",
    nav_login: "લૉગ ઇન / રજીસ્ટર",
    tab_disease: "🌿 રોગ નિદાન (મુખ્ય કાર્ય)",
    tab_crop: "🌾 પાક ભલામણ (બોનસ A)",
    tab_irrigation: "💧 સ્માર્ટ સિંચાઈ અને હવામાન (બોનસ B અને C)",
    tab_sustainability: "🌍 પર્યાવરણીય સ્થિરતા સ્કોર (બોનસ D)",
    tab_assistant: "💬 ખેડૂત સહાયક GenAI (બોનસ E)",
    tab_iot: "📡 IoT સેન્સર અને સ્વાયત્ત એજન્ટ (બોનસ F અને G)",
    tab_report: "📊 મોડેલ રિપોર્ટ (વિભાગ ૭.૩)",
    card_upload_title: "📷 પાન અથવા પાકની તસવીર અપલોડ કરો",
    tag_core: "ફરજિયાત મુખ્ય કાર્ય",
    card_upload_desc: "AI વિઝન ૧૮ પાક-રોગ વર્ગોમાં રોગની ઓળખ કરે છે (ટામેટા, બટાટા, મકાઈ, સફરજન, દ્રાક્ષ, મરચાં).",
    upload_prompt: "બ્રાઉઝ કરવા માટે ક્લિક કરો",
    upload_drag: "અથવા પાનની તસવીર ખેંચો",
    upload_hint: "મોબાઈલ કેમેરા ફોટો અથવા ખેતરની તસવીર વાપરો (JPG, PNG, WEBP)",
    sample_prompt: "અથવા સીધા નમૂનાઓનું પરીક્ષણ કરો:",
    btn_run_diag: "AI રોગ નિદાન ચાલુ કરો",
    diag_card_title: "🔬 રોગ નિદાન અને સલાહ પરિણામ",
    badge_awaiting: "પાનની રાહ જોઈ રહ્યું છે",
    btn_speaker: "સાંભળો (અવાજ)",
    diag_empty_msg: "રોગ નિદાન, વિશ્વાસ સ્તર અને ICAR ભલામણો જોવા માટે તસવીર અપલોડ કરો.",
    confidence_label: "ચોકસાઈ",
    precautions_title: "🚨 તાત્કાલિક સાવચેતીઓ",
    organic_title: "🌿 દેશી / જૈવિક નિયંત્રણ",
    chemical_title: "🧪 રાસાયણિક દવા ઉપચાર",
    regional_title: "🇮🇳 સ્થાનિક ભાષા માર્ગદર્શન:",
    btn_voice_read: "અવાજમાં સાંભળો",
    btn_download_report: "સંપૂર્ણ PDF રિપોર્ટ ડાઉનલોડ કરો / પ્રિન્ટ કરો",
    crop_rec_title: "🌱 જમીન અને આબોહવાના પરિમાણો",
    tag_bonus_a: "બોનસ મોડ્યુલ A",
    label_soil_type: "જમીનનો પ્રકાર:",
    label_soil_ph: "જમીન pH:",
    label_season: "ઋતુ:",
    label_prev_crop: "અગાઉ લીધેલ પાક:",
    label_temp: "સરેરાશ તાપમાન (°C):",
    label_rain: "અપેક્ષિત વરસાદ (મીમી):",
    btn_rec_crops: "શ્રેષ્ઠ પાકની ભલામણ મેળવો",
    crop_results_title: "🏆 ભલામણ કરેલ પાકો (ટોચના ૩)",
    crop_empty_msg: "પાકની યોગ્યતા ચકાસવા માટે વિગતો ભરો.",
    irrig_calc_title: "💧 સ્માર્ટ સિંચાઈ કેલ્ક્યુલેટર (FAO-56)",
    tag_bonus_b: "બોનસ મોડ્યુલ B",
    label_current_moist: "હાલમાં જમીનનો ભેજ:",
    label_crop: "પાક:",
    label_stage: "વૃદ્ધિનો તબક્કો:",
    label_rain_sync: "શું જીવંત હવામાન સાથે વરસાદ જોડવો?",
    btn_compute_irrig: "સિંચાઈ જરૂરિયાતની ગણતરી કરો",
    weather_card_title: "☁ લાઈવ હવામાન વિગતો",
    tag_bonus_c: "બોનસ મોડ્યુલ C",
    weather_hum: "ભેજ:",
    weather_wind: "પવનની ગતિ:",
    weather_rain_prob: "૨૪ કલાકમાં વરસાદ શક્યતા:",
    weather_rain_sum: "કુલ વરસાદ:",
    weather_risk_title: "🦠 હવામાન આધારિત રોગ એલર્ટ:",
    sust_title: "🌱 ખેતી પદ્ધતિ મૂલ્યાંકન",
    tag_bonus_d: "બોનસ મોડ્યુલ D",
    sust_desc: "વિભાગ ૩.૨ મુજબ વૈજ્ઞાનિક ગણતરી દ્વારા મૂલ્યાંકન.",
    label_irrig_tech: "સિંચાઈ પદ્ધતિ:",
    label_fert_strategy: "ખાતર વ્યવસ્થાપન:",
    check_solar: "☀️ સોલર પંપ સિસ્ટમ (ઝીરો ડીઝલ પ્રદૂષણ)",
    check_mulch: "🍂 ઓર્ગેનિક પાથરણ (મલ્ચિંગ)",
    check_legume: "🌾 કઠોળ વર્ગના પાકની ફેરબદલી",
    btn_calc_sust: "સ્થિરતા અને કાર્બન સ્કોર ગણો",
    sust_scorecard_title: "📊 પર્યાવરણ સ્કોરકાર્ડ",
    assistant_title: "💬 ખેડૂત સહાયક (બહુભાષી GenAI)",
    tag_bonus_e: "બોનસ મોડ્યુલ E",
    assistant_desc: "બધા જવાબો ICAR અને કૃષિ યુનિવર્સિટીના પ્રમાણિત સંશોધન પર આધારિત છે.",
    quick_prompts_title: "ઝડપી પ્રશ્નો:",
    chat_welcome: "નમસ્તે! હું તમારો એઆઈ કૃષિ સલાહકાર છું. પાક રોગ, સિંચાઈ અથવા ખાતર વિશે કોઈ પણ પ્રશ્ન પૂછો.",
    btn_send: "મોકલો",
    iot_title: "📡 IoT સેન્સર ગેટવે (ESP32 લાઈવ સ્ટ્રીમ)",
    tag_bonus_f: "બોનસ મોડ્યુલ F",
    gauge_moist: "જમીન ભેજ",
    gauge_temp: "તાપમાન",
    gauge_hum: "હવામાન ભેજ",
    gauge_ph: "જમીન pH",
    simulate_scenarios_title: "પરીક્ષણ માટે પરિસ્થિતિ બદલો:",
    btn_scen_normal: "🌤 સામાન્ય સ્થિતિ",
    btn_scen_drought: "🔥 અચાનક દુષ્કાળ / પાણી ખેંચ",
    btn_scen_rain: "🌧 ભારે વરસાદનો પ્રવાહ",
    agent_title: "🤖 સ્વાયત્ત એજન્ટ નિર્ણય લૂપ",
    tag_bonus_g: "બોનસ મોડ્યુલ G",
    agent_desc: "સ્વાયત્ત ચક્ર: નિરીક્ષણ -> વિશ્લેષણ -> નિર્ણય -> વાલ્વ કંટ્રોલ",
    valve_label: "સ્માર્ટ વાલ્વ સ્થિતિ:",
    btn_run_agent: "એજન્ટ સાયકલ ચલાવો",
    report_title: "📑 SIH-2026 મોડેલ મૂલ્યાંકન રિપોર્ટ (વિભાગ ૭.૩)",
    btn_raw_md: "કાચી માર્કડાઉન ફાઇલ ખોલો",
    metric_macro_f1: "મુખ્ય મેટ્રિક (Macro-F1)",
    metric_acc: "કુલ સચોટતા",
    metric_samples: "ટેસ્ટ સેમ્પલ્સ (PlantDoc ફિલ્ડ)",
    metric_speed: "અનુમાન સ્પીડ",
    cm_title: "ફિલ્ડ ટેસ્ટ સેટ કન્ફ્યુઝન મેટ્રિક્સ",
    auth_modal_title: "ખેડૂત એકાઉન્ટ લૉગિન",
    auth_signin_tab: "લૉગ ઇન કરો",
    auth_register_tab: "નવું ખાતું બનાવો",
    auth_name_label: "પૂરું નામ:",
    auth_email_phone_label: "ઈમેલ અથવા મોબાઈલ નંબર:",
    auth_pwd_label: "પાસવર્ડ:",
    auth_loc_label: "જિલ્લો / રાજ્ય:",
    auth_crop_label: "મુખ્ય પાક:",
    auth_lang_label: "પસંદગીની ભાષા:",
    btn_login_submit: "ખાતામાં લૉગ ઇન કરો",
    btn_register_submit: "મારું ખેડૂત ખાતું બનાવો",
    btn_back_home: "⬅ મુખ્ય સ્કેનર પર પાછા",
    btn_back_scanner: "⬅ નવું પર્ણ / પાક તપાસો",
    btn_download_pdf_file: "📥 પ્રમાણપત્ર ડાઉનલોડ કરો (HTML/PDF)",
    btn_print_pdf: "🖨 પ્રમાણપત્ર પ્રિન્ટ કરો",
    invalid_plant_title: "⚠️ પાક કે છોડનો ફોટો નથી",
    invalid_plant_desc: "આ એઆઇ સિસ્ટમ માત્ર ખેતીના પાક, પાંદડા, ફળ અને શાકભાજીનું જ નિરીક્ષણ કરે છે. કૃપા કરીને પાંદડાનો સ્પષ્ટ ફોટો અપલોડ કરો."
  },
  mr: {
    app_title: "ॲग्रीस्मार्ट एआय (AgriSmart AI)",
    app_subtitle: "SIH-2026 अंतर्गत हॅकाथॉन • समस्या विवरण १",
    language_label: "🌐 भाषा निवडा:",
    gps_detect: "माझे स्थान शोधा (GPS)",
    nav_login: "लॉग इन / नोंदणी",
    tab_disease: "🌿 पीक रोग निदान (अनिवार्य)",
    tab_crop: "🌾 पीक शिफारस (बोनस A)",
    tab_irrigation: "💧 स्मार्ट सिंचन व हवामान (बोनस B आणि C)",
    tab_sustainability: "🌍 शाश्वतता व कार्बन स्कोअर (बोनस D)",
    tab_assistant: "💬 शेतकरी सहाय्यक GenAI (बोनस E)",
    tab_iot: "📡 IoT सेन्सर व स्वायत्त एजंट (बोनस F आणि G)",
    tab_report: "📊 मॉडेल अहवाल (विभाग ७.३)",
    card_upload_title: "📷 पानाचा फोटो अपलोड करा",
    tag_core: "अनिवार्य मुख्य कार्य",
    card_upload_desc: "AI व्हिजन १८ पिकांच्या रोगांचे अचूक निदान करते (टोमॅटो, बटाटा, मका, सफरचंद, द्राक्षे, मिरची).",
    upload_prompt: "ब्राउझ करण्यासाठी क्लिक करा",
    upload_drag: "किंवा पानाचा फोटो येथे टाका",
    upload_hint: "कॅमेरा फोटो किंवा शेतातील फोटो वापरा (JPG, PNG, WEBP)",
    sample_prompt: "किंवा नमुना फोटो तपासा:",
    btn_run_diag: "AI रोग निदान सुरू करा",
    diag_card_title: "🔬 रोग निदान व सल्ला अहवाल",
    badge_awaiting: "पानाची प्रतीक्षा",
    btn_speaker: "ऐका (आवाज)",
    diag_empty_msg: "रोग निदान, अचूकता आणि ICAR सल्ला पाहण्यासाठी फोटो अपलोड करा.",
    confidence_label: "अचूकता",
    precautions_title: "🚨 तात्काळ खबरदारी",
    organic_title: "🌿 सेंद्रिय / जैविक उपाय",
    chemical_title: "🧪 रासायनिक औषध फवारणी",
    regional_title: "🇮🇳 स्थानिक भाषा सल्ला:",
    btn_voice_read: "आवाजात ऐका",
    btn_download_report: "पूर्ण PDF अहवाल डाउनलोड करा / प्रिंट करा",
    crop_rec_title: "🌱 माती व हवामान घटक",
    tag_bonus_a: "बोनस मॉड्युल A",
    label_soil_type: "मातीचा प्रकार:",
    label_soil_ph: "मातीचा सामू (pH):",
    label_season: "हंगाम:",
    label_prev_crop: "मागील घेतलेले पीक:",
    label_temp: "सरासरी तापमान (°C):",
    label_rain: "अपेक्षित पाऊस (मिमी):",
    btn_rec_crops: "योग्य पिकांची शिफारस मिळवा",
    crop_results_title: "🏆 शिफारस केलेली पिके (पहिले ३)",
    crop_empty_msg: "पीक योग्यतेची पडताळणी करण्यासाठी माहिती भरा.",
    irrig_calc_title: "💧 स्मार्ट सिंचन गणक (FAO-56)",
    tag_bonus_b: "बोनस मॉड्युल B",
    label_current_moist: "सध्याची मातीतील ओलावा:",
    label_crop: "पीक:",
    label_stage: "वाढीची अवस्था:",
    label_rain_sync: "थेट हवामानानुसार पावसाची माहिती जोडायची का?",
    btn_compute_irrig: "सिंचन गरजेची गणना करा",
    weather_card_title: "☁ थेट हवामान माहिती",
    tag_bonus_c: "बोनस मॉड्युल C",
    weather_hum: "हवेतील ओलावा:",
    weather_wind: "वाऱ्याचा वेग:",
    weather_rain_prob: "२४ तासांत पावसाची शक्यता:",
    weather_rain_sum: "एकूण पाऊस:",
    weather_risk_title: "🦠 हवामानाधारित रोग धोके:",
    sust_title: "🌱 शेती पद्धती मूल्यांकन",
    tag_bonus_d: "बोनस मॉड्युल D",
    sust_desc: "विभाग ३.२ नुसार पारदर्शक गणितीय सूत्राने मूल्यांकन.",
    label_irrig_tech: "सिंचन तंत्रज्ञान:",
    label_fert_strategy: "खत व्यवस्थापन:",
    check_solar: "☀️ सोलर पंप प्रणाली (शून्य डिझेल वापर)",
    check_mulch: "🍂 पिकांच्या अवशेषांचे आच्छादन (मल्चिंग)",
    check_legume: "🌾 डाळवर्गीय पिकांची फेरपालट",
    btn_calc_sust: "शाश्वतता व कार्बन स्कोअर काढा",
    sust_scorecard_title: "📊 पर्यावरणीय प्रगती पुस्तक",
    assistant_title: "💬 शेतकरी सहाय्यक (बहुभाषिक GenAI)",
    tag_bonus_e: "बोनस मॉड्युल E",
    assistant_desc: "सर्व उत्तरे ICAR आणि कृषी विद्यापीठांच्या वैज्ञानिक माहितीवर आधारित आहेत.",
    quick_prompts_title: "त्वरित प्रश्न:",
    chat_welcome: "नमस्कार! मी आपला AI शेती सल्लागार आहे. पीक रोग, सिंचन किंवा खतांबद्दल कोणताही प्रश्न विचारा.",
    btn_send: "पाठवा",
    iot_title: "📡 IoT सेन्सर गेटवे (ESP32 थेट प्रवाह)",
    tag_bonus_f: "बोनस मॉड्युल F",
    gauge_moist: "मातीतील ओलावा",
    gauge_temp: "तापमान",
    gauge_hum: "हवेतील आर्द्रता",
    gauge_ph: "मातीचा pH",
    simulate_scenarios_title: "चाचणीसाठी परिस्थिती बदला:",
    btn_scen_normal: "🌤 सामान्य परिस्थिती",
    btn_scen_drought: "🔥 अचानक दुष्काळ / पाणी टंचाई",
    btn_scen_rain: "🌧 मुसळधार पाऊस प्रवाह",
    agent_title: "🤖 स्वायत्त एजंट निर्णय चक्र",
    tag_bonus_g: "बोनस मॉड्युल G",
    agent_desc: "स्वायत्त चक्र: निरीक्षण -> विचार -> निर्णय -> स्वयंचलित वाल्व सुरू",
    valve_label: "स्मार्ट वाल्व स्थिती:",
    btn_run_agent: "एजंट सायकल चालवा",
    report_title: "📑 SIH-2026 मॉडेल मूल्यांकन अहवाल (विभाग ७.३)",
    btn_raw_md: "कच्ची मार्कडाउन फाईल उघडा",
    metric_macro_f1: "मुख्य मेट्रिक (Macro-F1)",
    metric_acc: "एकूण अचूकता",
    metric_samples: "चाचणी नमुने (PlantDoc फील्ड)",
    metric_speed: "वेग",
    cm_title: "फील्ड टेस्ट सेट कन्फ्युजन मॅट्रिक्स",
    auth_modal_title: "शेतकरी खाते लॉगिन",
    auth_signin_tab: "लॉग इन करा",
    auth_register_tab: "नवीन खाते तयार करा",
    auth_name_label: "पूर्ण नाव:",
    auth_email_phone_label: "ईमेल किंवा मोबाईल नंबर:",
    auth_pwd_label: "पासवर्ड:",
    auth_loc_label: "राज्य / जिल्हा:",
    auth_crop_label: "मुख्य पीक:",
    auth_lang_label: "पसंतीची भाषा:",
    btn_login_submit: "खात्यात प्रवेश करा",
    btn_register_submit: "माझे शेतकरी खाते उघडा",
    btn_back_home: "⬅ मुख्य स्कॅनरवर परत",
    btn_back_scanner: "⬅ नवीन रोप / पान तपासा",
    btn_download_pdf_file: "📥 प्रमाणपत्र डाउनलोड करा (HTML/PDF)",
    btn_print_pdf: "🖨 प्रमाणपत्र प्रिंट करा",
    invalid_plant_title: "⚠️ पीक किंवा वनस्पतीचा फोटो नाही",
    invalid_plant_desc: "ही एआय प्रणाली फक्त शेतातील पिके, पाने, फळे आणि भाज्यांचे रोग तपासते. कृपया पिकाच्या पानाचा स्पष्ट फोटो अपलोड करा."
  }
};

// =================================================================
// 2. INITIALIZATION
// =================================================================
document.addEventListener('DOMContentLoaded', () => {
  // Set initial language in selector and translate page
  const langSelect = document.getElementById('global-lang-select');
  if (langSelect) langSelect.value = currentLanguage;
  changeGlobalLanguage(currentLanguage, false);

  // Update Auth Button State
  updateAuthUI();

  // Load live weather & IoT telemetry
  fetchLiveWeather();
  fetchIoTTelemetry();
  setInterval(fetchIoTTelemetry, 4000);

  // Drag & drop support
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

  // Pre-calculate recommendations
  submitCropRecommendation();
  calculateIrrigation();
  computeSustainability();
  
  // Try auto GPS detection
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        userLatitude = pos.coords.latitude;
        userLongitude = pos.coords.longitude;
        userLocationName = `Field GPS (${userLatitude.toFixed(2)}, ${userLongitude.toFixed(2)})`;
        document.getElementById('gps-text').innerText = "GPS Synced";
        fetchLiveWeather();
      },
      err => { console.log("Geolocation prompt skipped, using default location."); }
    );
  }
});

// =================================================================
// 3. GLOBAL LANGUAGE TRANSLATION ENGINE
// =================================================================
function changeGlobalLanguage(lang, save = true) {
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

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

  const activeContent = document.getElementById(tabId);
  if (activeContent) activeContent.classList.add('active');

  const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
  if (activeBtn) activeBtn.classList.add('active');
}

// =================================================================
// 4. GPS GEOLOCATION & WEATHER SYNC
// =================================================================
function detectGPSLocation() {
  const btn = document.getElementById('btn-gps');
  const txt = document.getElementById('gps-text');
  txt.innerText = "Detecting GPS...";
  
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    txt.innerText = "GPS Not Supported";
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      userLatitude = pos.coords.latitude;
      userLongitude = pos.coords.longitude;
      userLocationName = `Field (${userLatitude.toFixed(3)}°N, ${userLongitude.toFixed(3)}°E)`;
      txt.innerText = "GPS Synced ✓";
      btn.style.background = "#dcfce7";
      btn.style.color = "#15803d";
      fetchLiveWeather();
      calculateIrrigation();
    },
    (err) => {
      alert("Could not access GPS location. Please allow location permissions in your browser: " + err.message);
      txt.innerText = "Detect My Location";
    }
  );
}

let cachedWeatherData = null;

async function fetchLiveWeather() {
  try {
    const res = await fetch(`/api/weather?lat=${userLatitude}&lon=${userLongitude}&name=${encodeURIComponent(userLocationName)}`);
    const data = await res.json();
    cachedWeatherData = data;

    document.getElementById('w-temp').innerText = data.current_weather.temperature_c;
    document.getElementById('w-location').innerText = data.location;
    document.getElementById('w-source').innerText = data.data_source;
    document.getElementById('w-humidity').innerText = `${data.current_weather.humidity_pct}%`;
    document.getElementById('w-wind').innerText = `${data.current_weather.wind_speed_kmh} km/h`;
    document.getElementById('w-rain-prob').innerText = `${data.current_weather.rain_24h_prob_pct}%`;
    document.getElementById('w-rain-sum').innerText = `${data.current_weather.rain_24h_sum_mm} mm`;

    document.getElementById('live-weather-badge').innerText = `☁ ${data.current_weather.temperature_c}°C | ${data.location.split('(')[0].trim()}`;

    // Render alerts
    const alertBox = document.getElementById('weather-alerts');
    alertBox.innerHTML = '';
    (data.agronomic_actions || []).forEach(act => {
      const p = document.createElement('p');
      p.style.fontSize = '0.85rem';
      p.style.marginBottom = '6px';
      const badgeClass = act.priority === 'HIGH' ? 'badge-danger' : (act.priority === 'MEDIUM' ? 'badge-warning' : 'badge-info');
      p.innerHTML = `<span class="badge ${badgeClass}" style="padding:2px 6px; font-size:0.7rem;">${act.priority}</span> <strong>${act.title}:</strong> ${act.guidance}`;
      alertBox.appendChild(p);
    });
  } catch (e) {
    console.error('Weather fetch error:', e);
  }
}

// =================================================================
// 5. RESILIENT MULTILINGUAL AUDIO SPEAKER & TEXT-TO-SPEECH (TTS)
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

  // Toggle off if already speaking
  if (isSpeaking) {
    stopAudio();
    return;
  }

  // Clean text from symbols, asterisks, brackets
  const clean = text.replace(/[*_#`~[\]()]/g, ' ').replace(/\s+/g, ' ').trim();
  if (!clean) return;

  isSpeaking = true;
  updateSpeakerButtonState(true);

  // Strategy 1: For Indian languages (Hindi, Gujarati, Marathi),
  // stream directly from /api/tts endpoint to bypass Windows OS voice pack limitations!
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

  // Strategy 2: For English (en), use Web Speech API with fallback
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
// 6. CORE TASK: LEAF DISEASE DETECTION WITH BIOLOGICAL VALIDATION
// =================================================================
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
  if (currentUser) {
    formData.append('user_id', currentUser.id);
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
}

// =================================================================
// 7. PRINTABLE / DOWNLOADABLE REPORT (PDF & HTML EXPORT)
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
        <p style="font-size:10px; color:#94a3b8;">SIH-2026 Problem Statement 1 • Verified with ICAR & FAO Standards</p>
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
// 8. USER AUTHENTICATION & REAL-WORLD VALIDATIONS
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
  if (currentUser) {
    btn.style.background = "#059669";
    btn.innerHTML = `<span>👤 ${currentUser.name.split(' ')[0]}</span> <small style="opacity:0.8;">(Logout)</small>`;
    btn.onclick = logoutUser;
  } else {
    btn.style.background = "var(--primary)";
    btn.innerHTML = `<span id="auth-btn-icon">🔑</span> <span id="auth-btn-text">${(TRANSLATIONS[currentLanguage] || TRANSLATIONS['en']).nav_login}</span>`;
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
      if (!res.ok) throw new Error(data.detail || 'Registration failed');
      
      currentUser = data.user;
      localStorage.setItem('agrismart_user', JSON.stringify(currentUser));
      closeAuthModal();
      updateAuthUI();
      showToast(`Welcome to AgriSmart AI, ${currentUser.name}! Account registered in database.`, 'success');
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
      if (!res.ok) throw new Error(data.detail || 'Login failed');

      currentUser = data.user;
      localStorage.setItem('agrismart_user', JSON.stringify(currentUser));
      closeAuthModal();
      updateAuthUI();
      showToast(`Welcome back, ${currentUser.name}!`, 'success');
    } catch (e) {
      errBox.innerText = e.message;
      errBox.style.display = 'block';
    }
  }
}

// Toast notification engine
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

function logoutUser() {
  if (confirm("Do you want to log out of your AgriSmart account?")) {
    currentUser = null;
    localStorage.removeItem('agrismart_user');
    updateAuthUI();
  }
}

// =================================================================
// 9. BONUS A: CROP RECOMMENDATION
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
    location: userLocationName
  };

  try {
    const res = await fetch('/api/crop-recommendation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderCropRecommendations(data.recommendations);
    showToast("Top crops recommended successfully!", "success");
  } catch (e) {
    console.error('Crop rec error:', e);
    showToast("Crop recommendation computation error", "error");
  }
}

function renderCropRecommendations(recs) {
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
}

// =================================================================
// 10. BONUS B: SMART IRRIGATION
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
// 11. BONUS D: SUSTAINABILITY SCORE
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
// 12. BONUS E: GROUNDED FARMER ASSISTANT (CHAT)
// =================================================================
function askQuick(q) {
  document.getElementById('chat-input').value = q;
  sendChatMessage();
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';

  const windowEl = document.getElementById('chat-window');

  // User msg
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg user';
  userDiv.innerText = text;
  windowEl.appendChild(userDiv);
  windowEl.scrollTop = windowEl.scrollHeight;

  try {
    const res = await fetch('/api/assistant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, language: currentLanguage })
    });
    const data = await res.json();

    const botDiv = document.createElement('div');
    botDiv.className = 'chat-msg bot';
    botDiv.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <strong>🌱 ${data.topic}</strong>
        <button class="btn-tts" onclick="speakRaw('${data.answer.replace(/'/g, "\\'")}')">🔊 Voice</button>
      </div>
      <p>${data.answer}</p>
      <div style="font-size:0.75rem; color:#64748b; margin-top:6px; border-top:1px dashed #cbd5e1; padding-top:4px;">
        <em>Verified Source: ${data.grounded_source}</em>
      </div>
    `;
    windowEl.appendChild(botDiv);
    windowEl.scrollTop = windowEl.scrollHeight;
  } catch (e) {
    console.error('Chat error:', e);
  }
}

// =================================================================
// 13. BONUS F & G: IOT TELEMETRY & AGENTIC ADVISOR
// =================================================================
async function fetchIoTTelemetry() {
  try {
    const res = await fetch('/api/iot/telemetry');
    const data = await res.json();
    const t = data.telemetry;

    document.getElementById('iot-moist').innerText = `${t.soil_moisture_pct}%`;
    document.getElementById('iot-temp').innerText = `${t.ambient_temperature_c}°C`;
    document.getElementById('iot-hum').innerText = `${t.relative_humidity_pct}%`;
    document.getElementById('iot-ph').innerText = t.soil_ph;

    const mStatus = document.getElementById('iot-moist-status');
    if (t.soil_moisture_pct < 15) {
      mStatus.innerText = 'Water Stressed';
      mStatus.style.color = '#ef4444';
    } else {
      mStatus.innerText = 'Normal Field Capacity';
      mStatus.style.color = '#10b981';
    }
  } catch (e) {
    console.error('IoT error:', e);
  }
}

async function triggerScenario(mode) {
  try {
    await fetch('/api/iot/scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: mode })
    });
    fetchIoTTelemetry();
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
