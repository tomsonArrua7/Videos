"""Episodio 13: secretos de películas (voz de Tomás, Argentina).

Matrix, Tiburón y El Señor de los Anillos, con objetos genéricos (letras verdes, sushi, una
aleta mecánica, una bota y un casco): ningún personaje ni logo con derechos de autor.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

from dibujo import (H, W, Capa, a_imagen, cartel, chispas, componer, e_back, e_in_out, encabezado, gradiente,
                    lerp, pildora, pop, prog, resplandor, sello, spr_brillo, texto, titulo)

SLUG = "peliculas_4"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
GANCHO_ETIQUETA = "DE PELÍCULAS 4"
PALABRAS_CIERRE = ("abajo", "seguinos")

BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades de películas que te van a explotar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE PELÍCULAS 4",
    },
    {
        "id": "matrix",
        "texto": "Uno: el código verde de {Matrix|Mátrix} son recetas de sushi. "
                 "¡Las escanearon de un libro de cocina japonés!",
        "titulo": "MATRIX",
        "subtitulo": "¡RECETAS DE SUSHI!",
    },
    {
        "id": "tiburon",
        "texto": "Dos: en Tiburón, el tiburón mecánico se rompía todo el tiempo. "
                 "¡Por eso casi no aparece, y da más miedo!",
        "titulo": "TIBURÓN",
        "subtitulo": "¡SE ROMPÍA TODO EL TIEMPO!",
    },
    {
        "id": "viggo",
        "texto": "Tres: en El Señor de los Anillos, {Viggo Mortensen|Vígo Mórtensen} se rompió dos dedos del pie "
                 "pateando un casco. ¡El grito que se escucha es real!",
        "titulo": "EL SEÑOR DE LOS ANILLOS",
        "subtitulo": "¡SE ROMPIÓ DOS DEDOS!",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"matrix": (40, 210, 90), "tiburon": (40, 140, 220), "viggo": (210, 150, 50), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
VERDE = (70, 255, 120)
TINTA = (24, 16, 48)


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "m_codigo": L.palabra("matrix", "código"),
        "m_sushi": L.palabra("matrix", "sushi"),
        "m_escanearon": L.palabra("matrix", "escanearon"),
        "m_japones": L.palabra("matrix", "japonés"),
        "t_mecanico": L.palabra("tiburon", "mecánico"),
        "t_rompia": L.palabra("tiburon", "rompía"),
        "t_aparece": L.palabra("tiburon", "aparece"),
        "t_miedo": L.palabra("tiburon", "miedo"),
        "v_viggo": L.palabra("viggo", "Viggo"),
        "v_rompio": L.palabra("viggo", "rompió"),
        "v_dedos": L.palabra("viggo", "dedos"),
        "v_pateando": L.palabra("viggo", "pateando"),
        "v_grito": L.palabra("viggo", "grito"),
        "v_escucha": L.palabra("viggo", "escucha"),
        "v_real": L.palabra("viggo", "real"),
    }


def efectos(E, L, S):
    patada = E["v_rompio"] + 0.2
    ini_t, fin_t = E["tiburon_ini"], E["viggo_ini"]
    return [
        (E["m_codigo"], S.subida(0.4, 900, 1800), 0.10), (E["m_sushi"], S.pop(900, 300), 0.30),
        (E["m_sushi"] + 0.05, S.brillo_sfx(), 0.20), (E["m_escanearon"], S.subida(0.7, 400, 1600), 0.14),
        (E["m_japones"], S.ding(), 0.22),
        (ini_t, S.viento(fin_t - ini_t), 0.10), (E["t_mecanico"], S.clic(), 0.4),
        (E["t_rompia"], S.chisporroteo(0.6), 0.18), (E["t_rompia"] + 0.1, S.bloop(), 0.35),
        (E["t_aparece"], S.whoosh(0.5, 2000, 200), 0.15), (E["t_miedo"], S.trueno(), 0.18),
        (E["v_viggo"], S.pop(800, 300), 0.22), (patada - 0.1, S.whoosh(0.3, 300, 3000), 0.25),
        (patada, S.golpe(), 0.45), (patada + 0.02, S.quiebre(), 0.45),
        (E["v_dedos"], S.pop(1200, 500), 0.2), (E["v_grito"], S.boom(), 0.30),
        (E["v_escucha"], S.golpe(), 0.35),
    ]


def sacudidas(E):
    return [(E["v_rompio"] + 0.2, 22, 0.35), (E["v_grito"], 12, 0.45), (E["t_miedo"], 8, 0.3)]


# ==================================================================== fondos
def fondo_matrix():
    a = gradiente([(0, (0, 10, 4)), (0.6, (2, 26, 10)), (1, (0, 8, 3))])
    resplandor(a, 540, 900, 520, (20, 90, 40), 0.35)
    return a_imagen(a, 130)


def fondo_mar():
    a = gradiente([(0, (120, 180, 230)), (0.40, (190, 220, 245)), (0.41, (40, 120, 190)), (1, (6, 30, 70))])
    resplandor(a, 820, 420, 200, (255, 250, 220), 0.5)
    return a_imagen(a, 131)


def fondo_campo():
    a = gradiente([(0, (60, 40, 90)), (0.35, (240, 150, 90)), (0.5, (250, 200, 130)), (0.51, (110, 130, 70)),
                   (1, (60, 80, 40))])
    img = a_imagen(a, 132)
    c = Capa(0, 0, W, H, ss=1)
    for x, r, col in ((150, 380, (90, 110, 60)), (700, 460, (80, 100, 55)), (1100, 400, (100, 120, 65))):
        c.circulo(x, 1000 + r * 0.55, r, fill=col)
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(matrix=fondo_matrix(), mar=fondo_mar(), campo=fondo_campo())


# ================================================================ 1 · Matrix
SIMBOLOS = "0123456789ABCDEFKXZ<>=+*"


@lru_cache(None)
def columna_codigo(i):
    """Tira de letras verdes (se la hace caer por la pantalla)."""
    rng = np.random.default_rng(200 + i)
    alto = 2600
    im = Image.new("RGBA", (60, alto), (0, 0, 0, 0))
    for k, y in enumerate(range(0, alto, 52)):
        ch = SIMBOLOS[int(rng.integers(len(SIMBOLOS)))]
        brillo = 0.35 + 0.65 * ((k % 18) / 17)
        col = tuple(int(v * brillo) for v in VERDE) if k % 18 != 17 else (220, 255, 230)
        tx = texto(ch, "negra", 40, color=col)
        im.alpha_composite(tx, (int(30 - tx.width / 2), y))
    return im


def lluvia_codigo(fr, t, alpha):
    for i in range(18):
        v = 160 + 90 * ((i * 7) % 5)
        x = 30 + i * 60
        im = columna_codigo(i)
        y0 = (t * v + i * 377) % im.height
        for y in (y0 - im.height, y0):
            componer(fr, im, x, y - im.height / 2 + 400, alpha=alpha)


def sushi(c, x, y, k):
    c.circulo(x, y + 10 * k, 118 * k, fill=(0, 0, 0, 80))
    c.circulo(x, y, 118 * k, fill=(28, 60, 36), borde=(10, 30, 16), grosor=6 * k)
    c.circulo(x, y, 98 * k, fill=(250, 250, 244))
    rng = np.random.default_rng(3)
    for _ in range(30):
        a, r = rng.uniform(0, 2 * math.pi), rng.uniform(52, 92)
        c.elipse(x + math.cos(a) * r * k, y + math.sin(a) * r * k, 7 * k, 4 * k, fill=(230, 230, 220))
    c.circulo(x - 8 * k, y, 42 * k, fill=(255, 130, 90))
    for i in range(3):
        c.arco(x - 8 * k, y, (16 + 10 * i) * k, (16 + 10 * i) * k, 200, 320, (255, 200, 170), 4 * k)
    c.circulo(x + 34 * k, y + 22 * k, 16 * k, fill=(120, 200, 90))


def nigiri(c, x, y, k):
    c.elipse(x, y + 22 * k, 92 * k, 42 * k, fill=(250, 250, 244), borde=(200, 200, 190), grosor=4 * k)
    c.elipse(x, y - 4 * k, 104 * k, 36 * k, fill=(255, 130, 90), borde=(210, 90, 60), grosor=4 * k)
    for dx in (-50, -10, 30):
        c.arco(x + dx * k, y + 12 * k, 30 * k, 30 * k, 230, 300, (255, 210, 180), 5 * k)


def libro_cocina(c, x, y, k, t):
    c.rrect(x - 250 * k, y - 140 * k, x + 250 * k, y + 150 * k, 16 * k, fill=(190, 40, 50), borde=(110, 20, 28),
            grosor=6 * k)
    for s in (-1, 1):
        c.rrect(x + (s * 120 - 115) * k, y - 125 * k, x + (s * 120 + 115) * k, y + 135 * k, 10 * k,
                fill=(255, 248, 230))
        for i in range(6):
            yy = y + (-95 + i * 36) * k
            c.linea([(x + (s * 120 - 90) * k, yy), (x + (s * 120 + (90 if i % 3 else 40)) * k, yy)],
                    (170, 160, 150), 6 * k)
    c.linea([(x, y - 125 * k), (x, y + 135 * k)], (200, 180, 160), 4 * k)
    nigiri(c, x + 170 * k, y + 60 * k, 0.4 * k)
    sushi(c, x - 170 * k, y + 70 * k, 0.32 * k)


def escena_matrix(t):
    fr = FONDOS["matrix"].copy()
    t0 = ESC["matrix"]["escena_ini"]
    ts, te = E["m_sushi"], E["m_escanearon"]
    atenua = 1 - 0.55 * e_in_out(prog(t, ts - 0.1, 0.4))
    lluvia_codigo(fr, t, 0.9 * atenua * min(1, (t - t0) / 0.3))
    c = Capa(0, 560, W, 900)
    s = e_back(prog(t, ts - 0.05, 0.5))
    if s > 0:
        sushi(c, 400, 820, 1.1 * s)
        nigiri(c, 720, 840, 1.1 * s)
        c.linea([(560, 640), (900, 980)], (180, 120, 60), 12 * s)
        c.linea([(610, 620), (930, 960)], (180, 120, 60), 12 * s)
    sl = e_back(prog(t, te, 0.5))
    if sl > 0:
        libro_cocina(c, 540, 1200, 0.95 * sl, t)
    c.pegar_en(fr)
    if t >= te + 0.3:   # la luz del escáner recorre el libro
        y = 1070 + 260 * ((t - te - 0.3) / 0.9 % 1)
        c = Capa(260, int(y - 30), 560, 60)
        c.rrect(290, y - 6, 790, y + 6, 6, fill=(120, 255, 160, 220))
        c.pegar_en(fr)
        componer(fr, spr_brillo(30, (180, 255, 200)), 790, y)
    if s > 0:
        chispas(fr, t, ts, 560, 830, n=22, seed=4, colores=((120, 255, 160), (255, 255, 255), (255, 170, 120)))
    encabezado(fr, t, 1, E["matrix_badge"])
    titulo(fr, t, TITULOS["matrix"]["titulo"], t0 + 0.15, color=(140, 255, 170))
    pildora(fr, t, TITULOS["matrix"]["subtitulo"], (30, 150, 70), ts, hasta=te)
    pildora(fr, t, "¡DE UN LIBRO DE COCINA!", (190, 40, 50), te + 0.1)
    return fr


# ================================================================ 2 · Tiburón
def aleta(c, x, y, k, ang, rota):
    """Aleta mecánica: metal gris con remaches; `rota` la muestra averiada."""
    pts = [(x - 90 * k, y), (x + 20 * k, y - 190 * k), (x + 90 * k, y)]
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(x + ca * (px - x) - sa * (py - y), y + sa * (px - x) + ca * (py - y)) for px, py in pts]
    c.poligono(P, fill=(120, 130, 142), borde=(60, 66, 76), grosor=6 * k)
    for u, v in ((0.3, 0.2), (0.5, 0.45), (0.62, 0.15), (0.45, 0.7)):
        px = P[0][0] + (P[2][0] - P[0][0]) * u + (P[1][0] - P[0][0]) * v * (1 - u)
        py = P[0][1] + (P[1][1] - P[0][1]) * v
        c.circulo(px, py, 7 * k, fill=(80, 86, 96))
    if rota:
        c.linea([(P[0][0] + 40 * k, P[0][1] - 20 * k), (P[1][0] - 10 * k, P[1][1] + 70 * k)], (40, 40, 48), 5 * k)


def escena_tiburon(t):
    fr = FONDOS["mar"].copy()
    t0 = ESC["tiburon"]["escena_ini"]
    tr, ta, tm = E["t_rompia"], E["t_aparece"], E["t_miedo"]
    mar = 787
    c = Capa(0, 560, W, 900)
    # bote a lo lejos
    by = mar - 12 + 6 * math.sin(t * 2)
    c.poligono([(760, by), (960, by), (930, by + 40), (790, by + 40)], fill=(240, 240, 245), borde=(120, 120, 130),
               grosor=4)
    c.linea([(860, by), (860, by - 90)], (120, 90, 60), 6)
    c.poligono([(866, by - 86), (866, by - 10), (930, by - 10)], fill=(250, 250, 250))
    # la aleta: navega, se rompe (chispas, burbujas) y se hunde
    hunde = e_in_out(prog(t, tr + 0.2, 0.9))
    if hunde < 1:
        x = lerp(160, 520, clamp01((t - t0) / max(0.1, tr - t0))) if t < tr else 520
        ang = 0.5 * hunde + (0.08 * math.sin(t * 30) if tr <= t < tr + 0.5 else 0)
        aleta(c, x, mar + 10 + 260 * hunde, 1.3, ang, t >= tr)
    # olas por encima de la aleta
    for i in range(24):
        x = i * 50 - (t * 40) % 50
        c.arco(x, mar + 6, 26, 10, 200, 340, (230, 240, 255, 200), 5)
    # la sombra bajo el agua (lo que no se ve da más miedo)
    sm = e_in_out(prog(t, ta, 0.6))
    if sm > 0:
        crece = 1 + 1.3 * e_in_out(prog(t, tm, 0.5))
        sx = 540 + 60 * math.sin(t * 0.8)
        c.elipse(sx, 1130, 170 * crece, 60 * crece, fill=(0, 10, 30, int(170 * sm)))
        c.poligono([(sx + 150 * crece, 1130), (sx + 230 * crece, 1090), (sx + 230 * crece, 1170)],
                   fill=(0, 10, 30, int(170 * sm)))
    c.pegar_en(fr)
    if tr <= t < tr + 1.4:   # burbujas y chispas de la avería
        chispas(fr, t, tr, 540, mar - 100, n=20, seed=8, colores=((255, 220, 120), (255, 255, 255)), arriba=True)
        rng = np.random.default_rng(5)
        for i in range(16):
            d = t - tr - rng.uniform(0, 0.6)
            if d > 0:
                componer(fr, spr_brillo(int(rng.integers(10, 20)), (200, 230, 255)),
                         540 + rng.uniform(-80, 80) + 10 * math.sin(d * 8 + i), mar + 220 - d * 260,
                         alpha=clamp01(1.2 - d))
    if t >= tm:   # latido rojo en los bordes
        p = 0.5 + 0.5 * math.sin((t - tm) * 7)
        componer(fr, rojo_bordes(), W / 2, H / 2, alpha=0.35 * p * clamp01((t - tm) / 0.3))
    sc = pop(t, E["t_mecanico"], 0.35) * (1 - pop(t, tr, 0.2))
    if sc > 0.01:
        componer(fr, cartel("MECÁNICO", None, (230, 234, 240), (50, 56, 66), 360, 70), 330, 660, escala=sc, rot=-4)
    encabezado(fr, t, 2, E["tiburon_badge"])
    titulo(fr, t, TITULOS["tiburon"]["titulo"], t0 + 0.15, color=(220, 240, 255))
    pildora(fr, t, TITULOS["tiburon"]["subtitulo"], (200, 60, 50), tr, hasta=tm)
    pildora(fr, t, "¡MENOS TIBURÓN, MÁS MIEDO!", (20, 60, 130), tm + 0.05)
    return fr


@lru_cache(None)
def rojo_bordes():
    yy, xx = np.ogrid[:H, :W]
    d = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a = (np.clip((d - 0.6) / 0.6, 0, 1) * 255).astype(np.uint8)
    im = Image.new("RGBA", (W, H), (200, 10, 20, 0))
    im.putalpha(Image.fromarray(a))
    return im


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


# ============================================================ 3 · la patada
def casco(c, x, y, k, ang=0.0):
    ca, sa = math.cos(ang), math.sin(ang)

    def r(px, py):
        return (x + ca * px - sa * py, y + sa * px + ca * py)
    c.poligono([r(-120 * k, 20 * k)] + [r(math.cos(a) * 120 * k, -math.sin(a) * 130 * k + 20 * k)
                                          for a in np.linspace(0, math.pi, 20)],
               fill=(70, 72, 80), borde=(30, 30, 36), grosor=6 * k)
    c.poligono([r(-130 * k, 20 * k), r(130 * k, 20 * k), r(120 * k, 46 * k), r(-120 * k, 46 * k)],
               fill=(90, 92, 100), borde=(30, 30, 36), grosor=5 * k)
    c.poligono([r(-8 * k, -110 * k), r(0, -170 * k), r(8 * k, -110 * k)], fill=(90, 92, 100))
    for i in range(5):
        c.circulo(*r((-80 + 40 * i) * k, 33 * k), 6 * k, fill=(150, 150, 160))


def bota(c, x, y, k, ang):
    ca, sa = math.cos(ang), math.sin(ang)

    def r(px, py):
        return (x + ca * px - sa * py, y + sa * px + ca * py)
    M, B = (120, 72, 36), (60, 34, 14)
    c.poligono([r(-40 * k, -220 * k), r(40 * k, -220 * k), r(46 * k, -20 * k), r(130 * k, 0), r(140 * k, 50 * k),
                r(-50 * k, 50 * k)], fill=M, borde=B, grosor=6 * k)
    c.poligono([r(-54 * k, 40 * k), r(146 * k, 40 * k), r(146 * k, 62 * k), r(-54 * k, 62 * k)], fill=(50, 34, 24))
    for i in range(4):
        c.linea([r(-30 * k, (-190 + 40 * i) * k), r(30 * k, (-170 + 40 * i) * k)], (220, 200, 160), 4 * k)


def estallido(fr, x, y, s, palabra, color=(255, 220, 60)):
    c = Capa(int(x - 260), int(y - 200), 520, 400)
    pts = []
    for i in range(28):
        r = (180 if i % 2 == 0 else 110) * s
        a = i * math.pi / 14
        pts.append((x + math.cos(a) * r * 1.25, y + math.sin(a) * r * 0.85))
    c.poligono(pts, fill=color, borde=TINTA, grosor=8)
    c.pegar_en(fr)
    componer(fr, texto(palabra, "titulo", 90, color=TINTA), x, y + 6, escala=s, rot=-6)


def escena_viggo(t):
    fr = FONDOS["campo"].copy()
    t0 = ESC["viggo"]["escena_ini"]
    tp = E["v_rompio"] + 0.2   # la patada
    c = Capa(0, 560, W, 900)
    s = e_back(prog(t, t0 + 0.3, 0.5))
    # el casco sale despedido con la patada
    vuelo = e_in_out(prog(t, tp, 0.6))
    cx = 690 + 170 * vuelo
    cy = 1250 - 150 * math.sin(math.pi * vuelo)
    casco(c, cx, cy, 1.25 * s, 0.9 * vuelo)
    # la bota toma envión y patea
    if t < tp - 0.25:
        ang = -0.35 + 0.05 * math.sin(t * 3)
    else:
        ang = lerp(-0.35, 0.5, e_back(prog(t, tp - 0.25, 0.3)))
    bota(c, 360, 1060, 1.35 * s, ang)
    c.pegar_en(fr)
    if tp <= t < tp + 1.0:
        estallido(fr, 600, 1170, pop(t, tp, 0.2) * (1 - prog(t, tp + 0.7, 0.3)), "¡CRAC!")
    sd = pop(t, E["v_dedos"], 0.35) * (1 - pop(t, E["v_grito"] - 0.1, 0.2))
    if sd > 0.01:   # los dos dedos rotos: estrellitas de dolor
        for i in range(5):
            a = t * 4 + i * 2 * math.pi / 5
            componer(fr, spr_brillo(26, (255, 230, 120)), 480 + 80 * math.cos(a), 1010 + 30 * math.sin(a), alpha=sd)
        componer(fr, cartel("2 DEDOS ROTOS", None, (255, 255, 255), (180, 40, 40), 380, 60), 300, 690,
                 escala=sd, rot=-4)
    sv = pop(t, E["v_viggo"], 0.35) * (1 - pop(t, tp, 0.2))
    if sv > 0.01:
        componer(fr, cartel("VIGGO MORTENSEN", "EL ACTOR", (255, 230, 170), (70, 40, 20), 560, 76), 540, 700,
                 escala=sv, rot=-2)
    tg = E["v_grito"]
    sg = pop(t, tg, 0.3)
    if sg > 0:
        temb = 6 * math.sin(t * 50) * math.exp(-(t - tg) * 2)
        componer(fr, texto("¡AAAAH!", "titulo", 150, color=(255, 240, 200), borde=12, color_borde=(140, 20, 20),
                           sombra=10), 560 + temb, 720, escala=sg, rot=-5)
    sr = pop(t, E["v_escucha"], 0.3)
    if sr > 0:
        componer(fr, sello("¡ES REAL!", (200, 40, 40), 84), 790, 930, escala=lerp(1.6, 1.0, sr) * sr, rot=10)
    encabezado(fr, t, 3, E["viggo_badge"])
    titulo(fr, t, TITULOS["viggo"]["titulo"], t0 + 0.15, tam=110, color=(255, 236, 190))
    pildora(fr, t, TITULOS["viggo"]["subtitulo"], (180, 50, 40), E["v_dedos"], hasta=E["v_pateando"])
    pildora(fr, t, "¡PATEANDO UN CASCO!", (120, 80, 40), E["v_pateando"] + 0.05)
    return fr


# ======================================================= íconos del cierre
def _icono_sushi(c, x, y, s, t):
    sushi(c, x, y, 0.8 * s)


def _icono_aleta(c, x, y, s, t):
    c.circulo(x, y + 40 * s, 100 * s, fill=(60, 140, 210))
    aleta(c, x, y + 40 * s, 0.7 * s, 0.0, False)


def _icono_casco(c, x, y, s, t):
    casco(c, x, y + 30 * s, 0.62 * s)


ICONOS = [_icono_sushi, _icono_aleta, _icono_casco]
ESCENAS = {"matrix": escena_matrix, "tiburon": escena_tiburon, "viggo": escena_viggo}
