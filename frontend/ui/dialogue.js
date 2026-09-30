export function createDialogueUI(bubbleAnchor, camera) {
  const bubbleElement = document.getElementById('dialogue-bubble');
  const headingElement = document.getElementById('bubble-heading');
  const textElement = document.getElementById('dialogue-text');
  const typingIndicator = document.getElementById('typing-indicator');
  const waveformElement = document.getElementById('bubble-waveform');

  let isVisible = false;
  let typingTimer = null;
  let autoHideTimer = null;

  function showBubble(fullText, onComplete, heading) {
    if (typingTimer) {
      clearInterval(typingTimer);
      typingTimer = null;
    }
    if (autoHideTimer) {
      clearTimeout(autoHideTimer);
      autoHideTimer = null;
    }

    isVisible = true;
    if (bubbleElement) {
      bubbleElement.classList.add('visible');
      bubbleElement.classList.add('speaking');
    }
    if (waveformElement) {
      waveformElement.classList.add('active');
    }

    if (heading && headingElement) {
      headingElement.innerHTML = heading;
    }
    if (textElement) textElement.textContent = "";
    if (typingIndicator) typingIndicator.style.display = "inline-block";

    let charIndex = 0;
    const speed = 18;

    typingTimer = setInterval(() => {
      if (charIndex < fullText.length) {
        if (textElement) textElement.textContent += fullText.charAt(charIndex);
        charIndex++;
      } else {
        clearInterval(typingTimer);
        typingTimer = null;
        if (typingIndicator) typingIndicator.style.display = "none";
        if (onComplete) onComplete();
      }
    }, speed);

    // Auto-hide de seguridad si no hay audio o tras terminar la lectura
    const readingDelay = Math.max(5000, fullText.length * 65);
    autoHideTimer = setTimeout(() => {
      hideBubble();
    }, readingDelay);
  }

  function setSpeaking(isSpeaking) {
    if (waveformElement) {
      waveformElement.classList.toggle('active', isSpeaking);
    }
    if (bubbleElement) {
      bubbleElement.classList.toggle('speaking', isSpeaking);
    }

    if (autoHideTimer) {
      clearTimeout(autoHideTimer);
      autoHideTimer = null;
    }

    if (!isSpeaking && isVisible) {
      // El personaje terminó de hablar: esperar 2 segundos y desvanecer la burbuja
      autoHideTimer = setTimeout(() => {
        hideBubble();
      }, 2000);
    }
  }

  function hideBubble() {
    isVisible = false;
    if (bubbleElement) {
      bubbleElement.classList.remove('visible');
      bubbleElement.classList.remove('speaking');
    }
    if (waveformElement) {
      waveformElement.classList.remove('active');
    }
    if (typingTimer) {
      clearInterval(typingTimer);
      typingTimer = null;
    }
    if (autoHideTimer) {
      clearTimeout(autoHideTimer);
      autoHideTimer = null;
    }
  }

  // Permitir cerrar la burbuja haciendo clic en ella
  if (bubbleElement) {
    bubbleElement.addEventListener('click', () => {
      hideBubble();
    });
  }

  function update() {
    // La posición está fijada en CSS
  }

  return {
    showBubble,
    hideBubble,
    setSpeaking,
    update,
    get isVisible() { return isVisible; }
  };
}
