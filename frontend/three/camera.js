import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function createCamera(canvas) {
  const camera = new THREE.PerspectiveCamera(
    40,
    window.innerWidth / window.innerHeight,
    0.1,
    100
  );

  // Posición encuadrando medio cuerpo con el personaje ligeramente a la izquierda (mockup idéntico)
  camera.position.set(0.18, 1.38, 3.2);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0.18, 1.14, 0);

  // Límites para evitar atravesar el suelo o alejarse demasiado
  controls.maxPolarAngle = Math.PI / 2 - 0.04;
  controls.minDistance = 1.2;
  controls.maxDistance = 7.0;

  // Estado de zoom cinemático conversacional
  let isTalkingMode = false;
  const normalPos = new THREE.Vector3(0.18, 1.38, 3.2);
  const normalTarget = new THREE.Vector3(0.18, 1.14, 0);
  const talkPos = new THREE.Vector3(0.12, 1.42, 2.5);
  const talkTarget = new THREE.Vector3(0.08, 1.28, 0);

  function setConversationalZoom(active) {
    isTalkingMode = active;
  }

  function update() {
    controls.update();

    const targetP = isTalkingMode ? talkPos : normalPos;
    const targetT = isTalkingMode ? talkTarget : normalTarget;

    if (isTalkingMode) {
      camera.position.lerp(targetP, 0.03);
      controls.target.lerp(targetT, 0.03);
    }
  }

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
  }

  window.addEventListener('resize', onResize);

  return {
    camera,
    controls,
    update,
    setConversationalZoom
  };
}

