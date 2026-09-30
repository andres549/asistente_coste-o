import * as THREE from 'three';

export function createAnimationController(character, animations, headBone, chestBone, camera) {
  const mixer = new THREE.AnimationMixer(character);
  const actions = {};

  // Mapear clips de animación disponibles
  animations.forEach((clip) => {
    const action = mixer.clipAction(clip);
    actions[clip.name] = action;
  });

  console.log("Animaciones cargadas en el Mixer:", Object.keys(actions));

  let currentAction = actions['Idle'] || Object.values(actions)[0];
  if (currentAction) {
    currentAction.play();
  }

  // Crossfade suave hacia otra animación
  function playAnimation(name, duration = 0.5) {
    const nextAction = actions[name];
    if (!nextAction || nextAction === currentAction) return;

    nextAction.reset();
    nextAction.enabled = true;
    nextAction.setEffectiveTimeScale(1);
    nextAction.setEffectiveWeight(1);
    nextAction.crossFadeFrom(currentAction, duration, true);
    nextAction.play();

    currentAction = nextAction;
  }

  // Reproducir un gesto que luego regresa automáticamente a Idle o Talk
  function playOneShot(name, returnTo = 'Idle', blendTime = 0.5) {
    const action = actions[name];
    if (!action) {
      console.warn(`Animación '${name}' no encontrada, usando 'Talk'.`);
      playAnimation('Talk', blendTime);
      return;
    }

    action.reset();
    action.setLoop(THREE.LoopOnce);
    action.clampWhenFinished = true;
    action.crossFadeFrom(currentAction, blendTime, true);
    action.play();
    currentAction = action;

    const onFinished = (e) => {
      if (e.action === action) {
        mixer.removeEventListener('finished', onFinished);
        playAnimation(returnTo, blendTime);
      }
    };
    mixer.addEventListener('finished', onFinished);
  }

  function update(delta) {
    mixer.update(delta);

    // Micro-atención orgánica del personaje hacia la cámara (suave y sin sobreescribir huesos individuales)
    if (camera && character) {
      const camPos = new THREE.Vector3();
      camera.getWorldPosition(camPos);

      const dx = camPos.x - character.position.x;
      const dz = camPos.z - character.position.z;
      const targetAngleY = Math.atan2(dx, dz);
      const clampedAngleY = THREE.MathUtils.clamp(targetAngleY, -0.28, 0.28);

      character.rotation.y = THREE.MathUtils.lerp(
        character.rotation.y,
        clampedAngleY * 0.35,
        0.04
      );
    }
  }

  return {
    mixer,
    actions,
    playAnimation,
    playOneShot,
    update
  };
}
