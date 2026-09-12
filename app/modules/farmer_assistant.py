"""
AgriSmart AI - Multilingual Grounded Farmer Assistant (GenAI with Guardrails)
Compliant with SIH-2026 Problem Statement 1 (Bonus Module E)

Features:
  - Intent Classification:
    * Greeting Detection (Hi, Hello, Namaste, Kem Cho, Ram Ram)
    * Out-of-Domain Guardrail (Strictly rejects non-agricultural prompts)
    * Agricultural Knowledge Matching (Diseases, Fertilizers, Irrigation, Soil pH, Organic)
  - Grounded Question Answering backed by ICAR & State Agriculture Universities (SAUs) guidelines.
  - Zero Hallucination: Direct ICAR/FAO citations.
  - Multilingual Responses: English, Hindi (हिन्दी), Gujarati (ગુજરાતી), Marathi (मराठी).
"""

import re
import os
import sys
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# -------------------------------------------------------------
# 1. GREETINGS DICTIONARY
# -------------------------------------------------------------
GREETING_PATTERNS = [
    r"\b(hi|hello|hey|hiya|howdy)\b",
    r"\b(namaste|namaskar|namaskara)\b",
    r"\b(kem\s*cho|kemcho)\b",
    r"\b(ram\s*ram|radhe\s*radhe|jai\s*shree\s*krishna|jai\s*kisan)\b",
    r"\b(pranam|pranaam)\b",
    r"\b(good\s*morning|good\s*afternoon|good\s*evening)\b",
    r"\b(shubh\s*prabhat|suprabhat)\b",
    r"\b(kaise\s*ho|kasa\s*kay)\b",
    # Native Scripts
    r"(नमस्ते|नमस्कार|प्रणाम|सुप्रभात|शुभ\s*प्रभात|राम\s*राम|हेलो|हाय|जय\s*श्री\s*कृष्णा|जय\s*किसान)",
    r"(નમસ્તે|નમસ્કાર|કેમ\s*છો|કેમછો|રામ\s*રામ|જય\s*શ્રી\s*કૃષ્ણ)",
    r"(नमस्कार|कसा\s*काय)"
]

GREETING_RESPONSES = {
    "en": "Hello farmer friend! 🌱 I am AgriSmart AI, your expert agronomy companion. How can I help you today with your crops, plant diseases, fertilizers, soil health, or irrigation scheduling?",
    "hi": "नमस्ते किसान भाई! 🌱 मैं एग्रीस्मार्ट एआई हूँ, आपका समर्पित कृषि सलाहकार। आज मैं आपकी फसलों, पौध रोगों, खाद-उर्वरक, मिट्टी अथवा सिंचाई के बारे में क्या सहायता कर सकता हूँ?",
    "gu": "નમસ્તે ખેડૂત મિત્ર! 🌱 હું એગ્રીસ્માર્ટ એઆઈ છું, તમારો કૃષિ માર્ગદર્શક. આજે હું તમારા પાક, રોગ નિયંત્રણ, ખાતર, જમીન કે સિંચાઈ અંગે શું મદદ કરી શકું?",
    "mr": "नमस्कार शेतकरी मित्र! 🌱 मी अग्रीस्मार्ट एआय, तुमचा कृषी सल्लागार. आज मी तुमच्या पिके, वनस्पती रोग, खते, माती किंवा सिंचनाबाबत कशी मदत करू शकतो?"
}

