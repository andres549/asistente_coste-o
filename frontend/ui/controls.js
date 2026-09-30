export function setupUIControls({
  chatManager,
  voiceRecognition,
  gestureManager,
  facialController,
  speechSystem,
  placesDrawer
}) {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const micBtn = document.getElementById('mic-btn');
  const sendBtn = document.getElementById('send-btn');
  const memoryModal = document.getElementById('memory-modal');
  const memoryBtn = document.getElementById('memory-btn');
  const closeMemoryBtn = document.getElementById('close-memory-btn');
  const teachForm = document.getElementById('teach-form');
  const teachInput = document.getElementById('teach-input');
  const memoryList = document.getElementById('memory-list');

  const gesturesBtn = document.getElementById('gestures-btn');
  const gesturesPopup = document.getElementById('gestures-popup');

  const audioBanner = document.getElementById('audio-unlock-banner');
  const closeAudioBanner = document.getElementById('close-audio-banner');

  // Banner de activación por autoplay policy
  if (audioBanner) {
    audioBanner.addEventListener('click', (e) => {
      e.stopPropagation();
      audioBanner.classList.add('hidden');
      speechSystem.unlockAudio();
    });

    if (closeAudioBanner) {
      closeAudioBanner.addEventListener('click', (e) => {
        e.stopPropagation();
        audioBanner.classList.add('hidden');
      });
    }
  }

  // Enviar mensaje desde el formulario inferior
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    speechSystem.unlockAudio();
    if (audioBanner) audioBanner.classList.add('hidden');
    const text = input.value.trim();
    if (text) {
      chatManager.sendMessage(text);
      input.value = '';
    }
  });

  // Botón de micrófono
  if (micBtn) {
    micBtn.addEventListener('click', () => {
      voiceRecognition.toggle();
    });
  }

  // Botón de Destello Mágico (Sparkle)
  const sparkleBtn = document.getElementById('sparkle-btn');
  if (sparkleBtn) {
    sparkleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      speechSystem.unlockAudio();
      if (audioBanner) audioBanner.classList.add('hidden');
      chatManager.sendMessage("¡Epa mani! Cuéntame un dato curioso o plan bien bacano en Barranquilla.");
    });
  }

  // Menú Lateral Flotante Izquierdo (Pills)
  const navPills = document.querySelectorAll('.nav-pill');
  navPills.forEach(pill => {
    pill.addEventListener('click', () => {
      speechSystem.unlockAudio();
      if (audioBanner) audioBanner.classList.add('hidden');

      navPills.forEach(p => p.classList.remove('active-yellow'));
      pill.classList.add('active-yellow');

      const placeId = pill.dataset.place;
      if (placeId && placesDrawer) {
        placesDrawer.toggleDrawer(placeId);
      }

      const query = pill.dataset.query;
      if (query) {
        input.value = query;
        chatManager.sendMessage(query);
        input.value = '';
      }
    });
  });

  // 4 Sub-Píldoras Rápidas debajo del Chat
  const subCategoryPills = document.querySelectorAll('.sub-category-pill');
  subCategoryPills.forEach(pill => {
    pill.addEventListener('click', () => {
      speechSystem.unlockAudio();
      if (audioBanner) audioBanner.classList.add('hidden');

      subCategoryPills.forEach(p => p.classList.remove('active-pill'));
      pill.classList.add('active-pill');

      const placeId = pill.dataset.place;
      if (placeId && placesDrawer) {
        placesDrawer.openDrawer(placeId);
      }

      const query = pill.dataset.query;
      if (query) {
        input.value = query;
        chatManager.sendMessage(query);
        input.value = '';
      }
    });
  });


  // Botón y Barra de Gestos 3D
  if (gesturesBtn && gesturesPopup) {
    gesturesBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      gesturesPopup.classList.toggle('visible');
    });

    document.addEventListener('click', (e) => {
      if (!gesturesPopup.contains(e.target) && e.target !== gesturesBtn) {
        gesturesPopup.classList.remove('visible');
      }
    });
  }

  // Botones de acción dentro del menú de Gestos 3D
  document.querySelectorAll('.test-action-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const action = btn.dataset.action;
      const emo = btn.dataset.emotion;
      if (action) gestureManager.triggerGesture(action, emo);
      else if (emo) facialController.setEmotion(emo, 1.0);
    });
  });

  // Modal de Memoria y Cultura
  async function loadMemoryData() {
    try {
      const res = await fetch('/api/memory');
      const data = await res.json();
      memoryList.innerHTML = '';
      if (data.aprendizajes_usuario && data.aprendizajes_usuario.length > 0) {
        data.aprendizajes_usuario.forEach(item => {
          const li = document.createElement('li');
          li.innerHTML = `<strong>${item.informacion}</strong> <small>(${item.fecha.split('T')[0]})</small>`;
          memoryList.appendChild(li);
        });
      } else {
        memoryList.innerHTML = '<li class="empty">Aún no le has enseñado datos nuevos a Mani. ¡Escribe uno abajo!</li>';
      }
    } catch (err) {
      memoryList.innerHTML = '<li class="error">No se pudo cargar la memoria.</li>';
    }
  }

  if (memoryBtn && memoryModal) {
    memoryBtn.addEventListener('click', () => {
      memoryModal.classList.add('active');
      loadMemoryData();
    });

    closeMemoryBtn.addEventListener('click', () => {
      memoryModal.classList.remove('active');
    });
  }

  if (teachForm) {
    teachForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fact = teachInput.value.trim();
      if (!fact) return;

      try {
        const res = await fetch('/api/teach', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fact })
        });
        await res.json();
        teachInput.value = '';
        loadMemoryData();

        // Notificar al asistente
        chatManager.sendMessage(`Aprende que: ${fact}`);
        memoryModal.classList.remove('active');
      } catch (err) {
        alert("Error al guardar conocimiento.");
      }
    });
  }
}

