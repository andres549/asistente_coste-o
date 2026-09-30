import * as THREE from 'three';

export function setupLighting(scene) {
  // 1. Luz de Hemisferio: Cielo azul caribeño y rebote cálido de adoquines
  const hemiLight = new THREE.HemisphereLight(0xb3e5fc, 0xd7ccc8, 1.2);
  hemiLight.position.set(0, 20, 0);
  scene.add(hemiLight);

  // 2. Sol Tropical Directo (Sol brillante a 45 grados)
  const sunLight = new THREE.DirectionalLight(0xfff8e7, 1.8);
  sunLight.position.set(4, 8, 4);
  sunLight.castShadow = true;

  // Optimización de sombras suaves PCF para abarcar la calle colonial completa
  sunLight.shadow.mapSize.width = 2048;
  sunLight.shadow.mapSize.height = 2048;
  sunLight.shadow.camera.near = 0.5;
  sunLight.shadow.camera.far = 35;
  sunLight.shadow.bias = -0.0003;

  const d = 9.5;
  sunLight.shadow.camera.left = -d;
  sunLight.shadow.camera.right = d;
  sunLight.shadow.camera.top = d;
  sunLight.shadow.camera.bottom = -d;

  scene.add(sunLight);

  // 3. Rim Light (Contraluz azulada sutil para silueta cinematográfica)
  const rimLight = new THREE.DirectionalLight(0x81d4fa, 0.9);
  rimLight.position.set(-3, 4, -4);
  scene.add(rimLight);

  // 4. Luz de relleno frontal para iluminar el rostro y detalles caribeños
  const fillLight = new THREE.DirectionalLight(0xfff3e0, 0.95);
  fillLight.position.set(0, 1.5, 3.2);
  scene.add(fillLight);

  // 5. Luz suave focalizada en el rostro y pecho para resaltar la expresión bajo el sombrero
  const faceLight = new THREE.PointLight(0xfff8e7, 1.2, 4.0, 1.5);
  faceLight.position.set(0, 1.45, 1.2);
  scene.add(faceLight);

  return {
    sunLight,
    hemiLight,
    rimLight,
    fillLight,
    faceLight
  };
}
