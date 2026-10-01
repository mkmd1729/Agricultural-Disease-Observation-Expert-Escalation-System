"""
Unit and Integration Tests for Multilingual Internationalization (i18n).
Verifies supported languages endpoint, translation dictionaries, and key parity between English and Tamil.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.i18n import TRANSLATIONS, SUPPORTED_LANGUAGES, get_translation_dictionary

client = TestClient(app)


def test_supported_languages_endpoint():
    """Verifies that GET /api/i18n/languages returns supported languages."""
    response = client.get("/api/i18n/languages")
    assert response.status_code == 200
    languages = response.json()
    assert isinstance(languages, list)
    codes = [l["code"] for l in languages]
    assert "en" in codes
    assert "ta" in codes


def test_translation_dictionaries_endpoint():
    """Verifies that GET /api/i18n/en and GET /api/i18n/ta return valid dictionaries."""
    res_en = client.get("/api/i18n/en")
    assert res_en.status_code == 200
    dict_en = res_en.json()
    assert isinstance(dict_en, dict)
    assert len(dict_en) > 50

    res_ta = client.get("/api/i18n/ta")
    assert res_ta.status_code == 200
    dict_ta = res_ta.json()
    assert isinstance(dict_ta, dict)
    assert len(dict_ta) > 50


def test_strict_key_parity_between_english_and_tamil():
    """
    Enforces strict key parity between English and Tamil translation dictionaries.
    Ensures no string is left untranslated or missing in either language.
    """
    en_keys = set(TRANSLATIONS["en"].keys())
    ta_keys = set(TRANSLATIONS["ta"].keys())

    missing_in_ta = en_keys - ta_keys
    missing_in_en = ta_keys - en_keys

    assert len(missing_in_ta) == 0, f"Translation keys missing in Tamil: {missing_in_ta}"
    assert len(missing_in_en) == 0, f"Translation keys missing in English: {missing_in_en}"
    assert en_keys == ta_keys


def test_translation_strings_non_empty():
    """Verifies that all translation values in en and ta are non-empty strings."""
    for lang in ["en", "ta"]:
        d = TRANSLATIONS[lang]
        for key, val in d.items():
            assert isinstance(val, str), f"Key '{key}' in lang '{lang}' is not a string."
            assert len(val.strip()) > 0, f"Key '{key}' in lang '{lang}' is empty."


def test_essential_domain_keys_present():
    """Verifies that key agricultural concepts and disclaimers are present."""
    required_keys = [
        "app_title",
        "nav_farmer",
        "nav_officer",
        "nav_expert",
        "nav_regional",
        "nav_tracking",
        "field_crop",
        "field_stage",
        "field_symptoms",
        "crop_tomato",
        "crop_rice",
        "sym_leaf_spots",
        "sym_wilting",
        "env_rainfall",
        "env_humidity",
        "voice_read_instructions",
        "voice_start_dictation",
        "ai_hypothesis_disclaimer",
        "location_privacy_notice",
        "track_case_heading",
        "regional_heading"
    ]
    for key in required_keys:
        assert key in TRANSLATIONS["en"], f"Missing essential key in en: {key}"
        assert key in TRANSLATIONS["ta"], f"Missing essential key in ta: {key}"


def test_fallback_on_unsupported_language():
    """Verifies that requesting an unsupported language falls back cleanly to English."""
    dict_fallback = get_translation_dictionary("fr")
    assert dict_fallback == TRANSLATIONS["en"]
