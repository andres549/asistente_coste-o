export function createVoiceRecognition(onTranscript, onStart, onEnd) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.warn("Reconocimiento de voz (Web Speech API) no soportado en este navegador.");
    return {
      isSupported: false,
      start: () => alert("Tu navegador no soporta reconocimiento de voz nativo. Por favor escribe tu mensaje en el chat."),
      stop: () => {},
      toggle: () => {}
    };
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'es-CO'; // Dialecto colombiano
  recognition.continuous = false;
  recognition.interimResults = true;

  let isListening = false;

  recognition.onstart = () => {
    isListening = true;
    if (onStart) onStart();
  };

  recognition.onresult = (event) => {
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
    const isFinal = Boolean(finalTranscript);
    if (onTranscript) onTranscript(text, isFinal);
  };

  recognition.onerror = (event) => {
    console.warn("Aviso en reconocimiento de voz:", event.error);
    isListening = false;
    if (onEnd) onEnd();
  };

  recognition.onend = () => {
    isListening = false;
    if (onEnd) onEnd();
  };

  function start() {
    if (!isListening) {
      try {
        recognition.start();
      } catch (err) {
        console.warn("Error al iniciar reconocimiento:", err);
      }
    }
  }

  function stop() {
    if (isListening) {
      recognition.stop();
      isListening = false;
    }
  }

  function toggle() {
    if (isListening) stop();
    else start();
  }

  return {
    isSupported: true,
    start,
    stop,
    toggle,
    get isListening() { return isListening; }
  };
}
