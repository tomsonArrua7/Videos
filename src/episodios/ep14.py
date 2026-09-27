"""Episodio 14: más curiosidades de películas (voz de Tomás, Argentina).

El Padrino, Monsters Inc. y Rocky, con objetos genéricos (un gato en un sillón, una bola de
pelo azul con ojos, una máquina de escribir y guantes de boxeo): ningún personaje ni logo.
"""
import math
from functools import lru_cache

import numpy as np

from dibujo import (W, Capa, a_imagen, cartel, chispas, componer, e_back, e_in_out, encabezado, gradiente, lerp,
                    pildora, pop, prog, resplandor, sello, spr_brillo, spr_resplandor, texto, titulo, viñeta)

SLUG = "peliculas_5"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
GANCHO_ETIQUETA = "DE PELÍCULAS 5"
PALABRAS_CIERRE = ("abajo", "seguinos")

BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades de películas que te van a explotar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE PELÍCULAS 5",
    },
    {
        "id": "padrino",
        "texto": "Uno: el gato de El Padrino era un gato callejero del estudio. "
                 "¡Su ronroneo tapaba la voz de {Marlon Brando|Márlon Brándo}!",
        "titulo": "EL PADRINO",
        "subtitulo": "¡UN GATO CALLEJERO!",
    },
    {
        "id": "monstruo",
        "texto": "Dos: en {Monsters Inc|Mónsters Ínc}, el monstruo azul tiene más de dos millones de pelos. "
                 "¡La computadora movía cada uno por separado!",
        "titulo": "MONSTERS INC.",
        "subtitulo": "¡MÁS DE 2 MILLONES DE PELOS!",
    },
    {
        "id": "rocky",
        "texto": "Tres: {Sylvester Stallone|Silvéster Estalón} escribió Rocky en tres días y medio. "
                 "¡Y solo la vendió si él era el protagonista!",
        "titulo": "ROCKY",
        "subtitulo": "¡ESCRITA EN 3 DÍAS Y MEDIO!",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"padrino": (170, 50, 45), "monstruo": (60, 150, 255), "rocky": (240, 180, 40), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
TINTA = (24, 16, 48)


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "p_gato": L.palabra("padrino", "gato"),
        "p_callejero": L.palabra("padrino", "callejero"),
        "p_ronroneaba": L.palabra("padrino", "ronroneo"),
        "p_voz": L.palabra("padrino", "voz"),
        "m_azul": L.palabra("monstruo", "azul"),
        "m_millones": L.palabra("monstruo", "millones"),
        "m_computadora": L.palabra("monstruo", "computadora"),
        "m_separado": L.palabra("monstruo", "separado"),
        "r_escribio": L.palabra("rocky", "escribió"),
        "r_dias": L.palabra("rocky", "días"),
        "r_vendio": L.palabra("rocky", "vendió"),
        "r_protagonista": L.palabra("rocky", "protagonista"),
    }


def _ronroneo(S, dur=1.6):
    t = S.tt(dur)
    rng = np.random.default_rng(14)
    pulsos = 0.5 + 0.5 * np.sin(2 * np.pi * 24 * t) ** 2
    ruido = S.filtro(rng.standard_normal(len(t)), "lowpass", 350)
    return ruido * pulsos * np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.3) * 2.5


def _miau(S, dur=0.55):
    t = S.tt(dur)
    f = 520 + 380 * np.sin(np.pi * t / dur) ** 1.5
    fase = 2 * np.pi * np.cumsum(f) / S.SR
    y = sum(np.sin(k * fase) / k for k in range(1, 6))
    return S.filtro(y, "bandpass", [500, 3000]) * np.sin(np.pi * t / dur) ** 0.6


def efectos(E, L, S):
    fx = [(E["p_gato"], _miau(S), 0.16), (E["p_callejero"], S.pop(800, 300), 0.22),
          (E["p_ronroneaba"], _ronroneo(S), 0.30), (E["p_voz"], S.error_(), 0.10),
          (E["m_azul"], S.whoosh(0.5, 800, 3000), 0.18), (E["m_computadora"], S.pop(1400, 1200, 0.06), 0.25),
          (E["m_computadora"] + 0.12, S.pop(1800, 1600, 0.06), 0.25), (E["m_separado"], S.brillo_sfx(), 0.22),
          (E["r_dias"], S.ding(), 0.25), (E["r_vendio"], S.error_(), 0.16),
          (E["r_protagonista"], S.golpe(), 0.40), (E["r_protagonista"] + 0.05, S.ding(), 0.25),
          (E["r_protagonista"] + 0.3, S.ding(), 0.22)]
    for i in range(14):   # contador de pelos
        fx.append((E["m_millones"] + 0.06 * i, S.tic(), 0.18))
    for i in range(16):   # máquina de escribir
        fx.append((E["r_escribio"] + 0.1 * i, S.clic(), 0.35))
    return fx


