import * as THREE from 'three';

export function createScene() {
  const scene = new THREE.Scene();

  // Cargar imagen de fondo del patio colonial de Barranquilla (idéntico al mockup)
  const textureLoader = new THREE.TextureLoader();
  textureLoader.load('/assets/courtyard_bg.jpg', (texture) => {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.generateMipmaps = true;
    texture.minFilter = THREE.LinearMipmapLinearFilter;
    scene.background = texture;
  });

  // Plano receptor de sombras suave para asentar al personaje sobre el suelo empedrado
  const shadowPlaneGeo = new THREE.PlaneGeometry(16, 16);
  const shadowPlaneMat = new THREE.ShadowMaterial({
    opacity: 0.42,
    transparent: true
  });
  const shadowPlane = new THREE.Mesh(shadowPlaneGeo, shadowPlaneMat);
  shadowPlane.rotation.x = -Math.PI / 2;
  shadowPlane.position.y = 0;
  shadowPlane.receiveShadow = true;
  scene.add(shadowPlane);

  return scene;
}

