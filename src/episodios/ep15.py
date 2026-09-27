"""Episodio 15: quiz de cultura general — cinco preguntas nuevas (voz de Tomás).

Las piezas del quiz están en quiz.py; acá van las preguntas y los dibujos (un murciélago,
un fémur, un tiburón en rayos X, Saturno con sus lunas y un mar lleno de islas).
"""
import math

import numpy as np

import quiz
from dibujo import (H, W, Capa, a_imagen, cartel, clamp, componer, e_back, e_in_out, gradiente, lerp, pop, prog,
                    resplandor, spr_estrella, viñeta)
from quiz import signo

SLUG = "quiz_cultura"
DURACION = 58.0                       # cinco preguntas con 3 s para pensar cada una
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
PALABRAS_CIERRE = ("abajo", "seguinos")
CIERRE_TITULO = ("¿CUÁNTAS", "ACERTASTE?")

BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Cinco preguntas de cultura general, tres segundos cada una! ¿Cuántas acertás?",
        "titulo": "5 PREGUNTAS",
    },
    {
        "id": "c1",
        "texto": "Uno: ¿cuál es el único mamífero que puede volar? [3s] ¡El murciélago! La ardilla voladora solo planea.",
        "titulo": "VOLAR",
        "pregunta": "¿Cuál es el único mamífero que puede volar?",
        "opciones": ["ARDILLA VOLADORA", "MURCIÉLAGO", "COLIBRÍ"],
        "correcta": 1,
    },
    {
        "id": "c2",
        "texto": "Dos: ¿cuál es el hueso más largo de tu cuerpo? [3s] ¡El fémur! Mide casi un cuarto de tu altura.",
        "titulo": "EL HUESO",
        "pregunta": "¿Cuál es el hueso más largo de tu cuerpo?",
        "opciones": ["FÉMUR", "HÚMERO", "TIBIA"],
        "correcta": 0,
    },
    {
        "id": "c3",
        "texto": "Tres: ¿cuántos huesos tiene un tiburón? [3s] ¡Ninguno! Su esqueleto es de cartílago, como tu nariz.",
        "titulo": "EL TIBURÓN",
        "pregunta": "¿Cuántos huesos tiene un tiburón?",
        "opciones": ["CIEN", "DOSCIENTOS", "NINGUNO"],
        "correcta": 2,
    },
    {
        "id": "c4",
        "texto": "Cuatro: ¿qué planeta tiene más lunas? [3s] ¡Saturno! Tiene más de doscientas.",
        "titulo": "LAS LUNAS",
        "pregunta": "¿Qué planeta tiene más lunas?",
        "opciones": ["JÚPITER", "SATURNO", "NEPTUNO"],
        "correcta": 1,
    },
    {
        "id": "c5",
        "texto": "Cinco: ¿qué país tiene más islas en el mundo? [3s] ¡Suecia! Tiene más de doscientas mil.",
        "titulo": "LAS ISLAS",
        "pregunta": "¿Qué país tiene más islas en el mundo?",
        "opciones": ["SUECIA", "INDONESIA", "FILIPINAS"],
        "correcta": 0,
    },
    {
        "id": "cierre",
        "texto": "¿Cuántas acertaste? Comentalo abajo y seguinos para más.",
        "titulo": "¿CUÁNTAS ACERTASTE?",
    },
]

PREGUNTAS = ["c1", "c2", "c3", "c4", "c5"]
ACENTO = {"c1": (130, 80, 210), "c2": (235, 120, 60), "c3": (30, 160, 200), "c4": (220, 170, 60),
          "c5": (40, 110, 210), "cierre": (255, 0, 110)}
POR_ID = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
TINTA = (24, 16, 48)


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        **quiz.eventos(L, PREGUNTAS),
        **quiz.eventos_gancho(L, "cinco", "cultura"),
        "c1_ardilla": L.palabra("c1", "ardilla"),
        "c2_cuarto": L.palabra("c2", "cuarto"),
        "c3_cartilago": L.palabra("c3", "cartílago"),
        "c3_nariz": L.palabra("c3", "nariz"),
        "c4_doscientas": L.palabra("c4", "doscientas"),
        "c5_mil": L.palabra("c5", "mil"),
    }