def sacudidas(E):
    return [(E["r_protagonista"], 14, 0.3)]


# ==================================================================== fondos
def fondo_despacho():
    a = gradiente([(0, (40, 24, 16)), (0.6, (70, 42, 26)), (1, (30, 18, 12))])
    resplandor(a, 250, 620, 420, (255, 190, 110), 0.35)
    viñeta(a, 0.6)
    img = a_imagen(a, 140)
    c = Capa(0, 0, W, 1920, ss=1)
    for x in range(60, W, 140):   # paneles de madera
        c.linea([(x, 0), (x, 1400)], (90, 56, 34, 120), 8, puntas=False)
    c.pegar_en(img)
    return img


def fondo_fabrica():
    a = gradiente([(0, (40, 30, 110)), (0.6, (90, 60, 170)), (1, (30, 20, 80))])
    resplandor(a, 540, 950, 520, (140, 200, 255), 0.35)
    img = a_imagen(a, 141)
    c = Capa(0, 0, W, 1920, ss=1)
    rng = np.random.default_rng(142)
    for _ in range(9):   # puertas de colores al fondo
        x, y = rng.uniform(40, W - 40), rng.uniform(560, 1400)
        col = [(255, 120, 160, 50), (120, 255, 200, 50), (255, 220, 100, 50)][int(rng.integers(3))]
        c.rrect(x - 50, y - 90, x + 50, y + 90, 10, fill=col)
    c.pegar_en(img)
    return img


def fondo_ring():
    a = gradiente([(0, (20, 20, 40)), (0.55, (50, 40, 70)), (0.56, (40, 90, 170)), (1, (20, 50, 110))])
    resplandor(a, 540, 700, 480, (255, 240, 200), 0.35)
    img = a_imagen(a, 143)
    c = Capa(0, 0, W, 1920, ss=1)
    for i, col in enumerate(((230, 60, 60), (255, 255, 255), (60, 110, 230))):
        c.linea([(0, 1260 + i * 50), (W, 1240 + i * 50)], col, 12, puntas=False)
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(despacho=fondo_despacho(), fabrica=fondo_fabrica(), ring=fondo_ring())


# ============================================================ 1 · el gato
def sillon(c, x, y):
    R, B = (130, 24, 30), (70, 10, 14)
    c.rrect(x - 230, y - 250, x + 230, y + 30, 70, fill=R, borde=B, grosor=6)
    c.rrect(x - 250, y - 10, x + 250, y + 120, 30, fill=(150, 30, 36), borde=B, grosor=6)
    for s in (-1, 1):
        c.rrect(x + s * 250 - 50, y - 90, x + s * 250 + 50, y + 110, 40, fill=R, borde=B, grosor=6)
        c.rrect(x + s * 200 - 16, y + 110, x + s * 200 + 16, y + 170, 6, fill=(60, 36, 20))
    for i in range(3):
        c.circulo(x - 120 + 120 * i, y - 170, 10, fill=(90, 14, 20))


def gato(c, x, y, k, t, ojos_cerrados=True):
    G, O, B = (150, 150, 160), (110, 110, 122), (70, 70, 80)
    c.elipse(x, y, 160 * k, 82 * k, fill=G, borde=B, grosor=5 * k)
    for i in range(4):   # rayas atigradas
        c.arco(x + (-40 + 50 * i) * k, y - 20 * k, 30 * k, 50 * k, 200, 340, O, 9 * k)
    cola = [(x + 150 * k, y + 20 * k), (x + 170 * k, y + 70 * k), (x + 60 * k, y + 90 * k),
            (x - 60 * k, y + 80 * k + 6 * math.sin(t * 2) * k)]
    c.linea(cola, B, 34 * k)
    c.linea(cola, G, 24 * k)
    hx, hy = x - 150 * k, y - 36 * k
    for s in (-1, 1):
        c.poligono([(hx + s * 22 * k, hy - 40 * k), (hx + s * 58 * k, hy - 86 * k), (hx + s * 62 * k, hy - 26 * k)],
                   fill=G, borde=B, grosor=4 * k)
    c.circulo(hx, hy, 66 * k, fill=G, borde=B, grosor=5 * k)
    for s in (-1, 1):
        ex, ey = hx + s * 26 * k, hy - 8 * k
        if ojos_cerrados:
            c.arco(ex, ey, 14 * k, 9 * k, 20, 160, (40, 40, 50), 5 * k)
        else:
            c.elipse(ex, ey, 10 * k, 13 * k, fill=(150, 200, 90))
            c.elipse(ex, ey, 3 * k, 10 * k, fill=(20, 20, 20))
        for d in (-1, 1):
            c.linea([(hx + s * 30 * k, hy + 22 * k), (hx + s * 90 * k, hy + (22 + d * 12) * k)], (230, 230, 235), 3 * k)
    c.poligono([(hx - 9 * k, hy + 12 * k), (hx + 9 * k, hy + 12 * k), (hx, hy + 22 * k)], fill=(240, 150, 170))


