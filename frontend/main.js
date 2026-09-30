import * as THREE from 'three';
import { createScene } from './three/scene.js';
import { createCamera } from './three/camera.js';
import { setupLighting } from './three/lighting.js';
import { createRenderer } from './three/renderer.js';

import { loadCharacterAndEnvironment } from './character/character.js?v=2.2';
import { createAnimationController } from './character/animation.js?v=2.2';
import { createFacialController } from './character/facial.js?v=2.2';
import { createGestureManager } from './character/gestures.js?v=2.2';
import { createLipSyncController } from './character/lipSync.js?v=2.2';

import { createDialogueUI } from './ui/dialogue.js?v=2.2';
import { createSpeechSystem } from './chat/speech.js?v=2.2';
import { createVoiceRecognition } from './chat/voice.js?v=2.2';
import { createChatManager } from './chat/chat.js?v=2.2';
import { setupUIControls } from './ui/controls.js?v=2.2';
import { createPlacesDrawer } from './ui/placesDrawer.js?v=2.2';

async function init() {

  const canvas = document.getElementById('webgl-canvas');
  const loadingOverlay = document.getElementById('loading-overlay');
  const loadingText = document.getElementById('loading-text');

  try {
    loadingText.textContent = "Preparando escenario caribeño...";

    // 1. Inicializar Three.js Core
    const scene = createScene();
    const cameraController = createCamera(canvas);
    setupLighting(scene);
    const renderer = createRenderer(canvas);

    loadingText.textContent = "Cargando personaje 3D y animaciones...";

    // 2. Cargar Mallas y Esqueleto
    const charData = await loadCharacterAndEnvironment(scene);

    loadingText.textContent = "Configurando controladores de animación y voz...";

    // 3. Controladores del Personaje
    const animationController = createAnimationController(
      charData.character,
      charData.animations,
      charData.headBone,
      charData.chestBone,
      cameraController.camera
    );

    const facialController = createFacialController(charData.headMesh);
    const gestureManager = createGestureManager(animationController, facialController);
    const lipSyncController = createLipSyncController(facialController);

    // 4. UI y Diálogo 3D
    const dialogueUI = createDialogueUI(charData.bubbleAnchor, cameraController.camera);

    // 5. Sistema de Voz y Reconocimiento
    const speechSystem = createSpeechSystem(
      lipSyncController,
      () => {
        // En habla
        gestureManager.setSpeakingState(true);
        animationController.playAnimation('Talk', 0.45);
        dialogueUI.setSpeaking(true);
      },
      () => {
        // Fin de habla
        gestureManager.setSpeakingState(false);
        dialogueUI.setSpeaking(false);
      }
    );

    const micBtn = document.getElementById('mic-btn');
    const voiceRecognition = createVoiceRecognition(
      (transcript, isFinal) => {
        const input = document.getElementById('chat-input');
        input.value = transcript;
        if (isFinal) {
          chatManager.sendMessage(transcript);
          input.value = '';
        }
      },
      () => {
        micBtn.classList.add('recording');
        micBtn.title = "Escuchando... Haz clic para detener";
      },
      () => {
        micBtn.classList.remove('recording');
        micBtn.title = "Hablar por micrófono";
      }
    );

    // 6. Panel Deslizable de Fichas de Sitios (Drawer)
    let chatManagerRef = null;
    const placesDrawer = createPlacesDrawer({
      get chatManager() { return chatManagerRef; },
      gestureManager,
      speechSystem
    });

    // 7. Gestor de Chat
    const chatManager = createChatManager({
      dialogueUI,
      gestureManager,
      speechSystem,
      cameraController,
      placesDrawer,
      onStateChange: (state) => {
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
          sendBtn.disabled = state.isProcessing;
          sendBtn.style.opacity = state.isProcessing ? '0.6' : '1';
        }
      }
    });
    chatManagerRef = chatManager;

    // 8. Enlazar eventos de UI
    setupUIControls({
      chatManager,
      voiceRecognition,
      gestureManager,
      facialController,
      speechSystem,
      placesDrawer
    });


    // 8. Ocultar pantalla de carga con transición suave
    loadingOverlay.classList.add('fade-out');
    setTimeout(() => {
      loadingOverlay.style.display = 'none';
      // Saludo inicial caribeño
      setTimeout(() => {
        gestureManager.triggerGesture('wave', 'happy');
        const audioBanner = document.getElementById('audio-unlock-banner');
        if (speechSystem.isUnlocked && audioBanner) {
          audioBanner.classList.add('hidden');
        }
        dialogueUI.showBubble("¡Epa, mani! Te muestro los mejores lugares de Barranquilla y sus alrededores. Playas, parques, monumentos, zonas turísticas y más. 🌴");
        speechSystem.speak("¡Epa, mani! Soy tu llave en Curramba la Bella. Pregúntame por planes en la ciudad, dónde clavarte un sancocho de guandú bien bacano, o la historia del Carnaval.", () => {
          gestureManager.returnToIdle();
          dialogueUI.setSpeaking(false);
        });
      }, 700);
    }, 600);

    // 9. Loop de Renderizado en Tiempo Real
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const delta = clock.getDelta();

      // Actualizar cámara
      cameraController.update();

      // Actualizar controladores del personaje
      animationController.update(delta);
      facialController.update(delta);
      lipSyncController.update();

      // Proyectar burbuja flotante 3D sobre la cabeza
      dialogueUI.update();

      // Renderizar frame
      renderer.render(scene, cameraController.camera);
    }

    animate();

  } catch (err) {
    console.error("Error crítico durante la inicialización:", err);
    loadingText.textContent = "Error al iniciar la experiencia 3D: " + err.message;
  }
}

// Iniciar aplicación al cargar el DOM
window.addEventListener('DOMContentLoaded', init);
