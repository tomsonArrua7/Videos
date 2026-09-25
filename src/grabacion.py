"""Voz humana: limpia una grabación propia y la acomoda al guion del episodio.

Pasos del retoque:
 1. Lee cualquier formato (m4a de celular, mp3, ogg de WhatsApp, wav...).
 2. Limpieza: saca la continua y los graves que retumban, y baja el ruido de fondo
    con una compuerta espectral (aprende el "perfil" del ruido de los silencios).
 3. Whisper detecta cada palabra con su tiempo, y cada comienzo y final se corrige con
    el nivel real del audio (Whisper adelanta los comienzos y corta las "s" finales).
 4. Ubica cada bloque del guion en la grabación. Si repetiste una frase porque te
    trabaste, se queda con la última toma completa.
 5. Recorta cada bloque, acorta las pausas largas, baja las respiraciones, empareja el volumen
    entre tomas y, solo si no entra en el tiempo, acelera un poquito sin cambiar el tono.

Los subtítulos usan el texto del guion (bien escrito) con los tiempos de tu voz.
Después, sonido.py le aplica la misma cadena de locución que a las voces sintéticas
(ecualización, compresor, de-esser y limitador).
"""
import difflib
import glob
import os
import subprocess

import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, convolve2d, istft, sosfiltfilt, stft

from tiempos import _norm

SR = 44100
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
TEMPO_MAX = 1.15        # más rápido que esto ya se nota
PAUSA_MAX = 0.40        # las pausas más largas dentro de una frase se acortan a esto


def buscar(raiz, patron):
    """Devuelve la grabación (cualquier extensión de audio) o None."""
    for ruta in sorted(glob.glob(os.path.join(raiz, patron + ".*"))):
        if os.path.splitext(ruta)[1].lower() in (".m4a", ".mp3", ".wav", ".ogg", ".opus", ".aac", ".flac",
                                                 ".webm", ".mp4", ".mov", ".3gp", ".amr"):
            return ruta
    return None


def leer(ruta):
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", ruta, "-vn", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def guardar(ruta, x):
    wavfile.write(ruta, SR, np.clip(x, -1, 1).astype(np.float32))


# ------------------------------------------------------------------ limpieza
def quitar_ruido(x, fuerza=2.0, piso_db=-18.0):
    """Compuerta espectral: resta la potencia del ruido medido en los tramos más silenciosos.

    Se resta en potencia (no en amplitud) para que las consonantes suaves que apenas superan
    el ruido ("v", "l", "tr") no se pierdan: con una grabación real, restar en amplitud
    empeoraba lo que entendía Whisper y así mejora respecto del original.
    """
    f, t, Z = stft(x, SR, nperseg=2048, noverlap=1536)
    mag = np.abs(Z)
    energia = mag.sum(axis=0)
    silencios = energia <= np.percentile(energia, 15)
    ruido = np.median(mag[:, silencios], axis=1, keepdims=True) if silencios.any() else \
        np.percentile(mag, 10, axis=1, keepdims=True)
    piso = 10 ** (piso_db / 20)
    ganancia = np.sqrt(np.clip(1 - fuerza * (ruido / (mag + 1e-12)) ** 2, piso ** 2, 1.0))
    # suavizado en tiempo y frecuencia para que no aparezca el "ruido musical"
    nucleo = np.ones((3, 5)) / 15
    ganancia = convolve2d(ganancia, nucleo, mode="same", boundary="symm")
    _, y = istft(Z * ganancia, SR, nperseg=2048, noverlap=1536)
    y = y[: len(x)]
    antes = 20 * np.log10(np.sqrt(np.mean(x[_tramos(x, silencios, t)] ** 2)) + 1e-12)
    despues = 20 * np.log10(np.sqrt(np.mean(y[_tramos(y, silencios, t)] ** 2)) + 1e-12)
    return y, antes, despues


def _tramos(x, mascara_frames, t):
    idx = np.zeros(len(x), bool)
    paso = t[1] - t[0] if len(t) > 1 else 0.01
    for tt in t[mascara_frames]:
        a, b = int(tt * SR), int((tt + paso) * SR)
        idx[a:min(b, len(x))] = True
    return idx if idx.any() else np.ones(len(x), bool)