def efectos(E, L, S):
    fx = quiz.efectos(E, S, PREGUNTAS) + quiz.efectos_gancho(E, S)
    fx += [(E["c1_revela"] + 0.2, S.whoosh(0.6, 400, 3000), 0.18), (E["c1_ardilla"], S.whoosh(0.8, 2000, 300), 0.12),
           (E["c2_cuarto"], S.pop(900, 400), 0.25), (E["c3_revela"] + 0.1, S.chisporroteo(0.4), 0.10),
           (E["c3_cartilago"], S.pop(700, 300), 0.22), (E["c4_revela"] + 0.2, S.brillo_sfx(), 0.2)]
    for i in range(12):
        fx.append((E["c4_doscientas"] + 0.05 * i, S.pop(1500 + 40 * i, 900, 0.05), 0.12))
        fx.append((E["c5_revela"] + 0.2 + 0.07 * i, S.bloop(), 0.05))
    fx.append((E["c5_mil"], S.ding(), 0.25))
    return fx


def sacudidas(E):
    return quiz.sacudidas_gancho(E)


def momento_portada(E):
    return E["gq_acertas"] + 0.7


# ==================================================================== fondos
def _estrellas(img, n, seed, alto=H):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        componer(img, spr_estrella(int(rng.integers(2, 6))), rng.uniform(0, W), rng.uniform(0, alto),
                 alpha=rng.uniform(0.3, 0.9))


def fondo_gancho():
    a = gradiente([(0, (20, 40, 110)), (0.55, (40, 140, 170)), (1, (250, 180, 40))])
    resplandor(a, 540, 1000, 620, (190, 255, 240), 0.3)
    viñeta(a)
    return a_imagen(a, 150)


def fondo_noche():
    a = gradiente([(0, (12, 10, 40)), (0.6, (40, 30, 90)), (1, (20, 16, 50))])
    img = a_imagen(a, 151)
    _estrellas(img, 70, 152, 1400)
    c = Capa(0, 0, W, H, ss=1)
    c.circulo(840, 640, 90, fill=(250, 245, 220))
    c.circulo(876, 620, 80, fill=(40, 30, 90, 0))
    c.pegar_en(img)
    return img


def fondo_cuerpo():
    a = gradiente([(0, (255, 226, 200)), (0.6, (255, 240, 225)), (1, (245, 210, 190))])
    viñeta(a, 0.3)
    return a_imagen(a, 153)


def fondo_rayosx():
    a = gradiente([(0, (6, 30, 60)), (0.6, (10, 60, 100)), (1, (4, 20, 44))])
    resplandor(a, 540, 800, 520, (60, 200, 255), 0.3)
    return a_imagen(a, 154)


def fondo_espacio():
    a = gradiente([(0, (6, 6, 24)), (0.6, (26, 18, 60)), (1, (8, 6, 26))])
    img = a_imagen(a, 155)
    _estrellas(img, 120, 156)
    return img


def fondo_mar():
    a = gradiente([(0, (160, 210, 245)), (0.3, (200, 230, 250)), (0.31, (50, 130, 200)), (1, (20, 70, 140))])
    return a_imagen(a, 157)


def preparar():
    FONDOS.update(gancho=fondo_gancho(), noche=fondo_noche(), cuerpo=fondo_cuerpo(), rayosx=fondo_rayosx(),
                  espacio=fondo_espacio(), mar=fondo_mar())


# ============================================================ 1 · murciélago
def murcielago(c, x, y, k, t):
    aleteo = 0.55 + 0.45 * math.sin(t * 14)
    B, C = (30, 20, 50), (170, 140, 220)
    for s in (-1, 1):
        pts = [(x + s * 30 * k, y - 10 * k), (x + s * 110 * k, y - 80 * k * aleteo), (x + s * 200 * k, y - 50 * k * aleteo),
               (x + s * 170 * k, y + 10 * k), (x + s * 130 * k, y - 5 * k), (x + s * 95 * k, y + 25 * k),
               (x + s * 60 * k, y + 5 * k), (x + s * 30 * k, y + 25 * k)]
        c.poligono(pts, fill=C, borde=B, grosor=4 * k)
    c.elipse(x, y + 10 * k, 38 * k, 50 * k, fill=(120, 90, 160), borde=B, grosor=4 * k)
    c.circulo(x, y - 40 * k, 30 * k, fill=(120, 90, 160), borde=B, grosor=4 * k)
    for s in (-1, 1):
        c.poligono([(x + s * 10 * k, y - 62 * k), (x + s * 28 * k, y - 96 * k), (x + s * 30 * k, y - 52 * k)],
                   fill=(120, 90, 160), borde=B, grosor=3 * k)
        c.circulo(x + s * 11 * k, y - 42 * k, 6 * k, fill=(255, 230, 120))


