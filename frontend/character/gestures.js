export function createGestureManager(animationController, facialController) {
  let isSpeaking = false;

  function setSpeakingState(speaking) {
    isSpeaking = speaking;
  }

  function triggerGesture(gestureName, emotionName = null) {
    if (emotionName && facialController) {
      facialController.setEmotion(emotionName, 1.0);
    }

    const returnAnim = isSpeaking ? 'Talk' : 'Idle';

    switch (gestureName ? gestureName.toLowerCase() : 'talk') {
      case 'wave':
        animationController.playOneShot('Wave', returnAnim, 0.45);
        break;
      case 'explain':
        animationController.playOneShot('Explain', returnAnim, 0.5);
        break;
      case 'point':
        animationController.playOneShot('Explain', returnAnim, 0.45);
        break;
      case 'laugh':
        animationController.playOneShot('Laugh', returnAnim, 0.5);
        break;
      case 'talk':
        animationController.playAnimation('Talk', 0.45);
        break;
      case 'think':
        animationController.playOneShot('Explain', returnAnim, 0.45);
        if (facialController) facialController.setEmotion('thinking', 1.0);
        break;
      default:
        animationController.playAnimation(returnAnim, 0.5);
        break;
    }
  }

  function returnToIdle() {
    isSpeaking = false;
    animationController.playAnimation('Idle', 0.6);
    if (facialController) {
      facialController.setEmotion('neutral');
    }
  }

  return {
    triggerGesture,
    returnToIdle,
    setSpeakingState
  };
}
