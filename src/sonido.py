"""Música original + efectos de sonido + mezcla con la voz.

Todo se sintetiza acá con numpy (nada de samples externos), así la música es
100 % propia y libre de derechos.

Salida (en build/<episodio>/): musica.wav, sfx.wav, audio_final.wav
"""
import json
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, lfilter, sosfilt, sosfiltfilt

from episodio import BUILD, EP
from tiempos import GANCHO_COMUN, Linea, eventos

SR = 44100
BPM = 120
BEAT = 60 / BPM
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- utilidades
def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a=0.005, r=0.03):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def filtro(x, tipo, f, orden=2):
    return sosfilt(butter(orden, f, btype=tipo, fs=SR, output="sos"), x)


def pegar(pista, sonido, t, gan=1.0):
    i = int(t * SR)
    if i >= len(pista) or i + len(sonido) <= 0:
        return
    if i < 0:
        sonido, i = sonido[-i:], 0
    j = min(len(pista), i + len(sonido))
    pista[i:j] += gan * sonido[: j - i]


def reverb(x, dur=1.8, caida=0.45, mezcla=0.25):
    t = tt(dur)
    ir = rng.standard_normal(len(t)) * np.exp(-t / caida)
    ir = filtro(ir, "lowpass", 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = fftconvolve(x, ir)[: len(x)]
    return x + mezcla * wet


# ------------------------------------------------------------- instrumentos
def pluck(f, dur=0.35):
    t = tt(dur)
    y = sum((1 / k ** 1.3) * np.sin(2 * np.pi * k * f * t) * np.exp(-t * (4 + 3 * k))
            for k in range(1, 9))
    return y * env_adsr(len(t), 0.002, 0.02)


def glock(f, dur=1.2):
    t = tt(dur)
    parciales = [(1, 1.0, 3.0), (2.76, 0.35, 7), (5.40, 0.15, 12), (8.93, 0.06, 18)]
    y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in parciales)
    return y * env_adsr(len(t), 0.001, 0.05)


def bajo(f, dur):
    t = tt(dur)
    y = sum((1 / k) * np.sin(2 * np.pi * k * f * t) for k in (1, 3, 5, 7)) * 0.6
    y += 0.8 * np.sin(2 * np.pi * f * t)
    y *= np.exp(-t * 2.5) * 0.7 + 0.3
    return np.tanh(1.5 * y) * env_adsr(len(t), 0.004, 0.04)


def pad(fs, dur):
    t = tt(dur)
    y = np.zeros_like(t)
    for f in fs:
        for det in (-0.004, 0.0, 0.004):
            ff = f * (1 + det)
            y += sum(((-1) ** k) / k * np.sin(2 * np.pi * k * ff * t) * np.exp(-k * 0.35)
                     for k in range(1, 10))
    y /= len(fs) * 3
    return y * env_adsr(len(t), 0.35, 0.5)


def bombo(dur=0.45):
    t = tt(dur)
    fase = 2 * np.pi * np.cumsum(48 + 120 * np.exp(-t * 32)) / SR
    y = np.sin(fase) * np.exp(-t * 8)
    clic = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.3
    return np.tanh(1.8 * (y + clic))


def palmas(dur=0.3):
    t = tt(dur)
    ruido = filtro(rng.standard_normal(len(t)), "bandpass", [900, 3200])
    env = np.exp(-t * 18)
    for d in (0.0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) * 180), 0) * 0.8
    return ruido * env * 0.9


def hihat(dur=0.06, caida=70):
    t = tt(dur)
    return filtro(rng.standard_normal(len(t)), "highpass", 7000) * np.exp(-t * caida) * 0.5


# ------------------------------------------------------------------- música
ACORDES = [  # La menor: Am - F - C - G (un acorde por compás)
    [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62],
]
ARP = [0, 1, 2, 1, 2, 0, 1, 2, 0, 2, 1, 2, 0, 1, 2, 1]          # 16 semicorcheas
MELODIA = [  # (pulso dentro de 2 compases, midi, duración) - motivo "curioso"
    (0, 76, 1), (1, 81, 0.5), (1.5, 79, 0.5), (2, 76, 1), (3, 74, 1),
    (4, 72, 0.5), (4.5, 74, 0.5), (5, 76, 1.5), (7, 69, 1),
]


