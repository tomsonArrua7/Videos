"""Genera la narración con una voz neuronal de internet (Microsoft Edge TTS).

Sintetiza cada bloque del guion por separado, guarda los tiempos de cada
palabra (para los subtítulos animados) y arma la línea de tiempo del video
para que todo entre en la duración del episodio.

Salida: build/<episodio>/voz/seg_XX.mp3 y build/<episodio>/timeline.json
"""
import asyncio
import json
import math
import os
import re
import ssl
import subprocess
import sys

import aiohttp
import edge_tts
import edge_tts.communicate as _edge_comm
import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile

import grabacion
from episodio import BUILD, EP, NOMBRE, RAIZ, argumentos
from tiempos import _norm

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

INICIO = 0.25                                  # silencio antes de la primera frase
PAUSA = getattr(EP, "VOZ_PAUSA", 0.30)         # respiro entre bloques
FINAL_MIN = getattr(EP, "VOZ_FINAL", 0.9)      # aire al final para el cierre musical


# Pronunciación: en el guion se escribe {cómo se muestra|cómo se dice}, por ejemplo
# "{Jurassic Park|Yúrasic Park}". La voz lee la segunda forma y los subtítulos
# muestran la primera. Lo dicho puede tener más palabras que lo mostrado
# ("{Jesse Pinkman|Yési Pínc man}"): las sobrantes se suman a la última palabra.
MARCA = re.compile(r"\{([^|{}]+)\|([^{}]+)\}")
PUNTUACION = ",.:;!?¡¿…\"'()"


def separar(texto):
    """Devuelve (texto a decir, texto a mostrar, [(palabra dicha, palabra mostrada)])."""
    pares = []
    pos = 0
    for m in list(MARCA.finditer(texto)) + [None]:
        tramo = texto[pos:m.start() if m else len(texto)]
        pares += [(w, w) for w in tramo.split()]
        if m:
            mostrar, decir = m.group(1).split(), m.group(2).split()
            if len(decir) < len(mostrar):
                raise ValueError(f"'{m.group(0)}': lo dicho no puede tener menos palabras que lo mostrado")
            mostrar += [None] * (len(decir) - len(mostrar))
            pares += list(zip(decir, mostrar))
            pos = m.end()
    return MARCA.sub(lambda m: m.group(2), texto), MARCA.sub(lambda m: m.group(1), texto), pares


# Silencio dentro de un bloque: "¿Qué animal...? [3s] ¡El koala!" deja 3 segundos entre la
# pregunta y la respuesta (el tiempo para pensar de los quiz). Cada parte se sintetiza, o se
# busca en la grabación, por separado; después se vuelven a juntar en un solo bloque.
SILENCIO = re.compile(r"\s*\[(\d+(?:[.,]\d+)?)\s*s\]\s*")


def partes(bloques):
    out = []
    for i, b in enumerate(bloques):
        trozos = SILENCIO.split(b["texto"])
        for k in range(0, len(trozos), 2):
            silencio = float(trozos[k + 1].replace(",", ".")) if k + 1 < len(trozos) else 0.0
            etiqueta = b["id"] if len(trozos) == 1 else f"{b['id']}.{k // 2 + 1}"
            out.append({**b, "texto": trozos[k].strip(), "_bloque": i, "_silencio": silencio, "_etiqueta": etiqueta})
    return out


def silencios(bloques):
    return sum(sum(float(x.replace(",", ".")) for x in SILENCIO.findall(b["texto"])) for b in bloques)


def unir(hechas, bloques):
    """Junta las partes de cada bloque: un solo audio y las palabras corridas por el silencio."""
    out = []
    for i, b in enumerate(bloques):
        ps = [p for p in hechas if p["_bloque"] == i]
        if len(ps) == 1:
            out.append({k: v for k, v in ps[0].items() if not k.startswith("_")})
            continue
        t, palabras, tramos, pistas = 0.0, [], [], []
        for p in ps:
            palabras += [{**w, "t": round(w["t"] + t, 3)} for w in p["palabras"]]
            tramos.append({"ini": round(t, 3), "fin": round(t + p["habla"], 3)})
            pistas.append((t, p["audio"]))
            t += p["habla"] + p["_silencio"]
        ruta = os.path.join(BUILD, "voz", f"bloque_{i:02d}.wav")
        dur = juntar_audios(pistas, ruta)
        out.append({**b, "texto": " ".join(p["texto"] for p in ps),
                    "texto_dicho": " ".join(p["texto_dicho"] for p in ps), "audio": ruta,
                    "palabras": palabras, "habla": tramos[-1]["fin"], "archivo_dur": dur, "partes": tramos})
    return out


def juntar_audios(pistas, destino, sr=44100):
    """Mezcla varios audios, cada uno en su segundo, en un wav."""
    sonidos = []
    for t, ruta in pistas:
        raw = subprocess.run([FFMPEG, "-v", "error", "-i", ruta, "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"],
                             capture_output=True, check=True).stdout
        sonidos.append((int(t * sr), np.frombuffer(raw, dtype=np.float32)))
    y = np.zeros(max(i + len(x) for i, x in sonidos), dtype=np.float32)
    for i, x in sonidos:
        y[i:i + len(x)] += x
    wavfile.write(destino, sr, y)
    return len(y) / sr


