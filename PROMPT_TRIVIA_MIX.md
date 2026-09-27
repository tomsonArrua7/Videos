# Prompt para un video largo de trivia: fútbol, películas y series

## Cómo usarlo

Igual que `PROMPT_VIDEO_LARGO.md`:

1. Bajá el repositorio en la rama `claude/animated-curiosities-video-0lcxhr`.
2. Abrí tu asistente de IA en esa carpeta.
3. Pegá todo lo que está debajo de **"PROMPT"**.

Las partes entre corchetes (`[...]`) las podés cambiar antes de pegarlo.

---

# PROMPT

Sos productor, guionista y programador de un **show de trivia para YouTube**. Vamos a hacer un video largo que la gente pueda **jugar mientras lo mira**, que mezcle **fútbol, películas y series** y que vaya variando todo el tiempo. Trabajás en mi PC, en la carpeta de este repositorio.

## La idea

- **Canal:** Trivia veloz. Público general de habla hispana, con tono argentino (voseo: "acertaste", "anotá", "fijate").
- **Video:** unos 40 desafíos en 8 a 12 minutos, horizontal a 1920×1080 y 30 fps.
- **Promesa del título:** "[40] preguntas de fútbol, películas y series: ¿cuántas acertás?".
- **La clave es que sea un juego.** El que mira anota sus puntos, compite contra el reloj y al final se compara con una tabla de resultados. Tiene que dar ganas de comentar el puntaje y de mandarle el video a un amigo.
- **Sin mascota ni estilo de dibujito.** La estética es la de un programa de preguntas de TV: estudio oscuro con luces, acentos de neón, tipografía grande y animaciones rápidas y limpias.

## Estructura (con rondas distintas para que no aburra)

| Parte | Duración aprox. | Qué pasa |
|---|---|---|
| **Gancho** | 20 s | 3 preguntas relámpago de muestra (una de cada tema) y el desafío: "Anotá un punto por cada acierto. ¿Llegás a 30?". Nada de "hola, bienvenidos". |
| **Ronda 1 · Calentamiento** | 2:30 | 10 preguntas fáciles, 3 opciones, 5 s de reloj. **1 punto** cada una. |
| **Ronda 2 · Verdadero o falso** | 1:30 | 8 afirmaciones, 3 s de reloj. **1 punto** cada una. |
| **Ronda 3 · Adiviná con emojis** | 1:30 | 6 desafíos: una película, una serie, un club o un jugador descrito con 3 o 4 emojis. Por ejemplo 🦁👑🌅 = El Rey León. 5 s. **2 puntos**. |
| **Ronda 4 · ¿Qué fue primero?** | 1:15 | 6 duelos A contra B ("¿Qué se estrenó primero?", "¿Qué Mundial fue antes?"). 3 s. **1 punto**. |
| **A mitad de video** | 5 s | "Si venís sumando, suscribite". Nada al principio. |
| **Ronda 5 · Difícil** | 2:30 | 8 preguntas difíciles, 4 opciones, 7 s. **3 puntos**. |
| **Pregunta imposible** | 30 s | Una sola, anunciada con suspenso. 10 s de reloj. **5 puntos**. |
| **Resultados** | 30 s | Puntaje máximo (65) y tabla de niveles: 0-15 "Suplente", 16-35 "Titular", 36-50 "Crack", 51-65 "Leyenda", más "Si sacaste el máximo, comentalo". Si cambia la cantidad de preguntas, los rangos se recalculan. |
| **Pantalla final** | 20 s | Fondo animado y espacio libre para las tarjetas finales de YouTube. |

**Reglas de variedad:**

- **Sorteo de tema:** en las rondas 1 y 5, antes de cada pregunta gira una ruleta de categorías de 1 segundo (⚽ Fútbol, 🎬 Películas, 📺 Series).
- **Mezcla:** cada ronda tiene los tres temas en partes parecidas, y nunca van más de dos seguidas del mismo.
- **Respuesta correcta:** la letra correcta se reparte parejo entre A, B, C y D, sin patrones.
- **Dificultad:** sube dentro de cada ronda.
- **Dato extra:** en 1 de cada 3 respuestas, una línea breve de curiosidad ("Y ese partido lo vieron…"). Da entretenimiento sin frenar el ritmo.

## Las preguntas

- **Formato:** escribí primero el banco de preguntas en un archivo de datos, `trivia/preguntas.json`, no dentro del código. Cada entrada lleva:
  - `id`, `ronda`, `categoria` (`futbol`, `peliculas` o `series`) y `dificultad`;
  - `pregunta` (lo que se lee y se ve) y `opciones`;
  - `correcta` y `dato_extra` (opcional);
  - `fuente`: un link o una referencia confiable.
