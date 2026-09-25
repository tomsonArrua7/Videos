"""Episodio 8: más curiosidades de películas (voz de Tomás, Argentina).

Las imágenes usan objetos y guiños genéricos (un baño, un frasco de chocolate,
un par de zapatos, un copo de nieve), nunca personajes o logos con derechos de autor.
"""
import math
from functools import lru_cache

import numpy as np

from dibujo import (H, W, Capa, a_imagen, cartel, chispas, componer, e_back, e_out, encabezado, gradiente,
                    lerp, mezcla, nota_musical, pelicula_vieja, pildora, pop, prog, sello, sepia,
                    spr_estrella, spr_resplandor, texto, titulo, viñeta)

SLUG = "peliculas_3"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
VOZ_FINAL = 0.8         # así Tomás habla a +2 % en vez de +4 %
GANCHO_ETIQUETA = "DE PELÍCULAS 3"
PALABRAS_CIERRE = ("abajo", "seguinos")

# Guion escrito para el oído. "Dorothy" se leía "Dorotí": no hace falta nombrarla.
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades más de películas que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE PELÍCULAS 3",
    },
    {
        "id": "ducha",
        "texto": "Uno: en la escena de la ducha de Psicosis, la sangre era jarabe de chocolate. "
                 "¡En blanco y negro no se notaba!",
        "titulo": "PSICOSIS",
        "subtitulo": "¡ERA JARABE DE CHOCOLATE!",
    },
    {
        "id": "zapatos",
        "texto": "Dos: en el libro de El Mago de Oz, los zapatos eran plateados. "
                 "¡Los hicieron rojos para lucir el color!",
        "titulo": "EL MAGO DE OZ",
        "subtitulo": "EN EL LIBRO ERAN PLATEADOS",
    },
    {
        "id": "elsa",
        "texto": "Tres: en {Frozen|Fróusen}, Elsa iba a ser la villana. ¡Todo cambió con la canción Libre soy!",
        "titulo": "FROZEN",
        "subtitulo": "¡IBA A SER LA VILLANA!",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"ducha": (120, 70, 40), "zapatos": (220, 30, 70),
          "elsa": (120, 200, 255), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
CHOCOLATE = (104, 52, 24)
PLATA, RUBI = (200, 204, 216), (206, 20, 52)
HORIZONTE_OZ = 1000
NIEVE = 1150


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "d_sangre": L.palabra("ducha", "sangre"),
        "d_chocolate": L.palabra("ducha", "chocolate"),
        "d_blanco": L.palabra("ducha", "blanco"),
        "z_libro": L.palabra("zapatos", "libro"),
        "z_plateados": L.palabra("zapatos", "plateados"),
        "z_rojos": L.palabra("zapatos", "rojos"),
        "e_elsa": L.palabra("elsa", "elsa"),
        "e_villana": L.palabra("elsa", "villana"),
        "e_cancion": L.palabra("elsa", "canción"),
        "e_libre": L.palabra("elsa", "libre"),
    }


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    ini_d, fin_d = E["ducha_ini"], E["zapatos_ini"]
    fx = [(ini_d, S.lluvia(fin_d - ini_d), 0.08),
          (E["ducha_ini"] + 0.5, S.pop(700, 300), 0.20),
          (E["d_chocolate"], S.bloop(), 0.35), (E["d_chocolate"] + 0.1, S.brillo_sfx(), 0.20),
          (E["d_blanco"], S.pop(600, 900), 0.25),
          (E["z_libro"], S.pop(800, 300), 0.25), (E["z_plateados"], S.brillo_sfx(), 0.18),
          (E["z_rojos"], S.brillo_sfx(), 0.30), (E["z_rojos"] + 0.1, S.ding(), 0.22)]
    ini_e, fin_e = E["elsa_ini"], E["cierre_ini"]
    fx += [(ini_e, S.viento(fin_e - ini_e), 0.14),
           (E["e_villana"], S.golpe(), 0.40), (E["e_villana"] + 0.05, S.error_(), 0.18),
           (E["e_cancion"], S.brillo_sfx(), 0.25), (E["e_cancion"] + 0.3, S.brillo_sfx(), 0.18),
           (E["e_libre"] + 0.2, S.golpe(), 0.40), (E["e_libre"] + 0.25, S.chisporroteo(0.5), 0.12),
           (E["e_libre"] + 0.3, S.ding(), 0.25)]
    return fx


