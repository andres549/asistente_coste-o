import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export async function loadCharacterAndEnvironment(scene) {
  const loader = new GLTFLoader();

  // 1. Cargar Personaje Costeño (El patio colonial se renderiza como fondo de escena)
  console.log("Cargando personaje costeño...");
  const charGltf = await loader.loadAsync('/assets/character.glb');
  const character = charGltf.scene;


  let headMesh = null;
  let headBone = null;
  let chestBone = null;
  let morphTargetDictionary = {};

  character.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;

      // Detectar malla con Shape Keys (Mesh_Head)
      if (child.morphTargetDictionary && Object.keys(child.morphTargetDictionary).length > 0) {
        headMesh = child;
        morphTargetDictionary = child.morphTargetDictionary;
      }

      // Optimizar materiales PBR
      if (child.material) {
        child.material.side = THREE.DoubleSide;
        if (child.material.name.includes("Skin")) {
          child.material.roughness = 0.5;
        }
      }
    }

    if (child.isBone) {
      if (child.name === "Head" || child.name === "mixamorig:Head") headBone = child;
      if (child.name === "Chest" || child.name === "mixamorig:Spine2" || child.name === "mixamorig:Spine1") chestBone = child;
    }
  });

  // Si no se detectó directamente por nombre en traverses, buscar en armature
  if (!headBone) {
    headBone = character.getObjectByName("Head") || character.getObjectByName("mixamorig:Head");
  }
  if (!chestBone) {
    chestBone = character.getObjectByName("Chest") || character.getObjectByName("mixamorig:Spine2");
  }

  // Anchor para la burbuja de diálogo flotante (offset sobre el sombrero vueltiao)
  const bubbleAnchor = new THREE.Object3D();
  bubbleAnchor.position.set(0, 0.38, 0);
  if (headBone) {
    headBone.add(bubbleAnchor);
  } else {
    bubbleAnchor.position.set(0, 2.05, 0);
    character.add(bubbleAnchor);
  }

  scene.add(character);

  return {
    character,
    animations: charGltf.animations,
    headMesh,
    headBone,
    chestBone,
    bubbleAnchor,
    morphTargetDictionary
  };
}
