/**
 * Costeño AI - Módulo de Memoria Controlada
 * Almacena y recupera aprendizajes autorizados por el usuario y el historial conversacional.
 */

const fs = require('fs');
const path = require('path');

const MEMORY_FILE = path.join(__dirname, '..', 'data', 'memoria.json');

// Cargar memoria desde disco
function loadMemory() {
  try {
    if (fs.existsSync(MEMORY_FILE)) {
      const raw = fs.readFileSync(MEMORY_FILE, 'utf-8');
      return JSON.parse(raw);
    }
  } catch (err) {
    console.error("Error al leer archivo de memoria:", err);
  }
  
  return {
    personaje: {
      nombre: "Mani Costeño",
      origen: "Barranquilla, Colombia",
      ocupacion: "Asistente Virtual 3D y Anfitrión Caribeño"
    },
    aprendizajes_usuario: [],
    preferencias_usuario: {}
  };
}

// Guardar memoria en disco
function saveMemory(data) {
  try {
    fs.writeFileSync(MEMORY_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch (err) {
    console.error("Error al guardar archivo de memoria:", err);
  }
}

// Agregar nuevo conocimiento autorizado por el usuario
function learnFromUser(fact, source = "Usuario") {
  const memory = loadMemory();
  const newEntry = {
    id: "learn_" + Date.now(),
    informacion: fact.trim(),
    fecha: new Date().toISOString(),
    fuente: source
  };
  memory.aprendizajes_usuario.push(newEntry);
  saveMemory(memory);
  return newEntry;
}

// Buscar en los aprendizajes del usuario por palabras clave
function searchUserLearnings(query) {
  const memory = loadMemory();
  if (!memory.aprendizajes_usuario || memory.aprendizajes_usuario.length === 0) return "";
  
  const tokens = query.toLowerCase()
    .replace(/[¿?¡!.,;:()"]/g, "")
    .split(/\s+/)
    .filter(w => w.length > 2);

  const matched = memory.aprendizajes_usuario.filter(entry => {
    const text = entry.informacion.toLowerCase();
    return tokens.some(token => text.includes(token));
  });

  if (matched.length === 0) return "";
  return matched.map(m => `- ${m.informacion} (Aprendido el ${m.fecha.split('T')[0]})`).join("\n");
}

module.exports = {
  loadMemory,
  saveMemory,
  learnFromUser,
  searchUserLearnings
};
