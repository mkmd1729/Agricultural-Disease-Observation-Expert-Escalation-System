/**
 * Internationalization (i18n) Controller for Agricultural Disease Observation.
 * Handles English and Tamil language switching, DOM string replacement,
 * and user input preservation across language changes.
 */

class I18nController {
  constructor() {
    this.currentLanguage = localStorage.getItem('app_language') || 'en';
    this.translations = (typeof TRANSLATIONS !== 'undefined') ? TRANSLATIONS : { en: {}, ta: {} };
    this.init();
  }

  init() {
    document.addEventListener('DOMContentLoaded', () => {
      this.bindSelector();
      this.updateDOM();
    });
  }

  bindSelector() {
    const selector = document.getElementById('language-select');
    if (selector) {
      selector.value = this.currentLanguage;
      selector.addEventListener('change', (e) => {
        this.setLanguage(e.target.value);
      });
    }
  }

  getLanguage() {
    return this.currentLanguage;
  }

  setLanguage(lang) {
    if (!this.translations[lang]) {
      console.warn(`[i18n] Language '${lang}' not loaded, falling back to 'en'.`);
      lang = 'en';
    }
    this.currentLanguage = lang;
    localStorage.setItem('app_language', lang);
    document.documentElement.lang = lang;

    const selector = document.getElementById('language-select');
    if (selector && selector.value !== lang) {
      selector.value = lang;
    }

    this.updateDOM();
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
  }

  t(key, fallback = '') {
    const dict = this.translations[this.currentLanguage] || this.translations['en'] || {};
    if (dict[key] !== undefined) {
      return dict[key];
    }
    // Try English fallback
    const enDict = this.translations['en'] || {};
    if (enDict[key] !== undefined) {
      return enDict[key];
    }
    return fallback || key;
  }

  /**
   * Updates all DOM elements with data-i18n attributes.
   * GUARANTEE: Never alters or wipes farmer form input values (value of input or textarea).
   */
  updateDOM() {
    // 1. Standard text content
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach((el) => {
      const tag = el.tagName.toUpperCase();
      // Skip overwriting user form inputs
      if (tag === 'INPUT' || tag === 'TEXTAREA') {
        return;
      }
      const key = el.getAttribute('data-i18n');
      const translated = this.t(key);
      if (translated) {
        el.textContent = translated;
      }
    });

    // 2. Placeholders
    const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
    placeholders.forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      const translated = this.t(key);
      if (translated) {
        el.setAttribute('placeholder', translated);
      }
    });

    // 3. Titles / tooltips
    const titles = document.querySelectorAll('[data-i18n-title]');
    titles.forEach((el) => {
      const key = el.getAttribute('data-i18n-title');
      const translated = this.t(key);
      if (translated) {
        el.setAttribute('title', translated);
      }
    });

    // 4. Aria labels
    const ariaLabels = document.querySelectorAll('[data-i18n-aria-label]');
    ariaLabels.forEach((el) => {
      const key = el.getAttribute('data-i18n-aria-label');
      const translated = this.t(key);
      if (translated) {
        el.setAttribute('aria-label', translated);
      }
    });
  }
}

// Global instance
window.I18n = new I18nController();
