"""
Multilingual Internationalization (i18n) Module for Agricultural Disease Observation.
Provides complete translation dictionaries for English (en) and Tamil (ta)
with strict key parity across all interface elements.
"""

from typing import Dict, Any, List

SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "nativeName": "English"},
    {"code": "ta", "name": "Tamil", "nativeName": "தமிழ்"}
]

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App Header & General
        "app_title": "Agricultural Disease Observation & Expert Escalation System",
        "app_subtitle": "Standardized field observation, MobileNetV3 AI decision-support, and authoritative expert validation.",
        "offline_banner_offline": "Offline Mode: Observations are stored locally and will automatically synchronize when connectivity is restored.",
        "offline_banner_online": "Connected: System online.",
        "sync_pending": "Pending Sync",
        "sync_now": "Sync Now",
        "language_select": "Language",

        # Navigation Tabs
        "nav_farmer": "Farmer Observation",
        "nav_tracking": "Track Case / Resubmit",
        "nav_officer": "Officer Dashboard",
        "nav_expert": "Expert Workstation",
        "nav_regional": "Regional Analytics",

        # Wizard Steps
        "step_1_title": "1. Crop & Stage",
        "step_2_title": "2. Symptoms & Severity",
        "step_3_title": "3. Environmental Context",
        "step_4_title": "4. Photographic Evidence",
        "step_5_title": "5. Review & Submit",
        "next_step": "Next Step →",
        "prev_step": "← Previous Step",
        "submit_observation": "Submit Observation",

        # Form Fields
        "field_crop": "Crop",
        "field_crop_select": "-- Select Crop --",
        "field_variety": "Crop Variety (Optional)",
        "field_stage": "Crop Stage",
        "field_stage_select": "-- Select Growth Stage --",
        "field_location": "Field Location / Sector",
        "field_first_symptom": "When did symptoms first appear?",
        "field_severity": "Estimated Severity",
        "field_symptoms": "Observed Symptoms",
        "field_farmer_notes": "Farmer Notes / Description",
        "field_env_notes": "Environmental & Microclimate Notes",

        # Crops
        "crop_tomato": "Tomato",
        "crop_rice": "Paddy / Rice",
        "crop_potato": "Potato",
        "crop_maize": "Maize / Corn",
        "crop_cassava": "Cassava",
        "crop_wheat": "Wheat",
        "crop_other": "Other Crop",

        # Stages
        "stage_seedling": "Seedling",
        "stage_vegetative": "Vegetative",
        "stage_tillering": "Tillering",
        "stage_flowering": "Flowering",
        "stage_fruiting": "Fruiting",
        "stage_maturity": "Maturity / Harvesting",

        # Symptoms
        "sym_leaf_spots": "Leaf spots or lesions",
        "sym_wilting": "Wilting / Drooping foliage",
        "sym_yellowing": "Yellowing (Chlorosis)",
        "sym_powdery": "White powdery coating",
        "sym_mosaic": "Mosaic / Mottled patterns",
        "sym_curling": "Leaf curling or twisting",
        "sym_water_soaked": "Water-soaked streaks",
        "sym_stem_rot": "Stem or collar rot",
        "sym_rust": "Rust pustules (orange/brown)",
        "sym_healthy": "No visible symptoms (Healthy)",

        # Severity
        "sev_low": "Low",
        "sev_medium": "Medium",
        "sev_high": "High",
        "sev_severe": "Severe",

        # Environmental Context
        "env_rainfall": "Recent Rainfall",
        "env_rain_none": "None (Dry period)",
        "env_rain_light": "Light Drizzle",
        "env_rain_moderate": "Moderate Rainfall",
        "env_rain_heavy": "Heavy Rain / Downpour",
        "env_humidity": "Observed Humidity",
        "env_hum_low": "Low (<50%)",
        "env_hum_mod": "Moderate (50-80%)",
        "env_hum_high": "High (>80%)",
        "env_hum_sat": "Very High / Saturated",
        "env_temp": "Temperature Band",
        "env_temp_cool": "Cool (<20°C)",
        "env_temp_mod": "Moderate (20-30°C)",
        "env_temp_warm": "Warm (30-38°C)",
        "env_temp_hot": "Hot (>38°C)",
        "env_soil_moisture": "Soil Moisture Condition",
        "env_soil_dry": "Dry / Crusty",
        "env_soil_normal": "Optimal / Normal",
        "env_soil_moist": "Moist / Wet",
        "env_soil_waterlogged": "Waterlogged / Standing Water",
        "env_irrigation": "Irrigation Type",
        "env_irrig_rainfed": "Rainfed (No irrigation)",
        "env_irrig_drip": "Drip Irrigation",
        "env_irrig_flood": "Flood / Furrow Irrigation",
        "env_irrig_sprinkler": "Sprinkler Irrigation",
        "env_weather_event": "Recent Weather Event",
        "env_event_none": "None",
        "env_event_wind": "Strong Winds / Storm",
        "env_event_rain": "Continuous Multi-day Rain",
        "env_event_hail": "Hailstorm",
        "env_event_heat": "Extended Heatwave",

        # Photographic Evidence
        "photo_instructions": "Attach clear photographs of the plant to help the expert team.",
        "photo_whole": "Whole Plant View",
        "photo_affected": "Affected Area View",
        "photo_detail": "Close-up Leaf / Symptom Detail",
        "photo_quality_label": "Real-Time Image Quality Check",

        # Voice Assistance
        "voice_read_instructions": "Read Step Instructions",
        "voice_read_diagnosis": "Read AI Hypothesis & Status",
        "voice_start_dictation": "Speak Notes (Tamil / English)",
        "voice_stop": "Stop Voice",
        "voice_not_supported": "Web Speech API is not supported in this browser. Text input remains fully active.",
        "voice_listening": "Listening... Speak now.",

        # Case Tracking & Resubmission
        "track_case_heading": "Track Case Status / Resubmit Follow-up",
        "track_enter_id": "Enter Case ID (e.g., CASE-2026-001)",
        "track_search_btn": "Check Status",
        "track_status_label": "Current Status",
        "track_expert_notes_label": "Expert Advice / Instructions",
        "resubmit_heading": "Submit Additional Information Requested by Expert",
        "resubmit_notes_placeholder": "Provide the requested details (e.g. stem cut test results, newer photos)...",
        "resubmit_btn": "Submit Follow-up Information",

        # Regional Analytics & Outbreak Visualization
        "regional_heading": "Regional Outbreak Analytics & Risk Matrix",
        "regional_disclaimer": "Simulated Decision-Support Data: Not real-world epidemiological confirmation.",
        "filter_all_crops": "All Crops",
        "filter_all_regions": "All Regions",
        "filter_all_severities": "All Severities",
        "filter_all_priorities": "All Priorities",
        "filter_all_statuses": "All Statuses",
        "filter_apply": "Filter Data",
        "regional_active_alerts": "Active Outbreak / Elevated Watch Alerts",
        "col_region": "Region / Sector",
        "col_total_cases": "Total Cases",
        "col_high_prio": "High Priority",
        "col_dominant_disease": "Dominant Pattern",
        "col_moisture_risk": "Moisture Risk",
        "col_risk_level": "Outbreak Watch Level",
        "t_review_card_title": "T_review Latency Analysis",
        "ai_monitoring_card_title": "AI Confidence & Agreement Monitoring",

        # Disclaimers & Ethics
        "ai_hypothesis_disclaimer": "Preliminary decision support hypothesis only. Not final diagnosis. Authoritative diagnosis is provided by agricultural extension experts.",
        "location_privacy_notice": "Location privacy active: GPS coordinates are obfuscated and approximate to protect farmer privacy.",

        # Operational Status
        "status_submitted": "Submitted",
        "status_under_review": "Under Review",
        "status_more_info": "More Information Required",
        "status_expert_validated": "Expert Validated",

        # Priority Labels
        "prio_urgent": "Urgent",
        "prio_high": "High",
        "prio_medium": "Medium",
        "prio_low": "Low"
    },
    "ta": {
        # App Header & General
        "app_title": "வேளாண் பயிர் நோய் கண்காணிப்பு மற்றும் நிபுணர் தீர்வு அமைப்பு",
        "app_subtitle": "தரப்படுத்தப்பட்ட களக் கண்காணிப்பு, மொபைல்நெட்V3 AI பரிந்துரை மற்றும் அங்கீகரிக்கப்பட்ட நிபுணர் சரிபார்ப்பு.",
        "offline_banner_offline": "ஆஃப்லைன் பயன்முறை: பதிவுகள் சாதனத்தில் சேமிக்கப்பட்டு, இணையம் கிடைத்ததும் தானாகவே ஒத்திசைக்கப்படும்.",
        "offline_banner_online": "இணைய இணைப்பு உள்ளது: அமைப்பு நேரலையில் உள்ளது.",
        "sync_pending": "ஒத்திசைவு நிலுவையில்",
        "sync_now": "இப்போது ஒத்திசை",
        "language_select": "மொழி",

        # Navigation Tabs
        "nav_farmer": "விவசாயி பதிவு",
        "nav_tracking": "வழக்கை கண்காணிக்க / மீண்டும் சமர்ப்பிக்க",
        "nav_officer": "அலுவலர் தகவல் பலகை",
        "nav_expert": "நிபுணர் பணித்தளம்",
        "nav_regional": "மண்டல பகுப்பாய்வு",

        # Wizard Steps
        "step_1_title": "1. பயிர் மற்றும் பருவம்",
        "step_2_title": "2. அறிகுறிகள் மற்றும் தீவிரம்",
        "step_3_title": "3. சுற்றுச்சூழல் சூழல்",
        "step_4_title": "4. புகைப்பட ஆதாரங்கள்",
        "step_5_title": "5. சரிபார்த்து சமர்ப்பிக்கவும்",
        "next_step": "அடுத்த படி →",
        "prev_step": "← முந்தைய படி",
        "submit_observation": "கண்காணிப்பை சமர்ப்பிக்கவும்",

        # Form Fields
        "field_crop": "பயிர்",
        "field_crop_select": "-- பயிரைத் தேர்ந்தெடுக்கவும் --",
        "field_variety": "பயிர் ரகம் (விருப்பத்தேர்வு)",
        "field_stage": "பயிர் வளர்ச்சிப் பருவம்",
        "field_stage_select": "-- பருவத்தைத் தேர்ந்தெடுக்கவும் --",
        "field_location": "நில அமைவிடம் / பகுதி",
        "field_first_symptom": "அறிகுறிகள் முதலில் எப்போது தென்பட்டன?",
        "field_severity": "மதிப்பிடப்பட்ட தீவிரம்",
        "field_symptoms": "கண்டறியப்பட்ட அறிகுறிகள்",
        "field_farmer_notes": "விவசாயியின் குறிப்புகள் / விளக்கம்",
        "field_env_notes": "சுற்றுச்சூழல் மற்றும் நிலக்குறிப்புகள்",

        # Crops
        "crop_tomato": "தக்காளி",
        "crop_rice": "நெல் / சம்பா",
        "crop_potato": "உருளைக்கிழங்கு",
        "crop_maize": "மக்காச்சோளம்",
        "crop_cassava": "மரவள்ளிக்கிழங்கு",
        "crop_wheat": "கோதுமை",
        "crop_other": "பிற பயிர்",

        # Stages
        "stage_seedling": "நாற்றுப் பருவம்",
        "stage_vegetative": "வளர்ச்சிப் பருவம்",
        "stage_tillering": "தூர்கட்டும் பருவம்",
        "stage_flowering": "பூக்கும் பருவம்",
        "stage_fruiting": "காய்க்கும் பருவம்",
        "stage_maturity": "முதிர்ச்சி / அறுவடைப் பருவம்",

        # Symptoms
        "sym_leaf_spots": "இலைப்புள்ளிகள் அல்லது புண்கள்",
        "sym_wilting": "இலை அல்லது தண்டு வாடல்",
        "sym_yellowing": "இலை மஞ்சள் நிறமாதல்",
        "sym_powdery": "வெள்ளை சாம்பல் படிவு",
        "sym_mosaic": "தேமல் / பலவண்ண இலை வடிவம்",
        "sym_curling": "இலை சுருளுதல்",
        "sym_water_soaked": "நீர் வடிந்த புண்கள் / கோடுகள்",
        "sym_stem_rot": "தண்டு அல்லது வேர் அழுகல்",
        "sym_rust": "துருப்புள்ளிகள் (ஆரஞ்சு/பழுப்பு)",
        "sym_healthy": "அறிகுறிகள் இல்லை (ஆரோக்கியமானது)",

        # Severity
        "sev_low": "குறைவு",
        "sev_medium": "நடுத்தரம்",
        "sev_high": "அதிகம்",
        "sev_severe": "மிகத் தீவிரமானது",

        # Environmental Context
        "env_rainfall": "சமீபத்திய மழைப்பொழிவு",
        "env_rain_none": "இல்லை (வறண்ட நிலை)",
        "env_rain_light": "லேசான தூறல்",
        "env_rain_moderate": "மிதமான மழை",
        "env_rain_heavy": "கனமழை / வெள்ளப்பெருக்கு",
        "env_humidity": "காற்றின் ஈரப்பதம்",
        "env_hum_low": "குறைவு (<50%)",
        "env_hum_mod": "மிதம் (50-80%)",
        "env_hum_high": "அதிகம் (>80%)",
        "env_hum_sat": "மிக அதிகம் / காற்றில் நீர் நிறைவு",
        "env_temp": "வெப்பநிலை அளவு",
        "env_temp_cool": "குளிர்ச்சி (<20°C)",
        "env_temp_mod": "மிதமான வெப்பம் (20-30°C)",
        "env_temp_warm": "வெதுவெதுப்பானது (30-38°C)",
        "env_temp_hot": "அதிக வெப்பம் (>38°C)",
        "env_soil_moisture": "மண் ஈரப்பத நிலை",
        "env_soil_dry": "வறண்டது / வெடிப்புற்றது",
        "env_soil_normal": "சரியான அளவு / இயல்பு",
        "env_soil_moist": "ஈரப்பதமானது",
        "env_soil_waterlogged": "நீர் தேங்கிய நிலை",
        "env_irrigation": "பாசன முறை",
        "env_irrig_rainfed": "மானாவாரி (மழை சார்ந்தது)",
        "env_irrig_drip": "சொட்டு நீர் பாசனம்",
        "env_irrig_flood": "வாய்க்கால் பாசனம்",
        "env_irrig_sprinkler": "தெளிப்பு நீர் பாசனம்",
        "env_weather_event": "சமீபத்திய வானிலை நிகழ்வு",
        "env_event_none": "எதுவுமில்லை",
        "env_event_wind": "பலத்த காற்று / புயல்",
        "env_event_rain": "தொடர் மழை",
        "env_event_hail": "ஆலங்கட்டி மழை",
        "env_event_heat": "நீடித்த வெப்ப அலை",

        # Photographic Evidence
        "photo_instructions": "நிபுணர் குழுவிற்கு உதவ பயிரின் தெளிவான புகைப்படங்களை இணைக்கவும்.",
        "photo_whole": "முழு பயிர் தோற்றம்",
        "photo_affected": "பாதிக்கப்பட்ட பகுதி தோற்றம்",
        "photo_detail": "இலை அல்லது அறிகுறியின் நெருக்கமான படம்",
        "photo_quality_label": "நேரலை படத் தர மதிப்பீடு",

        # Voice Assistance
        "voice_read_instructions": "படி வழிமுறைகளை வாசிக்க",
        "voice_read_diagnosis": "AI பரிந்துரையை வாசிக்க",
        "voice_start_dictation": "குரல் வழி உள்ளீடு பேசவும்",
        "voice_stop": "குரலை நிறுத்தவும்",
        "voice_not_supported": "உங்கள் உலாவியில் குரல் வசதி ஆதரிக்கப்படவில்லை. விசைப்பலகை உள்ளீடு இயல்பாக செயல்படும்.",
        "voice_listening": "கேட்கிறது... இப்போது பேசுங்கள்.",

        # Case Tracking & Resubmission
        "track_case_heading": "வழக்கு நிலையை அறிய / கூடுதல் தகவலை சமர்ப்பிக்க",
        "track_enter_id": "வழக்கு எண்ணை உள்ளிடவும் (எ.கா: CASE-2026-001)",
        "track_search_btn": "நிலையை சரிபார்க்கவும்",
        "track_status_label": "தற்போதைய நிலை",
        "track_expert_notes_label": "நிபுணரின் அறிவுரைகள்",
        "resubmit_heading": "நிபுணர் கோரிய கூடுதல் தகவலை சமர்ப்பிக்கவும்",
        "resubmit_notes_placeholder": "கோரப்பட்ட தகவல்களை உள்ளிடவும் (எ.கா: தண்டு வெட்டு சோதனை முடிவுகள், புதிய படங்கள்)...",
        "resubmit_btn": "கூடுதல் தகவலை சமர்ப்பிக்கவும்",

        # Regional Analytics & Outbreak Visualization
        "regional_heading": "மண்டல நோய் பரவல் பகுப்பாய்வு மற்றும் இடர் அளவீடு",
        "regional_disclaimer": "பரிந்துரைக்கான மாதிரி தரவு: இது நிஜ உலக நோய்ப்பரவல் உறுதிப்படுத்தல் அல்ல.",
        "filter_all_crops": "அனைத்து பயிர்கள்",
        "filter_all_regions": "அனைத்து பகுதிகள்",
        "filter_all_severities": "அனைத்து தீவிர நிலைகள்",
        "filter_all_priorities": "அனைத்து முன்னுரிமைகள்",
        "filter_all_statuses": "அனைத்து நிலைகள்",
        "filter_apply": "வடிகட்டு",
        "regional_active_alerts": "செயலில் உள்ள தீவிர எச்சரிக்கைகள்",
        "col_region": "பகுதி / மண்டலம்",
        "col_total_cases": "மொத்த வழக்குகள்",
        "col_high_prio": "அவசர வழக்குகள்",
        "col_dominant_disease": "முதன்மை அறிகுறி",
        "col_moisture_risk": "ஈரப்பத இடர்",
        "col_risk_level": "கண்காணிப்பு நிலை",
        "t_review_card_title": "T_review ஆய்வு நேர பகுப்பாய்வு",
        "ai_monitoring_card_title": "AI துல்லியம் மற்றும் ஏற்பு விகிதம்",

        # Disclaimers & Ethics
        "ai_hypothesis_disclaimer": "ஆரம்பகட்ட முடிவெடுக்கும் AI பரிந்துரை மட்டுமே. இறுதி நோய் நிர்ணயம் அல்ல. வேளாண் விரிவாக்க நிபுணரின் முடிவே இறுதியானது.",
        "location_privacy_notice": "இருப்பிட பாதுகாப்பு: விவசாயியின் தனிப்பட்ட இருப்பிடம் மறைக்கப்பட்டு தோராயமான இடமாக மட்டுமே குறிக்கப்படுகிறது.",

        # Operational Status
        "status_submitted": "சமர்ப்பிக்கப்பட்டது",
        "status_under_review": "ஆய்வில் உள்ளது",
        "status_more_info": "கூடுதல் தகவல் தேவை",
        "status_expert_validated": "நிபுணரால் சரிபார்க்கப்பட்டது",

        # Priority Labels
        "prio_urgent": "அவசரம்",
        "prio_high": "முக்கியத்துவம்",
        "prio_medium": "நடுத்தரம்",
        "prio_low": "குறைவு"
    }
}


def get_supported_languages() -> List[Dict[str, str]]:
    """Returns list of supported language descriptors."""
    return SUPPORTED_LANGUAGES


def get_translation_dictionary(lang: str) -> Dict[str, str]:
    """Returns dictionary of translations for specified language code (defaults to en)."""
    lang_code = lang.lower().strip()
    return TRANSLATIONS.get(lang_code, TRANSLATIONS["en"])