def musica(dur, t_final):
    n = int((dur + 2) * SR)
    drums, hats, bass, harm, arp, lead = (np.zeros(n) for _ in range(6))
    compases = int(np.ceil(t_final / (4 * BEAT)))

    for c in range(compases):
        t0 = c * 4 * BEAT
        acorde = ACORDES[c % 4]
        raiz = acorde[0] - 12
        lleno = c >= 1                      # el primer compás entra más liviano
        # batería
        for p in range(4):
            tb = t0 + p * BEAT
            if tb >= t_final:
                break
            if lleno or p % 2 == 0:
                pegar(drums, bombo(), tb, 0.9)
            if lleno and p in (1, 3):
                pegar(drums, palmas(), tb, 0.45)
            for s in (0, 0.5):
                abierto = lleno and s == 0.5 and p == 3 and c % 2
                pegar(hats, hihat(0.2, 14) if abierto else hihat(), tb + s * BEAT,
                      0.22 if s else 0.14)
            if lleno and c % 2 and p == 2:
                pegar(drums, bombo(), tb + 0.75 * BEAT, 0.5)   # síncopa
        # bajo: raíz en corcheas con salto de octava
        for k in range(8):
            tb = t0 + k * BEAT / 2
            if tb >= t_final:
                break
            nota = raiz + (12 if k in (3, 7) else 0)
            pegar(bass, bajo(hz(nota), BEAT / 2 * 0.9), tb, 0.33)
        # pad + arpegio
        pegar(harm, pad([hz(m) for m in acorde], 4 * BEAT + 0.4), t0, 0.16)
        for k, idx in enumerate(ARP):
            tb = t0 + k * BEAT / 4
            if tb >= t_final:
                break
            oct_ = 12 if k % 8 >= 4 else 0
            pegar(arp, pluck(hz(acorde[idx] + 12 + oct_)), tb, 0.11)
        # melodía cada dos compases
        if c % 2 == 0:
            for pulso, m, d in MELODIA:
                tb = t0 + pulso * BEAT
                if tb < t_final - 0.2:
                    pegar(lead, glock(hz(m), d * BEAT + 0.6), tb, 0.10)

    # "pumping" del pad y el bajo con el bombo, estilo sidechain
    t = np.arange(n) / SR
    fase = (t % BEAT) / BEAT
    bomba = 1 - 0.45 * np.exp(-fase * 9)
    centro = drums + (bass + harm) * bomba
    arp *= bomba
    # estéreo: arpegio un poco a la izquierda, campanitas y platillos a la derecha
    izq = centro + 0.85 * arp + 0.55 * lead + 0.6 * hats
    der = centro + 0.55 * arp + 0.85 * lead + 0.9 * hats

    # acorde final
    final = np.zeros(n)
    for m in [45, 57, 60, 64, 69, 76]:
        pegar(final, pad([hz(m)], 2.2), t_final, 0.18)
        pegar(final, glock(hz(m + 12), 2.0), t_final, 0.07)
    pegar(final, bombo(0.8), t_final, 0.9)
    izq += final
    der += final

    # una reverb distinta por canal (ruido distinto) abre la imagen estéreo
    mezcla = np.stack([reverb(izq, mezcla=0.18), reverb(der, mezcla=0.18)], axis=1)
    mezcla = mezcla[: int(dur * SR)]
    # fade in cortito y fade out al final
    f_in = int(0.05 * SR)
    mezcla[:f_in] *= np.linspace(0, 1, f_in)[:, None]
    f_out = int(0.6 * SR)
    mezcla[-f_out:] *= (np.linspace(1, 0, f_out) ** 2)[:, None]
    return mezcla