def sacudidas(E):
    return [(E["e_villana"], 8, 0.2), (E["e_libre"] + 0.2, 10, 0.25)]


# ==================================================================== fondos
def fondo_ducha():
    a = gradiente([(0, (206, 214, 222)), (0.64, (226, 232, 238)), (0.6401, (246, 246, 248)), (1, (214, 218, 224))])
    viñeta(a, 0.35)
    img = a_imagen(a, 60)
    c = Capa(0, 0, W, H)
    for y in range(40, 1228, 84):
        c.linea([(0, y), (W, y)], (178, 186, 196), 4, puntas=False)
    for x in range(40, W, 84):
        c.linea([(x, 0), (x, 1228)], (178, 186, 196), 4, puntas=False)
    c.rrect(-20, 1220, W + 20, 1262, 18, fill=(255, 255, 255), borde=(170, 176, 186), grosor=5)
    c.rrect(760, 520, 1000, 540, 8, fill=(170, 176, 190))   # caño
    c.linea([(990, 530), (990, 700)], (170, 176, 190), 18)
    c.poligono([(700, 560), (820, 520), (840, 590), (720, 630)], fill=(190, 196, 210), borde=(120, 126, 140), grosor=5)
    # cortina con aros
    c.linea([(0, 520), (360, 520)], (150, 156, 170), 12)
    for i in range(7):
        x = 20 + i * 50
        c.circulo(x, 530, 14, borde=(150, 156, 170), grosor=5)
    pts = [(x, 540 + 6 * math.sin(x / 20)) for x in range(0, 370, 10)]
    pts += [(340 + 30 * math.sin(y / 60), y) for y in range(540, 1240, 20)]
    pts += [(0, 1240)]
    c.poligono(pts, fill=(236, 240, 246, 220))
    for x in range(40, 340, 50):
        c.linea([(x, 560), (x + 12 * math.sin(x), 1220)], (206, 212, 224), 4, puntas=False)
    c.pegar_en(img)
    return img


def fondo_zapatos():
    corte = HORIZONTE_OZ / H
    a = gradiente([(0, (110, 186, 250)), (corte - 0.001, (206, 238, 255)), (corte, (120, 196, 110)),
                   (1, (70, 150, 70))])
    img = a_imagen(a, 61)
    c = Capa(0, 700, W, H - 700)
    for x0, alto, ancho in ((440, 150, 50), (500, 230, 60), (560, 280, 70), (630, 200, 56), (690, 130, 44)):
        c.rrect(x0 - ancho / 2, HORIZONTE_OZ - alto, x0 + ancho / 2, HORIZONTE_OZ, 6, fill=(60, 190, 110))
        c.poligono([(x0 - ancho / 2, HORIZONTE_OZ - alto), (x0, HORIZONTE_OZ - alto - 70),
                    (x0 + ancho / 2, HORIZONTE_OZ - alto)], fill=(40, 160, 90))
    for x, r in ((150, 260), (930, 240)):
        c.elipse(x, HORIZONTE_OZ + 40, r, 90, fill=(100, 180, 90))
    # camino de baldosas amarillas en perspectiva
    c.poligono([(510, HORIZONTE_OZ), (570, HORIZONTE_OZ), (1020, H), (60, H)], fill=(246, 206, 60))
    for i in range(1, 16):
        u = (i / 16) ** 1.8
        y = HORIZONTE_OZ + (H - HORIZONTE_OZ) * u
        xa, xb = lerp(510, 60, u), lerp(570, 1020, u)
        c.linea([(xa, y), (xb, y)], (196, 150, 30), 2 + 4 * u, puntas=False)
        for j in range(1, 6):
            x = lerp(xa, xb, (j + 0.5 * (i % 2)) / 6)
            c.linea([(x, y), (x, y - (H - HORIZONTE_OZ) * ((i / 16) ** 1.8 - ((i - 1) / 16) ** 1.8))],
                    (196, 150, 30), 2 + 3 * u, puntas=False)
    c.pegar_en(img)
    return img