- **Fútbol:** priorizá datos históricos que no cambian: Mundiales, Copa América, récords cerrados, historia de clubes. Evitá estadísticas de la temporada en curso, porque caducan. Si hay un dato que puede cambiar, anotá "vigente a [fecha]" en `fuente`. Equilibrá lo argentino (selección, Maradona, Messi, clásicos) con lo internacional.
- **Películas y series:** muy conocidas en Latinoamérica, con títulos como se conocen acá. Mezclá clásicos con cosas recientes.
- **Nada ambiguo:** una sola respuesta correcta sin discusión. Cuidado con "el máximo goleador" (¿de qué torneo? ¿hasta cuándo?).
- **Nada de mitos ni datos dudosos.** Si no hay fuente confiable, la pregunta no va.
- **Distractores:** las opciones incorrectas tienen que ser creíbles, del mismo tipo que la respuesta (años cercanos, jugadores de la misma época).
- **Revisión automática:** hacé un script `trivia/revisar.py` que controle el banco antes de producir:
  - que no haya preguntas repetidas;
  - la mezcla de categorías por ronda;
  - el reparto de letras correctas;
  - que no haya tres del mismo tema seguidas;
  - que el largo de las preguntas entre en pantalla;
  - la duración estimada del video.

## Voz

- **Dos conductores que se turnan:**
  - `es-AR-ElenaNeural` lee las preguntas.
  - `es-AR-TomasNeural` revela las respuestas y dice los datos extra.
  - Entre rondas, un intercambio corto y con onda entre los dos, de 2 frases como máximo.
- **Cómo escribir para la voz** (aprendido con los Shorts de este repo):
  - frases cortas;
  - números en palabras;
  - nombres extranjeros con la marca `{cómo se ve|cómo se dice}`, por ejemplo `{Mbappé|Embapé}` o `{Stranger Things|Estréinyer Zings}`;
  - verificar todo con `src/verificar_voz.py` (Whisper) y corregir lo que no se entienda.
- **Silencios:** los tiempos para pensar usan la marca `[5s]` que ya existe en `voz.py`.
- **Opcional:** si en `grabaciones/` hay un audio mío para el gancho o el cierre, usalo con `src/grabacion.py`.

## Cómo se ve (estética de programa de TV)

- **Fondo:** estudio oscuro con haces de luz que se mueven suave y un piso con reflejo.
- **Color por categoría:** fútbol verde césped, películas rojo y dorado, series violeta. El color tiñe las luces y el marco de la pregunta.
- **Pantalla de pregunta:**
  - arriba, la pregunta grande en una tarjeta;
  - abajo, las opciones A/B/C/D en dos columnas;
  - a la derecha, el reloj circular que se vacía de verde a rojo;
  - arriba a la izquierda, la ronda y el número ("RONDA 1 · 7/10");
  - arriba a la derecha, la dificultad y cuántos puntos vale.
- **Revelación:** la correcta se pone verde con un tilde y brillos, las otras se apagan, y suenan un "¡correcto!" y un aplauso corto.
- **Íconos:** cada pregunta lleva uno genérico hecho con código, de una biblioteca propia: pelota, arco, botín, trofeo, silbato, claqueta, pochoclo, cámara de cine, control remoto, televisor y demás. Para la ronda de emojis se usa la fuente **Noto Color Emoji** (licencia OFL, gratis) en `assets/fonts/`.
- **Placas de ronda:** entre rondas, una placa de 3 segundos con el nombre, las reglas en una línea y cuántos puntos vale cada acierto.
- **Contador de puntos máximos:** una píldora chica que dice "Puntos en juego: 23/65" y que el público usa de referencia.
- **Ritmo:** algo cambia cada 3 o 5 segundos. Nunca pantalla quieta.

## Derechos de autor (muy importante para no tener reclamos en YouTube)

- **Sin escudos, logos ni camisetas oficiales** de clubes, selecciones, ligas ni de la FIFA.
- **Sin fotos ni caras de jugadores o actores.** Se nombran, pero no se muestran.
- **Sin pósters, capturas ni personajes de películas y series.** Solo íconos genéricos.
- **Sin música con derechos:** ni himnos de torneos ni bandas sonoras. La música es original, sintetizada con `src/sonido.py` (con variaciones por ronda), o de la Biblioteca de audio de YouTube.
- **Los nombres de equipos, jugadores, películas y series sí se pueden decir y escribir**, porque son información.