# -------------------------------------------------------- efectos de sonido
def whoosh(dur=0.45, f0=300, f1=4000):
    n = int(dur * SR)
    out = np.zeros(n + 2048)
    ruido = rng.standard_normal(n + 2048)
    paso = 512
    win = np.hanning(1024)
    for i in range(0, n, paso):
        x = i / n
        fc = f0 * (f1 / f0) ** np.sin(np.pi * x * 0.85)
        seg = ruido[i: i + 1024]
        seg = filtro(seg, "bandpass", [fc * 0.7, min(fc * 1.4, SR / 2 - 100)])
        out[i: i + 1024] += seg * win * np.sin(np.pi * x) ** 1.5
    return out[:n] * 0.9


def pop(f0=900, f1=260, dur=0.12):
    t = tt(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)


def bloop():
    t = tt(0.25)
    f = 250 + 700 * (1 - np.exp(-t * 14))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * env_adsr(len(t), 0.01, 0.03)


def boom():
    t = tt(1.2)
    y = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t * 10)) / SR) * np.exp(-t * 3.5)
    ruido = filtro(rng.standard_normal(len(t)), "lowpass", 1800) * np.exp(-t * 5)
    return np.tanh(2.2 * (y + 0.8 * ruido)) * 0.9


def golpe():
    t = tt(0.4)
    y = np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 25)) / SR) * np.exp(-t * 12)
    ruido = filtro(rng.standard_normal(len(t)), "bandpass", [200, 2500]) * np.exp(-t * 25)
    return np.tanh(2 * (y + 0.6 * ruido))


def tic():
    t = tt(0.03)
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 200)


def tictac(agudo=True):
    """Tic de reloj de cuenta regresiva (madera + clic metálico)."""
    t = tt(0.08)
    f = 1900 if agudo else 1500
    madera = np.sin(2 * np.pi * f * t) * np.exp(-t * 90)
    clac = filtro(rng.standard_normal(len(t)), "bandpass", [2500, 7000]) * np.exp(-t * 160)
    return 0.7 * madera + 0.5 * clac


def acierto():
    """Respuesta correcta: dos notas que suben, con brillo."""
    y = np.zeros(int(1.3 * SR))
    pegar(y, glock(hz(84), 1.0), 0.0, 0.8)
    pegar(y, glock(hz(91), 1.2), 0.11, 1.0)
    pegar(y, glock(hz(96), 1.1), 0.11, 0.45)
    return y


def ding():
    return glock(hz(88), 1.4) + 0.5 * glock(hz(95), 1.4)


def clic():
    t = tt(0.05)
    return filtro(rng.standard_normal(len(t)), "bandpass", [1500, 6000]) * np.exp(-t * 120)


def error_():
    """Chicharra de 'incorrecto' (dos pulsos)."""
    t = tt(0.34)
    y = np.sign(np.sin(2 * np.pi * 160 * t)) + 0.6 * np.sign(np.sin(2 * np.pi * 241 * t))
    y = filtro(y, "lowpass", 2200) * 0.35
    return y * ((t < 0.13) | ((t > 0.18) & (t < 0.31))) * env_adsr(len(t), 0.004, 0.03)


def poof():
    t = tt(0.55)
    ruido = filtro(rng.standard_normal(len(t)), "lowpass", 1600) * np.exp(-t * 7)
    grave = np.sin(2 * np.pi * np.cumsum(110 + 220 * np.exp(-t * 18)) / SR) * np.exp(-t * 9)
    return (0.9 * ruido + 0.4 * grave) * env_adsr(len(t), 0.012, 0.05)


def nam():
    """Bocado: 'ñam'."""
    t = tt(0.17)
    y = np.sin(2 * np.pi * np.cumsum(130 + 380 * np.exp(-t * 16)) / SR) * np.exp(-t * 20)
    mordida = filtro(rng.standard_normal(len(t)), "bandpass", [900, 3500]) * np.exp(-t * 70) * 0.45
    return (y + mordida) * env_adsr(len(t), 0.003, 0.02)


