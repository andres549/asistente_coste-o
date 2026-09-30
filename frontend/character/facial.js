import * as THREE from 'three';

export function createFacialController(headMesh) {
  if (!headMesh || !headMesh.morphTargetDictionary || !headMesh.morphTargetInfluences) {
    console.warn("Malla facial o morph targets no encontrados.");
    return {
      setEmotion: () => {},
      setViseme: () => {},
      clearVisemes: () => {},
      update: () => {}
    };
  }

  const dict = headMesh.morphTargetDictionary;
  const influences = headMesh.morphTargetInfluences;

  // Objetivos de peso actuales y deseados para interpolación suave (lerp)
  const currentWeights = {};
  const targetWeights = {};

  // Inicializar todos los morph targets a 0
  for (const name in dict) {
    currentWeights[name] = 0;
    targetWeights[name] = 0;
  }

  // Lista de emociones mutuamente excluyentes (para resetear las anteriores al cambiar)
  const EMOTIONS = ['happy', 'laugh', 'surprised', 'confused', 'thinking', 'sad', 'excited'];

  function setEmotion(emotionName, intensity = 1.0) {
    // Apagar emociones previas
    for (const emo of EMOTIONS) {
      if (dict[emo] !== undefined) {
        targetWeights[emo] = 0;
      }
    }

    if (emotionName && emotionName !== 'neutral' && dict[emotionName] !== undefined) {
      targetWeights[emotionName] = Math.min(Math.max(intensity, 0), 1.0);
    }
  }

  function setViseme(visemeName, weight = 1.0) {
    if (dict[visemeName] !== undefined) {
      targetWeights[visemeName] = Math.min(Math.max(weight, 0), 1.0);
    }
  }

  function clearVisemes() {
    for (const name in dict) {
      if (name.startsWith('viseme_')) {
        targetWeights[name] = 0;
      }
    }
  }

  // Sistema de Parpadeo Natural Periódico (Microgesto autónomo)
  let blinkTimer = 0;
  let nextBlinkTime = 3.0 + Math.random() * 2.5; // Entre 3 y 5.5 segundos
  let isBlinking = false;
  let blinkProgress = 0;

  function update(delta) {
    // 1. Manejo del ciclo biológico de parpadeo
    blinkTimer += delta;
    if (!isBlinking && blinkTimer >= nextBlinkTime) {
      isBlinking = true;
      blinkProgress = 0;
      blinkTimer = 0;
      nextBlinkTime = 2.8 + Math.random() * 2.8;
    }

    if (isBlinking) {
      blinkProgress += delta * 7.5; // Duración ~130ms
      if (blinkProgress >= Math.PI) {
        isBlinking = false;
        if (dict['blink_L'] !== undefined) targetWeights['blink_L'] = 0;
        if (dict['blink_R'] !== undefined) targetWeights['blink_R'] = 0;
      } else {
        const blinkVal = Math.sin(blinkProgress);
        if (dict['blink_L'] !== undefined) targetWeights['blink_L'] = blinkVal;
        if (dict['blink_R'] !== undefined) targetWeights['blink_R'] = blinkVal;
      }
    }

    // 2. Interpolación suave de pesos hacia los targets
    const lerpSpeed = 12.0 * delta;
    for (const name in dict) {
      const idx = dict[name];
      const target = targetWeights[name] || 0;
      currentWeights[name] = THREE.MathUtils.lerp(currentWeights[name], target, Math.min(lerpSpeed, 1.0));
      influences[idx] = currentWeights[name];
    }
  }

  return {
    setEmotion,
    setViseme,
    clearVisemes,
    update
  };
}
