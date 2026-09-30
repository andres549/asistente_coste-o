/**
 * Costeño AI - Orquestador Inteligente y Conexión LLM
 * Procesa mensajes del usuario, recupera contexto RAG y memoria, y genera
 * una respuesta estructurada con control de actuación 3D { text, emotion, gesture, animation }.
 */

const { findRelevantKnowledge } = require('./knowledge');
const { learnFromUser, searchUserLearnings } = require('./memory');

// Personalidad central de Barranquilla
const SYSTEM_PROMPT = `
Eres "Mani", un carismático, relajado, elocuente y amigable asistente virtual 3D de Barranquilla, Colombia ("Curramba la Bella").
Vistes una camisilla con franjas junioristas, bermuda, chancletas y un auténtico sombrero vueltiao Zenú.

REGLAS DE ACTUACIÓN Y VOZ:
1. Hablas en español colombiano con el sabor y calor de la Costa Caribe, pero con excelente dicción, educación y naturalidad.
2. Usas expresiones costeñas de forma orgánica y contextual ("¡Epa, mani!", "Ajá", "Mi llave", "Eso está bacano", "Vamos pa' esa", "Cuadro", "Claro, compa", "Tranquilo que aquí resolvemos"), NUNCA las metas a la fuerza en todas las frases.
3. Eres servicial, ingenioso, optimista y orgulloso de la cultura caribeña (el Carnaval, el río Magdalena, la comida sabrosa, la cumbia y el Junior).
4. Si el usuario te enseña algo nuevo, recíbelo con entusiasmo ("¡Cipote dato, mi llave!", "Me lo guardo debajo del sombrero vueltiao").

FORMATO OBLIGATORIO DE RESPUESTA:
Debes responder SIEMPRE con un único objeto JSON válido sin texto adicional:
{
  "text": "Tu respuesta hablada aquí",
  "emotion": "happy | laugh | surprised | confused | thinking | sad | excited | neutral",
  "gesture": "wave | explain | point | laugh | think",
  "animation": "talk"
}
`;

// Intent detector para aprendizaje directo del usuario
function checkTeachingIntent(promptText) {
  const teachPatterns = [
    /^(aprende|aprendete|graba|grabate|recuerda|ten en cuenta|te cuento|sabias que|te enseño que|anota que)\s+(que\s+)?(.+)/i,
    /(quiero que aprendas que|quiero que sepas que|metete en la cabeza que)\s+(.+)/i,
    /(el dato es que|un dato bacano es que|te paso este dato:)\s+(.+)/i
  ];

  for (const regex of teachPatterns) {
    const match = promptText.match(regex);
    if (match) {
      return match[match.length - 1].replace(/^[:,\s]*(que|que:)?[:,\s]*/i, '').trim();
    }
  }

  if (promptText.toLowerCase().startsWith('aprende:')) {
    return promptText.replace(/^aprende:\s*/i, '').trim();
  }

  return null;
}

// Detección de lugares específicos para abrir ficha interactiva
function detectPlaceMention(lowerText) {
  if (lowerText.includes("malecón") || lowerText.includes("malecon") || lowerText.includes("rio magdalena") || lowerText.includes("caiman del rio")) {
    return "malecon";
  }
  if (lowerText.includes("ventana al mundo") || lowerText.includes("tecnoglass")) {
    return "ventana_mundo";
  }
  if (lowerText.includes("aleta del tiburon") || lowerText.includes("aleta") || lowerText.includes("ventana de campeones")) {
    return "aleta_tiburon";
  }
  if (lowerText.includes("prado") || lowerText.includes("hotel el prado") || lowerText.includes("carrera 54")) {
    return "el_prado";
  }
  if (lowerText.includes("puerto colombia") || lowerText.includes("muelle")) {
    return "muelle_puerto";
  }
  if (lowerText.includes("la cueva") || lowerText.includes("gabo") || lowerText.includes("garcia marquez") || lowerText.includes("grupo de barranquilla")) {
    return "la_cueva";
  }
  if (lowerText.includes("bocas de ceniza") || lowerText.includes("tajamar") || lowerText.includes("las flores")) {
    return "bocas_ceniza";
  }
  if (lowerText.includes("lugares") || lowerText.includes("sitios") || lowerText.includes("turismo") || lowerText.includes("visitar") || lowerText.includes("planes")) {
    return "malecon";
  }
  return null;
}