def ardilla(c, x, y, k):
    M, B = (170, 120, 80), (100, 64, 36)
    c.poligono([(x - 110 * k, y - 20 * k), (x + 110 * k, y - 30 * k), (x + 90 * k, y + 40 * k), (x - 90 * k, y + 50 * k)],
               fill=(190, 140, 95), borde=B, grosor=4 * k)
    c.elipse(x, y + 8 * k, 50 * k, 34 * k, fill=M, borde=B, grosor=4 * k)
    c.circulo(x + 62 * k, y - 10 * k, 26 * k, fill=M, borde=B, grosor=4 * k)
    c.circulo(x + 72 * k, y - 16 * k, 5 * k, fill=(20, 20, 20))
    c.linea([(x - 50 * k, y + 10 * k), (x - 130 * k, y + 20 * k), (x - 170 * k, y - 10 * k)], M, 26 * k)


def dibujo_murcielago(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 470, W, 550)
    if t >= tr:
        p = clamp((t - tr) / 2.2)
        murcielago(c, lerp(200, 880, p), 720 + 60 * math.sin(p * 9), 1.1, t)
    else:   # silueta que revolotea en sombra
        murcielago(c, 540 + 200 * math.sin(t * 1.3), 720 + 30 * math.sin(t * 2.1), 0.8 * s, t)
    ta = E["c1_ardilla"]
    sa = e_back(prog(t, ta - 0.1, 0.4))
    if sa > 0:
        p = clamp((t - ta) / 1.6)
        ardilla(c, lerp(180, 700, p), lerp(800, 900, p), 0.9 * sa)
    c.pegar_en(fr)
    if t < tr:
        c = Capa(0, 470, W, 550)
        c.rrect(0, 470, W, 1020, 0, fill=(12, 10, 40, 120))
        c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 900, 130)
    if sa > 0:
        componer(fr, cartel("SOLO PLANEA", None, (255, 240, 210), (110, 70, 36), 320, 56), 330, 560, escala=sa, rot=-4)


# ================================================================== 2 · fémur
def hueso_largo(c, x0, y0, x1, y1, k, col=(252, 246, 230), borde=(170, 150, 120)):
    for cc, extra in ((borde, 5 * k), (col, 0)):
        c.linea([(x0, y0), (x1, y1)], cc, 44 * k + 2 * extra)
        c.circulo(x0, y0, 34 * k + extra, fill=cc)
        c.circulo(x0 + 34 * k, y0 + 10 * k, 22 * k + extra, fill=cc)
        for s in (-1, 1):
            c.circulo(x1 + s * 26 * k, y1 + 6 * k, 28 * k + extra, fill=cc)


def persona(c, x, y, k, color):
    c.circulo(x, y - 380 * k, 56 * k, fill=color)
    c.rrect(x - 70 * k, y - 316 * k, x + 70 * k, y - 60 * k, 40 * k, fill=color)
    for s in (-1, 1):
        c.linea([(x + s * 36 * k, y - 80 * k), (x + s * 42 * k, y + 250 * k)], color, 50 * k)
        c.linea([(x + s * 70 * k, y - 290 * k), (x + s * 104 * k, y - 90 * k)], color, 34 * k)


def dibujo_femur(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 470, W, 560)
    brillo = e_in_out(prog(t, tr, 0.4))
    x, y = 360, 880
    persona(c, x, y - 40, 0.72 * s, (150, 190, 240, 170))
    if brillo > 0:
        hueso_largo(c, x - 26, y - 80, x - 30, y + 60, 0.55 * brillo)
    # el fémur grande a la derecha, con su medida
    sg = e_back(prog(t, tr + 0.15, 0.45))
    if sg > 0:
        hueso_largo(c, 760, 600, 740, 930, 1.0 * sg)
    tc = E["c2_cuarto"]
    if t >= tc:   # un cuarto de la altura: la regla se divide en cuatro
        p = e_in_out(prog(t, tc, 0.4))
        c.linea([(560, 560), (560, 560 + 440 * p)], (80, 80, 110), 6, puntas=False)
        for i in range(5):
            yy = 560 + 110 * i
            if yy <= 560 + 440 * p:
                c.linea([(540, yy), (580, yy)], (80, 80, 110), 6, puntas=False)
        c.rrect(548, 890, 572, 1000, 6, fill=(255, 150, 60, 200))
    c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 740, 760, 140)
    sc = pop(t, tc + 0.2, 0.35)
    if sc > 0:
        componer(fr, cartel("1/4 DE TU ALTURA", None, (255, 255, 255), (200, 90, 40), 420, 62), 560, 480,
                 escala=sc, rot=-3)


