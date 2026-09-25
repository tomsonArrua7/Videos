# Videos de curiosidades 🤯

Serie de videos animados de **30 segundos**, verticales (1080×1920, 30 fps), listos para Shorts, Reels y TikTok.

| Episodio | Curiosidades | Voz | Video | Guion |
|---|---|---|---|---|
| 1 | 🐙 pulpo · 🍯 miel · 🪐 Venus | Tomás (hombre, Argentina) | [`ep01_pulpo_miel_venus.mp4`](output/ep01_pulpo_miel_venus.mp4) · [portada](output/ep01_portada.png) | [guion](guiones/ep01_pulpo_miel_venus.md) |
| 2 | 🦈 tiburón · 🦩 flamenco · 🍌 banana | Elena (mujer, Argentina) | [`ep02_tiburon_flamenco_banana.mp4`](output/ep02_tiburon_flamenco_banana.mp4) · [portada](output/ep02_portada.png) | [guion](guiones/ep02_tiburon_flamenco_banana.md) |

Cada guion trae la tabla de escenas, los datos verificados y un texto listo para publicar.

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

1. Copiá `src/episodios/ep02.py` como `ep03.py`.
2. Cambiá `SLUG`, `VOZ` y los textos de `BLOQUES` (el primero es el gancho y el último el cierre; tienen que seguir diciendo "tres", "curiosidades" y "cabeza" en el gancho).
3. Anclá tus animaciones a palabras en `eventos()`, sumá efectos en `efectos()` y dibujá las escenas.
4. `python hacer_video.py ep03`. La velocidad de la voz se ajusta sola para que entre en 30 s; si no entra, avisa que hay que acortar el texto.

Voces en español argentino: `es-AR-ElenaNeural` (mujer) y `es-AR-TomasNeural` (hombre). Hay más en `edge-tts --list-voices`.

## Licencias y créditos

- **Música y efectos:** originales, generados por este código. Sin derechos de terceros.
- **Tipografías:** [Luckiest Guy](https://fonts.google.com/specimen/Luckiest+Guy) (Apache 2.0) y [Montserrat](https://github.com/JulietaUla/Montserrat) (SIL OFL). Licencias en `assets/fonts/`.
- **Voz:** servicio de lectura en voz alta de Microsoft Edge, usado a través de `edge-tts`. Si el canal se va a monetizar, conviene revisar los términos de Microsoft o reemplazar la voz por una con licencia comercial explícita.