def fondo_elsa():
    corte = NIEVE / H
    a = gradiente([(0, (14, 22, 66)), (0.4, (40, 70, 150)), (corte - 0.001, (120, 170, 230)), (corte, (226, 238, 255)),
                   (1, (180, 206, 240))])
    img = a_imagen(a, 62)
    rng = np.random.default_rng(63)
    for _ in range(80):
        componer(img, spr_estrella(int(rng.integers(2, 6))), rng.uniform(0, W), rng.uniform(0, 900),
                 alpha=rng.uniform(0.3, 0.9))
    c = Capa(0, 800, W, 360)
    for x0, alto, ancho, col in ((180, 300, 520, (200, 220, 250)), (820, 340, 560, (186, 208, 244)),
                                 (520, 220, 480, (214, 230, 252))):
        c.poligono([(x0 - ancho / 2, NIEVE + 2), (x0, NIEVE - alto), (x0 + ancho / 2, NIEVE + 2)], fill=col)
        c.poligono([(x0, NIEVE - alto), (x0 + ancho / 2, NIEVE + 2), (x0 + ancho / 6, NIEVE + 2)],
                   fill=tuple(int(v * 0.88) for v in col))
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(ducha=fondo_ducha(), zapatos=fondo_zapatos(), elsa=fondo_elsa())


# ================================================================ elementos
@lru_cache(None)
def frasco_chocolate(k=1.0):
    """Frasco de jarabe de chocolate genérico (parado)."""
    w, h = int(200 * k), int(360 * k)
    c = Capa(0, 0, w, h, ss=3)
    B = (40, 18, 6)
    c.rrect(62 * k, 8 * k, 138 * k, 60 * k, 10 * k, fill=(230, 60, 60), borde=B, grosor=4 * k)
    c.rrect(76 * k, 50 * k, 124 * k, 100 * k, 8 * k, fill=CHOCOLATE, borde=B, grosor=4 * k)
    c.rrect(20 * k, 90 * k, 180 * k, 350 * k, 40 * k, fill=CHOCOLATE, borde=B, grosor=6 * k)
    c.rrect(36 * k, 150 * k, 164 * k, 290 * k, 14 * k, fill=(250, 240, 220), borde=B, grosor=4 * k)
    c.rrect(40 * k, 110 * k, 60 * k, 320 * k, 10 * k, fill=(150, 90, 50))
    im = c.imagen()
    for txt, tam, y in (("JARABE", 30, 170), ("DE", 22, 208), ("CHOCOLATE", 24, 240)):
        tx = texto(txt, "negra", int(tam * k), color=B)
        im.alpha_composite(tx, (int(w / 2 - tx.width / 2), int(y * k)))
    return im


def zapato(c, x, y, k, color, brillo_seed=0):
    B = tuple(int(v * 0.35) for v in color)

    def P(dx, dy):
        return (x + dx * k, y + dy * k)

    c.poligono([P(-82, -12), P(-60, -12), P(-62, 44), P(-78, 44)], fill=mezcla(color, (0, 0, 0), 0.3), borde=B,
               grosor=4 * k)
    c.poligono([P(-72, 34), P(96, 36), P(98, 46), P(-70, 44)], fill=(40, 30, 30))
    cuerpo = [P(-80, -34), P(-54, -44), P(-30, -26), P(-6, -10), P(40, -4), P(78, 6), P(98, 30), P(90, 38),
              P(-70, 36)]
    c.poligono(cuerpo, fill=color, borde=B, grosor=5 * k)
    c.elipse(*P(-38, -30), 26 * k, 8 * k, fill=mezcla(color, (0, 0, 0), 0.55))
    rng = np.random.default_rng(brillo_seed)
    for _ in range(40):  # brillitos, solo adentro de la capellada
        dx, dy = rng.uniform(-76, 92), rng.uniform(-44, 32)
        borde_sup = np.interp(dx, [-80, -54, -30, -6, 40, 78, 98], [-34, -44, -26, -10, -4, 6, 30])
        if borde_sup + 6 < dy < 30:
            c.circulo(*P(dx, dy), rng.uniform(2, 4.5) * k, fill=mezcla(color, (255, 255, 255), rng.uniform(0.3, 0.8)))
    for s in (-1, 1):
        c.elipse(*P(46 + s * 14, -4), 16 * k, 10 * k, fill=mezcla(color, (0, 0, 0), 0.15), borde=B, grosor=3 * k)
    c.circulo(*P(46, -4), 7 * k, fill=mezcla(color, (255, 255, 255), 0.3), borde=B, grosor=3 * k)