def geiger(dur, tasa=18.0):
    """Clics al azar de un contador Geiger."""
    y = np.zeros(int(dur * SR))
    t = 0.0
    while True:
        t += rng.exponential(1 / tasa)
        if t >= dur - 0.01:
            break
        tc = tt(0.006)
        clic_ = filtro(rng.standard_normal(len(tc)), "bandpass", [1800, 9000]) * np.exp(-tc * 900)
        pegar(y, clic_, t, rng.uniform(0.6, 1.0))
    return y


def trueno():
    """Chasquido del rayo + retumbe grave que se apaga de a poco."""
    t = tt(2.4)
    chasquido = filtro(rng.standard_normal(len(t)), "highpass", 1500) * np.exp(-t * 28)
    retumbe = filtro(rng.standard_normal(len(t)), "lowpass", 200)
    retumbe *= np.exp(-t * 1.5) * (0.55 + 0.45 * np.sin(2 * np.pi * 2.6 * t) ** 2)
    retumbe /= np.max(np.abs(retumbe)) + 1e-9
    return np.tanh(1.4 * (0.8 * chasquido + retumbe)) * env_adsr(len(t), 0.002, 0.4)


def lluvia(dur):
    """Colchón de lluvia con gotitas sueltas, con entrada y salida suaves."""
    n = int(dur * SR)
    y = filtro(rng.standard_normal(n), "bandpass", [900, 7000]) * 0.25
    for _ in range(int(dur * 35)):
        tg = tt(0.01)
        gota = np.sin(2 * np.pi * rng.uniform(2500, 5000) * tg) * np.exp(-tg * 500)
        pegar(y, gota, rng.uniform(0, dur), rng.uniform(0.1, 0.35))
    rampa = int(min(0.4, dur / 3) * SR)
    y[:rampa] *= np.linspace(0, 1, rampa)
    y[-rampa:] *= np.linspace(1, 0, rampa)
    return y


def subida(dur=0.7, f0=300, f1=1400):
    """Tono que sube (algo que se llena)."""
    t = tt(dur)
    f = f0 * (f1 / f0) ** (t / dur) * (1 + 0.01 * np.sin(2 * np.pi * 9 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return y * env_adsr(len(t), 0.02, 0.12) * 0.6


def rugido_sfx(dur=0.75):
    """Rugido armado como en el cine: grave de 'caimán', medio de 'tigre' y agudo de 'elefante'."""
    t = tt(dur)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
    vib = 1 + 0.06 * np.sin(2 * np.pi * 7 * t)
    grave = np.tanh(3 * np.sin(2 * np.pi * np.cumsum(62 * vib) / SR))
    medio = filtro(np.sign(np.sin(2 * np.pi * np.cumsum(170 * vib * (1 - 0.3 * t / dur)) / SR)), "bandpass", [250, 900])
    agudo = np.sin(2 * np.pi * np.cumsum(720 * (1 + 0.15 * np.sin(2 * np.pi * 3 * t))) / SR) * np.exp(-t * 3)
    ruido = filtro(rng.standard_normal(len(t)), "bandpass", [150, 2500])
    y = 0.8 * grave + 0.7 * medio + 0.25 * agudo + 0.6 * ruido
    return np.tanh(1.6 * y) * env * env_adsr(len(t), 0.03, 0.15)


def chisporroteo(dur=0.6):
    """Chispazos eléctricos."""
    y = np.zeros(int(dur * SR))
    tc = tt(0.02)
    for _ in range(int(dur * 45)):
        chasq = filtro(rng.standard_normal(len(tc)), "highpass", 2500) * np.exp(-tc * 300)
        pegar(y, chasq, rng.uniform(0, dur - 0.02), rng.uniform(0.3, 1.0))
    y = y + 0.25 * np.sin(2 * np.pi * 120 * tt(dur)) * np.exp(-tt(dur) * 3)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.9


def zapping_sfx():
    """Clic de control remoto + fogonazo de estática."""
    t = tt(0.14)
    y = filtro(rng.standard_normal(len(t)), "highpass", 1200) * np.exp(-t * 25) * 0.6
    pegar(y, clic(), 0.0, 1.2)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.9


def tiza(dur=0.5):
    """Tiza raspando el pizarrón."""
    t = tt(dur)
    raspa = filtro(rng.standard_normal(len(t)), "bandpass", [1800, 5000])
    return raspa * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 9 * t))) * env_adsr(len(t), 0.02, 0.08) * 0.5


