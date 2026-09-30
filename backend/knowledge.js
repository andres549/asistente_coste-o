/**
 * Costeño AI - Base de Conocimiento Cultural y RAG
 * Información auténtica sobre Barranquilla, su cultura, gastronomía, música y lugares emblemáticos.
 */

const KNOWLEDGE_BASE = [
  {
    id: "barranquilla_general",
    tema: "Generalidades de Barranquilla",
    tags: ["barranquilla", "curramba", "arenosa", "puerta de oro", "ubicacion", "clima"],
    contenido: "Barranquilla es conocida como 'La Puerta de Oro de Colombia' y 'Curramba la Bella'. Es la capital del departamento del Atlántico, ubicada en la desembocadura del río Magdalena en el mar Caribe. Su gente se caracteriza por su alegría, calidez, hospitalidad y sentido del humor."
  },
  {
    id: "carnaval_barranquilla",
    tema: "Carnaval de Barranquilla",
    tags: ["carnaval", "batalla de flores", "gran parada", "joselito", "marimonda", "monocuco", "garabato", "reina"],
    contenido: "El Carnaval de Barranquilla es la fiesta folclórica y cultural más importante de Colombia, declarada por la UNESCO como Obra Maestra del Patrimonio Oral e Inmaterial de la Humanidad. Eventos clave: La Lectura del Bando, La Batalla de Flores, La Gran Parada de Tradición y el entierro de Joselito Carnaval. Personajes icónicos: La Marimonda, El Monocuco, El Rey Momo, El Congo y El Garabato."
  },
  {
    id: "musica_folclor",
    tema: "Música y Ritmos Caribeños",
    tags: ["musica", "cumbia", "vallenato", "champeta", "joe arroyo", "shakira", "tambora", "ritmo"],
    contenido: "Barranquilla vibra con la Cumbia, el Porro, el Merecumbé, el Vallenato y la Champeta. Es la tierra natal de Shakira y la casa adoptiva del gran Joe Arroyo, quien inmortalizó la frase 'En Barranquilla me quedo'. La cumbia se baila al son de la flauta de millo, el tambor alegre, el llamador y las maracas."
  },
  {
    id: "gastronomia_costena",
    tema: "Gastronomía Típica Costeña",
    tags: ["comida", "gastronomia", "arepa de huevo", "butifarra", "arroz de lisa", "sancocho", "guandú", "mojarra", "suero", "cayeye"],
    contenido: "La gastronomía barranquillera incluye delicias como: la arepa de huevo (frito insigne con carne y huevo), la butifarra de Soledad acompañada de limón y bollo de yuca, el arroz de lisa servido en hoja de bijao con suero costeño, el sancocho de guandú con carne salada y el pescado frito (mojarra o róbalo) con patacones y arroz de coco."
  },
  {
    id: "lugares_emblematicos",
    tema: "Sitios Icónicos y Turismo",
    tags: ["lugares", "sitios", "malecon", "rio magdalena", "ventana al mundo", "aleta del tiburon", "la cueva", "bocas de ceniza", "barrio el prado", "teatro amira"],
    contenido: "Sitios imperdibles en Barranquilla: El Gran Malecón del Río (a orillas del Magdalena), el monumento 'Ventana al Mundo', la 'Aleta del Tiburón' (homenaje al Junior), el histórico Barrio El Prado con su arquitectura republicana, La Cueva (donde se reunía Gabriel García Márquez con el Grupo de Barranquilla), Bocas de Ceniza y el Castillo de Salgar."
  },
  {
    id: "junior_barranquilla",
    tema: "Junior de Barranquilla",
    tags: ["junior", "futbol", "tiburon", "metropolitano", "equipo", "rojoblanco", "tu papa"],
    contenido: "El Club Deportivo Popular Junior es el equipo del alma de la ciudad y de toda la región Caribe. Se le conoce como 'El Tiburón' o 'Los Rojiblancos'. El grito de guerra sagrado es: '¡Junior tu papá!'. Juega de local en el Estadio Metropolitano Roberto Meléndez."
  },
  {
    id: "expresiones_costenas",
    tema: "Modismos y Dialecto Costeño",
    tags: ["expresiones", "palabras", "modismos", "costeno", "jerga", "mani", "llave", "bacano", "cipote", "nojoda", "aja"],
    contenido: "Expresiones típicas costeñas bien usadas: 'Mani' o 'Mi llave' (amigo, compadre), 'Ajá' (saludo, confirmación o comodín conversacional), 'Bacano' (bueno, agradable), 'Cipote' (algo grande o asombroso), 'Nojoda' (expresión de sorpresa o énfasis), 'Eche' (queja o desaprobación ligera), 'Cuadro' (amigo cercano), 'Pelar el diente' (sonreír alegremente)."
  }
];

function findRelevantKnowledge(query) {
  if (!query || typeof query !== "string") return "";
  
  const stopWords = new Set(["hola", "buenas", "epa", "mani", "llave", "cuadro", "compa", "como", "estas", "para", "este", "esta", "todo", "bien", "oye", "aja", "que", "los", "las", "una", "uno"]);
  
  const tokens = query.toLowerCase()
    .replace(/[¿?¡!.,;:()"]/g, "")
    .split(/\s+/)
    .filter(w => w.length > 2 && !stopWords.has(w));

  if (tokens.length === 0) return "";

  const scored = KNOWLEDGE_BASE.map(item => {
    let score = 0;
    for (const token of tokens) {
      if (item.tags.some(tag => tag === token || tag.split(/\s+/).includes(token))) {
        score += 4;
      }
      if (item.tema.toLowerCase().includes(token)) {
        score += 2;
      }
      if (item.contenido.toLowerCase().includes(token)) {
        score += 1;
      }
    }
    return { item, score };
  });

  const matches = scored.filter(s => s.score > 0).sort((a, b) => b.score - a.score);
  if (matches.length === 0) return "";
  
  // Devolver los 2 conocimientos más relevantes
  return matches.slice(0, 2).map(m => `[Tema: ${m.item.tema}]\n${m.item.contenido}`).join("\n\n");
}

module.exports = {
  KNOWLEDGE_BASE,
  findRelevantKnowledge
};