def microfono(c, x, y, k):
    c.linea([(x, y + 60 * k), (x, y + 240 * k)], (60, 60, 70), 10 * k)
    c.rrect(x - 60 * k, y + 232 * k, x + 60 * k, y + 250 * k, 6 * k, fill=(60, 60, 70))
    c.rrect(x - 32 * k, y - 70 * k, x + 32 * k, y + 60 * k, 32 * k, fill=(170, 170, 180), borde=(80, 80, 90),
            grosor=5 * k)
    for i in range(5):
        c.linea([(x - 26 * k, y + (-40 + 18 * i) * k), (x + 26 * k, y + (-40 + 18 * i) * k)], (110, 110, 120), 3 * k)


def escena_padrino(t):
    fr = FONDOS["despacho"].copy()
    t0 = ESC["padrino"]["escena_ini"]
    tr, tv = E["p_ronroneaba"], E["p_voz"]
    c = Capa(0, 560, W, 900)
    s = e_back(prog(t, t0 + 0.3, 0.5))
    sillon(c, 470, 1180)
    tapa = e_in_out(prog(t, tv - 0.2, 0.5))
    if t >= tr:
        for i in range(5):
            r = 90 + ((t - tr) * 260 + i * 70) % 360
            a = int(200 * (1 - r / 450))
            if a > 0:
                c.arco(380, 1080, r, r * 0.8, 290, 400, (255, 200, 120, a), 12 + 8 * tapa)
    sg = e_back(prog(t, E["p_gato"] - 0.1, 0.45))
    if sg > 0:
        respira = 1 + 0.03 * math.sin(t * (14 if t >= tr else 3))
        gato(c, 520, 1120, 0.95 * sg * respira, t, ojos_cerrados=t >= tr or t < E["p_gato"] + 0.6)
    microfono(c, 900, 860, 0.9 * s)
    # la voz (ondas finas del micrófono), tapada por el ronroneo (ondas gruesas, detrás del gato)
    for i in range(3):
        r = 40 + 30 * i + 12 * ((t * 3) % 1)
        c.arco(900, 800, r, r, 200, 340, (255, 255, 255, int(200 * (1 - tapa))), 5)
    c.pegar_en(fr)
    if t >= tr:
        temb = 5 * math.sin(t * 60)
        componer(fr, texto("RRRRR", "titulo", 76, color=(255, 214, 140), borde=7, color_borde=(90, 40, 10)),
                 300 + temb, 900, escala=pop(t, tr, 0.3), rot=-8)
    sc = pop(t, E["p_callejero"], 0.35)
    if sc > 0:
        componer(fr, cartel("GATO CALLEJERO", "ENCONTRADO EN EL ESTUDIO", (255, 214, 140), (70, 30, 14), 520, 76),
                 540, 690, escala=sc * (1 - pop(t, tr, 0.2)) if t < tr + 0.3 else 0.0, rot=-2)
    encabezado(fr, t, 1, E["padrino_badge"])
    titulo(fr, t, TITULOS["padrino"]["titulo"], t0 + 0.15, color=(255, 230, 190))
    pildora(fr, t, TITULOS["padrino"]["subtitulo"], (150, 40, 36), E["p_callejero"], hasta=tv)
    pildora(fr, t, "¡TAPABA LA VOZ!", (60, 60, 70), tv + 0.05)
    return fr


# ============================================================ 2 · los pelos
@lru_cache(None)
def pelos_base(n=760):
    rng = np.random.default_rng(15)
    r = 250 * np.sqrt(rng.uniform(0.05, 1, n))
    a = rng.uniform(0, 2 * math.pi, n)
    return np.stack([r * np.cos(a), r * np.sin(a), a, rng.uniform(0, 6.3, n), rng.uniform(34, 56, n),
                     rng.integers(0, 3, n)], axis=1)


