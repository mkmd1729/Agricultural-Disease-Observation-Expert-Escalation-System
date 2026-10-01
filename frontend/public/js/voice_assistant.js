/**
 * Voice & Audio Assistance Module for Agricultural Disease Observation.
 * Provides accessible Web Speech Text-to-Speech (TTS) and Speech-to-Text (STT) dictation
 * in Tamil (ta-IN) and Indian English (en-IN).
 * Designed with transparent status feedback and graceful browser fallbacks.
 */

class VoiceAssistant {
  constructor() {
    this.synth = window.speechSynthesis || null;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    this.recognition = SpeechRecognition ? new SpeechRecognition() : null;
    this.isListening = false;
    this.isSpeaking = false;
    this.currentTargetInput = null;

    this.init();
  }

  init() {
    if (this.recognition) {
      this.recognition.continuous = false;
      this.recognition.interimResults = false;

      this.recognition.onstart = () => {
        this.isListening = true;
        this.updateVoiceStatus('listening', window.I18n ? window.I18n.t('voice_listening') : 'Listening... Speak now.');
        this.updateMicButtonUI(true);
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (this.currentTargetInput) {
          const currentVal = this.currentTargetInput.value;
          this.currentTargetInput.value = currentVal ? `${currentVal} ${transcript}` : transcript;
          // Trigger input event so any listeners update
          this.currentTargetInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
        this.updateVoiceStatus('ready', `Transcribed: "${transcript}"`);
      };

      this.recognition.onerror = (event) => {
        console.warn('[VoiceAssistant] Speech recognition error:', event.error);
        this.isListening = false;
        this.updateMicButtonUI(false);
        let msg = 'Voice recognition error.';
        if (event.error === 'not-allowed') {
          msg = 'Microphone permission denied. Manual keyboard input remains active.';
        } else if (event.error === 'no-speech') {
          msg = 'No speech detected. Please try speaking again.';
        }
        this.updateVoiceStatus('error', msg);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.updateMicButtonUI(false);
      };
    }
  }

  getLangCode() {
    const lang = window.I18n ? window.I18n.getLanguage() : 'en';
    return lang === 'ta' ? 'ta-IN' : 'en-IN';
  }

  speak(text) {
    if (!this.synth) {
      this.updateVoiceStatus('error', window.I18n ? window.I18n.t('voice_not_supported') : 'Speech synthesis not supported in this browser.');
      return;
    }
    // Stop any ongoing speech
    this.stop();

    const utterance = new SpeechSynthesisUtterance(text);
    const targetLang = this.getLangCode();
    utterance.lang = targetLang;
    utterance.rate = 0.95; // Slightly slower for clarity in field conditions

    // Attempt to pick a native voice for the selected language if available
    const voices = this.synth.getVoices();
    const matchingVoice = voices.find(v => v.lang === targetLang || v.lang.startsWith(targetLang.split('-')[0]));
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.updateVoiceStatus('speaking', 'Playing audio...');
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.updateVoiceStatus('ready', '');
    };

    utterance.onerror = (e) => {
      console.warn('[VoiceAssistant] Speech error:', e);
      this.isSpeaking = false;
      this.updateVoiceStatus('ready', '');
    };

    this.synth.speak(utterance);
  }

  readCurrentStep() {
    const activeStepEl = document.querySelector('.wizard-step.active, .step-panel:not([style*="display: none"])');
    if (!activeStepEl) {
      this.speak(window.I18n ? window.I18n.t('app_title') : 'Agricultural Disease Observation');
      return;
    }
    // Collect visible text instructions
    const heading = activeStepEl.querySelector('h3, h4')?.textContent || '';
    const desc = activeStepEl.querySelector('p')?.textContent || '';
    const textToRead = `${heading}. ${desc}`.trim();
    if (textToRead) {
      this.speak(textToRead);
    }
  }

  startDictation(targetElementId) {
    if (!this.recognition) {
      const msg = window.I18n ? window.I18n.t('voice_not_supported') : 'Speech recognition is not supported in this browser.';
      this.updateVoiceStatus('error', msg);
      return;
    }

    this.currentTargetInput = document.getElementById(targetElementId);

    if (this.isListening) {
      this.recognition.stop();
      this.isListening = false;
      this.updateMicButtonUI(false);
      return;
    }

    try {
      this.recognition.lang = this.getLangCode();
      this.recognition.start();
    } catch (err) {
      console.warn('[VoiceAssistant] Recognition start error:', err);
    }
  }

  stop() {
    if (this.synth && this.synth.speaking) {
      this.synth.cancel();
      this.isSpeaking = false;
    }
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
    this.updateMicButtonUI(false);
    this.updateVoiceStatus('ready', '');
  }

  updateVoiceStatus(state, message) {
    const statusEl = document.getElementById('voice-status-feedback');
    if (statusEl) {
      statusEl.textContent = message;
      statusEl.className = `voice-status-pill ${state}`;
      statusEl.style.display = message ? 'inline-block' : 'none';
    }
  }

  updateMicButtonUI(isListening) {
    const micBtns = document.querySelectorAll('.voice-dictate-btn');
    micBtns.forEach(btn => {
      if (isListening) {
        btn.classList.add('recording');
        btn.setAttribute('aria-pressed', 'true');
      } else {
        btn.classList.remove('recording');
        btn.setAttribute('aria-pressed', 'false');
      }
    });
  }
}

// Global instance
window.VoiceAssistant = new VoiceAssistant();
