/**
 * Costeño AI - Módulo de Síntesis de Voz (TTS)
 * Soporta:
 * 1. Fish Audio (Ultra-alta fidelidad con clonación de voz por Voice ID / Reference ID)
 *    API Key: sk-fish-hGvjJrtgRSQqLc1w3pVIz9hBG6zqt8WperHCTk6dloQ
 *    Voice ID: 1eb7f28e0ad9458081214a0bf3ff76a7
 * 2. Motor Neural Colombiano (es-CO-GonzaloNeural) garantizado como respaldo de alta calidad
 * 3. Caché local persistente en assets/audio_cache/ para máxima velocidad y cero latencia
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { MsEdgeTTS, OUTPUT_FORMAT } = require('msedge-tts');

// Cargar variables de entorno de .env
const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const idx = trimmed.indexOf('=');
      if (idx !== -1) {
        const key = trimmed.slice(0, idx).trim();
        const val = trimmed.slice(idx + 1).trim();
        if (!process.env[key]) process.env[key] = val;
      }
    }
  });
}

// Configuración de Fish Audio (Proveedor Primario)
const FISH_AUDIO_CONFIG = {
  apiKey: process.env.FISH_AUDIO_API_KEY || 'sk-fish-hGvjJrtgRSQqLc1w3pVIz9hBG6zqt8WperHCTk6dloQ',
  voiceId: process.env.FISH_AUDIO_VOICE_ID || '48ba9bbe768c4607956eae49b00c7bee',
  apiUrl: process.env.FISH_AUDIO_API_URL || 'https://api.fish.audio/v1/tts',
  model: process.env.FISH_AUDIO_MODEL || 's2.1-pro-free'
};

// Configuración de MOSS / MOSI de respaldo
const MOSS_CONFIG = {
  voiceId: process.env.MOSS_VOICE_ID || FISH_AUDIO_CONFIG.voiceId,
  apiUrl: process.env.MOSS_API_URL || 'https://api.mosi.ai/v1/audio/speech',
  apiKey: process.env.MOSI_API_KEY || process.env.MOSS_API_KEY || '',
  model: process.env.MOSS_MODEL || 'moss-tts'
};

const CACHE_DIR = path.join(__dirname, '..', 'assets', 'audio_cache');
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

function getCachePath(text, voiceId) {
  const hash = crypto.createHash('md5').update(text + '_' + voiceId).digest('hex');
  return path.join(CACHE_DIR, hash + '.mp3');
}

/**
 * Genera audio mediante la API de Fish Audio
 */
async function generateFishAudioTTS(text, voiceId) {
  const apiKey = FISH_AUDIO_CONFIG.apiKey;
  const refId = voiceId || FISH_AUDIO_CONFIG.voiceId;
  if (!apiKey || !refId) return null;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const response = await fetch(FISH_AUDIO_CONFIG.apiUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'model': FISH_AUDIO_CONFIG.model
      },
      body: JSON.stringify({
        text: text,
        reference_id: refId,
        format: 'mp3',
        latency: 'normal'
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const arrayBuffer = await response.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      console.log(`🐟 Audio generado exitosamente con Fish Audio (${buffer.length} bytes, voice: ${refId})`);
      return buffer;
    } else {
      const errBody = await response.text();
      console.warn(`⚠️ Fish Audio API HTTP ${response.status}:`, errBody);
    }
  } catch (err) {
    clearTimeout(timeoutId);
    console.warn('⚠️ Error conectando con Fish Audio API:', err.message);
  }
  return null;
}

/**
 * Genera audio neural colombiano de alta fidelidad con MsEdgeTTS (es-CO-GonzaloNeural)
 */
async function generateNeuralTTS(text) {
  const tts = new MsEdgeTTS();
  await tts.setMetadata('es-CO-GonzaloNeural', OUTPUT_FORMAT.AUDIO_24KHZ_48KBITRATE_MONO_MP3);

  const hash = crypto.createHash('md5').update(text + '_neural').digest('hex');
  const tempDir = path.join(CACHE_DIR, 'tmp_' + hash);
  fs.mkdirSync(tempDir, { recursive: true });

  try {
    await tts.toFile(tempDir, text);
    const audioPath = path.join(tempDir, 'audio.mp3');
    if (fs.existsSync(audioPath)) {
      const buffer = fs.readFileSync(audioPath);
      try {
        fs.unlinkSync(audioPath);
        fs.rmdirSync(tempDir);
      } catch (e) {}
      return buffer;
    }
  } catch (err) {
    console.warn('Fallo en Neural TTS:', err.message);
    try {
      if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
    } catch (e) {}
  }
  return null;
}

/**
 * Sintetiza audio a partir de texto usando Fish Audio con fallback Neural Colombiano.
 * Retorna { buffer, format: 'audio/mpeg', fromCache: boolean, provider: string }
 */
async function generateSpeech(text, customVoiceId = null) {
  const voiceId = customVoiceId || FISH_AUDIO_CONFIG.voiceId;
  const cacheFile = getCachePath(text, voiceId);

  // 1. Revisar caché local persistente
  if (fs.existsSync(cacheFile)) {
    return { buffer: fs.readFileSync(cacheFile), format: 'audio/mpeg', fromCache: true, provider: 'cache' };
  }

  // 2. Intentar Fish Audio TTS con la clave y Voice ID proporcionados
  try {
    const fishBuffer = await generateFishAudioTTS(text, voiceId);
    if (fishBuffer && fishBuffer.length > 0) {
      try { fs.writeFileSync(cacheFile, fishBuffer); } catch (e) {}
      return { buffer: fishBuffer, format: 'audio/mpeg', fromCache: false, provider: 'fish.audio' };
    }
  } catch (err) {
    console.warn('Error en llamada a Fish Audio:', err.message);
  }

  // 3. Respaldo garantizado de alta fidelidad: Motor Neural Colombiano (es-CO-GonzaloNeural)
  try {
    const neuralBuffer = await generateNeuralTTS(text);
    if (neuralBuffer && neuralBuffer.length > 0) {
      try { fs.writeFileSync(cacheFile, neuralBuffer); } catch (e) {}
      return { buffer: neuralBuffer, format: 'audio/mpeg', fromCache: false, provider: 'neural-colombia' };
    }
  } catch (err) {
    console.error('Error generando audio neural de respaldo:', err);
  }

  return null;
}

module.exports = {
  FISH_AUDIO_CONFIG,
  MOSS_CONFIG,
  generateSpeech
};