def marcador(dur=0.35):
    t = tt(dur)
    y = filtro(rng.standard_normal(len(t)), "bandpass", [900, 3500])
    return y * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * env_adsr(len(t), 0.01, 0.05) * 0.5


def proyector(dur):
    """Traqueteo de proyector antiguo (24 cuadros por segundo)."""
    y = np.zeros(int(dur * SR))
    tc = tt(0.012)
    golpe_ = filtro(rng.standard_normal(len(tc)), "bandpass", [600, 3000]) * np.exp(-tc * 400)
    for k in range(int(dur * 24)):
        pegar(y, golpe_, k / 24, 0.5 + 0.2 * (k % 2))
    rampa = int(min(0.3, dur / 3) * SR)
    y[:rampa] *= np.linspace(0, 1, rampa)
    y[-rampa:] *= np.linspace(1, 0, rampa)
    return y


def sable_sfx(dur=1.6):
    """Sable de luz que se enciende y queda zumbando (motor de proyector + zumbido de tele)."""
    t = tt(dur)
    arranque = np.clip(t / 0.25, 0, 1)
    f = 90 * (0.6 + 0.4 * arranque) * (1 + 0.02 * np.sin(2 * np.pi * 5 * t))
    motor = sum((1 / k) * np.sin(2 * np.pi * k * np.cumsum(f) / SR) for k in (1, 2, 3, 4))
    tele_ = np.sin(2 * np.pi * np.cumsum(np.full(len(t), 470.0)) / SR) * 0.25
    tele_ += filtro(rng.standard_normal(len(t)), "bandpass", [2000, 5000]) * 0.08
    y = (motor * 0.6 + tele_) * (0.3 + 0.7 * arranque) * (1 + 0.15 * np.sin(2 * np.pi * 11 * t))
    y[: int(0.3 * SR)] += filtro(rng.standard_normal(int(0.3 * SR)), "bandpass", [300, 3000]) * \
        np.linspace(0.6, 0, int(0.3 * SR))
    return np.tanh(1.4 * y) * env_adsr(len(t), 0.01, 0.4) * 0.8


def redoblante():
    t = tt(0.25)
    parche = np.sin(2 * np.pi * np.cumsum(190 + 60 * np.exp(-t * 40)) / SR) * np.exp(-t * 25)
    bordona = filtro(rng.standard_normal(len(t)), "bandpass", [1500, 7000]) * np.exp(-t * 18)
    return np.tanh(1.5 * (0.7 * parche + 0.8 * bordona))


def quiebre():
    """Palito de madera que se parte."""
    t = tt(0.18)
    chasq = filtro(rng.standard_normal(len(t)), "bandpass", [1200, 6000]) * np.exp(-t * 60)
    madera = np.sin(2 * np.pi * 900 * t) * np.exp(-t * 80) * 0.5
    return np.tanh(2 * (chasq + madera))


def viento(dur):
    t = tt(dur)
    y = filtro(rng.standard_normal(len(t)), "bandpass", [250, 1200]) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t) ** 2)
    rampa = int(min(0.5, dur / 3) * SR)
    y[:rampa] *= np.linspace(0, 1, rampa)
    y[-rampa:] *= np.linspace(1, 0, rampa)
    return y * 0.6


def pajaritos(dur=1.2):
    """Trinos cortos de pájaros (mañana)."""
    y = np.zeros(int(dur * SR))
    for _ in range(int(dur * 5)):
        tc = tt(rng.uniform(0.06, 0.12))
        f0 = rng.uniform(2800, 4200)
        trino = np.sin(2 * np.pi * np.cumsum(f0 + 900 * np.sin(2 * np.pi * 28 * tc)) / SR) * np.sin(np.pi * tc / tc[-1])
        pegar(y, trino, rng.uniform(0, dur - 0.13), rng.uniform(0.3, 0.7))
    return y


