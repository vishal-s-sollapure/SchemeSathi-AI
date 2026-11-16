import { LanguageCode } from '../types';

// Browser Web Speech Recognition interface definitions for TypeScript
interface IWindow extends Window {
  webkitSpeechRecognition?: any;
  SpeechRecognition?: any;
}

export interface VoiceRecognitionState {
  isSupported: boolean;
  isListening: boolean;
  transcript: string;
  errorMessage: string | null;
}

export interface VoiceSynthesisState {
  isSupported: boolean;
  isSpeaking: boolean;
  isPaused: boolean;
}

export class BrowserVoiceAssistant {
  private recognition: any = null;
  private isRecognitionSupported: boolean = false;
  private isSynthesisSupported: boolean = false;

  constructor() {
    const win = typeof window !== 'undefined' ? (window as unknown as IWindow) : null;
    const SpeechRecognition = win?.SpeechRecognition || win?.webkitSpeechRecognition;

    if (SpeechRecognition) {
      this.isRecognitionSupported = true;
      try {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;
      } catch (e) {
        console.warn('SpeechRecognition initialization error:', e);
        this.isRecognitionSupported = false;
      }
    }

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.isSynthesisSupported = true;
    }
  }

  public getRecognitionSupport(): boolean {
    return this.isRecognitionSupported;
  }

  public getSynthesisSupport(): boolean {
    return this.isSynthesisSupported;
  }

  /**
   * Maps application language code to BCP 47 standard language tag for speech recognition & synthesis.
   */
  public getLocaleTag(lang: LanguageCode): string {
    switch (lang) {
      case 'kn':
        return 'kn-IN';
      case 'hi':
        return 'hi-IN';
      case 'te':
        return 'te-IN';
      case 'ta':
        return 'ta-IN';
      case 'mr':
        return 'mr-IN';
      case 'en':
      default:
        return 'en-IN';
    }
  }

  /**
   * Starts speech-to-text recognition in the target language.
   */
  public startListening(
    language: LanguageCode,
    onResult: (transcript: string, isFinal: boolean) => void,
    onError: (errorMsg: string) => void,
    onEnd: () => void
  ): boolean {
    if (!this.isRecognitionSupported || !this.recognition) {
      onError('Speech recognition is not supported in this browser. Please type your query in the text box.');
      return false;
    }

    try {
      this.recognition.lang = this.getLocaleTag(language);

      this.recognition.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        const text = finalTranscript || interimTranscript;
        if (text) {
          onResult(text.trim(), Boolean(finalTranscript));
        }
      };

      this.recognition.onerror = (event: any) => {
        let msg = 'Voice recognition error occurred.';
        if (event.error === 'not-allowed') {
          msg = 'Microphone permission was denied. Please grant microphone access in your browser or type your question below.';
        } else if (event.error === 'no-speech') {
          msg = 'No speech was detected. Please try speaking closer to the microphone.';
        } else if (event.error === 'network') {
          msg = 'Network connection required for speech recognition. Please check your connection or use text input.';
        } else if (event.error === 'audio-capture') {
          msg = 'No microphone was found or microphone is currently busy. Please check audio devices.';
        }
        onError(msg);
      };

      this.recognition.onend = () => {
        onEnd();
      };

      this.recognition.start();
      return true;
    } catch (err: any) {
      console.warn('Failed to start speech recognition:', err);
      onError('Failed to initiate microphone. Please type your query.');
      onEnd();
      return false;
    }
  }

  /**
   * Stops active speech recognition
   */
  public stopListening(): void {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch {
        // Safe ignore if already stopped
      }
    }
  }

  /**
   * Speaks out response text using Web SpeechSynthesis in the target language
   */
  public speak(
    text: string,
    language: LanguageCode,
    onStart?: () => void,
    onEnd?: () => void,
    onError?: (errorMsg: string) => void
  ): boolean {
    if (!this.isSynthesisSupported || typeof window === 'undefined') {
      if (onError) onError('Speech synthesis is not supported in this browser.');
      return false;
    }

    try {
      window.speechSynthesis.cancel(); // Stop any pending speech

      // Clean markdown symbols (e.g. *, #, _) for fluent natural narration
      const cleanText = text
        .replace(/[*_#`~[\]]/g, ' ')
        .replace(/\(http[^)]+\)/g, '')
        .replace(/\s+/g, ' ')
        .trim();

      if (!cleanText) return false;

      const utterance = new SpeechSynthesisUtterance(cleanText);
      const targetLocale = this.getLocaleTag(language);
      utterance.lang = targetLocale;
      utterance.rate = 0.95; // Slightly measured rate for civic clarity
      utterance.pitch = 1.0;

      // Select matching native voice if available
      const voices = window.speechSynthesis.getVoices();
      const matchedVoice = voices.find(v => v.lang.toLowerCase().startsWith(language.toLowerCase()) || v.lang === targetLocale);
      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }

      utterance.onstart = () => {
        if (onStart) onStart();
      };

      utterance.onend = () => {
        if (onEnd) onEnd();
      };

      utterance.onerror = (e) => {
        console.warn('SpeechSynthesis error:', e);
        if (onEnd) onEnd();
        if (onError) onError('Speech playback encountered an error.');
      };

      window.speechSynthesis.speak(utterance);
      return true;
    } catch (err: any) {
      console.warn('Failed to execute speak:', err);
      if (onError) onError('Speech playback failed.');
      if (onEnd) onEnd();
      return false;
    }
  }

  /**
   * Cancels active speech playback
   */
  public stopSpeaking(): void {
    if (this.isSynthesisSupported && typeof window !== 'undefined') {
      try {
        window.speechSynthesis.cancel();
      } catch {
        // Safe ignore
      }
    }
  }

  /**
   * Pauses active speech playback
   */
  public pauseSpeaking(): void {
    if (this.isSynthesisSupported && typeof window !== 'undefined') {
      try {
        window.speechSynthesis.pause();
      } catch {
        // Safe ignore
      }
    }
  }

  /**
   * Resumes paused speech playback
   */
  public resumeSpeaking(): void {
    if (this.isSynthesisSupported && typeof window !== 'undefined') {
      try {
        window.speechSynthesis.resume();
      } catch {
        // Safe ignore
      }
    }
  }
}

export const voiceAssistant = new BrowserVoiceAssistant();
