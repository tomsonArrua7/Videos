# Grabaciones con voz humana

Si en esta carpeta hay un audio con el nombre del episodio, el video usa esa voz en lugar de la sintética:

```
grabaciones/ep09.m4a      (o .mp3, .ogg, .opus, .wav, .aac, .flac, .webm, .mp4, .3gp, .amr)
```

`python hacer_video.py ep09` lo encuentra solo, lo limpia, ubica cada bloque del guion con Whisper,
lo recorta, lo sincroniza con las animaciones y los subtítulos, y arma el video.
El guion para leer y los consejos para grabar están en [`guiones/ep09_cuerpo_humano.md`](../guiones/ep09_cuerpo_humano.md).

## Cómo subir el audio desde el celular

1. En GitHub, entrá al repositorio y elegí la rama `claude/animated-curiosities-video-0lcxhr`.
2. Abrí esta carpeta (`grabaciones/`) y tocá **Add file → Upload files**.
3. Subí el audio con el nombre `ep09` y la extensión que tenga (por ejemplo `ep09.m4a`) y confirmá con **Commit changes**.

Para probar otro archivo sin moverlo:

```bash
cd src
python voz.py ep09 --grabacion ../ruta/a/mi_audio.m4a
python verificar_voz.py ep09      # opcional: Whisper confirma que se entiende todo
```

El retoque necesita `pip install -r requirements-verificacion.txt` (Whisper) además de `requirements.txt`.