def grillos(dur=1.5):
    """Grillos (noche)."""
    t = tt(dur)
    pulsos = (np.sin(2 * np.pi * 30 * t) > 0.3) * (np.sin(2 * np.pi * 1.5 * t) > -0.2)
    y = np.sin(2 * np.pi * 4600 * t) * pulsos * 0.5
    rampa = int(0.2 * SR)
    y[:rampa] *= np.linspace(0, 1, rampa)
    y[-rampa:] *= np.linspace(1, 0, rampa)
    return y


def brillo_sfx():
    y = np.zeros(int(1.2 * SR))
    for i, m in enumerate((84, 88, 91, 96)):
        pegar(y, glock(hz(m), 1.0), 0.05 * i, 0.6)
    return y


def efectos(dur, L, E):
    """Efectos comunes (transiciones, gancho y cierre) + los del episodio."""
    fx = np.zeros(int(dur * SR))
    for b in L.bloques[1:]:
        pegar(fx, whoosh(), b["escena_ini"] - 0.22, 0.30)
        pegar(fx, pop(1100, 350), E[f"{b['id']}_badge"], 0.35)
    # gancho (si el episodio trae el suyo, pone sus efectos en EP.efectos)
    if GANCHO_COMUN:
        pegar(fx, golpe(), E["g_tres"], 0.55)
        pegar(fx, pop(), E["g_curio"], 0.35)
        pegar(fx, pop(700, 200), E["g_cara"], 0.35)
        pegar(fx, whoosh(0.5, 200, 6000), E["g_boom"] - 0.45, 0.22)
        pegar(fx, boom(), E["g_boom"], 0.65)
    # cierre
    for i in range(3):
        pegar(fx, pop(700 + 150 * i, 280), E["cierre_ini"] + 0.35 + 0.15 * i, 0.30)
    pegar(fx, pop(900, 400), E["c_comentarios"], 0.30)
    pegar(fx, clic(), E["c_seguinos"] + 0.25, 0.50)
    pegar(fx, ding(), E["c_seguinos"] + 0.30, 0.30)
    # propios del episodio
    for t, senal, gan in EP.efectos(E, L, sys.modules[__name__]):
        pegar(fx, senal, t, gan)
    return fx


# -------------------------------------------------------------------- mezcla
def leer_mp3(ruta):
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", ruta, "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def _envolvente(x, tau):
    """Envolvente RMS con constante de tiempo `tau` (segundos)."""
    a = np.exp(-1 / (tau * SR))
    return np.sqrt(np.maximum(lfilter([1 - a], [1, -a], x * x), 1e-12))


def procesar_voz(x):
    """Cadena de voz tipo locución: limpieza, compresión, presencia y de-esser."""
    x = filtro(x, "highpass", 80)
    x = x - 0.15 * filtro(x, "bandpass", [200, 450])          # menos "caja"
    x = x / (np.max(np.abs(x)) + 1e-9)
    # compresor 3,5:1 (ataque 3 ms, suelta 120 ms): nivela sílabas fuertes y débiles
    x = x * _ganancia(x, umbral_db=-26.0, ratio=3.5, ataque=0.003, suelta=0.12, medida="rms")
    x = x / (np.max(np.abs(x)) + 1e-9)
    x = x + 0.18 * filtro(x, "bandpass", [2000, 4500])        # más presencia
    x = _deesser(x)                                            # después de comprimir, las eses resaltan
    x = x / (np.max(np.abs(x)) + 1e-9)
    # limitador (ataque instantáneo, suelta 60 ms)
    x = x * _ganancia(x, umbral_db=-6.0, ratio=20.0, ataque=0.0, suelta=0.06, medida="pico")
    return x / (np.max(np.abs(x)) + 1e-9)


def _deesser(x, corte=4500, umbral_db=-13.0, ratio=4.0):
    """Baja la banda aguda solo cuando se dispara (eses, 'ch', 'z').

    La banda se separa con un filtro de fase cero para que al restarla se
    cancele de verdad (con fase corrida, restar agudos casi no los baja).
    """
    agudos = sosfiltfilt(butter(4, corte, btype="highpass", fs=SR, output="sos"), x)
    env_a = _envolvente(agudos, 0.002)
    env_x = _envolvente(x, 0.05)
    rms_voz = np.sqrt(np.mean(x[env_x > 0.03 * env_x.max()] ** 2))
    g = np.minimum(1.0, (rms_voz * 10 ** (umbral_db / 20) / env_a) ** (1 - 1 / ratio))
    return x - agudos * (1 - g)