def bola_de_pelo(c, x, y, k, t, resalta=-1):
    COLS = [(60, 150, 255), (40, 110, 220), (130, 195, 255)]
    c.circulo(x, y, 250 * k, fill=(40, 110, 220))
    for i, (px, py, a, fase, largo, col) in enumerate(pelos_base()):
        ang = a + 0.35 * math.sin(t * 3 + fase)
        x0, y0 = x + px * k, y + py * k
        x1, y1 = x0 + math.cos(ang) * largo * k, y0 + math.sin(ang) * largo * k
        color = (255, 230, 90) if resalta >= 0 and i % 97 == resalta % 97 else COLS[int(col)]
        c.linea([(x0, y0), (x1, y1)], color, 8 * k)
    for s in (-1, 1):   # ojos
        c.circulo(x + s * 70 * k, y - 40 * k, 44 * k, fill=(255, 255, 255), borde=(20, 30, 60), grosor=5 * k)
        c.circulo(x + s * 70 * k + 8 * k * math.sin(t), y - 34 * k, 18 * k, fill=(20, 30, 60))


def escena_monstruo(t):
    fr = FONDOS["fabrica"].copy()
    t0 = ESC["monstruo"]["escena_ini"]
    tm, tc, ts = E["m_millones"], E["m_computadora"], E["m_separado"]
    pantalla = e_in_out(prog(t, tc - 0.1, 0.4))
    k = lerp(1.1, 0.72, pantalla) * e_back(prog(t, E["m_azul"] - 0.2, 0.5))
    c = Capa(0, 520, W, 900)
    if pantalla > 0:   # la bola de pelo pasa a estar dentro de una computadora
        c.rrect(170, 700, 910, 1230, 30, fill=(40, 44, 56), borde=(20, 22, 30), grosor=8)
        c.rrect(200, 730, 880, 1200, 16, fill=(18, 22, 40))
        c.rrect(480, 1230, 600, 1300, 8, fill=(60, 64, 76))
        c.rrect(400, 1296, 680, 1320, 10, fill=(60, 64, 76))
    if k > 0:
        resalta = int((t - ts) * 12) if t >= ts else -1
        bola_de_pelo(c, 540, lerp(960, 965, pantalla), k, t, resalta)
    c.pegar_en(fr)
    if t >= ts:   # cada pelo por separado: algunos brillan
        for i in range(4):
            a = t * 2 + i * 1.6
            componer(fr, spr_brillo(26, (255, 240, 150)), 540 + 170 * math.cos(a), 965 + 150 * math.sin(a))
    sc = pop(t, tm, 0.35)
    if sc > 0:
        n = int(2320413 * clamp01((t - tm) / 0.9))
        componer(fr, cartel(f"{n:,}".replace(",", "."), "PELOS", (255, 255, 255), (30, 70, 160), 470, 90), 540, 650,
                 escala=sc, rot=-3)
    encabezado(fr, t, 2, E["monstruo_badge"])
    titulo(fr, t, TITULOS["monstruo"]["titulo"], t0 + 0.15, color=(200, 230, 255))
    pildora(fr, t, TITULOS["monstruo"]["subtitulo"], (40, 110, 220), tm, hasta=tc)
    pildora(fr, t, "¡CADA PELO POR SEPARADO!", (120, 60, 200), tc + 0.05)
    return fr


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


# ============================================================ 3 · Rocky
def maquina(c, x, y, k, t, escribe):
    c.rrect(x - 190 * k, y - 170 * k, x + 190 * k, y - 60 * k, 8 * k, fill=(250, 248, 240), borde=(180, 176, 160),
            grosor=3 * k)
    for i in range(int(6 * escribe)):
        c.linea([(x - 160 * k, y - (150 - 16 * i) * k), (x + (60 + 60 * ((i * 37) % 3)) * k, y - (150 - 16 * i) * k)],
                (60, 60, 70), 5 * k)
    c.rrect(x - 240 * k, y - 80 * k, x + 240 * k, y - 40 * k, 14 * k, fill=(60, 60, 70))
    c.rrect(x - 260 * k, y - 50 * k, x + 260 * k, y + 120 * k, 30 * k, fill=(40, 42, 50), borde=(20, 20, 26),
            grosor=6 * k)
    for fila in range(3):
        for col in range(9):
            kx = x + (-200 + col * 50 + fila * 12) * k
            ky = y + (-5 + fila * 40) * k
            baja = 5 * k if escribe < 1 and (int(t * 12) + col + fila) % 7 == 0 else 0
            c.circulo(kx, ky + baja, 16 * k, fill=(220, 220, 210), borde=(20, 20, 26), grosor=3 * k)