def libro(c, x, y, k=1.0):
    B = (70, 40, 20)
    c.rrect(x - 230 * k, y - 110 * k, x + 230 * k, y + 120 * k, 16 * k, fill=(130, 70, 40), borde=B, grosor=5 * k)
    for s in (-1, 1):
        c.poligono([(x, y - 100 * k), (x + s * 214 * k, y - 110 * k), (x + s * 214 * k, y + 106 * k), (x, y + 112 * k)],
                   fill=(252, 244, 222), borde=B, grosor=3 * k)
    for i in range(6):
        c.linea([(x - 190 * k, y - 60 * k + i * 26 * k), (x - 30 * k, y - 62 * k + i * 26 * k)], (190, 176, 150),
                5 * k, puntas=False)
    zapato(c, x + 110 * k, y + 10 * k, 0.9 * k, PLATA, 7)


def copo(c, x, y, r, ang, color, grosor=14):
    for i in range(6):
        a = ang + i * math.pi / 3
        ux, uy = math.cos(a), math.sin(a)
        c.linea([(x, y), (x + r * ux, y + r * uy)], color, grosor)
        for f, largo in ((0.45, 0.28), (0.72, 0.2)):
            bx, by = x + r * f * ux, y + r * f * uy
            for s in (-1, 1):
                b = a + s * math.radians(45)
                c.linea([(bx, by), (bx + r * largo * math.cos(b), by + r * largo * math.sin(b))], color, grosor * 0.8)
        c.circulo(x + r * ux, y + r * uy, grosor * 0.9, fill=color)
    c.circulo(x, y, r * 0.16, fill=color)


# =================================================================== escenas
def escena_ducha(t):
    fr = FONDOS["ducha"].copy()
    t0 = ESC["ducha"]["escena_ini"]
    tc, tb = E["d_chocolate"], E["d_blanco"]
    c = Capa(0, 560, W, 900)
    # agua de la ducha
    rng = np.random.default_rng(int(t * 30))
    for _ in range(26):
        x0 = rng.uniform(700, 840)
        y0 = rng.uniform(620, 1180)
        c.linea([(x0 - 60 * (y0 - 600) / 600, y0), (x0 - 60 * (y0 + 40 - 600) / 600, y0 + 40)], (170, 200, 230, 200), 4)
    # el "chocolate" que gira en la rejilla
    cx, cy = 540, 1340
    c.elipse(cx, cy, 240, 60, fill=(220, 224, 230))
    for i in range(5):
        a0 = t * 2.5 + i * 2 * math.pi / 5
        pts = [(cx + (180 - 150 * u) * math.cos(a0 + 3 * u), cy + (48 - 40 * u) * math.sin(a0 + 3 * u))
               for u in np.linspace(0, 1, 14)]
        c.linea(pts, CHOCOLATE, 14 - 8 * i / 5)
    c.circulo(cx, cy, 30, fill=(150, 150, 160), borde=(90, 90, 100), grosor=4)
    for dx in (-12, 0, 12):
        c.linea([(cx + dx, cy - 18), (cx + dx, cy + 18)], (70, 70, 80), 4)
    # el frasco que vuelca el chocolate
    s = pop(t, tc - 0.1, 0.4)
    if s > 0:
        c.linea([(716, 1050), (690, 1180), (620, 1320)], CHOCOLATE, 16)
    c.pegar_en(fr)
    if s > 0:
        componer(fr, frasco_chocolate(1.0), 790, 960, escala=s, rot=125)
    sc = pop(t, t0 + 0.5, 0.4) * (1 - e_out(prog(t, tc - 0.2, 0.25)))
    if sc > 0.01:
        componer(fr, cartel("ALFRED HITCHCOCK", "1960", (240, 240, 240), (30, 30, 34), 560, 76), 540, 660,
                 escala=sc, rot=-2)
    # blanco y negro hasta que aparece el chocolate; después, comparación lado a lado
    color = e_out(prog(t, tc, 0.4))
    viejo = pelicula_vieja(fr, t, color)
    if t >= tb:
        p = e_out(prog(t, tb, 0.35))
        corte = int(W / 2 * p)
        bn = pelicula_vieja(fr, t, 0.0)
        viejo = fr.copy()
        viejo.paste(bn.crop((0, 0, corte, H)), (0, 0))
        c = Capa(0, 560, W, 1000)
        c.linea([(corte, 560), (corte, 1470)], (255, 255, 255), 8, puntas=False)
        c.pegar_en(viejo)
        if p > 0.9:
            componer(viejo, texto("EN LA PELÍCULA", "negra", 40, borde=7), 270, 610)
            componer(viejo, texto("EN LA REALIDAD", "negra", 40, color=(255, 214, 150), borde=7), 810, 610)
    fr = viejo
    encabezado(fr, t, 1, E["ducha_badge"])
    titulo(fr, t, TITULOS["ducha"]["titulo"], t0 + 0.15, color=(255, 255, 255))
    pildora(fr, t, TITULOS["ducha"]["subtitulo"], CHOCOLATE, tc)
    return fr


