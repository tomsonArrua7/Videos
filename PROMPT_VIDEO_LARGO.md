# Prompt para hacer un video largo de curiosidades en tu PC

## Cómo usarlo

1. Instalá en tu PC:
   - [Python 3.10 o más nuevo](https://www.python.org/downloads/). En Windows, tildá "Add Python to PATH" al instalarlo.
   - [Git](https://git-scm.com/downloads).
2. Bajá este repositorio en la rama donde está todo:
   ```bash
   git clone https://github.com/tomsonArrua7/Videos.git
   cd Videos
   git checkout claude/animated-curiosities-video-0lcxhr
   ```
3. Abrí tu asistente de IA en esa carpeta. Lo ideal es uno que pueda ejecutar comandos en tu PC, como Claude Code (`claude` en la terminal) o Cursor. Si usás un chat común, igual sirve, pero vas a tener que correr vos los comandos que te diga.
4. Copiá todo lo que está debajo de la línea **"PROMPT"** y pegalo como primer mensaje. Si querés un tema en particular, cambialo en la sección "Lo que quiero".

---

# PROMPT

Sos mi productor de video y programador. Vamos a hacer un **video largo de curiosidades para YouTube (7 a 10 minutos, horizontal)**, animado por código y narrado por dos voces neuronales de Microsoft en español argentino que se van turnando. Trabajás en mi PC, en la carpeta de este repositorio.

## Lo que quiero

- **Canal:** curiosidades, para público general de habla hispana, con tono argentino (voseo: "sabías", "mirá", "fijate").
- **Duración:** entre 7 y 10 minutos.
- **Formato:** 1920×1080, 30 fps, listo para subir a YouTube.
- **Voces:** dos conductores que se turnan y conversan.
  - **Tomás:** `es-AR-TomasNeural`.
  - **Elena:** `es-AR-ElenaNeural`.
  - Tienen que sonar como un dúo, no como dos lecturas pegadas. Por ejemplo, Elena plantea la pregunta, Tomás cuenta el dato y Elena remata o agrega algo.
- **Tema:** curiosidades variadas agrupadas en **3 o 4 capítulos temáticos**, por ejemplo animales, cuerpo humano, espacio y cosas de todos los días. Proponeme vos los temas.
- **Estilo visual:** el mismo de mis Shorts, que están en este repo. Mismas tipografías (Luckiest Guy para títulos, Montserrat Black para textos), colores vivos, animaciones con rebote, subtítulos grandes y efectos de sonido.

## Lo que ya existe en este repo (reutilizalo, no empieces de cero)

Leé primero el `README.md` y los archivos de `src/`. Ya están resueltos y probados:

| Archivo | Qué hace | Qué hay que cambiar para el video largo |
|---|---|---|
| `src/voz.py` | Voz con `edge-tts`. Pide MP3 de 96 kbps (parche en `send_str`), guarda los tiempos de cada palabra (WordBoundary) y arma la línea de tiempo. Entiende `{cómo se ve\|cómo se dice}` y los silencios `[3s]` dentro de un bloque. | Hoy usa una voz por episodio (`EP.VOZ`). Tiene que aceptar una voz por bloque (`"voz": "tomas"` o `"elena"`), cada una con su tono y velocidad. |
| `src/sonido.py` | Música original sintetizada, biblioteca de efectos (whoosh, pop, ding, tic-tac, etc.), cadena de voz (EQ, compresor, de-esser, limitador), la música que baja cuando se habla y loudnorm a −14 LUFS. | Para 10 minutos, la música no puede ser un solo loop: variá acordes o tempo por capítulo, con fundidos. Emparejá el volumen de Tomás y Elena antes de mezclar. |
| `src/dibujo.py` | Kit de dibujo: lienzo con antialias (`Capa`), textos, fondos, carteles, píldoras, sprites y easings (`pop`, `e_back`, etc.). | Hoy `W, H = 1080, 1920`, fijos. Hacé que la resolución sea configurable sin romper los Shorts. |
| `src/animacion.py` | Subtítulos karaoke, transiciones de barrido, sacudidas de cámara y exportación en paralelo a ffmpeg. | Adaptarlo al formato horizontal y a capítulos. |
| `src/tiempos.py` | Anclar eventos visuales a palabras de la voz (`L.palabra("bloque", "palabra")`). | Se usa igual. |
| `src/verificar_voz.py` | Whisper escucha la voz y marca las palabras que no se entienden. | Se usa igual en cada bloque. |
| `src/episodios/*.py` y `guiones/*.md` | Ejemplos de episodios y de guiones. | Copiá el formato. |

**Regla:** no rompas el flujo de los Shorts (`python hacer_video.py epNN` tiene que seguir andando). Lo del video largo puede ir en `src/largo/`, o como un modo "horizontal" configurable.

## Cómo quiero el guion

Unas 1.200 a 1.500 palabras en total. Estructura sugerida para unos 9 minutos:

1. **Gancho (0:00 a 0:30):** los 2 o 3 datos más locos del video en frases de 3 segundos, y la promesa: "quedate hasta el final, que la última es la más increíble". Nada de "hola, bienvenidos" al principio.
2. **Capítulos:** 3 o 4 capítulos con 3 o 4 curiosidades cada uno, unos 12 a 15 datos en total. Cada capítulo arranca con una placa de título de 2 o 3 segundos.
3. **Cada curiosidad (30 a 45 s):**
   - Pregunta o planteo (Elena).
   - Explicación con el dato (Tomás).
   - Remate o dato extra (Elena o los dos).
   - Una transición corta ("Pero esperá, que la siguiente es peor…").
4. **A mitad de video (5 s):** "Si te está gustando, suscribite". Nada al principio.
5. **Final:** la curiosidad más impactante, guardada para el cierre. Después, un pedido de comentario ("¿Cuál no sabías?").
6. **Pantalla final:** 20 segundos con fondo animado y espacio libre para las tarjetas finales de YouTube (dos videos y el botón de suscripción). Esos 20 segundos van sin texto en las zonas donde YouTube pone esos elementos.

Reglas de escritura (aprendidas con los Shorts; respetalas):

- **Frases cortas**, puntuación donde se respira y `¡!` para dar energía en los remates.
- **Números escritos en palabras** ("cuarenta y dos", no "42").
- **Nombres en inglés:** con la marca `{cómo se ve|cómo se dice}`. Por ejemplo `{Titanic|Titánic}` o `{Friends|Fréns}`. La voz lee la segunda forma y los subtítulos muestran la primera.
- **Choques de sonidos y palabras ambiguas:** evitalos. Antes pasó que "a Rose son" se escuchaba "arroz se son".
- **Voces:** cada bloque lleva `"voz": "tomas"` o `"voz": "elena"`. Que no hable la misma persona más de dos bloques seguidos.
- **Datos verdaderos:** con al menos una fuente confiable para cada uno, listada en el guion. Descartá los mitos conocidos:
  - usamos el 10 % del cerebro;
  - la memoria de 3 segundos del pez dorado;
  - la Muralla China se ve desde el espacio;
  - los toros odian el rojo;
  - un rayo nunca cae dos veces en el mismo lugar.
- **Sin personajes ni logos con derechos de autor.** Si se habla de una película o marca, se dibujan objetos genéricos, como en mis Shorts.

## Cómo quiero lo visual (1920×1080)

- **Presentadores:** dos avatares originales y simples en una esquina inferior (una carita con un color distinto para cada uno). El que habla se agranda un poco y mueve la boca según el volumen de su voz. Así se entiende quién habla.
- **Escenas:** cada curiosidad tiene su escena animada con un dibujo propio hecho con `Capa`, carteles con el número clave y píldoras de texto. Las animaciones se anclan a palabras de la voz.
- **Algo nuevo cada 5 a 8 segundos:** un dibujo que aparece, un número, un zoom o un cambio de fondo. Nunca más de 8 segundos de pantalla quieta.
- **Subtítulos:** abajo al centro, más chicos que en los Shorts (unos 64 px), con la palabra activa resaltada. Tienen que dejar libre la zona de los avatares.
- **Ubicación en el video:** arriba a la izquierda, una píldora con el capítulo ("🐾 ANIMALES · 2/4"). Arriba a la derecha, el contador de curiosidades ("7/13").
- **Transiciones:** el barrido diagonal de `animacion.py` entre curiosidades, y una placa de título más grande entre capítulos.
- **Márgenes:** 5 % en todos los bordes, sin texto cortado.

## Sonido

- **Voces:** las dos pasan por la cadena de `sonido.py`, emparejadas en volumen, sin que una suene más fuerte que la otra.
- **Música:** original y sintetizada, con una variación por capítulo, que baja cuando se habla. Opcional: música gratuita de la Biblioteca de audio de YouTube en `assets/musica/`, pero solo de ahí, para no tener reclamos de derechos.
- **Efectos:** los de `sonido.py` en cada aparición importante, sin saturar.
- **Volumen final:** −14 LUFS integrado y pico real de −1,5 dBFS o menos.

## Forma de trabajo (con puntos de control conmigo)

1. **Propuesta:** 3 opciones de título, los capítulos y la lista de curiosidades con su fuente. **Esperá mi aprobación.**
2. **Guion completo** en `guiones/largo01_<tema>.md`: tabla con tiempo estimado, voz, texto y qué se ve. **Esperá mi aprobación.**
3. **Código:**
   - Voz por bloque.
   - Resolución configurable.
   - Modo largo por capítulos.
   - Avatares y adaptaciones de layout.
   - Probalo primero con un solo capítulo.
4. **Voces:** generalas y corré `verificar_voz.py`. Todo lo que Whisper no entienda se corrige en el guion (cambiando palabras o con `{…|…}`) y se vuelve a verificar hasta que quede todo OK.
5. **Vista previa rápida:** `--previa` con cuadros sueltos y una hoja de contactos por capítulo, para que yo revise los dibujos antes de renderizar todo.
6. **Render por capítulos:**
   - Cada capítulo a un mp4 separado en `build/`. Así, si algo falla, se vuelve a hacer solo esa parte.
   - Al final se unen con ffmpeg (`concat`) y se mezcla el audio completo.
   - Agregá un modo `--rapido` (960×540 a 15 fps) para probar.
7. **Controles finales antes de entregar:**
   - duración entre 7 y 10 minutos;
   - −14 LUFS;
   - voz sincronizada con subtítulos y animaciones;
   - ningún texto cortado ni superpuesto;
   - los 20 segundos finales libres para la pantalla final.
8. **Entregables en `output/`:**
   - el video `largo01_<tema>.mp4`;
   - la miniatura de 1280×720, en PNG y de menos de 2 MB: texto grande de 3 o 4 palabras, un dibujo llamativo y colores contrastados;
   - un `.md` con el título, la descripción, los capítulos con sus minutos y las etiquetas.
   - Los capítulos salen de la línea de tiempo real: el primero en 0:00, al menos 3 y de 10 segundos o más cada uno.

## Detalles técnicos que ya sé que importan

- **Dependencias:** `pip install -r requirements.txt` (edge-tts, imageio-ffmpeg, numpy, pillow, scipy) y, para verificar, `pip install -r requirements-verificacion.txt` (faster-whisper). ffmpeg ya viene con `imageio-ffmpeg`.
- **edge-tts** necesita internet. Si hay error de certificado SSL, `voz.py` ya toma el archivo de la variable `SSL_CERT_FILE`.
- **Windows:** `multiprocessing` usa `spawn`. Todo lo que arranca el render tiene que estar bajo `if __name__ == "__main__":`, y los trabajadores no tienen que recalcular fondos pesados en cada cuadro (cachealos).
- **Tiempo de render:** un video de 9 minutos son más de 16.000 cuadros. Mostrá el progreso y estimá cuánto falta.
- **Duración de la voz:** si la narración no entra en el tiempo, primero recortá texto. No aceleres las voces más de +10 %.
- **Licencia de las voces:** si el canal se monetiza, conviene revisar los términos de uso de Microsoft para `edge-tts`. Existe Azure Speech, que tiene las mismas voces con licencia comercial y un nivel gratuito mensual. Dejá preparado un interruptor para usar Azure con una clave (`AZURE_SPEECH_KEY`) sin cambiar el resto.
- **Commits:** hacé commits chicos y con mensajes claros.

Arrancá por el paso 1: leé el repo y proponeme título, capítulos y curiosidades.