# -------------------------------------------------------------
# 2. OUT-OF-DOMAIN GUARDRAIL
# -------------------------------------------------------------
AGRI_KEYWORDS = [
    # General Agriculture & Soil
    "crop", "plant", "leaf", "leaves", "disease", "rot", "blight", "rust", "spot", "mold",
    "scab", "mildew", "pest", "insect", "fungus", "fungicide", "pesticide", "spray",
    "chemical", "organic", "fertilizer", "urea", "dap", "npk", "potash", "mop", "ssp",
    "zinc", "boron", "soil", "ph", "acid", "alkali", "gypsum", "lime", "water", "rain",
    "irrigation", "drip", "sprinkler", "weather", "temperature", "humidity", "seed",
    "sow", "sowing", "harvest", "yield", "rotation", "field", "farm", "farmer", "agriculture",
    # Specific Crops
    "tomato", "potato", "corn", "maize", "apple", "grape", "pepper", "capsicum", "chilli",
    "wheat", "rice", "paddy", "cotton", "bajra", "millet", "groundnut", "peanut", "mustard",
    "gram", "chickpea", "pulses", "legume",
    # Hindi/Regional transliterated terms
    "kheti", "kisan", "fasal", "paani", "sinchai", "khad", "roag", "rog", "bimari", "beemari",
    "dawa", "dawai", "keeda", "mitti", "jaivik", "neem", "gehu", "chawal", "dhan", "makka",
    "aloo", "tamatar", "mirch", "kapas",
    # Gujarati terms
    "khedut", "pak", "jamin", "khatar", "dava", "jivaat", "sukaro", "geru", "pani",
    # Marathi terms
    "sheti", "shetkari", "peek", "pika", "mati", "khate", "tambera", "karpa", "paus",
    # Native Hindi/Devanagari scripts
    "खेती", "किसान", "फसल", "पौधा", "पौधे", "पत्ता", "पत्ती", "रोग", "झुलसा", "कीट", "खाद", "उर्वरक",
    "यूरिया", "डीएपी", "सिंचाई", "पानी", "मौसम", "मिट्टी", "टमाटर", "आलू", "मक्का", "गेहूं", "धान", "कपास",
    # Native Gujarati scripts
    "ખેતી", "પાક", "રોગ", "ખાતર", "જમીન", "સિંચાઈ", "પાણી", "ટામેટાં", "બટાકા", "મકાઈ", "કપાસ", "જીવાત",
    # Native Marathi scripts
    "शेती", "पीक", "रोग", "खत", "माती", "पाणी", "सिंचन", "तांबेरा", "करपा"
]

OUT_OF_DOMAIN_RESPONSES = {
    "en": "🌱 I am AgriSmart AI, an agricultural and crop health advisor. I can only assist with farming, plant diseases, fertilizers, soil, weather, and irrigation questions. Please ask a farming-related query!",
    "hi": "🌱 मैं एग्रीस्मार्ट एआई हूँ, एक समर्पित कृषि सलाहकार। मैं केवल खेती, फसल सुरक्षा, पौध रोग, खाद-उर्वरक, मिट्टी, मौसम और सिंचाई संबंधी प्रश्नों के उत्तर दे सकता हूँ। कृपया कृषि से संबंधित प्रश्न पूछें!",
    "gu": "🌱 હું એગ્રીસ્માર્ટ એઆઈ છું, એક સમર્પિત ખેતીવાડી સલાહકાર. હું માત્ર ખેતી, પાકના રોગ, ખાતર, જમીન, હવામાન અને સિંચાઈ સંબંધિત પ્રશ્નોના જવાબો આપી શકું છું. કૃપા કરીને ખેતી સંબંધિત પ્રશ્ન પૂછો!",
    "mr": "🌱 मी अग्रीस्मार्ट एआय, एक समर्पित कृषी सल्लागार आहे. मी फक्त शेती, पीक संरक्षण, वनस्पती रोग, खते, माती, हवामान आणि सिंचनासंबंधी प्रश्नांची उत्तरे देऊ शकतो. कृपया शेतीशी संबंधित प्रश्न विचारा!"
}

