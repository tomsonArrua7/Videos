# Videos de curiosidades 🤯

Serie de videos animados de **30 segundos**, verticales (1080×1920, 30 fps), listos para Shorts, Reels y TikTok.

| Episodio | Curiosidades | Voz | Video | Guion |
|---|---|---|---|---|
| 1 | 🐙 pulpo · 🍯 miel · 🪐 Venus | Tomás (hombre, Argentina) | [`ep01_pulpo_miel_venus.mp4`](output/ep01_pulpo_miel_venus.mp4) · [portada](output/ep01_portada.png) | [guion](guiones/ep01_pulpo_miel_venus.md) |
| 2 | 🦈 tiburón · 🦩 flamenco · 🍌 banana | Elena (mujer, Argentina) | [`ep02_tiburon_flamenco_banana.mp4`](output/ep02_tiburon_flamenco_banana.mp4) · [portada](output/ep02_portada.png) | [guion](guiones/ep02_tiburon_flamenco_banana.md) |
| 3 | 🦦 nutrias · ⚡ rayo · 🌳 árboles | Elena (mujer, Argentina) | [`ep03_nutrias_rayo_arboles.mp4`](output/ep03_nutrias_rayo_arboles.mp4) · [portada](output/ep03_portada.png) | [guion](guiones/ep03_nutrias_rayo_arboles.md) |
| 4 | 🎬 películas: Jurassic Park · Volver al futuro · Titanic | Tomás (hombre, Argentina) | [`ep04_peliculas.mp4`](output/ep04_peliculas.mp4) · [portada](output/ep04_portada.png) | [guion](guiones/ep04_peliculas.md) |
| 5 | 📺 series: El Chavo del 8 · Breaking Bad · Friends | Tomás (hombre, Argentina) | [`ep05_series.mp4`](output/ep05_series.mp4) · [portada](output/ep05_portada.png) | [guion](guiones/ep05_series.md) |
| 6 | 🎨 dibujos animados: Los Simpson · Bob Esponja · Mickey Mouse | Tomás (hombre, Argentina) | [`ep06_dibujos_animados.mp4`](output/ep06_dibujos_animados.mp4) · [portada](output/ep06_portada.png) | [guion](guiones/ep06_dibujos_animados.md) |
| 7 | 🎬 películas 2: Star Wars · Buscando a Nemo · Harry Potter | Tomás (hombre, Argentina) | [`ep07_peliculas_2.mp4`](output/ep07_peliculas_2.mp4) · [portada](output/ep07_portada.png) | [guion](guiones/ep07_peliculas_2.md) |
| 8 | 🎬 películas 3: Psicosis · El Mago de Oz · Frozen | Tomás (hombre, Argentina) | [`ep08_peliculas_3.mp4`](output/ep08_peliculas_3.mp4) · [portada](output/ep08_portada.png) | [guion](guiones/ep08_peliculas_3.md) |
| 9 | 🧠 tu cuerpo: más alto a la mañana · huesos · brillás en la oscuridad | **Tu voz** (por ahora, muestra con Tomás) | [`ep09_cuerpo_humano.mp4`](output/ep09_cuerpo_humano.mp4) · [portada](output/ep09_portada.png) | [guion y guía para grabar](guiones/ep09_cuerpo_humano.md) |

Cada guion trae la tabla de escenas, los datos verificados y un texto listo para publicar.
En los episodios de películas, series y dibujos se usan objetos y guiños genéricos: nunca se
dibujan personajes ni logos con derechos de autor.

## Cómo está hecho

Todo se genera con código, sin editor de video:

| Parte | Cómo | Archivo |
|---|---|---|
| Episodios | Guion, personajes y escenas de cada video | `src/episodios/epNN.py` |
| Voz | Voz neuronal gratuita de Microsoft Edge vía [`edge-tts`](https://github.com/rany2/edge-tts), en MP3 de 96 kbps y con tiempos por palabra | `src/voz.py` |
| Sonido | Tema original sintetizado con numpy + efectos (whoosh, pops, explosión, Geiger, "ñam"...). La voz pasa por una cadena de locución (EQ, compresor, de-esser, limitador), la música baja sola cuando se habla y todo sale a −14 LUFS | `src/sonido.py` |
| Animación común | Gancho (la carita que explota), cierre, subtítulos karaoke, transiciones y exportación | `src/animacion.py` |
| Kit de dibujo | Lienzo con antialias, textos, fondos, carteles, sprites | `src/dibujo.py` |
| Sincronía | Momentos clave anclados a palabras de la voz | `src/tiempos.py` |
| Control de la voz | Whisper escucha la narración y marca lo que no se entiende | `src/verificar_voz.py` |
| Voz humana | Limpia una grabación de celular, ubica cada bloque del guion con Whisper y la sincroniza con el video | `src/grabacion.py` |

## Generar los videos

Requiere Python 3.10+ y conexión a internet (para la voz). ffmpeg viene incluido con `imageio-ffmpeg`.

```bash
pip install -r requirements.txt
python hacer_video.py          # el último episodio
python hacer_video.py ep01     # uno en particular
python hacer_video.py todos    # todos
```

Cada episodio tarda alrededor de un minuto. Para ver cuadros sueltos sin exportar todo:

```bash
cd src && python animacion.py ep02 --previa 2.5 5 12.3   # -> build/ep02/previa/*.png
```

### Hacer un episodio nuevo

1. Copiá el último episodio (por ejemplo `src/episodios/ep09.py`) como `ep10.py`.
2. Cambiá `SLUG`, `VOZ` y los textos de `BLOQUES` (el primero es el gancho y el último el cierre; tienen que seguir diciendo "tres", "curiosidades" y "cabeza" en el gancho).
3. Anclá tus animaciones a palabras en `eventos()`, sumá efectos en `efectos()` y dibujá las escenas.
4. `python hacer_video.py ep10`. La velocidad de la voz se ajusta sola para que entre en 30 s; si no entra, avisa que hay que acortar el texto.

Voces en español argentino: `es-AR-ElenaNeural` (mujer) y `es-AR-TomasNeural` (hombre). Hay más en `edge-tts --list-voices`.

### Guiones que suenan bien

La voz es una máquina leyendo: el guion se escribe para el oído.

- **Frases cortas** y puntuación donde se respira; los signos `¡!` le dan energía al remate.
- **Números en palabras** ("cuarenta y dos", no "42").
- **Nombres en inglés:** se escribe `{como se ve|como se dice}`. La voz lee la segunda forma y los
  subtítulos muestran la primera. Por ejemplo `{Friends|Fréns}` o `{Jesse Pinkman|Yési Pínc man}`.
  Lo dicho puede tener más palabras que lo mostrado.
- **Evitar choques de sonidos** ("a Rose son" se escuchaba "arroz se son") y palabras ambiguas
  ("zapping" → "cambiás de canal").
- Si hace falta un respiro después de un bloque (por ejemplo, para que ruja un dinosaurio), se agrega
  `"pausa_despues": 0.6` a ese bloque. `VOZ_PAUSA` y `VOZ_FINAL` ajustan las pausas del episodio.

Para comprobarlo sin escuchar, está el verificador (opcional, necesita `pip install -r requirements-verificacion.txt`):

```bash
cd src
python verificar_voz.py ep05                                   # transcribe y marca lo que no se entiende
python verificar_voz.py ep05 --probar "La serie Frends." "La serie Fréns."   # compara variantes
```

## Grabar con tu voz

Cualquier episodio puede usar una voz humana en lugar de la sintética:

1. Grabá los bloques del guion en **un solo audio** con el celular, con un silencio corto entre bloque
   y bloque. Si te trabás, repetí el bloque entero: se usa la última toma completa.
2. Guardalo como `grabaciones/ep09.m4a` (sirve cualquier formato de audio; ver [`grabaciones/LEEME.md`](grabaciones/LEEME.md)).
3. `python hacer_video.py ep09`: detecta la grabación y la usa.

El retoque (`src/grabacion.py`, necesita `pip install -r requirements-verificacion.txt`) hace esto:

- **Ruido:** saca el zumbido grave y el ruido de fondo con una compuerta espectral que aprende de los silencios.
- **Sincronía:** Whisper transcribe con tiempos por palabra, ubica cada bloque (también las repeticiones)
  y ancla las animaciones y los subtítulos a tus palabras.
- **Edición:** corta los bloques, baja las respiraciones y empareja el volumen.
- **Tiempo:** si no entra en 30 s, acelera hasta un 15 % sin cambiar el tono. Si aun así no entra,
  el video se estira unas décimas.
- **Sonido:** después pasa por la misma cadena de locución y mezcla que la voz sintética.

El informe queda en `build/ep09/grabacion_informe.txt`. Para probar otro archivo:
`cd src && python voz.py ep09 --grabacion ../mi_audio.m4a`. Para que un episodio nuevo busque su grabación,
se le agrega `GRABACION = "grabaciones/epNN"`.

## Licencias y créditos

- **Música y efectos:** originales, generados por este código. Sin derechos de terceros.
- **Tipografías:** [Luckiest Guy](https://fonts.google.com/specimen/Luckiest+Guy) (Apache 2.0) y [Montserrat](https://github.com/JulietaUla/Montserrat) (SIL OFL). Licencias en `assets/fonts/`.
- **Voz:** en los episodios con voz sintética, servicio de lectura en voz alta de Microsoft Edge, usado a través de `edge-tts`. Si el canal se va a monetizar, conviene revisar los términos de Microsoft o reemplazar la voz por una con licencia comercial explícita.