# ================================================================ 3 · tiburón
def tiburon(c, x, y, k, t, rayos):
    col = (60, 220, 255, 230) if rayos else (120, 140, 160)
    relleno = (10, 60, 100, 160) if rayos else (120, 140, 160)
    cola = 12 * math.sin(t * 5)
    cuerpo = [(x - 240 * k, y), (x - 160 * k, y - 60 * k), (x, y - 80 * k), (x + 160 * k, y - 50 * k),
              (x + 250 * k, y - 10 * k), (x + 250 * k, y + 10 * k), (x + 150 * k, y + 50 * k), (x, y + 60 * k),
              (x - 160 * k, y + 40 * k)]
    c.poligono(cuerpo, fill=relleno, borde=col, grosor=6 * k)
    c.poligono([(x - 20 * k, y - 76 * k), (x + 40 * k, y - 170 * k), (x + 70 * k, y - 60 * k)], fill=relleno, borde=col,
               grosor=6 * k)
    c.poligono([(x + 240 * k, y), (x + 320 * k, y - 90 * k + cola), (x + 300 * k, y + 5 * k),
                (x + 320 * k, y + 80 * k + cola)], fill=relleno, borde=col, grosor=6 * k)
    c.poligono([(x - 40 * k, y + 50 * k), (x - 10 * k, y + 120 * k), (x + 30 * k, y + 52 * k)], fill=relleno,
               borde=col, grosor=5 * k)
    c.circulo(x - 170 * k, y - 20 * k, 9 * k, fill=(255, 255, 255) if rayos else (20, 20, 30))
    for i in range(4):
        c.arco(x - 110 * k + i * 16 * k, y, 10 * k, 26 * k, 270, 450, col, 3 * k)
    if rayos:   # donde tendría huesos: solo una columna blanda de cartílago
        c.linea([(x - 150 * k, y - 10 * k), (x + 250 * k, y - 4 * k)], (140, 255, 220, 150), 10 * k)


def dibujo_tiburon(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 470, W, 560)
    x = 540 + 60 * math.sin(t * 0.9)
    tiburon(c, x, 780 + 12 * math.sin(t * 1.7), 1.05 * s, t, t >= tr)
    c.pegar_en(fr)
    if t >= tr:
        componer(fr, cartel("0 HUESOS", None, (255, 255, 255), (20, 110, 160), 300, 76), 300, 620,
                 escala=pop(t, tr + 0.1, 0.35), rot=-5)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 620, 120)
    tc = E["c3_cartilago"]
    sc = pop(t, tc, 0.35)
    if sc > 0:
        componer(fr, cartel("CARTÍLAGO", "COMO TU NARIZ", (160, 255, 220), (10, 60, 80), 380, 70), 760, 960,
                 escala=sc, rot=3)


# ================================================================ 4 · Saturno
def planeta(c, x, y, r, tipo, t):
    if tipo == "jupiter":
        c.circulo(x, y, r, fill=(220, 170, 120))
        for i, col in enumerate(((190, 130, 90), (240, 210, 170), (180, 110, 80))):
            c.elipse(x, y - r * 0.5 + i * r * 0.45, r * 0.95, r * 0.12, fill=col)
        c.elipse(x + r * 0.3, y + r * 0.35, r * 0.2, r * 0.12, fill=(200, 90, 70))
    elif tipo == "neptuno":
        c.circulo(x, y, r, fill=(70, 120, 230))
        c.elipse(x - r * 0.2, y - r * 0.2, r * 0.3, r * 0.15, fill=(120, 170, 250))
    else:
        c.elipse(x, y, r * 2.1, r * 0.5, borde=(230, 210, 160), grosor=r * 0.12)
        c.circulo(x, y, r, fill=(235, 205, 140))
        c.elipse(x, y - r * 0.3, r * 0.95, r * 0.14, fill=(215, 180, 120))
        c.arco(x, y, r * 2.1, r * 0.5, 0, 180, (240, 220, 170), r * 0.12)