def limpiar(x):
    x = x - np.mean(x)
    x = sosfiltfilt(butter(4, 75, btype="highpass", fs=SR, output="sos"), x)
    y, antes, despues = quitar_ruido(x)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.9, antes, despues


# ------------------------------------------------- palabras y ubicación
def palabras_oidas(ruta_wav, pista):
    from faster_whisper import WhisperModel
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(ruta_wav, language="es", word_timestamps=True, beam_size=5,
                                initial_prompt=pista, vad_filter=False)
    out = []
    for s in segs:
        for w in s.words or []:
            n = _norm(w.word)
            if n:
                out.append({"n": n, "t0": w.start, "t1": w.end, "w": w.word.strip()})
    return out


def _tokens(texto):
    return [(tok, _norm(tok)) for tok in texto.split() if _norm(tok)]


def ubicar(oidas, bloques_texto):
    """Para cada bloque, la ventana de palabras oídas que mejor coincide (la última, si hay tomas repetidas)."""
    ubicados, desde = [], 0
    for i, texto in enumerate(bloques_texto):
        esperado = [n for _, n in _tokens(texto)]
        m = len(esperado)
        resto_min = sum(max(1, len(_tokens(tx)) - 3) for tx in bloques_texto[i + 1:])
        mejor = (-1.0, desde, desde + m)
        for s in range(desde, max(desde + 1, len(oidas) - resto_min - max(1, m - 3) + 1)):
            for largo in range(max(1, m - 3), m + 4):
                if s + largo > len(oidas):
                    break
                r = difflib.SequenceMatcher(None, esperado, [o["n"] for o in oidas[s:s + largo]]).ratio()
                if r >= mejor[0] - 1e-9 and (r > mejor[0] + 0.02 or s >= mejor[1]):
                    mejor = (r, s, s + largo)
        r, s, e = mejor
        ubicados.append((r, s, e))
        desde = e
    return ubicados


def tiempos_de_palabras(texto, ventana):
    """Tiempos (absolutos) para cada palabra del guion, usando las palabras oídas de la ventana."""
    tok = _tokens(texto)
    esperado = [n for _, n in tok]
    oido = [o["n"] for o in ventana]
    t0s = [None] * len(tok)
    t1s = [None] * len(tok)
    sm = difflib.SequenceMatcher(None, esperado, oido)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            t0s[a + k], t1s[a + k] = ventana[b + k]["t0"], ventana[b + k]["t1"]
    # las que no se reconocieron quedan entre sus vecinas
    conocidos = [i for i, v in enumerate(t0s) if v is not None]
    if not conocidos:
        raise ValueError(f"No se reconoció el bloque: {texto}")
    for i in range(len(tok)):
        if t0s[i] is None:
            antes = max([j for j in conocidos if j < i], default=None)
            despues = min([j for j in conocidos if j > i], default=None)
            ini = t1s[antes] if antes is not None else t0s[despues] - 0.3
            fin = t0s[despues] if despues is not None else t1s[antes] + 0.3
            huecos = (despues if despues is not None else len(tok)) - (antes if antes is not None else -1)
            paso = (fin - ini) / huecos
            orden = i - (antes if antes is not None else -1)
            t0s[i], t1s[i] = ini + paso * (orden - 1), ini + paso * orden
    return [(tok[i][0], t0s[i], t1s[i]) for i in range(len(tok))]


# ----------------------------------------------- ajuste fino con la señal
def _envolvente(x):
    """Nivel en dB cada 10 ms, en la banda de la voz (sin retumbes graves que confundan un silencio con habla)."""
    x = sosfiltfilt(butter(4, [250, 8000], btype="bandpass", fs=SR, output="sos"), x)
    h = int(0.01 * SR)
    n = len(x) // h
    return 20 * np.log10(np.sqrt(np.mean(x[:n * h].reshape(n, h) ** 2, axis=1)) + 1e-9)


