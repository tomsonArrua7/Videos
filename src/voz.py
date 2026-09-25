"""Genera la narración con una voz neuronal de internet (Microsoft Edge TTS).

Sintetiza cada bloque del guion por separado, guarda los tiempos de cada
palabra (para los subtítulos animados) y arma la línea de tiempo del video
para que todo entre en la duración del episodio.

Salida: build/<episodio>/voz/seg_XX.mp3 y build/<episodio>/timeline.json
"""
import asyncio
import json
import os
import ssl
import subprocess
import sys

import aiohttp
import edge_tts
import edge_tts.communicate as _edge_comm
import imageio_ffmpeg

from episodio import BUILD, EP, NOMBRE

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Si hay un proxy corporativo con su propia CA, edge-tts tiene que confiar en ella.
_ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
if _ca and os.path.exists(_ca):
    _edge_comm._SSL_CTX = ssl.create_default_context(cafile=_ca)

# edge-tts pide siempre MP3 de 48 kbps; el servicio también entrega 96 kbps,
# que es la misma voz con la mitad de artefactos de compresión.
FORMATO = "audio-24khz-96kbitrate-mono-mp3"
_send_str = aiohttp.ClientWebSocketResponse.send_str


async def _send_str_hq(self, data, *args, **kwargs):
    return await _send_str(self, data.replace("audio-24khz-48kbitrate-mono-mp3", FORMATO),
                           *args, **kwargs)


aiohttp.ClientWebSocketResponse.send_str = _send_str_hq

INICIO = 0.25      # silencio antes de la primera frase
PAUSA = 0.30       # respiro entre bloques
FINAL_MIN = 0.9    # aire al final para el cierre musical


async def sintetizar(texto, destino, rate):
    com = edge_tts.Communicate(texto, EP.VOZ, rate=rate, pitch=getattr(EP, "VOZ_TONO", "+0Hz"),
                               boundary="WordBoundary")
    palabras = []
    with open(destino, "wb") as f:
        async for trozo in com.stream():
            if trozo["type"] == "audio":
                f.write(trozo["data"])
            elif trozo["type"] == "WordBoundary":
                palabras.append({
                    "t": trozo["offset"] / 1e7,
                    "d": trozo["duration"] / 1e7,
                    "w": trozo["text"],
                })
    return palabras


def duracion_audio(ruta):
    """Duración real del mp3 (ffmpeg la informa al decodificar a null)."""
    out = subprocess.run([FFMPEG, "-i", ruta, "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    t = [linea for linea in out.splitlines() if "time=" in linea][-1]
    hh, mm, ss = t.split("time=")[1].split()[0].split(":")
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


async def generar(rate):
    os.makedirs(os.path.join(BUILD, "voz"), exist_ok=True)
    bloques = []
    for i, b in enumerate(EP.BLOQUES):
        ruta = os.path.join(BUILD, "voz", f"seg_{i:02d}.mp3")
        palabras = await sintetizar(b["texto"], ruta, rate)
        # Edge agrega un poco de silencio al final; usamos el fin de la última palabra.
        fin_habla = palabras[-1]["t"] + palabras[-1]["d"]
        bloques.append({**b, "audio": ruta, "palabras": palabras,
                        "habla": fin_habla, "archivo_dur": duracion_audio(ruta)})
    return bloques


def main():
    print(f"Episodio {NOMBRE} · voz {EP.VOZ}")
    # Probamos velocidades hasta que la narración entre en el tiempo pedido.
    for pct in range(getattr(EP, "VOZ_VELOCIDAD_MIN", 0), 21, 2):
        rate = f"+{pct}%"
        bloques = asyncio.run(generar(rate))
        total = INICIO + sum(b["habla"] for b in bloques) + PAUSA * (len(bloques) - 1)
        print(f"velocidad {rate}: narración {total:.2f}s")
        if total <= EP.DURACION - FINAL_MIN:
            break
    else:
        sys.exit("El guion es demasiado largo para la duración pedida: acortá el texto.")

    # Repartimos el sobrante como pausas extra entre bloques (sin pasarnos).
    sobra = EP.DURACION - FINAL_MIN - total
    extra = min(sobra / max(1, len(bloques) - 1), 0.35)

    t = INICIO
    for b in bloques:
        b["inicio"] = round(t, 3)
        t += b["habla"] + PAUSA + extra
    # Cada escena empieza un poquito antes que su voz (entra la transición).
    for i, b in enumerate(bloques):
        b["escena_ini"] = 0.0 if i == 0 else round(b["inicio"] - 0.25, 3)
    for i, b in enumerate(bloques):
        b["escena_fin"] = bloques[i + 1]["escena_ini"] if i + 1 < len(bloques) else EP.DURACION

    with open(os.path.join(BUILD, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump({"duracion": EP.DURACION, "voz": EP.VOZ, "velocidad": rate, "bloques": bloques},
                  f, ensure_ascii=False, indent=2)
    for b in bloques:
        print(f"  {b['id']:<9} escena {b['escena_ini']:5.2f}-{b['escena_fin']:5.2f}s  "
              f"voz {b['inicio']:5.2f}+{b['habla']:.2f}s  {b['texto']}")


if __name__ == "__main__":
    main()