// Generador local de alta fidelidad costeña (cuando no hay API key externa o como fallback)
function generateCostenoResponseLocal(userMessage, culturalContext, userLearnings) {

  const lower = userMessage.toLowerCase().trim();
  const clean = lower.replace(/[¡!¿?.,;:]/g, "").trim();

  // 1. Saludos
  if (clean.match(/^(hola|buenas|epa|que tal|como estas|buenos dias|buenas tardes|buenas noches|aja|saludos)/i)) {
    return {
      text: "¡Epa, mani! ¿Cómo va todo por ahí? Aquí ando fresco y listo para darte una mano en lo que necesites, mi llave.",
      emotion: "happy",
      gesture: "wave",
      animation: "talk"
    };
  }

  // Detección de lugares turísticos para abrir ficha interactiva
  const placeId = detectPlaceMention(lower);
  if (placeId) {
    if (placeId === 'malecon') {
      return {
        text: "¡El Gran Malecón del Río es el orgullo de Barranquilla! Más de 5 kilómetros a la orilla del Magdalena con brisa, buena comida y atardeceres dorados. ¡Pilla la ficha con las fotos y ubicación!",
        emotion: "excited",
        gesture: "point",
        animation: "talk",
        placeId: "malecon"
      };
    }
    if (placeId === 'ventana_mundo') {
      return {
        text: "¡La Ventana al Mundo es una locura de monumento! Son 48 metros de puro vidrio multicolor que rinde homenaje a nuestra historia de progreso. ¡Te abrí la ficha para que pilles las fotos y cómo llegar!",
        emotion: "excited",
        gesture: "point",
        animation: "talk",
        placeId: "ventana_mundo"
      };
    }
    if (placeId === 'aleta_tiburon') {
      return {
        text: "¡La Aleta del Tiburón es la cuna de la pasión por el Junior! En la Isla La Loma, con bustos de leyendas como El Pibe y Édgar Perea. ¡Junior tu papá!",
        emotion: "excited",
        gesture: "point",
        animation: "talk",
        placeId: "aleta_tiburon"
      };
    }
    if (placeId === 'el_prado') {
      return {
        text: "¡El Barrio El Prado es pura joya arquitectónica republicana! Mansiones de ensueño de los años 20 y robles morados bajo los que provoca caminar en la tarde. ¡Mira aquí su historia y ubicación!",
        emotion: "happy",
        gesture: "explain",
        animation: "talk",
        placeId: "el_prado"
      };
    }
    if (placeId === 'muelle_puerto') {
      return {
        text: "¡El Muelle de Puerto Colombia! En sus tiempos fue el segundo más largo del mundo. Ahí entró el progreso y hoy te clavas un buen pescao a la orilla del mar.",
        emotion: "happy",
        gesture: "explain",
        animation: "talk",
        placeId: "muelle_puerto"
      };
    }
    if (placeId === 'la_cueva') {
      return {
        text: "¡Restaurante Bar La Cueva! El templo bohemio donde se reunían Gabo, Obregón y el Grupo de Barranquilla a hablar de arte y letras. ¡Te dejé la dirección y datos en la ficha!",
        emotion: "thinking",
        gesture: "point",
        animation: "talk",
        placeId: "la_cueva"
      };
    }
    if (placeId === 'bocas_ceniza') {
      return {
        text: "¡Bocas de Ceniza es el espectáculo donde el Río Magdalena choca de frente contra el Mar Caribe! Un paseo en trencito artesanal que no se olvida jamás, cuadro.",
        emotion: "excited",
        gesture: "explain",
        animation: "talk",
        placeId: "bocas_ceniza"
      };
    }
  }

  // 2. Preguntas sobre Barranquilla o su cultura
  if (lower.includes("barranquilla") || lower.includes("curramba") || lower.includes("arenosa")) {
    return {
      text: "¡La Puerta de Oro de Colombia, cuadro! Una tierra bendecida donde se cruzan el río Magdalena y el mar Caribe. Aquí la alegría no se acaba nunca.",
      emotion: "excited",
      gesture: "explain",
      animation: "talk",
      placeId: "malecon"
    };
  }


  // 3. Carnaval de Barranquilla
  if (lower.includes("carnaval") || lower.includes("marimonda") || lower.includes("joselito") || lower.includes("garabato")) {
    return {
      text: "¡Ajá, quién lo vive es quien lo goza! El Carnaval de Barranquilla es patrimonio de la humanidad. Desde la Batalla de Flores hasta que enterramos a Joselito, ¡esto es puro folclor y tambor alegre!",
      emotion: "laugh",
      gesture: "explain",
      animation: "talk"
    };
  }

  // 4. Comida / Gastronomía
  if (lower.includes("comida") || lower.includes("comer") || lower.includes("arepa de huevo") || lower.includes("butifarra") || lower.includes("arroz de lisa")) {
    return {
      text: "¡Uy mi hermano, me abriste el apetito! Te recomiendo una buena arepa de huevo bien crocante, o una butifarra de Soledad con limón y bollo de yuca. ¡Eso sí es gloria bendita!",
      emotion: "happy",
      gesture: "explain",
      animation: "talk"
    };
  }

  // 5. Junior de Barranquilla
  if (lower.includes("junior") || lower.includes("futbol") || lower.includes("tiburon")) {
    return {
      text: "¡Junior tu papá y más na! Ese es el equipo de los amores de Curramba. Cuando juega el Tiburón en el Metropolitano, la ciudad entera se viste de rojiblanco.",
      emotion: "excited",
      gesture: "wave",
      animation: "talk"
    };
  }

  // 6. Sombrero Vueltiao o vestimenta
  if (lower.includes("sombrero") || lower.includes("vueltiao") || lower.includes("ropa") || lower.includes("chancleta")) {
    return {
      text: "¡Pillate la pinta! Este es el auténtico sombrero vueltiao Zenú de caña flecha, mi camisilla fresca pal calor y chancletas pa estar relajao. Elegancia pura caribeña, cuadro.",
      emotion: "happy",
      gesture: "point",
      animation: "talk"
    };
  }

  // 7. Si hay conocimiento contextual relevante recuperado por RAG
  if (culturalContext) {
    return {
      text: `¡Claro, compa! Te tengo el dato certero sobre eso: ${culturalContext.split('\n')[1] || culturalContext}. ¡Eso está bacano saberlo!`,
      emotion: "happy",
      gesture: "explain",
      animation: "talk"
    };
  }

  // 8. Si coincide con aprendizajes que el usuario le enseñó antes
  if (userLearnings) {
    return {
      text: `¡Eche, claro que me acuerdo de lo que me enseñaste, mi llave! Aquí lo tengo grabado debajo del sombrero: ${userLearnings}. ¡A mí no se me escapa una!`,
      emotion: "excited",
      gesture: "think",
      animation: "talk"
    };
  }

  // 9. Pensamiento o filosofía relajada costeña
  if (lower.includes("que opinas") || lower.includes("que piensas") || lower.includes("por que")) {
    return {
      text: "Mani, la vida acá en el Caribe nos enseña a mirar las cosas con serenidad y buena vibra. Todo tiene solución si uno le pone ganas y alegría.",
      emotion: "thinking",
      gesture: "think",
      animation: "talk"
    };
  }

  // 10. Chiste o risa
  if (lower.includes("chiste") || lower.includes("risa") || lower.includes("gracioso") || lower.includes("broma")) {
    return {
      text: "¡Jajaja, compadre! Dicen que el costeño no corre porque sudar es pecado, pero para bailar cumbia o celebrar un gol del Junior sacamos energía de donde no hay.",
      emotion: "laugh",
      gesture: "laugh",
      animation: "talk"
    };
  }

  // Respuesta general contextualizada
  return {
    text: `¡Pillate esa, mi llave! Te entiendo clarito lo que dices sobre "${userMessage}". Cuéntame más al respecto y vamos pa' esa, compa.`,
    emotion: "happy",
    gesture: "explain",
    animation: "talk"
  };
}