def a_mostrar(palabras, pares):
    """Cambia cada palabra que devolvió la voz por su versión para subtítulos."""
    j = 0
    salida = []
    for w in palabras:
        for k in range(j, len(pares)):
            if _norm(pares[k][0]) == _norm(w["w"]):
                j = k + 1
                if pares[k][1] is None and salida:   # sílaba extra de un nombre: se une a la anterior
                    salida[-1]["d"] = w["t"] + w["d"] - salida[-1]["t"]
                    w = None
                else:
                    w["w"] = pares[k][1].strip(PUNTUACION)
                break
        if w is not None:
            salida.append(w)
    return salida


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
    for i, b in enumerate(partes(EP.BLOQUES)):
        ruta = os.path.join(BUILD, "voz", f"seg_{i:02d}.mp3")
        decir, mostrar, pares = separar(b["texto"])
        palabras = a_mostrar(await sintetizar(decir, ruta, rate), pares)
        # Edge agrega un poco de silencio al final; usamos el fin de la última palabra.
        fin_habla = palabras[-1]["t"] + palabras[-1]["d"]
        bloques.append({**b, "texto": mostrar, "texto_dicho": decir, "audio": ruta, "palabras": palabras,
                        "habla": fin_habla, "archivo_dur": duracion_audio(ruta)})
    return unir(bloques, EP.BLOQUES)


def grabacion_propia():
    """Ruta de la grabación humana del episodio (o None): `--grabacion archivo` o EP.GRABACION."""
    args = argumentos()
    if "--grabacion" in args:
        return args[args.index("--grabacion") + 1]
    patron = getattr(EP, "GRABACION", None)
    return grabacion.buscar(RAIZ, patron) if patron else None


def con_voz_humana(ruta):
    fijo = (INICIO + PAUSA * (len(EP.BLOQUES) - 1) + sum(b.get("pausa_despues", 0) for b in EP.BLOQUES)
            + silencios(EP.BLOQUES))
    presupuesto = EP.DURACION - FINAL_MIN - fijo
    hechas, informe = grabacion.procesar(ruta, partes(EP.BLOQUES), os.path.join(BUILD, "voz"), presupuesto,
                                         separar)
    bloques = unir(hechas, EP.BLOQUES)
    print("\n".join(informe))
    with open(os.path.join(BUILD, "grabacion_informe.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(informe) + "\n")
    total = INICIO + sum(b["habla"] + b.get("pausa_despues", 0) for b in bloques) + PAUSA * (len(bloques) - 1)
    return bloques, total, "grabación"


def main():
    ruta = grabacion_propia()
    if ruta:
        print(f"Episodio {NOMBRE} · voz humana ({ruta})")
        bloques, total, rate = con_voz_humana(ruta)
    else:
        print(f"Episodio {NOMBRE} · voz {EP.VOZ}")
        # Probamos velocidades hasta que la narración entre en el tiempo pedido.
        for pct in range(getattr(EP, "VOZ_VELOCIDAD_MIN", 0), 21, 2):
            rate = f"+{pct}%"
            bloques = asyncio.run(generar(rate))
            total = (INICIO + sum(b["habla"] + b.get("pausa_despues", 0) for b in bloques)
                     + PAUSA * (len(bloques) - 1))
            print(f"velocidad {rate}: narración {total:.2f}s")
            if total <= EP.DURACION - FINAL_MIN:
                break
        else:
            sys.exit("El guion es demasiado largo para la duración pedida: acortá el texto.")

    # Con voz humana, si aun acelerando no entra, el video se estira unas décimas (mejor que cortar la voz).
    duracion = max(EP.DURACION, math.ceil((total + FINAL_MIN) * 10 - 1e-6) / 10)
    if duracion > EP.DURACION:
        print(f"AVISO: la narración no entra en {EP.DURACION:.0f} s; el video dura {duracion:.1f} s.")
    # Repartimos el sobrante como pausas extra entre bloques (sin pasarnos).
    sobra = max(0.0, duracion - FINAL_MIN - total)
    extra = min(sobra / max(1, len(bloques) - 1), 0.35)

    t = INICIO
    for b in bloques:
        b["inicio"] = round(t, 3)
        t += b["habla"] + PAUSA + extra + b.get("pausa_despues", 0)
    # Cada escena empieza un poquito antes que su voz (entra la transición).
    for i, b in enumerate(bloques):
        b["escena_ini"] = 0.0 if i == 0 else round(b["inicio"] - 0.25, 3)
    for i, b in enumerate(bloques):
        b["escena_fin"] = bloques[i + 1]["escena_ini"] if i + 1 < len(bloques) else duracion

    with open(os.path.join(BUILD, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump({"duracion": duracion, "voz": "humana" if ruta else EP.VOZ, "velocidad": rate,
                   "bloques": bloques},
                  f, ensure_ascii=False, indent=2)
    for b in bloques:
        print(f"  {b['id']:<9} escena {b['escena_ini']:5.2f}-{b['escena_fin']:5.2f}s  "
              f"voz {b['inicio']:5.2f}+{b['habla']:.2f}s  {b['texto']}")


if __name__ == "__main__":
    main()
