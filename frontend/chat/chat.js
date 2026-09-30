export function createChatManager({
  dialogueUI,
  gestureManager,
  speechSystem,
  cameraController,
  placesDrawer,
  onStateChange
}) {
  let isProcessing = false;

  async function sendMessage(userText) {
    if (!userText || !userText.trim() || isProcessing) return;

    isProcessing = true;
    if (onStateChange) onStateChange({ isProcessing: true, userText });

    try {
      // 1. Enviar al backend
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
      });

      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();

      console.log("Respuesta estructurada recibida de la IA:", data);

      // 2. Acercamiento cinemático de cámara al hablar
      if (cameraController) {
        cameraController.setConversationalZoom(true);
      }

      // 3. Activar gestos y emoción
      gestureManager.triggerGesture(data.gesture || 'explain', data.emotion || 'happy');

      // 3.1 Si la respuesta detectó un lugar emblemático, abrir su ficha interactiva
      if (data.placeId && placesDrawer) {
        placesDrawer.openDrawer(data.placeId);
      }

      // 4. Mostrar burbuja flotante 3D
      dialogueUI.showBubble(data.text);


      // 5. Reproducir voz y sincronizar labios
      speechSystem.speak(data.text, () => {
        // Al terminar de hablar:
        setTimeout(() => {
          dialogueUI.hideBubble();
          gestureManager.returnToIdle();
          if (cameraController) {
            cameraController.setConversationalZoom(false);
          }
        }, 1800);
      });

      if (onStateChange) onStateChange({ isProcessing: false, response: data });
    } catch (err) {
      console.error("Error al procesar mensaje con la IA:", err);
      dialogueUI.showBubble("¡Eche mani! Se me fue la onda un momento. Vuelve a preguntarme.");
      gestureManager.triggerGesture('think', 'confused');
      setTimeout(() => {
        dialogueUI.hideBubble();
        gestureManager.returnToIdle();
        if (cameraController) cameraController.setConversationalZoom(false);
      }, 3000);
      if (onStateChange) onStateChange({ isProcessing: false, error: err });
    } finally {
      isProcessing = false;
    }
  }

  return {
    sendMessage,
    get isProcessing() { return isProcessing; }
  };
}