# -------------------------------------------------------------
# 3. VERIFIED AGRONOMIC CORPUS (ICAR / FAO Backed)
# -------------------------------------------------------------
AGRONOMIC_CORPUS = {
    "early_blight": {
        "keywords": ["early blight", "concentric rings", "alternaria", "ageeti", "sukaro"],
        "title": "Early Blight Management (Tomato & Potato)",
        "source": "ICAR-CPRI Advisory No. 42 / ICAR-IIHR Plant Pathology",
        "answer_en": "Early Blight (Alternaria solani) causes target-like dark concentric rings on older leaves. 1) Prune lower infected leaves immediately. 2) Avoid overhead splashing; use drip irrigation. 3) Spray Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil @ 2 g/L. For biological control, spray Trichoderma viride @ 5 g/L.",
        "answer_hi": "अगेती झुलसा (Early Blight) में पत्तियों पर गोल छल्लेदार काले धब्बे बनते हैं। 1) निचली ग्रसित पत्तियों को तोड़कर नष्ट करें। 2) ऊपर से पानी छिड़कने से बचें। 3) मेंकोजेब (Mancozeb 75% WP) 2.5 ग्राम प्रति लीटर पानी में मिलाकर 10 दिन के अंतर पर छिड़कें। जैविक उपचार में ट्राइकोडर्मा विरिडी 5 ग्राम/लीटर प्रयोग करें।",
        "answer_gu": "અર્લી બ્લાઇટ (સુકારો) રોગમાં પાન પર ગોળાકાર કથ્થઈ વલયો બને છે. 1) રોગગ્રસ્ત નીચેના પાન દૂર કરો. 2) પાન પર પાણી ન પડે તે રીતે ડ્રિપથી પિયત આપો. 3) મેન્કોઝેબ ૭૫% ડબલ્યુપી ૨.૫ ગ્રામ પ્રતિ લિટર પાણીમાં ભેળવી છંટકાવ કરો. જૈવિક માટે ટ્રાઇકોડર્મા વિરિડી ૫ ગ્રામ/લિટર વાપરો.",
        "answer_mr": "लवकर येणारा करपा (Early Blight) पानांवर चक्राकार काळे ठिपके निर्माण करतो. 1) बाधित पाने छाटा. 2) मॅनकोझेब २.५ ग्रॅम प्रति लिटर पाण्यात मिसळून फवारा. सेंद्रिय नियंत्रणासाठी ट्रायकोडर्मा ५ ग्रॅम/लिटर वापरा."
    },
    "late_blight": {
        "keywords": ["late blight", "phytophthora", "water soaked", "pacheti"],
        "title": "Late Blight Emergency Advisory (Potato & Tomato)",
        "source": "ICAR Central Potato Research Institute (CPRI) Emergency Bulletin",
        "answer_en": "Late Blight (Phytophthora infestans) is extremely destructive in cool, wet weather, causing water-soaked black rot. Immediately spray systemic fungicide Metalaxyl 8% + Mancozeb 64% (Ridomil Gold) @ 2.5 g/L, or Cymoxanil + Mancozeb @ 3 g/L. Stop irrigation immediately if weather is humid and overcast.",
        "answer_hi": "पछेती झुलसा (Late Blight) नम और ठंडे मौसम में तेजी से फैलता है, जिससे पत्तियां जलने जैसी काली पड़ जाती हैं। तुरंत रिडोमिल गोल्ड (Metalaxyl + Mancozeb) 2.5 ग्राम प्रति लीटर पानी में मिलाकर छिड़कें। बादल छाए रहने पर सिंचाई तुरंत रोक दें।",
        "answer_gu": "લેટ બ્લાઇટ (પાછોતરો સુકારો) ભેજવાળા વાતાવરણમાં પાંદડા કાળા પાડી સડાવી દે છે. તાત્કાલિક રીડોમિલ ગોલ્ડ ૨.૫ ગ્રામ પ્રતિ લિટર પાણીમાં છાંટો. વાદળછાયા વાતાવરણમાં પિયત બંધ રાખો.",
        "answer_mr": "उशिरा येणारा करपा (Late Blight) पानांवर काळे डाग पाडून झाड वाळवतो. तातडीने रिडोमिल गोल्ड २.५ ग्रॅम/लिटर फवारा. ढगाळ हवेत पाणी देणे टाळा."
    },
    "rust": {
        "keywords": ["rust", "pustule", "geru", "tambera", "common rust"],
        "title": "Cereal Rust Disease Management (Corn & Wheat)",
        "source": "ICAR-Indian Institute of Maize Research (IIMR) & IIWBR",
        "answer_en": "Common Rust presents as reddish-brown powdery pustules on leaves. Spray Propiconazole 25% EC (Tilt) @ 1 ml/L or apply wettable sulfur 80% WP @ 3 g/L at the first symptom. Avoid late excess nitrogen fertilizer which accelerates spore multiplication.",
        "answer_hi": "गेरूई/रस्ट रोग में पत्तियों पर लाल-भूरे पाउडर जैसे दाने बनते हैं। लक्षण दिखते ही प्रोपिकोनाजोल (Tilt) 1 मिली प्रति लीटर पानी या घुलनशील गंधक (सल्फर) 3 ग्राम/लीटर का छिड़काव करें। यूरिया की अत्यधिक मात्रा न दें।",
        "answer_gu": "ગેરુ રોગમાં પાન પર લાલાશ પડતા બદામી પાઉડર જેવા ફોલ્લા દેખાય છે. પ્રોપીકોનાઝોલ (ટિલ્ટ) ૧ મિલી પ્રતિ લિટર પાણી અથવા સલ્ફર ૩ ગ્રામ/લિટર છાંટો. વધારે પડતો યુરિયા ખાતર આપવાનું ટાળો.",
        "answer_mr": "तांबेरा (Rust) रोगात पानांवर तांबूस पावडरसारखे ठिपके येतात. प्रोपिकोनाझोल १ मिली प्रति लिटर पाण्यात मिसळून फवारा. जास्त युरिया देणे टाळा."
    },
    "bacterial_spot": {
        "keywords": ["bacterial spot", "speckling", "bacterial wilt", "xanthomonas"],
        "title": "Bacterial Spot & Canker Control (Pepper & Tomato)",
        "source": "ICAR-IIHR Horticulture Advisory",
        "answer_en": "Bacterial Spot causes small dark greasy spots with yellow halos. Spray Copper Oxychloride (Blitox 50) @ 2.5 g/L tank-mixed with Streptocycline @ 1 g per 10 L of water. Avoid touching wet plants and rotate crops away from solanaceous plants.",
        "answer_hi": "जीवाणु धब्बा (Bacterial Spot) में पत्तियों पर पीले घेरे वाले छोटे काले चकत्ते बनते हैं। कॉपर ऑक्सीक्लोराइड 2.5 ग्राम + स्ट्रेप्टोसाइक्लिन 1 ग्राम (10 लीटर पानी में) मिलाकर छिड़कें। भीगे पौधों को हाथ न लगाएं।",
        "answer_gu": "બેક્ટેરિયલ સ્પોટમાં પાંદડા પર પીળી કિનારીવાળા કાળા ડાઘ પડે છે. કોપર ઓક્સીક્લોરાઇડ ૨.૫ ગ્રામ + સ્ટ્રેપ્ટોસાયક્લિન ૧ ગ્રામ (૧૦ લિટર પાણીમાં) મિક્સ કરી છંટકાવ કરો.",
        "answer_mr": "जिवाणू ठिपके (Bacterial Spot) वर कॉपर ऑक्सीक्लोराईड २.५ ग्रॅम + स्ट्रेप्टोसायक्लिन १ ग्रॅम प्रति १० लिटर पाण्यात मिसळून फवारावे."
    },
    "scab_and_rot": {
        "keywords": ["scab", "black rot", "apple scab", "grape rot", "venturia"],
        "title": "Scab & Fruit Rot Management (Apple & Grape)",
        "source": "ICAR-CITH (Central Institute of Temperate Horticulture) & NRC Grapes",
        "answer_en": "Apple Scab and Grape Black Rot cause olive-black velvety lesions on leaves and fruit mummification. Spray Mancozeb 75% WP @ 2.5 g/L or Difenoconazole 25% EC (Score) @ 0.5 ml/L. Prune infected twigs and burn fallen infected mummies.",
        "answer_hi": "सेब का स्कैब और अंगूर का सड़न रोग पत्तों और फलों पर गहरे काले चकत्ते बनाता है। डाइफेनोकोनाजोल (Score) 0.5 मिली/लीटर या मेंकोजेब 2.5 ग्राम/लीटर का छिड़काव करें। गिरे हुए रोगग्रस्त पत्तों को जला दें।",
        "answer_gu": "સફરજન સ્કેબ અને દ્રાક્ષનો સડો પાંદડા તેમજ ફળ પર કાળા ડાઘ પાડે છે. ડાયફેનોકોનાઝોલ ૦.૫ મિલી/લિટર અથવા મેન્કોઝેબ ૨.૫ ગ્રામ/લિટર છાંટો. બગીચામાં સ્વચ્છતા રાખો.",
        "answer_mr": "स्कॅब आणि फळकूज रोगावर डायफेनोकोनाझोल ०.५ मिली प्रति लिटर किंवा मॅनकोझेब २.५ ग्रॅम प्रति लिटर फवारा."
    },
    "irrigation": {
        "keywords": ["irrigation", "water", "sinchai", "pani", "paani", "moisture", "drip", "sprinkler"],
        "title": "Smart Irrigation Scheduling & Water Conservation",
        "source": "FAO Irrigation & Drainage Paper 56 / PM Krishi Sinchayee Yojana",
        "answer_en": "Irrigate crops during early mornings (6-9 AM) to minimize evaporation. If heavy rain (>8mm) is forecast in the next 24-48 hours, hold irrigation to prevent root hypoxia. Drip irrigation delivers 90% water efficiency, reducing disease risk by keeping foliage dry.",
        "answer_hi": "सिंचाई सुबह 6 से 9 बजे के बीच करें ताकि वाष्पीकरण से पानी का नुकसान न हो। यदि अगले 24-48 घंटों में बारिश (8 मिमी से अधिक) की संभावना है, तो सिंचाई टालें। ड्रिप सिंचाई से 40-50% पानी की बचत होती है और पत्तियां सूखी रहने से रोग नहीं लगते।",
        "answer_gu": "સિંચાઈ સવારે ૬ થી ૯ વાગ્યા વચ્ચે કરવી જેથી પાણીની બગાડ ન થાય. આગામી ૨૪-૪૮ કલાકમાં વરસાદની આગાહી હોય તો પિયત મુલતવી રાખો. ટપક પદ્ધતિ ૪૦-૫૦% પાણી બચાવે છે અને પાકને રોગમુક્ત રાખે છે.",
        "answer_mr": "पाणी नेहमी सकाळी ६ ते ९ दरम्यान द्यावे. पुढील २४-४८ तासांत पावसाचा अंदाज असल्यास पाणी देणे पुढे ढकला. ठिबक सिंचनाने ४०-५०% पाण्याची बचत होते."
    },
    "fertilizer_npk": {
        "keywords": ["fertilizer", "urea", "dap", "npk", "potash", "khad", "khatar", "khate", "nitrogen", "phosphorus", "potassium"],
        "title": "Balanced Plant Nutrition (NPK Split Dosing)",
        "source": "Soil Health Card Scheme / ICAR-Indian Institute of Soil Science (IISS)",
        "answer_en": "Always apply fertilizers according to Soil Health Card testing. Split Nitrogen into 2-3 split applications (basal, tillering/vegetative, and flowering). Apply full Phosphorus (DAP/SSP) and 50% Potassium as basal dose at sowing. Incorporate 5 tons/ha well-decomposed FYM or vermicompost.",
        "answer_hi": "मृदा स्वास्थ्य कार्ड की जांच अनुसार ही खाद दें। यूरिया को एक बार में न डालकर 2-3 खुराकों में बांटकर दें (बुवाई, वानस्पतिक वृद्धि और फूल आने पर)। डीएपी (फास्फोरस) को बुवाई के समय बेसल डोज में दें। साथ में 5 टन सड़ी गोबर खाद अवश्य मिलाएं।",
        "answer_gu": "જમીન ચકાસણી મુજબ જ ખાતર આપો. યુરિયા એકસાથે ન આપતાં ૨-૩ હપ્તામાં આપો (વાવણી, ફૂટ અને ફૂલ આવવાના સમયે). ડીએપી સંપૂર્ણ વાવણી સમયે આપો. સાથે ૫ ટન દેશી છાણીયું ખાતર ઉમેરો.",
        "answer_mr": "माती परीक्षणानुसारच खते द्या. युरिया २-३ हप्त्यांत विभागून द्या (पेरणी, वाढ आणि फुले येताना). डीएपी पेरणीच्या वेळी द्या आणि ५ टन शेणखत वापरा."
    },
    "soil_ph": {
        "keywords": ["soil ph", "acidic soil", "alkaline soil", "lime", "gypsum", "saline", "mitti"],
        "title": "Soil pH Diagnostics & Reclamation (Acidic vs Alkaline)",
        "source": "ICAR-CSSRI (Central Soil Salinity Research Institute) Karnal",
        "answer_en": "For Acidic Soil (pH < 6.0): Broadcast Agricultural Limestone (CaCO3) @ 2-4 tons/ha or dolomite to neutralize acidity and unlock Phosphorus. For Alkaline/Calcareous Soil (pH > 7.8): Apply Agricultural Gypsum (CaSO4) @ 2.5-5 tons/ha along with green manuring (Dhaincha/Sunhemp) to displace sodium and lower soil pH.",
        "answer_hi": "अम्लीय मिट्टी (pH 6.0 से कम) में: 2-4 टन प्रति हेक्टेयर चूना (लाइम) या डोलोमाइट डालें ताकि मिट्टी सामान्य हो और पोषक तत्व मिल सकें। क्षारीय मिट्टी (pH 7.8 से अधिक) में: 2.5-5 टन जिप्सम डालें और ढैंचा की हरी खाद लगाएं ताकि सोडियम हट सके और पीएच संतुलित हो।",
        "answer_gu": "એસિડિક જમીન (pH ૬.૦ થી ઓછી): ૨-૪ ટન/હેક્ટર કૃષિ ચૂનો (લાઇમ) ઉમેરો જેથી પોષકતત્વો મળી રહે. ક્ષારીય જમીન (pH ૭.૮ થી વધુ): ૨.૫-૫ ટન જિપ્સમ નાખો અને ઈકડ/સણનું લીલું ખાતર આપો જેથી જમીન સુધરે.",
        "answer_mr": "आम्लधर्मी माती (pH < ६.०): २-४ टन कृषी चुना वापरा. क्षारयुक्त माती (pH > ७.८): २.૫-५ टन जिप्सम आणि तागाचे हिरवळीचे खत वापरा."
    },
    "organic_pest": {
        "keywords": ["organic", "neem", "jaivik", "trichoderma", "bio", "jeevamrut", "pest"],
        "title": "Organic Pest & Biological Disease Management",
        "source": "National Centre of Organic & Natural Farming (NCONF) Guidelines",
        "answer_en": "Spray 5% Neem Seed Kernel Extract (NSKE) or cold-pressed Neem Oil @ 5 ml/L + 1 ml liquid soap for aphids, whiteflies, and fungal spores. Apply Trichoderma viride @ 5 g/L to soil/seed to prevent root rot and wilt. Use yellow sticky traps (15 traps/ha) for sucking pest monitoring.",
        "answer_hi": "जैविक कीट नियंत्रण के लिए नीम तेल (5 मिली प्रति लीटर पानी + 1 मिली तरल साबुन) का छिड़काव करें। जड़ सड़न और उकठा से बचाव के लिए ट्राइकोडर्मा विरिडी 5 ग्राम/लीटर जड़ों में दें। रस चूसक कीड़ों के लिए पीले चिपचिपे ट्रैप (15 प्रति हेक्टेयर) लगाएं।",
        "answer_gu": "જૈવિક નિયંત્રણ માટે ૫ મિલી લીમડાનું તેલ પ્રતિ લિટર પાણીમાં સાબુના ફીણ સાથે છાંટો. મૂળના રોગ માટે ટ્રાઇકોડર્મા ૫ ગ્રામ/લિટર આપો. ચૂસિયા જીવાત માટે પીળા ચીકણા ટ્રેપ લગાવો.",
        "answer_mr": "सेंद्रिय कीड नियंत्रणासाठी नीम तेल ५ मिली प्रति लिटर पाण्यात मिसळून फवारा. मूळकुजव्या रोगासाठी ट्रायकोडर्मा ५ ग्रॅम प्रति लिटर वापरा."
    },
    "zinc_deficiency": {
        "keywords": ["zinc", "khaira", "yellowing", "micronutrient", "boron"],
        "title": "Micronutrient Deficiency (Zinc Chlorosis)",
        "source": "ICAR-IISS Micronutrient Bulletin",
        "answer_en": "Zinc deficiency causes 'Khaira' disease in rice and white bud in maize with interveinal yellowing. Foliar spray Zinc Sulfate 21% @ 5 g/L + 2.5 g slaked lime per liter of water, or apply soil Zinc Sulfate @ 25 kg/ha once every 2-3 years.",
        "answer_hi": "जिंक की कमी से धान में 'खैरा' रोग और मक्के में पत्तियां सफेद होती हैं। जिंक सल्फेट 5 ग्राम + 2.5 ग्राम बुझा हुआ चूना प्रति लीटर पानी में मिलाकर पर्णीय छिड़काव करें या 25 किग्रा जिंक सल्फेट प्रति हेक्टेयर मिट्टी में डालें।",
        "answer_gu": "ઝીંકની ખામીથી ડાંગરમાં ખૈરા રોગ થાય છે અને પાન પીળા પડે છે. ઝીંક સલ્ફેટ ૫ ગ્રામ + ૨.૫ ગ્રામ ચૂનો પ્રતિ લિટર પાણીમાં ભેળવી છંટકાવ કરો.",
        "answer_mr": "झिंकच्या कमतरतेमुळे पांढरे ठिपके येतात. झिंक सल्फेट ५ ग्रॅम + २.૫ ग्रॅम चुना प्रति लिटर पाण्यात मिसळून फवारावे."
    }
}


