/**
 * Costeño AI - Sistema de Voz, Reproducción y Sincronización Labial
 * Motor Primario: Fish Audio MP3 (Voz Clonada con Voice ID 48ba9bbe768c4607956eae49b00c7bee)
 * Motor Secundario: Voz Neural Colombiana (es-CO-GonzaloNeural)
 * Motor Terciario: Web SpeechSynthesis API nativa del navegador
 */

export function createSpeechSystem(lipSyncController, onSpeechStart, onSpeechEnd) {
  const VOICE_ID = '48ba9bbe768c4607956eae49b00c7bee';
  const synth = window.speechSynthesis;

  let preferredVoice = null;
  let isMuted = false;
  let isAudioUnlocked = false;
  let pendingSpeech = null;
  let currentAudio = null;
  let isPlaying = false;

  // Cargar voces del navegador para fallback
  function loadVoices() {
    if (!synth) return null;
    const voices = synth.getVoices();
    if (!voices || voices.length === 0) return null;

    let selected = voices.find(v => v.lang.toLowerCase() === 'es-co' || v.lang.toLowerCase() === 'es_co');
    if (!selected) selected = voices.find(v => v.lang.toLowerCase() === 'es-419' || v.lang.toLowerCase() === 'es_419');
    if (!selected) selected = voices.find(v => ['es-mx', 'es-us', 'es-cl', 'es-ar', 'es-pe'].includes(v.lang.toLowerCase()));
    if (!selected) selected = voices.find(v => v.lang.toLowerCase().startsWith('es'));
    if (!selected) selected = voices.find(v => v.name.toLowerCase().includes('spanish') || v.name.toLowerCase().includes('español'));
    if (!selected) selected = voices.find(v => v.default) || voices[0] || null;

    preferredVoice = selected;
    return preferredVoice;
  }

  if (synth) {
    loadVoices();
    if (synth.onvoiceschanged !== undefined) {
      synth.onvoiceschanged = () => loadVoices();
    }
  }

  /**
   * Desbloquea el audio del navegador ante la primera interacción del usuario
   */
  function unlockAudio() {
    if (isAudioUnlocked) return;
    isAudioUnlocked = true;

    // Desbloquear AudioContext
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        const ctx = new AudioCtx();
        if (ctx.state === 'suspended') ctx.resume();
      }
    } catch (e) {}

    // Desbloquear SpeechSynthesis
    try {
      if (synth && synth.paused) synth.resume();
    } catch (e) {}

    const banner = document.getElementById('audio-unlock-banner');
    if (banner) banner.classList.add('hidden');

    console.log("🔊 Canal de audio desbloqueado exitosamente.");

    // Reproducir la locución pendiente si existía
    if (pendingSpeech && !isPlaying) {
      const p = pendingSpeech;
      pendingSpeech = null;
      speak(p.text, p.callback);
    }
  }

  // Escuchar cualquier interacción en la ventana para desbloquear el audio
  const unlockEvents = ['click', 'touchstart', 'pointerdown', 'keydown'];
  const onGlobalInteract = () => {
    unlockAudio();
    unlockEvents.forEach(evt => window.removeEventListener(evt, onGlobalInteract, true));
  };
  unlockEvents.forEach(evt => window.addEventListener(evt, onGlobalInteract, { capture: true, once: true }));

  function stop() {
    isPlaying = false;
    try {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.onplay = null;
        currentAudio.onended = null;
        currentAudio.onerror = null;
        currentAudio = null;
      }
      if (synth && (synth.speaking || synth.pending)) {
        synth.cancel();
      }
      if (lipSyncController && typeof lipSyncController.stopSpeaking === 'function') {
        lipSyncController.stopSpeaking();
      }
      if (onSpeechEnd) onSpeechEnd();
    } catch (err) {
      console.warn("Advertencia en stop():", err);
    }
  }

  /**
   * Reproduce voz a partir de texto (Fish Audio / Neural / Fallback)
   */
  async function speak(text, callback) {
    if (!text || !text.trim()) return;

    if (isMuted) {
      if (callback) callback();
      return;
    }

    // Si aún no ha habido interacción del usuario, guardar locución en espera y mostrar banner
    if (!isAudioUnlocked) {
      pendingSpeech = { text, callback };
      const banner = document.getElementById('audio-unlock-banner');
      if (banner) banner.classList.remove('hidden');
      console.log("ℹ️ Audio guardado en cola en espera del primer clic del usuario.");
      return;
    }

    stop();
    isPlaying = true;

    // 1. Intentar reproducir el MP3 del servidor (Fish Audio con nuevo modelo entrenado)
    try {
      const audioUrl = `/api/tts?text=${encodeURIComponent(text)}&voice_id=${encodeURIComponent(VOICE_ID)}&_t=${Date.now()}`;
      const audio = new Audio(audioUrl);
      currentAudio = audio;
      audio.volume = 1.0;

      audio.onplay = () => {
        console.log("🔊 Audio sonando:", text.slice(0, 35) + "...");
        lipSyncController.startSpeakingText(text);
        if (onSpeechStart) onSpeechStart();
      };

      audio.onended = () => {
        console.log("✅ Audio completado.");
        isPlaying = false;
        currentAudio = null;
        lipSyncController.stopSpeaking();
        if (onSpeechEnd) onSpeechEnd();
        if (callback) callback();
      };

      audio.onerror = (e) => {
        console.warn("⚠️ Audio element error, activando síntesis de respaldo:", e);
        isPlaying = false;
        currentAudio = null;
        speakFallback(text, callback);
      };

      await audio.play();
      return;
    } catch (err) {
      console.warn("⚠️ Error en audio.play(), activando síntesis de respaldo:", err.message);
      isPlaying = false;
      currentAudio = null;
      speakFallback(text, callback);
    }
  }

  function speakFallback(text, callback) {
    if (!synth) {
      lipSyncController.startSpeakingText(text);
      if (onSpeechStart) onSpeechStart();
      setTimeout(() => {
        lipSyncController.stopSpeaking();
        if (onSpeechEnd) onSpeechEnd();
        if (callback) callback();
      }, Math.max(text.length * 65, 2000));
      return;
    }

    if (!preferredVoice) loadVoices();

    if (synth.speaking || synth.pending) {
      synth.cancel();
    }

    setTimeout(() => {
      if (synth.paused) synth.resume();

      const utterance = new SpeechSynthesisUtterance(text);
      if (preferredVoice) {
        utterance.voice = preferredVoice;
        utterance.lang = preferredVoice.lang;
      } else {
        utterance.lang = 'es-CO';
      }

      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      let finished = false;
      const finish = () => {
        if (finished) return;
        finished = true;
        isPlaying = false;
        lipSyncController.stopSpeaking();
        if (onSpeechEnd) onSpeechEnd();
        if (callback) callback();
      };

      utterance.onstart = () => {
        isPlaying = true;
        lipSyncController.startSpeakingText(text);
        if (onSpeechStart) onSpeechStart();
      };

      utterance.onend = finish;
      utterance.onerror = finish;

      try {
        synth.speak(utterance);
        synth.resume();
      } catch (e) {
        finish();
      }
    }, 50);
  }

  function toggleMute() {
    isMuted = !isMuted;
    if (isMuted) stop();
    return isMuted;
  }

  function testVoice() {
    isMuted = false;
    unlockAudio();
    speak("¡Epa, mani! Todo nítido con el sonido en Curramba la Bella.");
  }

  return {
    speak,
    stop,
    loadVoices,
    unlockAudio,
    toggleMute,
    testVoice,
    get isMuted() { return isMuted; },
    get isUnlocked() { return isAudioUnlocked; },
    get isSpeaking() { return isPlaying; },
    voiceId: VOICE_ID
  };
}