def guante(c, x, y, k, espejo=1):
    R, B = (220, 40, 40), (120, 10, 10)
    c.elipse(x, y, 90 * k, 110 * k, fill=R, borde=B, grosor=6 * k)
    c.elipse(x - espejo * 70 * k, y + 10 * k, 40 * k, 60 * k, fill=R, borde=B, grosor=5 * k)
    c.rrect(x - 70 * k, y + 80 * k, x + 70 * k, y + 160 * k, 20 * k, fill=(250, 250, 250), borde=(160, 160, 160),
            grosor=5 * k)
    c.arco(x + espejo * 20 * k, y - 40 * k, 40 * k, 40 * k, 200, 280, (255, 160, 160), 8 * k)


def bolsa_plata(c, x, y, k):
    c.elipse(x, y, 90 * k, 100 * k, fill=(200, 170, 90), borde=(120, 90, 40), grosor=6 * k)
    c.rrect(x - 36 * k, y - 118 * k, x + 36 * k, y - 90 * k, 10 * k, fill=(170, 140, 70))


def escena_rocky(t):
    fr = FONDOS["ring"].copy()
    t0 = ESC["rocky"]["escena_ini"]
    te, tv, tp = E["r_escribio"], E["r_vendio"], E["r_protagonista"]
    c = Capa(0, 520, W, 900)
    s = e_back(prog(t, t0 + 0.3, 0.5))
    escribe = clamp01((t - te) / 1.6)
    baja = e_in_out(prog(t, tp - 0.1, 0.4))
    maquina(c, 540, 1000 + 400 * baja, 1.0 * s, t, escribe)
    sb = e_back(prog(t, tv - 0.1, 0.4)) * (1 - e_in_out(prog(t, tp - 0.2, 0.3)))
    if sb > 0.01:
        bolsa_plata(c, 860, 780, 0.9 * sb)
    sgl = e_back(prog(t, tp, 0.45))
    if sgl > 0:
        guante(c, 330, 930, 1.3 * sgl, 1)
        guante(c, 750, 930, 1.3 * sgl, -1)
    c.pegar_en(fr)
    if 0.01 < sb:
        componer(fr, texto("$", "titulo", 90, color=(90, 60, 10)), 860, 800, escala=sb)
        componer(fr, sello("¡NO!", (200, 40, 40), 70), 860, 700, escala=pop(t, tv + 0.3, 0.3) * sb, rot=12)
    sd = pop(t, E["r_dias"], 0.35) * (1 - pop(t, tv, 0.2))
    if sd > 0.01:
        componer(fr, cartel("3 DÍAS Y MEDIO", None, (255, 240, 200), (140, 60, 20), 460, 76), 540, 690, escala=sd,
                 rot=-3)
    if t >= tp:
        componer(fr, sello("¡PROTAGONISTA!", (220, 160, 20), 76), 540, 700, escala=lerp(1.6, 1.0, pop(t, tp, 0.3)),
                 rot=-6)
        chispas(fr, t, tp + 0.05, 540, 900, n=26, seed=6, colores=((255, 214, 80), (255, 255, 255), (255, 90, 90)))
        componer(fr, spr_resplandor(300, (255, 230, 150)), 540, 900, alpha=0.3)
    encabezado(fr, t, 3, E["rocky_badge"])
    titulo(fr, t, TITULOS["rocky"]["titulo"], t0 + 0.15, color=(255, 230, 150))
    pildora(fr, t, TITULOS["rocky"]["subtitulo"], (200, 80, 30), E["r_dias"], hasta=tv)
    pildora(fr, t, "¡SOLO SI ÉL ERA ROCKY!", (200, 40, 40), tv + 0.05)
    return fr


# ======================================================= íconos del cierre
def _icono_gato(c, x, y, s, t):
    gato(c, x + 40 * s, y + 20 * s, 0.55 * s, t)


def _icono_pelo(c, x, y, s, t):
    bola_de_pelo(c, x, y, 0.36 * s, t)


def _icono_guante(c, x, y, s, t):
    guante(c, x, y - 20 * s, 0.7 * s)


ICONOS = [_icono_gato, _icono_pelo, _icono_guante]
ESCENAS = {"padrino": escena_padrino, "monstruo": escena_monstruo, "rocky": escena_rocky}
