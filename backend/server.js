/**
 * Costeño AI - Servidor Express Principal
 * Sirve los archivos estáticos (frontend, assets GLB) y expone la API REST para el asistente.
 */

const fs = require('fs');
const path = require('path');

// Cargar variables de entorno desde .env si existe
const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split(/\r?\n/).forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const idx = trimmed.indexOf('=');
      if (idx !== -1) {
        const key = trimmed.substring(0, idx).trim();
        const val = trimmed.substring(idx + 1).trim();
        if (key && !process.env[key]) {
          process.env[key] = val;
        }
      }
    }
  });
}

const express = require('express');
const cors = require('cors');
const { processUserMessage } = require('./ai');
const { loadMemory, learnFromUser } = require('./memory');
const { KNOWLEDGE_BASE } = require('./knowledge');

const app = express();
const PORT = process.env.PORT || 3000;


app.use(cors());
app.use(express.json());

// Servir frontend y assets estáticos
const FRONTEND_DIR = path.join(__dirname, '..', 'frontend');
const ASSETS_DIR = path.join(__dirname, '..', 'assets');

app.use(express.static(FRONTEND_DIR));
app.use('/assets', express.static(ASSETS_DIR));

// Endpoint principal de chat
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: "El campo 'message' es requerido." });
    }

    const aiResponse = await processUserMessage(message);
    res.json(aiResponse);
  } catch (err) {
    console.error("Error en /api/chat:", err);
    res.status(500).json({
      text: "¡Eche mani! Algo se desconectó por un segundo, pero ya me estoy recomponiendo.",
      emotion: "confused",
      gesture: "think",
      animation: "talk"
    });
  }
});

// Endpoint para consultar memoria
app.get('/api/memory', (req, res) => {
  res.json(loadMemory());
});

// Endpoint para enseñar directamente
app.post('/api/teach', (req, res) => {
  const { fact } = req.body;
  if (!fact || fact.length < 3) {
    return res.status(400).json({ error: "El dato a enseñar debe tener al menos 3 caracteres." });
  }
  const entry = learnFromUser(fact, "Panel de Conocimiento");
  res.json({
    success: true,
    message: `¡Aprendido con éxito! "${fact}"`,
    entry
  });
});

// Endpoint para consultar base de conocimiento
app.get('/api/knowledge', (req, res) => {
  res.json(KNOWLEDGE_BASE);
});

// Cargar catálogo de lugares emblemáticos y turísticos
const PLACES_DATA = require('./data/places.json');

// Endpoint para consultar todos los lugares
app.get('/api/places', (req, res) => {
  res.json(PLACES_DATA);
});

// Módulo de Síntesis de Voz con Fish Audio y Respaldo Neural
const { FISH_AUDIO_CONFIG, MOSS_CONFIG, generateSpeech } = require('./tts');

// Endpoint para síntesis de voz con Voice ID
app.get('/api/tts', async (req, res) => {
  const text = req.query.text;
  const voiceId = req.query.voice_id || FISH_AUDIO_CONFIG.voiceId;

  if (!text || text.trim().length === 0) {
    return res.status(400).json({ error: "El parámetro 'text' es requerido." });
  }

  const result = await generateSpeech(text, voiceId);
  if (!result || !result.buffer) {
    return res.status(503).json({
      error: "TTS remoto no disponible o clave de API no configurada.",
      fallback: true,
      voiceId: FISH_AUDIO_CONFIG.voiceId
    });
  }

  res.set({
    'Content-Type': result.format || 'audio/mpeg',
    'Content-Length': result.buffer.length,
    'X-Voice-ID': voiceId,
    'X-TTS-Provider': result.provider || 'unknown'
  });
  res.send(result.buffer);
});

// Endpoint para consultar configuración de voz
app.get('/api/tts/config', (req, res) => {
  res.json({
    provider: 'fish.audio',
    voiceId: FISH_AUDIO_CONFIG.voiceId,
    apiUrl: FISH_AUDIO_CONFIG.apiUrl,
    hasApiKey: Boolean(FISH_AUDIO_CONFIG.apiKey)
  });
});



app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`🌴 Costeño AI - Asistente Virtual 3D de Barranquilla`);
  console.log(`🚀 Servidor ejecutándose en: http://localhost:${PORT}`);
  console.log(`====================================================`);
});