def _ganancia(x, umbral_db, ratio, ataque, suelta, medida, bloque=0.001):
    """Curva de ganancia de un compresor, calculada por bloques de 1 ms."""
    nb = int(bloque * SR)
    n = len(x) // nb + 1
    xp = np.pad(x, (0, n * nb - len(x))).reshape(n, nb)
    nivel = np.sqrt(np.mean(xp ** 2, axis=1)) if medida == "rms" else np.max(np.abs(xp), axis=1)
    if medida == "pico":  # mira un bloque adelante para no dejar pasar picos
        nivel = np.maximum(nivel, np.append(nivel[1:], 0))
    nivel_db = 20 * np.log10(nivel + 1e-9)
    objetivo = np.minimum(0.0, (umbral_db - nivel_db) * (1 - 1 / ratio))
    ca = np.exp(-bloque / ataque) if ataque > 0 else 0.0
    cs = np.exp(-bloque / suelta)
    g = np.empty(n)
    actual = 0.0
    for i, obj in enumerate(objetivo):
        coef = ca if obj < actual else cs
        actual = coef * actual + (1 - coef) * obj
        g[i] = actual
    centros = (np.arange(n) + 0.5) * nb
    return 10 ** (np.interp(np.arange(len(x)), centros, g) / 20)


def guardar(ruta, x):
    wavfile.write(ruta, SR, np.clip(x, -1, 1).astype(np.float32))


def main():
    os.makedirs(BUILD, exist_ok=True)
    L = Linea()
    E = eventos(L)
    dur = L.duracion
    n = int(dur * SR)

    voz = np.zeros(n)
    for b in L.bloques:
        pegar(voz, leer_mp3(b["audio"]), b["inicio"])
    voz = procesar_voz(voz)

    mus = musica(dur, E["c_fin_voz"] + 0.15)
    mus = mus / (np.max(np.abs(mus)) + 1e-9)
    fx = efectos(dur, L, E)

    # ducking: la música baja cuando habla la voz
    ventana = int(0.12 * SR)
    envol = np.convolve(np.abs(voz), np.ones(ventana) / ventana, mode="same")
    envol = np.clip(envol / (np.percentile(envol[envol > 1e-4], 90) + 1e-9), 0, 1)
    duck = 1 - 0.55 * envol
    duck = np.convolve(duck, np.ones(ventana) / ventana, mode="same")

    final = 0.95 * voz[:, None] + 0.40 * mus * duck[:, None] + fx[:, None]
    final = final / (np.max(np.abs(final)) + 1e-9) * 0.89

    guardar(os.path.join(BUILD, "musica.wav"), mus * 0.8)
    guardar(os.path.join(BUILD, "sfx.wav"), fx / (np.max(np.abs(fx)) + 1e-9) * 0.8)
    crudo = os.path.join(BUILD, "audio_mezcla.wav")
    guardar(crudo, final)
    normalizar(crudo, os.path.join(BUILD, "audio_final.wav"))
    print("audio listo:", os.path.join(BUILD, "audio_final.wav"))


def normalizar(entrada, salida, lufs=-14.0, pico=-1.5):
    """Loudnorm de dos pasadas (lineal): volumen estándar de redes sociales."""
    filtro_ = f"loudnorm=I={lufs}:TP={pico}:LRA=11"
    med = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", entrada, "-af",
                          filtro_ + ":print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(med[med.rindex("{"):med.rindex("}") + 1])
    filtro_ += (f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
                f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
                f":offset={m['target_offset']}:linear=true")
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", entrada, "-af", filtro_, "-ar", str(SR),
                    "-c:a", "pcm_s16le", salida], check=True)


if __name__ == "__main__":
    main()