## Lo que ya existe en este repo (reutilizalo)

Leé primero el `README.md`, `src/quiz.py` y un episodio quiz (`src/episodios/ep12.py`):

| Archivo | Qué ya resuelve |
|---|---|
| `src/quiz.py` | Tarjeta de pregunta, opciones, reloj de cuenta regresiva con tic-tac y revelación de la correcta. Hoy es vertical y de 3 opciones: pasalo a horizontal y a 2, 3 o 4 opciones. |
| `src/voz.py` | Voces con `edge-tts`, tiempos por palabra, marcas `{…\|…}` y silencios `[3s]` dentro de un bloque. Falta agregar una voz por bloque. |
| `src/sonido.py` | Música original, efectos (tic-tac, acierto, pops, whoosh), cadena de voz y mezcla a −14 LUFS. |
| `src/dibujo.py` | Kit de dibujo, textos y carteles. Hoy la resolución está fija en 1080×1920: hacela configurable sin romper los Shorts. |
| `src/animacion.py` | Subtítulos, transiciones y exportación en paralelo. |

**Regla:** los Shorts actuales (`python hacer_video.py epNN`) tienen que seguir funcionando igual. Lo nuevo puede ir en `src/trivia/`.

**Motor de trivia:** la meta es que el video se arme **a partir del archivo de preguntas**. Si mañana cambio `preguntas.json`, con un comando sale un video nuevo:

```
python hacer_trivia.py trivia/preguntas.json
```

## Extra: Shorts desde el mismo banco

Agregá un modo que tome 5 preguntas del banco y arme un Short vertical de menos de 60 segundos con el formato de `ep12`, terminando con "El video completo con 40 preguntas está en el canal". Así cada video largo alimenta varios Shorts y los Shorts llevan gente al largo.

## Forma de trabajo (con puntos de control conmigo)

1. **Propuesta:** 3 títulos posibles, la estructura final y las primeras 12 preguntas de muestra (4 de cada tema) con sus fuentes. **Esperá mi aprobación.**
2. **Banco completo** en `trivia/preguntas.json` y el resultado de `revisar.py`. **Esperá mi aprobación.**
3. **Código:**
   - horizontal;
   - 4 opciones;
   - ruleta de categorías y rondas especiales (verdadero o falso, emojis, qué fue primero);
   - placas de ronda y contador de puntos;
   - voz por bloque.
   - Probalo primero con la ronda 1 sola.
4. **Voces:** generalas y verificalas con Whisper hasta que todo se entienda.
5. **Vista previa:** una hoja de cuadros sueltos por ronda, para que yo revise antes del render completo.
6. **Render:** por rondas (un mp4 por ronda en `build/`), unidas al final con ffmpeg. Agregá un modo `--rapido` (960×540 a 15 fps) para probar.
7. **Controles finales:**
   - duración de 8 a 12 minutos;
   - −14 LUFS;
   - relojes y respuestas sincronizados con la voz;
   - ningún texto cortado;
   - los 20 segundos finales libres para las tarjetas.
8. **Entregables en `output/`:**
   - el video;
   - la miniatura de 1280×720: "¿CUÁNTAS ACERTÁS?", "40 PREGUNTAS", los íconos ⚽🎬📺 y colores fuertes, de menos de 2 MB;
   - un `.md` con el título, la descripción, los capítulos por ronda con sus minutos, etiquetas y el comentario fijado sugerido ("¿Cuántos puntos sacaste? 👇");
   - 2 o 3 Shorts armados con el mismo banco.

## Detalles técnicos que ya sé que importan

- **Dependencias:** `pip install -r requirements.txt` y, para verificar, `pip install -r requirements-verificacion.txt`. ffmpeg ya viene con `imageio-ffmpeg`.
- **Windows:** `multiprocessing` usa `spawn`. Poné todo lo que arranca el render bajo `if __name__ == "__main__":` y cacheá los fondos pesados.
- **Tiempo de render:** 10 minutos a 30 fps son unos 18.000 cuadros. Mostrá el progreso y cuánto falta.
- **Voces:** no las aceleres más de +10 %. Si no entra, sacá preguntas.
- **Licencia:** si el canal se monetiza, revisá los términos de uso de las voces de Microsoft (`edge-tts`). Dejá preparado el cambio a Azure Speech con una clave (`AZURE_SPEECH_KEY`).
- **Commits:** hacé commits chicos y con mensajes claros.

Arrancá por el paso 1.