def escena_zapatos(t):
    fr = FONDOS["zapatos"].copy()
    t0 = ESC["zapatos"]["escena_ini"]
    tr = E["z_rojos"]
    rojo = e_out(prog(t, tr, 0.6))
    s = pop(t, E["z_libro"], 0.4) * (1 - e_out(prog(t, tr + 0.4, 0.3)))
    if s > 0.01:
        c = Capa(270, 540, 540, 300)
        libro(c, 540, 690, s)
        c.pegar_en(fr)
        componer(fr, texto("EL LIBRO (1900)", "negra", 34, color=(255, 255, 255), borde=6), 540, 552, escala=s)
    c = Capa(200, 1020, 680, 320)
    sz = e_back(prog(t, t0 + 0.2, 0.5))
    if sz > 0:
        salto = 12 * abs(math.sin(t * 3)) if t >= tr else 0
        color = mezcla(PLATA, RUBI, rojo)
        zapato(c, 470, 1190 - salto, 1.5 * sz, mezcla(color, (0, 0, 0), 0.12), 2)
        zapato(c, 610, 1210 - salto, 1.6 * sz, color, 3)
    c.pegar_en(fr)
    for i in range(12):  # destellos de los zapatos
        a = i * 2 * math.pi / 12 + t
        tw = 0.5 + 0.5 * math.sin(t * 6 + i * 1.3)
        componer(fr, spr_resplandor(12, (255, 255, 255)), 540 + 230 * math.cos(a), 1190 + 90 * math.sin(a),
                 alpha=tw * 0.6 * sz)
    if tr <= t < tr + 1.0:
        chispas(fr, t, tr, 540, 1180, n=28, seed=11, colores=((255, 90, 120), (255, 255, 255), (255, 214, 10)),
                vel=(250, 700), grav=400, dur=1.0)
    fr = sepia(fr, 1 - rojo)
    encabezado(fr, t, 2, E["zapatos_badge"])
    titulo(fr, t, TITULOS["zapatos"]["titulo"], t0 + 0.15, color=mezcla((255, 236, 200), (120, 230, 140), rojo))
    pildora(fr, t, TITULOS["zapatos"]["subtitulo"], (120, 124, 140), E["z_plateados"], hasta=tr)
    pildora(fr, t, "¡ROJOS PARA LUCIR EL COLOR!", RUBI, tr + 0.1)
    return fr