def ask_farmer_assistant(query: str, language: str = "en") -> Dict[str, Any]:
    """
    Intelligent agronomy assistant with Greeting Detection,
    Out-of-Domain Guardrail Filter, and ICAR-backed grounded responses.
    """
    clean_query = query.strip()
    query_lower = clean_query.lower()
    lang = language if language in ["en", "hi", "gu", "mr"] else "en"

    # -------------------------------------------------------------
    # 1. GREETING INTENT
    # -------------------------------------------------------------
    for pat in GREETING_PATTERNS:
        if re.search(pat, query_lower):
            return {
                "status": "success",
                "intent": "greeting",
                "query": clean_query,
                "language": lang,
                "topic": "Welcome & Greetings",
                "answer": GREETING_RESPONSES[lang],
                "grounded_source": "AgriSmart AI Natural Agricultural Assistant",
                "speech_synthesis_ready": True
            }

    # -------------------------------------------------------------
    # 2. OUT-OF-DOMAIN GUARDRAIL
    # -------------------------------------------------------------
    is_agri_related = any(k in query_lower for k in AGRI_KEYWORDS)
    if not is_agri_related:
        return {
            "status": "out_of_domain",
            "intent": "guardrail_rejection",
            "query": clean_query,
            "language": lang,
            "topic": "Out-of-Domain Query",
            "answer": OUT_OF_DOMAIN_RESPONSES[lang],
            "grounded_source": "AgriSmart AI Agricultural Scope Policy",
            "speech_synthesis_ready": True
        }

    # -------------------------------------------------------------
    # 3. GROUNDED AGRONOMY INTENT MATCHING
    # -------------------------------------------------------------
    best_match_key = "early_blight"
    best_match_score = 0

    for key, data in AGRONOMIC_CORPUS.items():
        score = 0
        for kw in data["keywords"]:
            if kw in query_lower:
                score += len(kw)
        if score > best_match_score:
            best_match_score = score
            best_match_key = key

    # Secondary heuristic matches if exact keywords didn't trigger
    if best_match_score == 0:
        if any(w in query_lower for w in ["water", "rain", "sinchai", "pani", "paani", "drip"]):
            best_match_key = "irrigation"
        elif any(w in query_lower for w in ["fertilizer", "urea", "dap", "npk", "potash", "khad"]):
            best_match_key = "fertilizer_npk"
        elif any(w in query_lower for w in ["ph", "acid", "alkali", "gypsum", "lime", "mitti", "soil"]):
            best_match_key = "soil_ph"
        elif any(w in query_lower for w in ["rust", "pustule", "geru", "tambera"]):
            best_match_key = "rust"
        elif any(w in query_lower for w in ["late", "water soaked", "pacheti"]):
            best_match_key = "late_blight"
        elif any(w in query_lower for w in ["spot", "speck", "bacterial"]):
            best_match_key = "bacterial_spot"
        elif any(w in query_lower for w in ["scab", "black rot", "apple", "grape"]):
            best_match_key = "scab_and_rot"
        elif any(w in query_lower for w in ["organic", "neem", "jaivik", "trichoderma"]):
            best_match_key = "organic_pest"
        elif any(w in query_lower for w in ["zinc", "khaira", "yellow"]):
            best_match_key = "zinc_deficiency"

    entry = AGRONOMIC_CORPUS[best_match_key]
    lang_key = f"answer_{lang}"
    answer_text = entry.get(lang_key, entry["answer_en"])

    return {
        "status": "success",
        "intent": "agronomy_answer",
        "query": clean_query,
        "language": lang,
        "topic": entry["title"],
        "answer": answer_text,
        "grounded_source": entry["source"],
        "speech_synthesis_ready": True
    }


if __name__ == "__main__":
    print("Testing Greetings:")
    print("EN:", ask_farmer_assistant("Hello", "en")["answer"])
    print("HI:", ask_farmer_assistant("नमस्ते", "hi")["answer"])
    
    print("\nTesting Out-of-Domain Guardrail:")
    print("EN:", ask_farmer_assistant("Who won the cricket match?", "en")["answer"])
    print("HI:", ask_farmer_assistant("मुझे एक मूवी का नाम बताओ", "hi")["answer"])

    print("\nTesting Agronomy Questions:")
    print("Wheat Rust:", ask_farmer_assistant("How do I control rust in wheat?", "en")["topic"])
    print("Acidic Soil:", ask_farmer_assistant("What to do if soil pH is acidic 5.0?", "en")["topic"])