def _nucleo(env, a, z, umbral, hueco=0.2):
    """Tramo con sonido de una palabra. Whisper suele estirarla sobre el silencio de al lado (antes o
    después): si adentro hay un hueco largo, la palabra es el tramo con más sonido."""
    i0, i1 = int(a * 100), min(int(z * 100), len(env))
    activos = [k for k in range(i0, i1) if env[k] > umbral]
    if not activos:
        return a, z
    grupos = [[activos[0], activos[0]]]
    for k in activos[1:]:
        if k - grupos[-1][1] > hueco * 100:
            grupos.append([k, k])
        else:
            grupos[-1][1] = k
    g = max(grupos, key=lambda g: g[1] - g[0])
    return g[0] / 100, (g[1] + 1) / 100


def _fin_real(env, t1, limite, umbral):
    """Whisper también suele cortar antes el final (la "s" de "seis"): se extiende mientras siga sonando."""
    k, tope = int(t1 * 100), min(int(limite * 100), len(env))
    ultimo, hueco = k - 1, 0
    while k < tope and hueco <= 4:
        if env[k] > umbral:
            ultimo, hueco = k, 0
        else:
            hueco += 1
        k += 1
    return max(t1, (ultimo + 1) / 100)


def ajustar_a_la_voz(env, pals, limite, umbral_voz, umbral_cola):
    """Corrige los tiempos de Whisper con el nivel real de la grabación."""
    pals = [(w, *_nucleo(env, a, z, umbral_voz)) for w, a, z in pals]
    out = []
    for i, (w, a, z) in enumerate(pals):
        sig = pals[i + 1][1] - 0.03 if i + 1 < len(pals) else limite
        z = min(_fin_real(env, z, min(sig, z + 0.6), umbral_cola), max(sig, z))
        out.append((w, a, max(z, a + 0.05)))
    return out


# ------------------------------------------------------------ armado
def _cortar(x, a, b):
    a, b = max(0, int(a * SR)), min(len(x), int(b * SR))
    seg = x[a:b].copy()
    f = int(0.012 * SR)
    if len(seg) > 2 * f:
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
    return seg


def _bajar_respiraciones(seg, palabras, db=-12.0):
    """Baja los huecos largos entre palabras (respiraciones, ruiditos de boca)."""
    g = np.ones(len(seg))
    rampa = int(0.015 * SR)
    for (_, _, fin), (_, ini, _) in zip(palabras, palabras[1:]):
        if ini - fin > 0.2:
            a, b = int((fin + 0.04) * SR), int((ini - 0.04) * SR)
            if b - a > 2 * rampa:
                g[a:b] = 10 ** (db / 20)
                g[a:a + rampa] = np.linspace(1, 10 ** (db / 20), rampa)
                g[b - rampa:b] = np.linspace(10 ** (db / 20), 1, rampa)
    return seg * g


def _acortar_pausas(seg, pals, maximo=PAUSA_MAX):
    """Saca el aire de más de las pausas largas dentro de un bloque, como un corte de edición."""
    cortes = []
    for (_, _, fin), (_, ini, _) in zip(pals, pals[1:]):
        if ini - fin > maximo:
            medio, sobra = (fin + ini) / 2, ini - fin - maximo
            cortes.append((medio - sobra / 2, medio + sobra / 2))
    if not cortes:
        return seg, pals, 0.0
    fundido = int(0.01 * SR)
    trozos, pos = [], 0
    for a, b in cortes:
        trozos.append(seg[pos:int(a * SR)])
        pos = int(b * SR)
    trozos.append(seg[pos:])
    out = trozos[0]
    for tr in trozos[1:]:
        n = min(fundido, len(out), len(tr))
        cruce = out[len(out) - n:] * np.linspace(1, 0, n) + tr[:n] * np.linspace(0, 1, n)
        out = np.concatenate([out[:len(out) - n], cruce, tr[n:]])
    quitado = [(b, b - a + fundido / SR) for a, b in cortes]
    nuevas = [(w, a - sum(q for b, q in quitado if b <= a + 1e-9), z - sum(q for b, q in quitado if b <= a + 1e-9))
              for w, a, z in pals]
    return out, nuevas, sum(q for _, q in quitado)


def _atempo(ruta, factor):
    tmp = ruta + ".tmp.wav"
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", ruta, "-filter:a", f"atempo={factor:.4f}", tmp], check=True)
    os.replace(tmp, ruta)


