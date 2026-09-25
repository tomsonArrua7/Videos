# Videos de curiosidades 🤯

Video animado de **30 segundos**, vertical (1080×1920, 30 fps), listo para Shorts, Reels y TikTok:
**"3 curiosidades que te van a volar la cabeza"** (el pulpo, la miel y Venus).

- 🎬 Video final: [`output/curiosidades_30s.mp4`](output/curiosidades_30s.mp4)
- 🖼️ Portada / miniatura: [`output/portada.png`](output/portada.png)
- 📝 Guion con tiempos, datos verificados y texto para publicar: [`guion.md`](guion.md)

## Cómo está hecho

Todo se genera con código, sin editor de video:

| Parte | Cómo | Archivo |
|---|---|---|
| Guion | Texto de cada escena | `src/guion.py` |
| Voz | Voz neuronal gratuita de Microsoft Edge (`es-AR-TomasNeural`) vía [`edge-tts`](https://github.com/rany2/edge-tts), con tiempos por palabra | `src/voz.py` |
| Música y efectos | Tema original sintetizado con numpy (batería, bajo, pizzicato, campanitas) + whooshes, pops, explosión, "ding"; la música baja sola cuando habla la voz y todo sale a −14 LUFS | `src/sonido.py` |
| Animación | Personajes, fondos, subtítulos karaoke y transiciones dibujados con Pillow, sincronizados con cada palabra de la voz | `src/animacion.py` |
| Sincronía | Momentos clave anclados a palabras ("cabeza", "sangre", "comer", "año"...) | `src/tiempos.py` |

## Regenerar el video

Requiere Python 3.10+ y conexión a internet (para la voz). ffmpeg viene incluido con `imageio-ffmpeg`.

```bash
pip install -r requirements.txt
python hacer_video.py
```

Tarda alrededor de un minuto. Para ver cuadros sueltos sin exportar todo:

```bash
cd src && python animacion.py --previa 2.5 5 12.3   # -> build/previa/*.png
```

### Cambiar cosas

- **Texto de la voz:** editá `BLOQUES` en `src/guion.py`. La velocidad de la voz se ajusta sola para que entre en 30 s.
- **Otra voz:** cambiá `VOZ` en `src/guion.py`. Algunas opciones: `es-AR-ElenaNeural` (mujer, Argentina), `es-MX-JorgeNeural`, `es-MX-DaliaNeural`, `es-ES-AlvaroNeural`. Lista completa: `edge-tts --list-voices`.
- **Duración:** `DURACION` en `src/guion.py`.
- Si cambiás palabras que disparan animaciones (por ejemplo "cabeza" o "comer"), actualizá `eventos()` en `src/tiempos.py`.

## Licencias y créditos

- **Música y efectos:** originales, generados por este código. Sin derechos de terceros.
- **Tipografías:** [Luckiest Guy](https://fonts.google.com/specimen/Luckiest+Guy) (Apache 2.0) y [Montserrat](https://github.com/JulietaUla/Montserrat) (SIL OFL). Licencias en `assets/fonts/`.
- **Voz:** servicio de lectura en voz alta de Microsoft Edge, usado a través de `edge-tts`. Si el canal se va a monetizar, conviene revisar los términos de Microsoft o reemplazar la voz por una con licencia comercial explícita.