def escena_elsa(t):
    fr = FONDOS["elsa"].copy()
    t0 = ESC["elsa"]["escena_ini"]
    tl = E["e_libre"]
    heroe = e_out(prog(t, tl + 0.2, 0.5))
    # nieve que cae
    rng = np.random.default_rng(64)
    c = Capa(0, 0, W, H, ss=1)
    for _ in range(90):
        x0, y0, v, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(80, 200), rng.uniform(3, 8)
        y = (y0 + v * t) % (H + 40) - 20
        c.circulo(x0 + 30 * math.sin(t + x0), y, r, fill=(255, 255, 255, 210))
    c.pegar_en(fr)
    # el copo: oscuro (villana) y después brillante (heroína)
    componer(fr, spr_resplandor(330, mezcla((110, 40, 150), (150, 220, 255), heroe)), 540, 900,
             alpha=0.55 + 0.25 * math.sin(t * 3))
    s = e_back(prog(t, t0 + 0.2, 0.5))
    if s > 0:
        c = Capa(260, 620, 560, 560)
        col = mezcla((96, 50, 140), (190, 235, 255), heroe)
        copo(c, 540, 900, 230 * s * (1 + 0.08 * heroe * math.sin(t * 6)), t * 0.3, col, 18)
        copo(c, 540, 900, 230 * s, t * 0.3, mezcla((150, 110, 200), (255, 255, 255), heroe), 7)
        c.pegar_en(fr)
    # la canción: notas que vuelan
    if t >= E["e_cancion"]:
        c = Capa(0, 560, W, 900)
        for i in range(8):
            ph = ((t - E["e_cancion"]) * 0.6 + i / 8) % 1
            x = 150 + i * 110 + 30 * math.sin(t * 2 + i)
            nota_musical(c, x, 1400 - 700 * ph, 1.0, (255, 255, 255, int(255 * math.sin(math.pi * ph))), i % 3 == 0)
        c.pegar_en(fr)
        sc = pop(t, E["e_cancion"], 0.4)
        componer(fr, cartel("LIBRE SOY", "LA CANCIÓN", (190, 235, 255), (20, 40, 100), 480, 84), 540, 660,
                 escala=sc, rot=-2)
    elif t >= E["e_elsa"]:
        componer(fr, cartel("ELSA", "EL PERSONAJE", (190, 235, 255), (20, 40, 100), 420, 84), 540, 660,
                 escala=pop(t, E["e_elsa"], 0.35), rot=2)
    # sellos: villana -> heroína
    if E["e_villana"] <= t < tl + 0.2:
        p = prog(t, E["e_villana"], 0.22)
        componer(fr, sello("VILLANA", (170, 20, 40), 110), 540, 910, escala=lerp(2.2, 1.0, e_out(p)), rot=-10,
                 alpha=min(1.0, p * 3))
    if t >= tl + 0.2:
        p = prog(t, tl + 0.2, 0.22)
        componer(fr, sello("HEROÍNA", (30, 120, 220), 110), 540, 910, escala=lerp(2.2, 1.0, e_out(p)), rot=8,
                 alpha=min(1.0, p * 3))
        chispas(fr, t, tl + 0.2, 540, 910, n=26, seed=9, colores=((190, 235, 255), (255, 255, 255)),
                vel=(300, 750), grav=300, dur=1.0)
    encabezado(fr, t, 3, E["elsa_badge"])
    titulo(fr, t, TITULOS["elsa"]["titulo"], t0 + 0.15, color=(200, 240, 255))
    pildora(fr, t, TITULOS["elsa"]["subtitulo"], (150, 30, 60), E["e_villana"], hasta=tl)
    pildora(fr, t, "¡LA SALVÓ UNA CANCIÓN!", (30, 120, 220), tl + 0.1)
    return fr


# ======================================================= íconos del cierre
def _icono_ducha(c, x, y, s, t):
    return [(frasco_chocolate(0.55), x, y + 4 * s)] if s > 0.05 else []


def _icono_zapatos(c, x, y, s, t):
    zapato(c, x - 4 * s, y + 10 * s, 1.1 * s, RUBI, 3)


def _icono_elsa(c, x, y, s, t):
    copo(c, x, y, 92 * s, t * 0.3, (120, 200, 255), 10 * s)
    copo(c, x, y, 92 * s, t * 0.3, (230, 248, 255), 4 * s)


ICONOS = [_icono_ducha, _icono_zapatos, _icono_elsa]
ESCENAS = {"ducha": escena_ducha, "zapatos": escena_zapatos, "elsa": escena_elsa}
