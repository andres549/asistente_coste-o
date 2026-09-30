/**
 * Costeño AI - Controlador del Panel Detallado de Lugares Turísticos (Place Inspector)
 * Muestra fotografía principal con favoritos/compartir, badges, 3 stats, galería de fotos,
 * mapa interactivo con enlace a Google Maps y tarjetas de lugares cercanos interactivos.
 */

export function createPlacesDrawer({ chatManager, gestureManager, speechSystem }) {
  const panel = document.getElementById('place-detail-panel');

  const heroImg = document.getElementById('panel-hero-img');
  const favBtn = document.getElementById('fav-btn');
  const shareBtn = document.getElementById('share-btn');
  const locText = document.getElementById('panel-location-text');
  const statusBadge = document.getElementById('panel-status-badge');
  const placeTitle = document.getElementById('panel-place-title');
  const placeDesc = document.getElementById('panel-place-description');

  const galleryGrid = document.getElementById('panel-gallery-grid');
  const viewAllBtn = document.getElementById('view-all-photos-btn');

  const mapName = document.getElementById('panel-map-name');
  const mapSub = document.getElementById('panel-map-sub');
  const mapsBtn = document.getElementById('panel-maps-btn');

  const nearbyRow = document.getElementById('nearby-places-row');
  const closeBtn = document.getElementById('close-place-panel-btn');
  const launcherBtn = document.getElementById('open-place-panel-pill');

  let placesData = [];
  let currentPlaceId = 'malecon';
  let isFavorite = false;

  // 1. Cargar datos del catálogo
  async function loadPlaces() {
    try {
      const res = await fetch('/api/places');
      placesData = await res.json();
      if (placesData.length > 0) {
        setPlace('malecon', false);
      }
    } catch (err) {
      console.error('Error cargando catálogo de lugares:', err);
    }
  }

  // 2. Establecer el lugar visible en el panel
  function setPlace(id, animateMani = true) {
    const place = placesData.find(p => p.id === id);
    if (!place) return;

    currentPlaceId = place.id;

    // Actualizar campos principales
    if (heroImg) {
      heroImg.src = place.image;
      heroImg.alt = place.name;
    }

    if (locText) locText.textContent = place.locationLabel || 'Barranquilla, Colombia';
    if (statusBadge) statusBadge.textContent = place.badge || '⭐ Imperdible';
    if (placeTitle) placeTitle.textContent = place.name;
    if (placeDesc) placeDesc.textContent = place.shortDescription || place.description;

    // Actualizar las 3 estadísticas
    const stats = place.stats || [
      { icon: '🏃', value: '5+ km', label: 'De extensión' },
      { icon: '🕒', value: 'Abierto', label: 'Todo el día' },
      { icon: '📍', value: 'Av. del Río', label: 'Sector Puerta de Oro' }
    ];

    stats.forEach((st, idx) => {
      const iconEl = document.getElementById(`stat-icon-${idx}`);
      const valEl = document.getElementById(`stat-val-${idx}`);
      const lblEl = document.getElementById(`stat-lbl-${idx}`);
      if (iconEl) iconEl.textContent = st.icon;
      if (valEl) valEl.textContent = st.value;
      if (lblEl) lblEl.textContent = st.label;
    });

    // Galería de 4 fotos
    if (galleryGrid) {
      galleryGrid.innerHTML = '';
      const galleryPhotos = place.gallery || [place.image];
      galleryPhotos.slice(0, 4).forEach((imgSrc, i) => {
        const thumb = document.createElement('div');
        thumb.className = `gallery-thumb ${imgSrc === place.image ? 'active' : ''}`;
        thumb.style.backgroundImage = `url('${imgSrc}')`;
        thumb.title = `Foto ${i + 1} de ${place.name}`;

        thumb.addEventListener('click', () => {
          if (heroImg) {
            heroImg.src = imgSrc;
            document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
            thumb.classList.add('active');
          }
        });

        galleryGrid.appendChild(thumb);
      });
    }

    // Mapa y Google Maps
    if (mapName) mapName.textContent = place.locationName || place.name;
    if (mapSub) mapSub.textContent = place.locationSub || 'Barranquilla, Atlántico';
    if (mapsBtn) mapsBtn.href = place.mapsUrl || `https://maps.google.com/?q=${encodeURIComponent(place.name + ' Barranquilla')}`;

    // Lugares Cercanos
    if (nearbyRow) {
      nearbyRow.innerHTML = '';
      const nearbyList = place.nearbyPlaces || [];
      nearbyList.forEach(nb => {
        const card = document.createElement('div');
        card.className = 'nearby-card';
        card.innerHTML = `
          <div class="nearby-img" style="background-image: url('${nb.image}')"></div>
          <div class="nearby-info">
            <span class="nearby-name">${nb.name}</span>
            <span class="nearby-dist">📍 ${nb.distance}</span>
          </div>
        `;

        card.addEventListener('click', () => {
          setPlace(nb.id, true);
          if (chatManager) {
            chatManager.sendMessage(`Háblame de ${nb.name}`);
          }
        });

        nearbyRow.appendChild(card);
      });
    }

    // Sincronizar gesture de Mani
    if (animateMani && gestureManager) {
      gestureManager.triggerGesture('point', 'excited');
    }
  }

  // Botón de Favoritos
  if (favBtn) {
    favBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      isFavorite = !isFavorite;
      favBtn.classList.toggle('active', isFavorite);
      favBtn.innerHTML = isFavorite
        ? `<svg viewBox="0 0 24 24" width="18" height="18" fill="#ef4444"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>`
        : `<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>`;
    });
  }

  // Botón de Compartir
  if (shareBtn) {
    shareBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const place = placesData.find(p => p.id === currentPlaceId);
      const textToShare = `¡Pilla este lugar en Barranquilla con Costeño AI! ${place ? place.name : 'Gran Malecón'}: ${window.location.href}`;
      if (navigator.share) {
        try {
          await navigator.share({ title: 'Costeño AI', text: textToShare, url: window.location.href });
        } catch (err) {}
      } else if (navigator.clipboard) {
        await navigator.clipboard.writeText(textToShare);
        alert('¡Enlace del lugar copiado al portapapeles!');
      }
    });
  }

  // Ver todas las fotos
  if (viewAllBtn) {
    viewAllBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const place = placesData.find(p => p.id === currentPlaceId);
      if (place && chatManager) {
        chatManager.sendMessage(`Muéstrame fotos de ${place.name}`);
      }
    });
  }

  // Eventos de botones de abrir y cerrar
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeDrawer();
    });
  }

  if (launcherBtn) {
    launcherBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openDrawer(currentPlaceId);
    });
  }

  // Abrir y Cerrar panel
  function openDrawer(placeId = null) {
    if (placeId) {
      setPlace(placeId, true);
    }
    if (panel) {
      panel.classList.add('visible');
    }
    if (launcherBtn) {
      launcherBtn.classList.remove('launcher-active');
    }

    // Resaltar píldora de Lugares en el menú
    const lugaresNav = document.querySelector('.nav-pill[data-category="lugares"]');
    if (lugaresNav) lugaresNav.classList.add('active-yellow');

    if (gestureManager) {
      gestureManager.triggerGesture('explain', 'happy');
    }
  }

  function closeDrawer() {
    if (panel) {
      panel.classList.remove('visible');
    }
    if (launcherBtn) {
      launcherBtn.classList.add('launcher-active');
    }

    // Quitar resaltado de píldora de Lugares al cerrar
    const lugaresNav = document.querySelector('.nav-pill[data-category="lugares"]');
    if (lugaresNav) lugaresNav.classList.remove('active-yellow');
  }

  function toggleDrawer(placeId = null) {
    if (panel && panel.classList.contains('visible')) {
      closeDrawer();
    } else {
      openDrawer(placeId || currentPlaceId);
    }
  }

  // Inicializar carga de datos
  loadPlaces();

  return {
    openDrawer,
    closeDrawer,
    toggleDrawer,
    setPlace,
    get isOpen() {
      return panel && panel.classList.contains('visible');
    }
  };
}
