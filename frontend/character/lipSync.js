export function createLipSyncController(facialController) {
  let isSpeaking = false;
  let audioContext = null;
  let analyser = null;
  let dataArray = null;

  // Sincronizador de ritmo silábico basado en texto para SpeechSynthesis
  let textLipSyncInterval = null;

  function initAudioContext() {
    if (!audioContext) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        audioContext = new AudioCtx();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        dataArray = new Uint8Array(analyser.frequencyBinCount);
      }
    }
  }

  // Lip-sync impulsado por análisis de frecuencia FFT en tiempo real
  function updateFromAudio() {
    if (!analyser || !dataArray || !isSpeaking) return;

    analyser.getByteFrequencyData(dataArray);

    let sumLow = 0;
    let sumMid = 0;
    let sumHigh = 0;

    for (let i = 0; i < 8; i++) sumLow += dataArray[i];
    for (let i = 8; i < 24; i++) sumMid += dataArray[i];
    for (let i = 24; i < 64; i++) sumHigh += dataArray[i];

    const lowEnergy = sumLow / (8 * 255);
    const midEnergy = sumMid / (16 * 255);
    const highEnergy = sumHigh / (40 * 255);

    if (midEnergy > 0.15) {
      facialController.setViseme('viseme_aa', midEnergy * 1.3);
    } else {
      facialController.setViseme('viseme_aa', 0);
    }

    if (lowEnergy > 0.25) {
      facialController.setViseme('viseme_O', lowEnergy * 0.9);
    } else {
      facialController.setViseme('viseme_O', 0);
    }

    if (highEnergy > 0.2) {
      facialController.setViseme('viseme_E', highEnergy * 0.8);
      facialController.setViseme('viseme_SS', highEnergy * 0.6);
    } else {
      facialController.setViseme('viseme_E', 0);
      facialController.setViseme('viseme_SS', 0);
    }
  }

  // Cadencia silábica de alta fidelidad para Web Speech API
  function startSpeakingText(text) {
    initAudioContext();
    isSpeaking = true;

    if (textLipSyncInterval) clearInterval(textLipSyncInterval);

    // Mapear vocales del texto para alternar visemas rítmicamente
    const cleanWords = text.toLowerCase().replace(/[^a-záéíóúüñ\s]/gi, '').split(/\s+/);
    let wordIdx = 0;
    let charIdx = 0;

    const visemeMap = {
      'a': 'viseme_aa',
      'á': 'viseme_aa',
      'e': 'viseme_E',
      'é': 'viseme_E',
      'i': 'viseme_I',
      'í': 'viseme_I',
      'o': 'viseme_O',
      'ó': 'viseme_O',
      'u': 'viseme_U',
      'ú': 'viseme_U',
      'p': 'viseme_PP',
      'b': 'viseme_PP',
      'm': 'viseme_PP',
      'f': 'viseme_FF',
      'v': 'viseme_FF',
      's': 'viseme_SS',
      'd': 'viseme_DD',
      't': 'viseme_DD'
    };

    textLipSyncInterval = setInterval(() => {
      if (!isSpeaking) {
        clearInterval(textLipSyncInterval);
        facialController.clearVisemes();
        return;
      }

      const currentWord = cleanWords[wordIdx];
      if (!currentWord) {
        // Pausa entre frases
        facialController.clearVisemes();
        return;
      }

      const char = currentWord[charIdx] || 'a';
      const targetViseme = visemeMap[char] || 'viseme_aa';

      facialController.clearVisemes();
      // Apertura con variación natural
      const weight = 0.65 + Math.random() * 0.35;
      facialController.setViseme(targetViseme, weight);

      charIdx++;
      if (charIdx >= currentWord.length) {
        charIdx = 0;
        wordIdx = (wordIdx + 1) % cleanWords.length;
      }
    }, 110); // ~110ms por fonema, ritmo natural de conversación
  }

  // Conectar elemento de audio HTML5 para análisis FFT de frecuencias en tiempo real (MOSS-TTS)
  function startSpeakingAudio(audioElement) {
    initAudioContext();
    if (audioContext && audioContext.state === 'suspended') {
      audioContext.resume();
    }
    if (audioContext && analyser && !audioElement._connectedToLipSync) {
      try {
        const source = audioContext.createMediaElementSource(audioElement);
        source.connect(analyser);
        analyser.connect(audioContext.destination);
        audioElement._connectedToLipSync = true;
      } catch (err) {
        console.warn("MediaElementSource no pudo conectarse directamente al analyser:", err);
      }
    }
    isSpeaking = true;
  }

  function stopSpeaking() {
    isSpeaking = false;
    if (textLipSyncInterval) {
      clearInterval(textLipSyncInterval);
      textLipSyncInterval = null;
    }
    if (facialController && typeof facialController.clearVisemes === 'function') {
      facialController.clearVisemes();
    }
  }

  function update() {
    if (isSpeaking && analyser) {
      updateFromAudio();
    }
  }

  return {
    initAudioContext,
    startSpeakingText,
    startSpeakingAudio,
    stopSpeaking,
    update,
    get isSpeaking() { return isSpeaking; }
  };
}

