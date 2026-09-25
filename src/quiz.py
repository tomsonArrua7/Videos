"""Piezas comunes de los episodios de preguntas (quiz).

Cada bloque de pregunta del guion lleva, además de su texto:
    "texto":    "Uno: ¿pregunta...? [3s] ¡Respuesta! Dato."   ([3s] = tiempo para pensar)
    "pregunta": lo que se lee en la tarjeta de arriba
    "opciones": ["A", "B", "C"]
    "correcta": índice de la opción correcta

La escena muestra la pregunta, las opciones mientras se pregunta, un reloj de cuenta
regresiva durante el silencio y, cuando la voz responde, marca la correcta. El dibujo del
medio lo pone el episodio: dibujo(fr, t, ev), con ev = los momentos de esa pregunta.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import ImageDraw

from dibujo import (F, TINTA, W, Capa, _pildora, chispas, clamp, componer, e_back, e_out, lerp, mezcla, pop,
                    prog, rayos_sol, spr_brillo, texto, texto_ajustado)

LETRAS = "ABC"
Y_OPCIONES = (1045, 1185, 1325)
Y_RELOJ = 760
VERDE = (34, 180, 90)


# ================================================================== tiempos
def eventos(L, ids):
    """Momentos de cada pregunta: la pregunta, las opciones, la cuenta y la respuesta."""
    E = {}
    for bid in ids:
        (q0, q1), (r0, _) = L.parte(bid, 0), L.parte(bid, 1)
        E[f"{bid}_preg"] = q0
        E[f"{bid}_opc"] = max(q0 + 0.3, q1 - 0.9)
        E[f"{bid}_cuenta"] = q1 + 0.12
        E[f"{bid}_revela"] = r0
    return E


def efectos(E, S, ids):
    fx = []
    for bid in ids:
        for i in range(3):
            fx.append((E[f"{bid}_opc"] + 0.18 * i, S.pop(800 + 160 * i, 320, 0.09), 0.20))
        c, r = E[f"{bid}_cuenta"], E[f"{bid}_revela"]
        paso = (r - c) / 3
        for k in range(3):
            fx.append((c + k * paso, S.tictac(True), 0.50))
            fx.append((c + k * paso + paso / 2, S.tictac(False), 0.30))
        fx.append((c, S.subida(r - c, 180, 520), 0.05))
        fx.append((r - 0.03, S.acierto(), 0.34))
    return fx


# ================================================================ elementos
@lru_cache(None)
def _encabezado(numero, total, color):
    txt = texto(f"PREGUNTA {numero} DE {total}", "negra", 44, color=TINTA)
    w, h = txt.width + 150, 96
    c = Capa(0, 0, w + 10, h + 16, ss=3)
    c.rrect(5, 11, w + 5, h + 11, h / 2, fill=(10, 5, 30, 90))
    c.rrect(5, 5, w + 5, h + 5, h / 2, fill=(255, 255, 255))
    c.circulo(5 + h / 2, 5 + h / 2, h / 2 - 8, fill=color, borde=TINTA, grosor=4)
    im = c.imagen()
    q = texto("?", "titulo", 62, color=TINTA)
    im.alpha_composite(q, (int(5 + h / 2 - q.width / 2), int(5 + h / 2 - q.height / 2 + 2)))
    im.alpha_composite(txt, (int(h + 12), int(5 + h / 2 - txt.height / 2)))
    return im


def _renglones(txt, f, ancho):
    lineas, actual = [], ""
    for palabra in txt.split():
        prueba = (actual + " " + palabra).strip()
        if actual and f.getlength(prueba) > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    return lineas + [actual]


@lru_cache(None)
def _tarjeta(txt, color):
    f = F("negra", 58)
    lineas = _renglones(txt, f, 860)
    alto_l = 70
    w, h = 960, len(lineas) * alto_l + 56
    c = Capa(0, 0, w + 10, h + 18, ss=3)
    c.rrect(5, 13, w + 5, h + 13, 40, fill=(10, 5, 30, 110))
    c.rrect(5, 5, w + 5, h + 5, 40, fill=(255, 255, 255), borde=color, grosor=8)
    im = c.imagen()
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lineas):
        d.text((5 + w / 2, 5 + 28 + alto_l * (i + 0.5)), ln, font=f, fill=TINTA, anchor="mm")
    return im


@lru_cache(None)
def _opcion(letra, txt, estado, color):
    """Píldora de opción. estado: "normal", "bien" o "mal"."""
    w, h = 860, 112
    fondo, tinta, insignia, letra_col = (255, 255, 255), TINTA, color, (255, 255, 255)
    if estado == "bien":
        fondo, tinta, insignia, letra_col = VERDE, (255, 255, 255), (255, 255, 255), VERDE
    elif estado == "mal":
        fondo, tinta, insignia = (226, 224, 236), (130, 126, 150), (170, 166, 186)
    c = Capa(0, 0, w + 10, h + 16, ss=3)
    c.rrect(5, 13, w + 5, h + 13, h / 2, fill=(10, 5, 30, 100))
    c.rrect(5, 5, w + 5, h + 5, h / 2, fill=fondo, borde=(255, 255, 255), grosor=6)
    c.circulo(5 + h / 2, 5 + h / 2, h / 2 - 12, fill=insignia, borde=(255, 255, 255) if estado == "bien" else None,
              grosor=4)
    if estado == "bien":  # tilde
        x, y, k = w - 55, 5 + h / 2, 30
        pts = [(x - k, y), (x - k * 0.3, y + k * 0.7), (x + k, y - k * 0.8)]
        c.linea(pts, (255, 255, 255), 14)
    im = c.imagen()
    le = texto(letra, "titulo", 60, color=letra_col)
    im.alpha_composite(le, (int(5 + h / 2 - le.width / 2), int(5 + h / 2 - le.height / 2 + 3)))
    tx = texto_ajustado(txt, "negra", 54, w - 230, color=tinta)
    im.alpha_composite(tx, (int(5 + h + 26), int(5 + h / 2 - tx.height / 2)))
    return im


def reloj(fr, t, c, r, x=W / 2, y=Y_RELOJ):
    """Cuenta regresiva 3-2-1 con un aro que se vacía (verde → rojo)."""
    if t < c - 0.05 or t > r + 0.3:
        return
    s = e_back(prog(t, c - 0.05, 0.3)) * (1 - e_out(prog(t, r, 0.25)))
    if s <= 0.01:
        return
    resto = clamp(1 - (t - c) / (r - c))
    n = max(1, min(3, math.ceil(resto * 3 - 1e-6)))
    dentro = (1 - resto) * 3 - (3 - n)          # 0..1 dentro de cada número
    R = 150 * s
    capa = Capa(int(x - 230), int(y - 230), 460, 470)
    capa.circulo(x, y + 12, R + 22, fill=(10, 5, 30, 100))
    capa.circulo(x, y, R + 22, fill=(255, 255, 255))
    capa.circulo(x, y, R, fill=(28, 18, 58))
    col = mezcla((60, 210, 110), (240, 60, 70), 1 - resto)
    if resto > 0.002:
        capa.arco(x, y, R - 16, R - 16, -90, -90 + 360 * resto, col, 24 * s)
    capa.pegar_en(fr)
    latido = 1 + 0.35 * math.exp(-dentro * 7)
    componer(fr, texto(str(n), "titulo", 170, color=(255, 255, 255)), x, y + 10, escala=s * latido)


# ================================================================== escenas
def escena_pregunta(bid, numero, total, fondo, dibujo, acento, E, ESC, BLOQUES, FONDOS):
    """Arma la escena de una pregunta. `E`, `ESC` y `FONDOS` se llenan después (son diccionarios)."""
    b = BLOQUES[bid]

    def escena(t):
        fr = FONDOS[fondo].copy()
        ev = {k: E[f"{bid}_{k}"] for k in ("preg", "opc", "cuenta", "revela", "badge")}
        ev["t0"] = ESC[bid]["escena_ini"]
        dibujo(fr, t, ev)
        reloj(fr, t, ev["cuenta"], ev["revela"])
        tr = ev["revela"]
        for i, (y, txt) in enumerate(zip(Y_OPCIONES, b["opciones"])):
            s = pop(t, ev["opc"] + 0.18 * i, 0.35)
            if s <= 0:
                continue
            estado, alpha, rot = "normal", 1.0, 0.0
            if t >= tr:
                p = e_out(prog(t, tr, 0.3))
                if i == b["correcta"]:
                    estado = "bien"
                    s *= 1 + 0.07 * e_back(prog(t, tr, 0.35))
                    rot = 2 * math.sin((t - tr) * 14) * math.exp(-(t - tr) * 4)
                else:
                    estado, alpha = "mal", lerp(1, 0.55, p)
                    s *= lerp(1, 0.94, p)
            elif ev["cuenta"] <= t:  # durante la cuenta, las opciones "respiran"
                s *= 1 + 0.02 * math.sin((t - ev["cuenta"]) * 9 + i * 1.3)
            componer(fr, _opcion(LETRAS[i], txt, estado, acento), W / 2, y, escala=s, alpha=alpha, rot=rot)
        chispas(fr, t, tr, W / 2 + 360, Y_OPCIONES[b["correcta"]], n=26, seed=numero,
                colores=((255, 240, 150), (120, 255, 170), (255, 255, 255)))
        s = pop(t, ev["badge"], 0.4)
        if s > 0:
            componer(fr, _encabezado(numero, total, acento), W / 2, 150 + 3 * math.sin(t * 2.5), escala=s)
        s = pop(t, ev["badge"] + 0.12, 0.4)
        if s > 0:
            im = _tarjeta(b["pregunta"], acento)
            componer(fr, im, W / 2, 222 + im.height / 2, escala=s)
        return fr

    return escena


# ================================================================== gancho
def cronometro(c, x, y, r, t, aguja, color=(255, 214, 10)):
    """Cronómetro de juego (sin números): corona, aro y una aguja."""
    c.rrect(x - r * 0.18, y - r * 1.32, x + r * 0.18, y - r * 1.12, r * 0.06, fill=TINTA)
    c.rrect(x - r * 0.1, y - r * 1.16, x + r * 0.1, y - r * 0.95, r * 0.04, fill=TINTA)
    for s in (-1, 1):
        c.linea([(x + s * r * 0.62, y - r * 0.9), (x + s * r * 0.78, y - r * 1.06)], TINTA, r * 0.13)
    c.circulo(x, y + r * 0.05, r + r * 0.1, fill=(10, 5, 30, 90))
    c.circulo(x, y, r + r * 0.1, fill=TINTA)
    c.circulo(x, y, r, fill=color)
    c.circulo(x, y, r * 0.84, fill=(255, 255, 255))
    for k in range(12):
        a = k * math.pi / 6
        c.linea([(x + math.sin(a) * r * 0.72, y - math.cos(a) * r * 0.72),
                 (x + math.sin(a) * r * 0.8, y - math.cos(a) * r * 0.8)], TINTA, r * 0.035, puntas=False)
    c.linea([(x, y), (x + math.sin(aguja) * r * 0.62, y - math.cos(aguja) * r * 0.62)], (235, 50, 70), r * 0.05)
    c.circulo(x, y, r * 0.06, fill=TINTA)


def escena_gancho(t, E, FONDOS, etiqueta):
    """Gancho de los quiz: "3 PREGUNTAS", la etiqueta y un cronómetro con un signo de pregunta."""
    fr = FONDOS["gancho"].copy()
    rayos_sol(fr, 540, 960, t * 0.35, n=16, color=(255, 255, 255, 22))
    ta, tp, ts = E["gq_acertas"], E["gq_preguntas"], E["gq_segundos"]
    # cronómetro con "?" (el signo late al preguntar "¿cuántas acertás?")
    s = pop(t, ts - 0.1, 0.45)
    if s > 0:
        c = Capa(140, 560, 800, 900)
        aguja = 2 * math.pi * clamp((t - ts) / 1.4) * 3 if t < ts + 1.4 else 0
        cronometro(c, 540, 1000 + 8 * math.sin(t * 2.3), 300 * s, t, aguja)
        c.pegar_en(fr)
        golpe = 1 + 0.3 * math.exp(-max(0, t - ta) * 6) if t >= ta else 1
        rot = 10 * math.sin((t - ta) * 16) * math.exp(-(t - ta) * 4) if t >= ta else 0
        componer(fr, texto("?", "titulo", 330, color=(255, 0, 110), borde=12, color_borde=TINTA, sombra=10),
                 540, 1010 + 8 * math.sin(t * 2.3), escala=s * golpe, rot=rot)
    if t >= ta:
        chispas(fr, t, ta, 540, 1000, n=30, seed=11, arriba=True)
    # textos
    s3 = 0 if t < E["gq_tres"] else lerp(2.4, 1.0, e_out(prog(t, E["gq_tres"], 0.22)))
    if s3 > 0:
        componer(fr, texto_ajustado("3 PREGUNTAS", "titulo", 160, 1000, color=(255, 255, 255), borde=14, sombra=12),
                 540, 330 + 5 * math.sin(t * 2.2), escala=s3 if t < tp else 1.0,
                 alpha=clamp((t - E["gq_tres"]) / 0.08))
    s = pop(t, ts, 0.4)
    if s > 0:
        componer(fr, _pildora(etiqueta, (255, 0, 110), 50), 540, 480, escala=s, rot=-3)
    # brillitos que titilan alrededor
    rng = np.random.default_rng(9)
    for i in range(10):
        x, y, fase = rng.uniform(100, 980), rng.uniform(600, 1400), rng.uniform(0, 6)
        a = 0.5 + 0.5 * math.sin(t * 3 + fase)
        if t > ts:
            componer(fr, spr_brillo(int(14 + 10 * a)), x, y, alpha=a * clamp((t - ts) / 0.4))
    return fr