def procesar(ruta, bloques, carpeta, presupuesto, separar):
    """Devuelve los bloques con su audio recortado y los tiempos de cada palabra.

    `presupuesto`: segundos disponibles para la voz (sin contar pausas).
    `separar`: función de voz.py que devuelve (texto dicho, texto mostrado, pares).
    """
    os.makedirs(carpeta, exist_ok=True)
    x, ruido_antes, ruido_despues = limpiar(leer(ruta))
    limpio = os.path.join(carpeta, "grabacion_limpia.wav")
    guardar(limpio, x)
    textos = [separar(b["texto"])[1] for b in bloques]
    oidas = palabras_oidas(limpio, " ".join(textos))
    ubicados = ubicar(oidas, textos)

    env = _envolvente(x)
    ruido = np.percentile(env, 10)
    umbral_voz = max(ruido + 18, env.max() - 32)     # vocales y consonantes fuertes
    umbral_cola = max(ruido + 12, env.max() - 40)    # finales suaves ("s", "f"), no respiraciones ni eco

    salida, informe, acortado = [], [], 0.0
    for i, (b, texto, (r, s, e)) in enumerate(zip(bloques, textos, ubicados)):
        limite = len(x) / SR
        if e < len(oidas):
            limite = _nucleo(env, oidas[e]["t0"], oidas[e]["t1"], umbral_voz)[0] - 0.03
        pals = ajustar_a_la_voz(env, tiempos_de_palabras(texto, oidas[s:e]), limite, umbral_voz, umbral_cola)
        ini = max(pals[0][1] - 0.10, oidas[s - 1]["t1"] + 0.02 if s > 0 else 0)
        fin = min(pals[-1][2] + 0.10, limite)
        seg = _cortar(x, ini, fin)
        rel = [(w, a - ini, z - ini) for w, a, z in pals]
        seg, rel, quitado = _acortar_pausas(seg, rel)
        acortado += quitado
        seg = _bajar_respiraciones(seg, rel)
        salida.append({"b": b, "texto": texto, "seg": seg, "pals": rel})
        informe.append(f"  {b.get('_etiqueta', b['id']):<11} coincidencia {r:.0%}  "
                       f"({ini:5.2f}s → {fin:5.2f}s de la grabación)")

    # volumen parejo entre tomas
    rms = [np.sqrt(np.mean(o["seg"][np.abs(o["seg"]) > 0.02] ** 2)) for o in salida]
    objetivo = float(np.median(rms))
    for o, r in zip(salida, rms):
        o["seg"] = o["seg"] * (objetivo / (r + 1e-9))
    pico = max(np.max(np.abs(o["seg"])) for o in salida)

    habla = sum(o["pals"][-1][2] for o in salida)
    factor = 1.0
    if habla > presupuesto:
        factor = min(TEMPO_MAX, habla / presupuesto)
    bloques_out = []
    for i, o in enumerate(salida):
        ruta_seg = os.path.join(carpeta, f"seg_{i:02d}.wav")
        guardar(ruta_seg, o["seg"] / pico * 0.9)
        if factor > 1.001:
            _atempo(ruta_seg, factor)
        palabras = [{"t": a / factor, "d": (z - a) / factor, "w": w.strip(",.:;!?¡¿…\"'()")} for w, a, z in o["pals"]]
        decir, mostrar, _ = separar(o["b"]["texto"])
        bloques_out.append({**o["b"], "texto": mostrar, "texto_dicho": decir, "audio": ruta_seg,
                            "palabras": palabras, "habla": palabras[-1]["t"] + palabras[-1]["d"],
                            "archivo_dur": len(o["seg"]) / SR / factor})
    informe = [f"Grabación: {os.path.basename(ruta)}",
               f"Ruido de fondo: {ruido_antes:.1f} dBFS → {ruido_despues:.1f} dBFS",
               f"Velocidad: {'sin cambios' if factor <= 1.001 else f'+{(factor - 1) * 100:.0f} % (sin cambiar el tono)'}"
               + (" — ¡AVISO: sigue sin entrar, conviene leer un poco más rápido!" if habla / factor > presupuesto + 0.05
                  else ""),
               f"Pausas largas acortadas: {acortado:.1f} s en total",
               "Bloques ubicados:"] + informe
    return bloques_out, informe
