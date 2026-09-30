# asistente costeño
 
# 🌴 Costeño AI - Asistente Virtual 3D de Barranquilla (Mani)

<div align="center">

![Three.js](https://img.shields.io/badge/Three.js-0.160.0-black?style=for-the-badge&logo=three.js)
![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=for-the-badge&logo=node.js&logoColor=white)
![Express](https://img.shields.io/badge/Express.js-4.21-000000?style=for-the-badge&logo=express&logoColor=white)
![Fish Audio](https://img.shields.io/badge/Fish%20Audio-Cloned%20TTS-0070F3?style=for-the-badge)
![Blender](https://img.shields.io/badge/Blender-5.2-E87D0D?style=for-the-badge&logo=blender&logoColor=white)
![Status](https://img.shields.io/badge/Status-Activo%20%26%20Listo-success?style=for-the-badge)

**¡Epa, mani! Asistente conversacional tridimensional en tiempo real con la calidez, la cultura, la gastronomía y el acento auténtico de Curramba la Bella.**

[Características](#-características-principales) • [Tecnologías](#-herramientas-y-tecnologías) • [Instalación](#-guía-de-instalación-paso-a-paso) • [Guía de Uso](#-cómo-interactuar-con-mani) • [Comandos](#-comandos-disponibles)

</div>

---

## 📖 ¿Qué es Costeño AI?

**Costeño AI** es una experiencia web interactiva 3D que cobra vida a través de **Mani**, un carismático avatar barranquillero. Diseñado para funcionar en cualquier navegador moderno sin instalaciones de plugins ni configuraciones complejas, Mani combina gráficos tridimensionales en tiempo real, síntesis de voz propia con acento costeño real, reconocimiento de voz por micrófono y una rica base de conocimientos culturales de Barranquilla.

Ya sea que busques saber dónde comer el mejor sancocho de guandú con carne salá, la historia de los carnavales, o explorar sitios turísticos como el Gran Malecón y la Ventana al Mundo con fotos reales y mapas, Mani te guía con sabor y sabrosura caribeña.

---

## 🚀 Características Principales

* 🎭 **Avatar 3D en Tiempo Real:** Renderizado con **Three.js (WebGL)**, sombreado PBR, iluminación cinemática caribeña y clips de animación esquelética (hablar, saludar, explicar, reír, pensar y reposo).
* 🔊 **Voz Costeña Clonada de Alta Fidelidad:** Motor primario impulsado por **Fish Audio (S2.1)** entrenado con muestras de locución caribeña real para un acento currambero genuino.
* 🛡️ **Tolerancia a Fallos Multinivel (TTS):** Si la conexión remota oscila, el sistema conmuta automáticamente a **Microsoft Edge Neural TTS** (`es-CO-GonzaloNeural`, voz colombiana) o a la **Web Speech API** nativa del navegador.
* ⚡ **Caché Criptográfica Instantánea:** Las locuciones generadas se guardan en formato MP3 en `assets/audio_cache/` mediante hashes MD5. ¡Las respuestas frecuentes cargan a **0 ms de latencia**!
* 🗺️ **Inspector de Lugares Turísticos:** Panel deslizable con fotografías reales de alta calidad, mapas de ubicación y datos curiosos de sitios icónicos (Gran Malecón del Río, Bocas de Ceniza, Aleta del Tiburón, Barrio El Prado, La Cueva, etc.).
* 🎤 **Interacción por Voz y Teclado:** Habla por micrófono con reconocimiento de voz en español o escribe tus dudas en la barra inferior.
* 🧠 **Memoria y Cultura Caribeña:** Base de conocimientos RAG sobre gastronomía típica, tradiciones del Carnaval de Barranquilla y jerga local, con capacidad de aprender nuevos datos que le enseñes.
* ✨ **Diseño Glassmorphism Premium:** Interfaz moderna y oscura con efectos de desenfoque (`backdrop-filter`), navegación por píldoras flotantes y burbuja de diálogo 3D sincronizada.

---

## 🛠️ Herramientas y Tecnologías

| Capa | Tecnología / Herramienta | Propósito en el Proyecto |
| :--- | :--- | :--- |
| **Gráficos 3D** | `Three.js v0.160.0` (WebGL) | Renderizado del personaje 3D, luces cinemáticas, `AnimationMixer` y cámara orbital. |
| **Frontend** | `HTML5` + `Vanilla CSS` + `ES Modules` | Diseño Glassmorphism responsivo, modular, ligero y sin frameworks pesados. |
| **Backend** | `Node.js` + `Express.js v4.21` | Servidor HTTP y API REST para chat, TTS, memoria cultural y catálogo turístico. |
| **IA y Voz Primaria** | `Fish Audio API` | Síntesis y clonación de voz neuronal personalizada (modelo costeño entrenado). |
| **Voz de Respaldo** | `msedge-tts` + `Web Speech API` | Respaldo neural colombiano y reconocimiento de voz por micrófono en el cliente. |
| **Modelado 3D** | `Blender 5.2` (Python Scripting) | Automatización y exportación de esqueletos y mallas en formato `.glb`. |
| **Almacenamiento** | `Crypto` + `Sistema de Archivos` | Caché persistente de audios y memoria dinámica JSON. |

---

## 📂 Estructura del Proyecto

```text
costeno-ai/
├── assets/                     # Recursos multimedia
│   ├── audio_cache/            # Audios MP3 generados en caché persistente
│   ├── cards/                  # Tarjetas visuales de categorías
│   └── places/                 # Fotografías reales de sitios turísticos
├── backend/                    # Servidor Node.js y API REST
│   ├── data/
│   │   ├── memory.json         # Base de datos de memoria dinámica aprendida
│   │   └── places.json         # Catálogo estructurado de lugares turísticos
│   ├── voice_samples/          # Muestras de audio para entrenamiento de voz
│   ├── ai.js                   # Procesamiento de lenguaje natural y respuestas
│   ├── knowledge.js            # Base de conocimiento cultural y currambero
│   ├── memory.js               # Gestor de lectura y persistencia de memoria
│   ├── server.js               # Servidor Express principal (rutas /api/*)
│   └── tts.js                  # Orquestador de síntesis de voz (Fish Audio + Neural)
├── blender/                    # Scripts de modelado 3D procedural (Blender Python)
│   ├── generate_character.py   # Generador del personaje Mani
│   └── generate_environment.py # Generador del entorno escénico
├── frontend/                   # Aplicación cliente WebGL
│   ├── character/              # Controladores de animación, expresiones y gestos
│   ├── chat/                   # Módulos de chat, voz por micrófono y audio
│   ├── three/                  # Configuración de escena, luces y cámara
│   ├── ui/                     # Diálogos flotantes 3D, panel de lugares y controles
│   ├── index.html              # Documento principal HTML
│   ├── main.js                 # Punto de entrada y loop de renderizado Three.js
│   └── style.css               # Estilos globales y diseño glassmorphism
├── .env                        # Claves de API y configuración preconfigurada
├── package.json                # Dependencias del proyecto y scripts ejecutables
├── README.md                   # Documentación oficial
└── Costeno_AI_Documentacion.pdf# Documento oficial en PDF
```

---

## ⚙️ Requisitos Previos

Para ejecutar este proyecto en cualquier computador solo se necesita:

1. **Node.js:** Versión 18.0.0 o superior ([Descargar gratis aquí](https://nodejs.org/)).
2. **Navegador Web Moderno:** Google Chrome, Microsoft Edge, Brave, Opera o Firefox.
3. *(Opcional)* **Blender 5.2:** Solo si se desean compilar nuevos modelos 3D. El avatar actual ya viene compilado y listo para usar en el proyecto.

---

## 📥 Guía de Instalación Paso a Paso (Para Cualquier Usuario)

Si recibiste este proyecto en un archivo comprimido `.zip` o lo clonaste en tu computador, sigue estos sencillos pasos:

### 1️⃣ Descomprimir el proyecto
Si tienes un archivo `.zip`, haz clic derecho sobre él y selecciona **"Extraer todo..."** en la carpeta que prefieras (por ejemplo, en tu *Escritorio*, *Descargas* o *Documentos*).

### 2️⃣ Abrir la terminal en la carpeta
Abre una consola o terminal (PowerShell o CMD en Windows, Terminal en Mac/Linux) dentro de la carpeta del proyecto.

> **💡 Truco rápido en Windows:**  
> Abre la carpeta `costeno-ai` en el Explorador de Archivos, haz clic en la barra de direcciones superior (donde sale la ruta), escribe `cmd` o `powershell` y presiona `Enter`. La consola se abrirá directamente en esa carpeta.
> 
> O navega con el comando `cd`:
> ```bash
> cd "ruta/donde/descomprimiste/costeno-ai"
> ```

### 3️⃣ Instalar las dependencias
Ejecuta el siguiente comando para instalar automáticamente los paquetes necesarios:
```bash
npm install
```
*(Esto descargará las dependencias en la carpeta `node_modules` en pocos segundos).*

### 4️⃣ Variables de entorno (.env)
El archivo `.env` **ya viene completamente configurado** con la clave de API y el identificador de voz de Mani activado, por lo que no requieres registrarte ni configurar nada adicional:
```env
PORT=3000
FISH_AUDIO_API_KEY=sk-fish-hGvjJrtgRSQqLc1w3pVIz9hBG6zqt8WperHCTk6dloQ
FISH_AUDIO_VOICE_ID=48ba9bbe768c4607956eae49b00c7bee
FISH_AUDIO_MODEL=s2.1-pro-free
```

### 5️⃣ Iniciar el servidor
Ejecuta el comando para encender el servidor:
```bash
npm run dev
```

Verás la confirmación en la consola:
```text
====================================================
🌴 Costeño AI - Asistente Virtual 3D de Barranquilla
🚀 Servidor ejecutándose en: http://localhost:3000
====================================================
```

### 6️⃣ Abrir en tu navegador
Abre tu navegador favorito y accede a:
👉 **http://localhost:3000**

---

## 🎮 Cómo Interactuar con Mani

1. **Activar el Sonido:** Al cargar la página verás un banner amarillo en la parte superior. Haz clic en el banner o en cualquier parte de la pantalla para activar el audio (requisito de seguridad de los navegadores para permitir la reproducción automática).
2. **Hablar por Chat:** Escribe tu pregunta en la barra inferior (ejemplo: *"¿Qué planes hay en Barranquilla?"* o *"¿Dónde como un buen sancocho?"*) y presiona `Enter` o el botón de enviar.
3. **Hablar por Micrófono:** Haz clic en el botón de **micrófono 🎤** para hablarle con tu voz natural.
4. **Explorar Lugares Turísticos:** Haz clic en el botón **🗺️ Lugares** en el menú lateral izquierdo o en el muelle inferior para abrir la ficha del Gran Malecón del Río con su galería fotográfica y mapa. Puedes cerrarlo con **[ ✕ ]** y reabrirlo con la pestaña flotante **[ 🗺️ Ver Lugar ]**.
5. **Probar Gestos 3D:** En la parte superior derecha, haz clic en **✨ Gestos 3D** para ver a Mani saludar, reír, explicar o pensar interactivamente.
6. **Memoria y Cultura:** Presiona **📖 Memoria y Cultura** para explorar los datos culturales que Mani domina o enseñarle nueva información para que la recuerde.

---

## 📜 Comandos Disponibles

| Comando | Acción |
| :--- | :--- |
| `npm run dev` | Inicia el servidor de desarrollo en `http://localhost:3000`. |
| `npm start` | Inicia el servidor en modo de producción. |
| `npm run generate:model` | *(Opcional)* Recompila el modelo 3D del personaje con Blender. |
| `npm run generate:scene` | *(Opcional)* Regenera el entorno escénico caribeño. |

---

## ❓ Preguntas Frecuentes

> **¿Por qué no suena la voz al entrar de inmediato?**  
> Los navegadores modernos (Chrome, Edge, Safari) bloquean la reproducción de audio hasta que el usuario interactúa con la página por primera vez. Solo haz clic en el banner amarillo superior o en cualquier punto de la pantalla.

> **¿Qué hago si el puerto 3000 está ocupado?**  
> Abre el archivo `.env`, cambia `PORT=3000` por `PORT=3001` (o cualquier otro número) y entra a `http://localhost:3001`.

> **¿El proyecto necesita internet para funcionar?**  
> Requiere internet para generar respuestas nuevas y sintetizar frases nuevas con Fish Audio. Sin embargo, las frases de bienvenida y respuestas ya generadas quedan guardadas en `assets/audio_cache/` y funcionan sin latencia.

---

<div align="center">

🌴 **Costeño AI** — Desarrollado con pasión y sabor caribeño en Barranquilla, Colombia. 🌴

</div>