def dibujo_saturno(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    foco = e_in_out(prog(t, tr, 0.5))
    if foco < 1:   # Júpiter y Neptuno se desvanecen con la respuesta
        otros = Capa(0, 470, W, 560)
        planeta(otros, 220, 800, 90 * s, "jupiter", t)
        planeta(otros, 860, 800, 70 * s, "neptuno", t)
        componer(fr, otros.imagen(), W / 2, 470 + 280, alpha=1 - foco)
    c = Capa(0, 470, W, 560)
    planeta(c, 540, 790, lerp(80, 150, foco) * s, "saturno", t)
    td = E["c4_doscientas"]
    n = int(220 * clamp((t - tr - 0.2) / 1.8)) if t >= tr else 0
    rng = np.random.default_rng(4)
    for i in range(n):   # lunas que van apareciendo en órbita
        a = rng.uniform(0, 2 * math.pi) + t * rng.uniform(0.3, 0.9)
        rx, ry = rng.uniform(250, 480), rng.uniform(90, 200)
        c.circulo(540 + math.cos(a) * rx, 790 + math.sin(a) * ry, rng.uniform(3, 7), fill=(230, 230, 240))
    c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 620, 120)
    sc = pop(t, td, 0.35)
    if sc > 0:
        componer(fr, cartel("+200 LUNAS", None, (255, 240, 190), (90, 60, 20), 360, 76), 540, 520, escala=sc, rot=-3)


# ================================================================== 5 · islas
def bandera_suecia(c, x, y, k):
    c.rrect(x - 90 * k, y - 56 * k, x + 90 * k, y + 56 * k, 6 * k, fill=(0, 106, 167), borde=(255, 255, 255),
            grosor=5 * k)
    c.rrect(x - 40 * k, y - 56 * k, x - 14 * k, y + 56 * k, 0, fill=(254, 204, 0))
    c.rrect(x - 90 * k, y - 13 * k, x + 90 * k, y + 13 * k, 0, fill=(254, 204, 0))


def dibujo_islas(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 470, W, 560)
    rng = np.random.default_rng(15)
    total = 140
    n = int(total * clamp((t - tr - 0.1) / 1.6)) if t >= tr else 6
    for i in range(total):
        x, y = rng.uniform(60, W - 60), rng.uniform(640, 990)
        r = rng.uniform(8, 26)
        forma = [(x + math.cos(a) * r * rng.uniform(0.7, 1.3), y + math.sin(a) * r * 0.7 * rng.uniform(0.7, 1.3))
                 for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
        if i < n:
            c.poligono(forma, fill=(120, 190, 110), borde=(230, 220, 170), grosor=3)
    c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 800, 140)
    if t >= tr:
        c = Capa(660, 470, 320, 200)
        bandera_suecia(c, 820, 560, 0.9 * e_back(prog(t, tr, 0.4)))
        c.pegar_en(fr)
    tm = E["c5_mil"]
    sc = pop(t, tm, 0.35)
    if sc > 0:
        componer(fr, cartel("267.570 ISLAS", None, (255, 255, 255), (20, 80, 160), 440, 76), 360, 560, escala=sc,
                 rot=-3)


# ======================================================= íconos del cierre
def _icono_murcielago(c, x, y, s, t):
    murcielago(c, x, y + 20 * s, 0.55 * s, t)


def _icono_hueso(c, x, y, s, t):
    hueso_largo(c, x - 50 * s, y - 60 * s, x + 50 * s, y + 60 * s, 0.6 * s)


def _icono_tiburon(c, x, y, s, t):
    tiburon(c, x - 20 * s, y + 10 * s, 0.32 * s, t, False)


def _icono_saturno(c, x, y, s, t):
    planeta(c, x, y, 52 * s, "saturno", t)


def _icono_bandera(c, x, y, s, t):
    bandera_suecia(c, x, y, 0.75 * s)


ICONOS = [_icono_murcielago, _icono_hueso, _icono_tiburon, _icono_saturno, _icono_bandera]
ESCENAS = {
    "gancho": lambda t: quiz.escena_gancho(t, E, FONDOS, "CULTURA GENERAL", titulo="5 PREGUNTAS"),
    "c1": quiz.escena_pregunta("c1", 1, 5, "noche", dibujo_murcielago, ACENTO["c1"], E, ESC, POR_ID, FONDOS),
    "c2": quiz.escena_pregunta("c2", 2, 5, "cuerpo", dibujo_femur, ACENTO["c2"], E, ESC, POR_ID, FONDOS),
    "c3": quiz.escena_pregunta("c3", 3, 5, "rayosx", dibujo_tiburon, ACENTO["c3"], E, ESC, POR_ID, FONDOS),
    "c4": quiz.escena_pregunta("c4", 4, 5, "espacio", dibujo_saturno, ACENTO["c4"], E, ESC, POR_ID, FONDOS),
    "c5": quiz.escena_pregunta("c5", 5, 5, "mar", dibujo_islas, ACENTO["c5"], E, ESC, POR_ID, FONDOS),
}