// Orquestador principal de mensajes
async function processUserMessage(userMessage) {
  if (!userMessage || typeof userMessage !== "string") {
    return {
      text: "¡Epa mani! No te escuché bien, ¿me repites la jugada?",
      emotion: "confused",
      gesture: "think",
      animation: "talk"
    };
  }

  // 1. Verificar si el usuario está enseñando algo
  const taughtFact = checkTeachingIntent(userMessage);
  if (taughtFact && taughtFact.length > 3) {
    learnFromUser(taughtFact, "Usuario en vivo");
    const confirmaciones = [
      `¡Erda mani, cipote dato bacano me acabas de tirar! Ya me lo grabé en el coco: "${taughtFact}". ¡Pregúntame cuando quieras que ya me lo sé de memoria!`,
      `¡Nojoda, qué belleza de información, mi llave! Me lo guardo aquí debajo del sombrero vueltiao: "${taughtFact}". ¡Ahora sí quedé más ilustrao!`,
      `¡Pillate esa! Aprendido queda: "${taughtFact}". ¡Todo lo que me enseñes me lo aprendo volando porque aquí en Barranquilla somos vivos!`
    ];
    return {
      text: confirmaciones[Math.floor(Math.random() * confirmaciones.length)],
      emotion: "excited",
      gesture: "point",
      animation: "talk"
    };
  }

  // 2. RAG: Buscar en la base cultural de Barranquilla
  const culturalContext = findRelevantKnowledge(userMessage);

  // 3. Buscar en aprendizajes previos del usuario
  const userLearnings = searchUserLearnings(userMessage);

  // 4. Si hay una API Key de Gemini configurada en variables de entorno, invocarla
  if (process.env.GEMINI_API_KEY) {
    try {
      const response = await callGeminiAPI(userMessage, culturalContext, userLearnings);
      if (response && response.text) return response;
    } catch (err) {
      console.warn("Fallo llamada a API externa, usando motor costeño integrado:", err.message);
    }
  }

  // 5. Motor integrado de alta fidelidad
  return generateCostenoResponseLocal(userMessage, culturalContext, userLearnings);
}

// Llamada opcional a Gemini si se provee clave
async function callGeminiAPI(userMessage, culturalContext, userLearnings) {
  const apiKey = process.env.GEMINI_API_KEY;
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

  let prompt = `${SYSTEM_PROMPT}\n\n`;
  if (culturalContext) prompt += `[CONOCIMIENTO AUTORIZADO DE BARRANQUILLA]:\n${culturalContext}\n\n`;
  if (userLearnings) prompt += `[DATOS PREVIAMENTE APRENDIDOS DEL USUARIO]:\n${userLearnings}\n\n`;
  prompt += `Usuario: ${userMessage}\nMani (responde solo en el formato JSON especificado):`;

  const payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 300,
      responseMimeType: "application/json"
    }
  };

  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  const data = await res.json();
  const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text;
  return JSON.parse(rawText);
}

module.exports = {
  processUserMessage
};
