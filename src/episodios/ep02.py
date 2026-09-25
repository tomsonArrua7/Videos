"""Episodio 2: el tiburón, el flamenco y la banana (voz de Elena, Argentina)."""
import math
from functools import lru_cache

import numpy as np
from PIL import ImageDraw

from dibujo import (TINTA, H, W, Capa, a_imagen, algas, bezier, burbujas, cartel, chispas, componer,
                    e_back, e_in_out, e_out, encabezado, gradiente, lerp, mezcla, parpadeo,
                    pildora, pop, prog, rayos_luz, resplandor, spr_resplandor, texto, titulo, viñeta)

SLUG = "tiburon_flamenco_banana"
DURACION = 30.0
VOZ = "es-AR-ElenaNeural"
VOZ_TONO = "+0Hz"
VOZ_VELOCIDAD_MIN = 4
GANCHO_ETIQUETA = "PARTE 2"
PALABRAS_CIERRE = ("abajo", "seguinos")

BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Otras tres curiosidades que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "PARTE 2",
    },
    {
        "id": "tiburon",
        "texto": "Uno: los tiburones son más antiguos que los árboles. Ya nadaban hace más de "
                 "cuatrocientos millones de años.",
        "titulo": "TIBURONES",
        "subtitulo": "MÁS ANTIGUOS QUE LOS ÁRBOLES",
    },
    {
        "id": "flamenco",
        "texto": "Dos: los flamencos nacen grises, ¡y se vuelven rosados por los camarones y "
                 "algas que comen!",
        "titulo": "FLAMENCOS",
        "subtitulo": "NACEN GRISES",
    },
    {
        "id": "banana",
        "texto": "Tres: las bananas son un poquito radiactivas por el potasio. Tranqui: tendrías "
                 "que comer millones para que te hagan mal.",
        "titulo": "BANANAS",
        "subtitulo": "UN POQUITO RADIACTIVAS",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"tiburon": (0, 150, 199), "flamenco": (255, 92, 160),
          "banana": (255, 214, 10), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS, EXTRA = {}, {}, {}, {}
HORIZONTE = 1000        # línea del mar en la escena del tiburón
LAGUNA = 1150           # horizonte de la laguna de los flamencos


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "t_antiguos": L.palabra("tiburon", "antiguos"),
        "t_arboles": L.palabra("tiburon", "árboles"),
        "t_contador": L.palabra("tiburon", "cuatrocientos"),
        "t_contador_fin": L.fin_palabra("tiburon", "años"),
        "f_nacen": L.palabra("flamenco", "nacen"),
        "f_grises": L.palabra("flamenco", "grises"),
        "f_vuelven": L.palabra("flamenco", "vuelven"),
        "f_rosados": L.palabra("flamenco", "rosados"),
        "f_camarones": L.palabra("flamenco", "camarones"),
        "b_radiactivas": L.palabra("banana", "radiactivas"),
        "b_potasio": L.palabra("banana", "potasio"),
        "b_tranqui": L.palabra("banana", "tranqui"),
        "b_millones": L.palabra("banana", "millones"),
    }


# Bocados que vuela hacia el pico del flamenco: (tipo, x de salida)
BOCADOS = [("camaron", 330), ("camaron", 820), ("alga", 260), ("camaron", 900), ("alga", 380)]


def _llegada(E, i):
    return E["f_camarones"] - 0.1 + 0.22 * i + 0.55


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    fx = [(E["t_antiguos"], S.pop(700, 300), 0.30),
          (E["t_arboles"], S.bloop(), 0.30),
          (E["t_arboles"] + 0.35, S.error_(), 0.30),
          (E["t_contador"] - 0.1, S.pop(1000, 400), 0.30)]
    t = E["t_contador"]
    while t < E["t_contador_fin"]:
        fx.append((t, S.tic(), 0.16))
        t += 0.06
    fx += [(E["f_nacen"] - 0.45, S.clic(), 0.30), (E["f_nacen"] - 0.25, S.clic(), 0.30),
           (E["f_nacen"], S.pop(900, 250), 0.40), (E["f_nacen"], S.clic(), 0.45),
           (E["f_grises"], S.pop(600, 250), 0.25),
           (E["f_vuelven"], S.poof(), 0.55),
           (E["f_rosados"], S.pop(600, 250), 0.25)]
    fx += [(_llegada(E, i), S.nam(), 0.45) for i in range(len(BOCADOS))]
    fx += [(_llegada(E, len(BOCADOS) - 1) + 0.15, S.brillo_sfx(), 0.30),
           (E["b_radiactivas"], S.geiger(E["b_tranqui"] - E["b_radiactivas"]), 0.35),
           (E["b_radiactivas"], S.pop(600, 250), 0.25),
           (E["b_potasio"], S.pop(800, 300), 0.35),
           (E["b_tranqui"], S.whoosh(0.35, 3000, 400), 0.25),
           (E["b_tranqui"] + 0.3, S.clic(), 0.40),
           (E["b_millones"], S.golpe(), 0.50),
           (E["b_millones"] + 0.05, S.ding(), 0.25)]
    return fx


def sacudidas(E):
    return [(E["t_arboles"] + 0.35, 8, 0.2), (E["b_millones"], 12, 0.3)]


# ==================================================================== fondos
def fondo_tiburon():
    corte = HORIZONTE / H
    a = gradiente([(0, (96, 186, 248)), (corte - 0.001, (205, 238, 255)), (corte, (70, 182, 222)),
                   (0.72, (22, 104, 172)), (1, (6, 28, 86))])
    resplandor(a, 880, 560, 260, (255, 252, 225), 0.5)
    img = a_imagen(a, 6)
    c = Capa(0, 380, W, HORIZONTE - 380 + 70)
    # nubes
    for nx, ny, e in [(150, 560, 1.0), (560, 780, 0.7)]:
        for dx, dy, r in [(-60, 10, 40), (0, -8, 55), (60, 8, 42), (25, 18, 40), (-25, 20, 38)]:
            c.circulo(nx + dx * e, ny + dy * e + 6, r * e, fill=(215, 232, 245))
        for dx, dy, r in [(-60, 10, 40), (0, -8, 55), (60, 8, 42)]:
            c.circulo(nx + dx * e, ny + dy * e, r * e, fill=(255, 255, 255))
    # volcano a lo lejos
    c.poligono([(700, HORIZONTE + 2), (882, 848), (982, 848), (1130, HORIZONTE + 2)], fill=(116, 92, 118))
    c.poligono([(932, 848), (982, 848), (1130, HORIZONTE + 2), (1000, HORIZONTE + 2)], fill=(96, 74, 100))
    c.elipse(932, 850, 52, 10, fill=(255, 120, 60))
    # isla pelada, sin un solo árbol
    pts = [(230 + 210 * math.cos(a), HORIZONTE + 4 - 58 * math.sin(a)) for a in np.linspace(0, math.pi, 30)]
    c.poligono(pts, fill=(242, 212, 150), borde=(170, 130, 80), grosor=4)
    for rx, ry, rr in [(150, 975, 18), (300, 982, 14), (330, 986, 10)]:
        c.elipse(rx, ry, rr * 1.4, rr, fill=(150, 140, 140))
    c.pegar_en(img)
    return img


def fondo_flamenco():
    corte = LAGUNA / H
    a = gradiente([(0, (70, 190, 222)), (corte - 0.001, (205, 242, 232)), (corte, (96, 196, 206)),
                   (1, (20, 108, 140))])
    resplandor(a, 180, 700, 300, (255, 250, 210), 0.55)
    img = a_imagen(a, 7)
    c = Capa(0, 900, W, 300)
    for base, amp, fase, col in [(LAGUNA - 40, 45, 0.5, (110, 186, 164)), (LAGUNA - 10, 30, 2.0, (78, 156, 140))]:
        pts = [(x, base - amp * (0.6 + 0.4 * math.sin(x / 140 + fase))) for x in range(-20, W + 40, 20)]
        c.poligono(pts + [(W + 40, LAGUNA + 2), (-20, LAGUNA + 2)], fill=col)
    c.pegar_en(img)
    return img


def fondo_banana():
    a = gradiente([(0, (14, 34, 26)), (0.5, (16, 62, 40)), (1, (8, 24, 20))])
    viñeta(a, 0.5)
    img = a_imagen(a, 8)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 90):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 14), width=2)
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 14), width=2)
    return img


def preparar():
    FONDOS.update(tiburon=fondo_tiburon(), flamenco=fondo_flamenco(), banana=fondo_banana())
    EXTRA["rayos"] = rayos_luz()


# ================================================================ personajes
def tiburon(c, x, y, t, k=1.0, dir_=1):
    AZUL, OSC, PANZA, BORDE = (98, 132, 172), (74, 104, 146), (238, 243, 250), (28, 38, 62)
    largo = 390 * k
    wag = math.sin(t * 7)

    def px(s):
        return x + dir_ * (largo * 0.5 - s * largo)

    def alto(s):
        return 92 * k * math.sqrt(s + 0.05) * (1.05 - s) / 0.444

    def cy(s):
        return y + (s ** 2.2) * 24 * k * wag

    S = np.linspace(0, 1, 40)
    arriba = [(px(s), cy(s) - alto(s)) for s in S]
    abajo = [(px(s), cy(s) + alto(s) * 0.78) for s in S]
    # cola en media luna, que se mueve con el nado
    xb, yb = px(1.0), cy(1.0)
    ang = wag * 0.3

    def cola(dx, dy):
        dx, dy = dx * k, dy * k
        return (xb - dir_ * (dx * math.cos(ang) - dy * math.sin(ang)), yb + dx * math.sin(ang) + dy * math.cos(ang))

    c.poligono([cola(-6, -14), cola(115, -128), cola(58, -4), cola(96, 82), cola(-6, 14)],
               fill=OSC, borde=BORDE, grosor=5 * k)
    # aleta dorsal (detrás del cuerpo)
    c.poligono([arriba[11], (px(0.56), cy(0.4) - alto(0.4) - 108 * k), arriba[21]],
               fill=OSC, borde=BORDE, grosor=5 * k)
    c.poligono([arriba[32], (px(0.9), cy(0.84) - alto(0.84) - 34 * k), arriba[36]], fill=OSC, borde=BORDE,
               grosor=4 * k)
    # cuerpo
    c.poligono(arriba + abajo[::-1], fill=AZUL, borde=BORDE, grosor=6 * k)
    panza = [(px(s), cy(s) + alto(s) * 0.78 - 5 * k) for s in S[2:33]]
    panza += [(px(s), cy(s) + alto(s) * 0.22) for s in S[2:33][::-1]]
    c.poligono(panza, fill=PANZA)
    c.elipse(px(0.1), cy(0.1) - alto(0.1) * 0.55, 22 * k, 7 * k, fill=(140, 170, 205))
    # branquias
    for s in (0.24, 0.275, 0.31):
        c.arco(px(s) + dir_ * 18 * k, cy(s), 16 * k, alto(s) * 0.34, 150 if dir_ > 0 else -30,
               210 if dir_ > 0 else 30, OSC, 4 * k)
    # aleta pectoral (adelante)
    c.poligono([abajo[10], (px(0.44), cy(0.3) + alto(0.3) * 0.78 + 78 * k), abajo[15]],
               fill=OSC, borde=BORDE, grosor=5 * k)
    # ojo
    ex, ey = px(0.13), cy(0.13) - alto(0.13) * 0.22
    c.circulo(ex, ey, 17 * k, fill=(255, 255, 255), borde=BORDE, grosor=3.5 * k)
    abre = parpadeo(t, 3.1, 0.4)
    c.elipse(ex + dir_ * 5 * k, ey + 1 * k, 9.5 * k, 9.5 * k * abre, fill=(20, 20, 30))
    c.circulo(ex + dir_ * 8 * k, ey - 3 * k, 3.5 * k, fill=(255, 255, 255))
    # sonrisa abierta con dientitos
    SB = np.linspace(0.035, 0.2, 12)

    def labio(s):
        return cy(s) + alto(s) * (0.26 + 0.6 * (s - 0.035))

    arriba_b = [(px(s), labio(s)) for s in SB]
    abajo_b = [(px(s), labio(s) + 24 * k * math.sin(math.pi * (s - 0.035) / 0.165)) for s in SB]
    c.poligono(arriba_b + abajo_b[::-1], fill=(96, 28, 52), borde=BORDE, grosor=3.5 * k)
    c.elipse(px(0.12), labio(0.12) + 15 * k, 16 * k, 6 * k, fill=(236, 110, 130))
    for j in range(1, 11, 2):
        x_, y_ = arriba_b[j]
        c.poligono([(x_ - 6 * k, y_), (x_ + 6 * k, y_), (x_, y_ + 11 * k)], fill=(255, 255, 255))


def pez(c, x, y, k, dir_, color):
    c.elipse(x, y, 26 * k, 13 * k, fill=color)
    c.poligono([(x - dir_ * 20 * k, y), (x - dir_ * 42 * k, y - 13 * k), (x - dir_ * 42 * k, y + 13 * k)], fill=color)


def arbol_fantasma(c, x, base, s):
    blanco, relleno = (255, 255, 255, 235), (255, 255, 255, 80)
    copa = [(0, -150, 62), (-50, -118, 46), (50, -118, 46), (-28, -176, 42), (30, -178, 40)]
    c.rrect(x - 16 * s, base - 110 * s, x + 16 * s, base, 6 * s, fill=relleno, borde=blanco, grosor=5)
    for dx, dy, r in copa:
        c.circulo(x + dx * s, base + dy * s, r * s + 5, fill=blanco)
    for dx, dy, r in copa:
        c.circulo(x + dx * s, base + dy * s, r * s, fill=relleno)


def pichon(c, x, y, t, k=1.0):
    GRIS, OSC, BORDE = (178, 178, 188), (142, 142, 154), (70, 62, 74)
    for dx in (-18, 18):
        c.linea([(x + dx * k, y + 50 * k), (x + dx * k, y + 92 * k)], (150, 140, 150), 7 * k)
    pelusa = [(62 * math.cos(a), 58 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
    for col, extra in ((BORDE, 5), (GRIS, 0)):
        c.circulo(x, y, 60 * k + extra * k, fill=col)
        for dx, dy in pelusa:
            c.circulo(x + dx * k, y + dy * k, 16 * k + extra * k, fill=col)
        c.circulo(x + 30 * k, y - 72 * k, 40 * k + extra * k, fill=col)
        for dx in (-10, 4, 18):
            c.circulo(x + (30 + dx) * k, y - 112 * k, 10 * k + extra * k, fill=col)
    c.elipse(x - 18 * k, y + 8 * k, 34 * k, 24 * k, fill=OSC)
    abre = parpadeo(t, 2.2)
    c.circulo(x + 42 * k, y - 78 * k, 12 * k, fill=(255, 255, 255), borde=BORDE, grosor=3 * k)
    c.elipse(x + 45 * k, y - 77 * k, 7 * k, 7 * k * abre, fill=(20, 20, 30))
    c.poligono([(x + 64 * k, y - 76 * k), (x + 92 * k, y - 66 * k), (x + 64 * k, y - 58 * k)],
               fill=(90, 84, 92), borde=BORDE, grosor=3 * k)


def flamenco(c, x, y, t, k=1.0, rosa=1.0):
    base = mezcla((186, 186, 196), (255, 122, 172), rosa)
    osc = mezcla((146, 146, 156), (232, 72, 134), rosa)
    patas = mezcla((160, 160, 166), (255, 142, 172), rosa)
    BORDE = (72, 30, 52)
    # patas: una parada y otra doblada (el clásico "4")
    for pts in ([(x + 5 * k, y + 50 * k), (x + 14 * k, y + 190 * k), (x + 6 * k, y + 332 * k)],
                [(x - 12 * k, y + 50 * k), (x + 48 * k, y + 148 * k), (x - 6 * k, y + 176 * k)]):
        c.linea(pts, BORDE, 13 * k)
        c.linea(pts, patas, 8 * k)
        c.circulo(*pts[1], 8 * k, fill=patas)
    # cola
    c.poligono([(x - 92 * k, y - 22 * k), (x - 152 * k, y - 4 * k), (x - 98 * k, y + 22 * k)],
               fill=osc, borde=BORDE, grosor=4 * k)

    def elipse_rotada(cx, cy, rx, ry, grados):
        a = math.radians(grados)
        return [(cx + rx * math.cos(u) * math.cos(a) - ry * math.sin(u) * math.sin(a),
                 cy + rx * math.cos(u) * math.sin(a) + ry * math.sin(u) * math.cos(a))
                for u in np.linspace(0, 2 * math.pi, 48, endpoint=False)]

    c.poligono(elipse_rotada(x, y, 112 * k, 68 * k, -12), fill=base, borde=BORDE, grosor=6 * k)
    c.poligono(elipse_rotada(x - 18 * k, y - 4 * k, 80 * k, 42 * k, -18), fill=osc)
    for i in range(3):
        c.arco(x - 30 * k + i * 22 * k, y - 4 * k, 26 * k, 30 * k, 60, 130, BORDE, 3 * k)
    # cuello en S
    vaiven = 8 * k * math.sin(t * 2)
    cuello = bezier((x + 88 * k, y - 36 * k), (x + 165 * k + vaiven, y - 130 * k),
                    (x - 30 * k + vaiven, y - 170 * k), (x + 46 * k + vaiven, y - 276 * k))
    rad = [17 * k - 5 * k * i / len(cuello) for i in range(len(cuello))]
    c.tubo(cuello, [r + 5 * k for r in rad], BORDE)
    c.tubo(cuello, rad, base)
    hx, hy = cuello[-1]
    c.circulo(hx, hy, 36 * k, fill=BORDE)
    c.circulo(hx, hy, 31 * k, fill=base)
    # pico curvo con punta negra
    pico = [(hx + 20 * k, hy - 17 * k), (hx + 62 * k, hy - 7 * k), (hx + 81 * k, hy + 17 * k),
            (hx + 71 * k, hy + 52 * k), (hx + 58 * k, hy + 30 * k), (hx + 24 * k, hy + 14 * k)]
    c.poligono(pico, fill=(248, 242, 228), borde=BORDE, grosor=4 * k)
    c.poligono([(hx + 64 * k, hy + 3 * k), (hx + 81 * k, hy + 17 * k), (hx + 71 * k, hy + 52 * k),
                (hx + 56 * k, hy + 24 * k)], fill=(30, 24, 30))
    abre = parpadeo(t, 2.9, 1.1)
    c.circulo(hx + 6 * k, hy - 8 * k, 10 * k, fill=(255, 255, 255), borde=BORDE, grosor=2.5 * k)
    c.elipse(hx + 9 * k, hy - 7 * k, 6 * k, 6 * k * abre, fill=(20, 20, 30))
    c.elipse(hx - 12 * k, hy + 12 * k, 11 * k, 6 * k, fill=mezcla((200, 200, 205), (255, 90, 140), rosa))
    return hx + 60 * k, hy + 22 * k  # dónde está la boca


def camaron(c, x, y, ang, k=1.0):
    CUERPO, BORDE = (255, 124, 92), (150, 50, 30)
    pts, rad = [], []
    for i in range(14):
        u = i / 13
        a = ang + math.radians(-100 + 210 * u)
        pts.append((x + 22 * k * math.cos(a), y + 22 * k * math.sin(a)))
        rad.append((12 - 8 * u) * k)
    c.tubo(pts, [r + 3 * k for r in rad], BORDE)
    c.tubo(pts, rad, CUERPO)
    ex, ey = pts[0]
    c.circulo(ex, ey, 3.5 * k, fill=(20, 20, 30))
    tx, ty = pts[-1]
    c.poligono([(tx, ty), (tx + 12 * k * math.cos(ang + 1.2), ty + 12 * k * math.sin(ang + 1.2)),
                (tx + 12 * k * math.cos(ang + 2.2), ty + 12 * k * math.sin(ang + 2.2))], fill=CUERPO, borde=BORDE,
               grosor=2 * k)


def alga_bocado(c, x, y, ang, k=1.0):
    pts = []
    for u in np.linspace(0, 2 * math.pi, 20, endpoint=False):
        lx, ly = 26 * k * math.cos(u), 10 * k * math.sin(u)
        pts.append((x + lx * math.cos(ang) - ly * math.sin(ang), y + lx * math.sin(ang) + ly * math.cos(ang)))
    c.poligono(pts, fill=(84, 192, 92), borde=(30, 100, 40), grosor=3 * k)


def banana(c, cx, cy, t, k=1.0, lentes=0.0, brillo=0.0, cara=True):
    R = 320 * k
    ox, oy = cx, cy - 300 * k

    def punto(s, dr=0.0):
        a = math.radians(130 - 80 * s)
        return (ox + (R + dr) * math.cos(a), oy + (R + dr) * math.sin(a))

    S = np.linspace(0, 1, 44)
    grosor = [8 * k + 62 * k * math.sin(math.pi * s) ** 0.55 for s in S]
    eje = [punto(s) for s in S]
    if brillo > 0:
        c.tubo(eje, [g + 24 * k * brillo for g in grosor], (110, 255, 140, 150))
    c.tubo(eje, [g + 6 * k for g in grosor], (110, 70, 10))
    c.tubo(eje, grosor, (255, 222, 60))
    medio = [s for s in S if 0.12 < s < 0.88]
    c.tubo([punto(s, 0.45 * (8 * k + 62 * k * math.sin(math.pi * s) ** 0.55)) for s in medio],
           [0.3 * (8 * k + 62 * k * math.sin(math.pi * s) ** 0.55) for s in medio], (238, 186, 32))
    c.tubo([punto(s, -0.5 * (8 * k + 62 * k * math.sin(math.pi * s) ** 0.55)) for s in medio],
           [0.18 * (8 * k + 62 * k * math.sin(math.pi * s) ** 0.55) for s in medio], (255, 244, 160))
    # cabito y puntita
    x1, y1 = punto(1.0)
    c.linea([(x1, y1), (x1 + 20 * k, y1 - 22 * k)], (110, 76, 30), 16 * k)
    c.circulo(*punto(0.0), 9 * k, fill=(84, 54, 20))
    if not cara:
        return
    fx, fy = punto(0.5)
    fy -= 22 * k
    BORDE = (80, 50, 10)
    abre = parpadeo(t, 2.6, 0.3)
    for s in (-1, 1):
        ex = fx + s * 40 * k
        c.circulo(ex, fy, 17 * k, fill=(255, 255, 255), borde=BORDE, grosor=3.5 * k)
        c.elipse(ex + 2 * k, fy + 2 * k, 9 * k, 9 * k * abre, fill=(20, 20, 30))
        c.circulo(ex + 5 * k, fy - 3 * k, 3.5 * k, fill=(255, 255, 255))
        c.elipse(fx + s * 70 * k, fy + 26 * k, 13 * k, 7 * k, fill=(255, 150, 90))
    if brillo > 0.05 and lentes < 1:   # asustada mientras brilla
        c.elipse(fx, fy + 30 * k, 11 * k, 13 * k, fill=BORDE)
    else:
        c.arco(fx, fy + 20 * k, 30 * k, 22 * k, 15, 165, BORDE, 6 * k)
    if lentes > 0:
        ly = fy - (1 - e_out(lentes)) * 260 * k
        for s in (-1, 1):
            c.rrect(fx + s * 40 * k - 30 * k, ly - 18 * k, fx + s * 40 * k + 30 * k, ly + 18 * k, 12 * k,
                    fill=(18, 18, 24))
            c.linea([(fx + s * 40 * k - 14 * k, ly - 8 * k), (fx + s * 40 * k - 2 * k, ly - 14 * k)],
                    (255, 255, 255, 200), 4 * k)
        c.linea([(fx - 12 * k, ly - 6 * k), (fx + 12 * k, ly - 6 * k)], (18, 18, 24), 6 * k)


def trebol(c, cx, cy, r, ang):
    """Símbolo de radiación."""
    c.circulo(cx, cy, r, fill=(255, 214, 10), borde=(20, 20, 20), grosor=10)
    for i in range(3):
        a0 = ang + math.radians(i * 120 - 30)
        a1 = a0 + math.radians(60)
        arcos = np.linspace(a0, a1, 16)
        pts = [(cx + r * 0.84 * math.cos(a), cy + r * 0.84 * math.sin(a)) for a in arcos]
        pts += [(cx + r * 0.24 * math.cos(a), cy + r * 0.24 * math.sin(a)) for a in arcos[::-1]]
        c.poligono(pts, fill=(20, 20, 20))
    c.circulo(cx, cy, r * 0.16, fill=(20, 20, 20))


def contador_geiger(c, x, y, t, calma):
    c.rrect(x - 96, y - 72, x + 96, y + 72, 20, fill=(255, 196, 30), borde=(60, 40, 10), grosor=5)
    dial = [(x + 64 * math.cos(a), y + 18 + 64 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 24)]
    c.poligono(dial, fill=(255, 255, 255), borde=(60, 40, 10), grosor=4)
    for a in np.linspace(math.pi * 1.1, math.pi * 1.9, 7):
        c.linea([(x + 52 * math.cos(a), y + 18 + 52 * math.sin(a)), (x + 62 * math.cos(a), y + 18 + 62 * math.sin(a))],
                (60, 40, 10), 3, puntas=False)
    loco = -90 + 40 * (0.6 * math.sin(t * 17) + 0.4 * math.sin(t * 43))
    tranqui = -150 + 4 * math.sin(t * 3)
    a = math.radians(lerp(loco, tranqui, calma))
    c.linea([(x, y + 18), (x + 56 * math.cos(a), y + 18 + 56 * math.sin(a))], (220, 30, 40), 6)
    c.circulo(x, y + 18, 8, fill=(60, 40, 10))


@lru_cache(None)
def _elemento_potasio():
    w, h = 200, 222
    c = Capa(0, 0, w + 16, h + 22, ss=3)
    c.rrect(8, 16, w + 8, h + 16, 22, fill=(10, 0, 30, 110))
    c.rrect(8, 8, w + 8, h + 8, 22, fill=(248, 246, 255), borde=(124, 62, 210), grosor=8)
    im = c.imagen()
    for txt, fuente, tam, color, pos in [("19", "negra", 34, TINTA, (28, 20)),
                                         ("POTASIO", "negra", 30, TINTA, None)]:
        tx = texto(txt, fuente, tam, color=color)
        if pos is None:
            pos = (int(8 + w / 2 - tx.width / 2), h - 38)
        im.alpha_composite(tx, pos)
    k_ = texto("K", "titulo", 128, color=(124, 62, 210))
    im.alpha_composite(k_, (int(8 + w / 2 - k_.width / 2), int(8 + h / 2 - k_.height / 2 - 4)))
    return im


@lru_cache(None)
def spr_banana(tam):
    c = Capa(0, 0, tam, tam, ss=3)
    banana(c, tam / 2, tam * 0.62, 0, tam / 520, cara=False)
    return c.imagen()


# =================================================================== escenas
def escena_tiburon(t):
    fr = FONDOS["tiburon"].copy()
    t0 = ESC["tiburon"]["escena_ini"]
    # humo del volcán
    c = Capa(820, 520, 260, 360)
    for i in range(6):
        ph = ((t * 0.35) + i / 6) % 1
        c.circulo(932 + 70 * ph + 12 * math.sin(t * 2 + i), 846 - 300 * ph, 16 + 42 * ph,
                  fill=(222, 222, 232, int(210 * (1 - ph))))
    c.pegar_en(fr)
    # bajo el agua: rayos de luz, burbujas, peces, algas y el tiburón
    ray = EXTRA["rayos"]
    ox = int(150 + 60 * math.sin(t * 0.7))
    fr.alpha_composite(ray, (0, HORIZONTE), (ox, 0, ox + W, H - HORIZONTE))
    burbujas(fr, t, n=18, seed=8, y_min=HORIZONTE + 30)
    c = Capa(0, HORIZONTE - 20, W, H - HORIZONTE + 20)
    for i, (y0, v, k, col) in enumerate([(1480, 90, 0.9, (40, 110, 170)), (1640, -70, 1.1, (30, 90, 150)),
                                        (1760, 110, 0.8, (40, 120, 180))]):
        x = (200 + i * 330 + v * t) % (W + 200) - 100
        pez(c, x, y0 + 10 * math.sin(t * 2 + i), k, 1 if v > 0 else -1, col)
    algas(c, t, [(60, 420, 0, (24, 150, 96)), (1020, 380, 2.1, (40, 180, 110)),
                 (140, 260, 1.3, (40, 180, 110))])
    if t < t0 + 1.1:
        tx, dir_ = lerp(-420, 540, e_out(prog(t, t0 - 0.1, 1.2))), 1
    else:
        fase = 0.9 * (t - t0 - 1.1)
        tx, dir_ = 540 + 230 * math.sin(fase), 1 if math.cos(fase) >= 0 else -1
    tiburon(c, tx, 1255 + 18 * math.sin(t * 1.8), t, 1.1, dir_)
    # olitas en la superficie
    ola = [(x, HORIZONTE + 5 * math.sin(x / 55 + t * 3)) for x in range(-10, W + 20, 12)]
    c.linea(ola, (235, 250, 255, 200), 6)
    c.pegar_en(fr)
    # árbol fantasma tachado: todavía no existían
    s = pop(t, E["t_arboles"], 0.4)
    if s > 0:
        c = Capa(60, 700, 340, 300)
        arbol_fantasma(c, 230, HORIZONTE - 50, s)
        x_ = e_back(prog(t, E["t_arboles"] + 0.35, 0.3))
        if x_ > 0:
            for (a, b) in (((150, 760), (310, 930)), ((310, 760), (150, 930))):
                p1 = (230 + (a[0] - 230) * x_, 845 + (a[1] - 845) * x_)
                p2 = (230 + (b[0] - 230) * x_, 845 + (b[1] - 845) * x_)
                c.linea([p1, p2], (255, 255, 255), 34)
            for (a, b) in (((150, 760), (310, 930)), ((310, 760), (150, 930))):
                p1 = (230 + (a[0] - 230) * x_, 845 + (a[1] - 845) * x_)
                p2 = (230 + (b[0] - 230) * x_, 845 + (b[1] - 845) * x_)
                c.linea([p1, p2], (235, 40, 60), 22)
        c.pegar_en(fr)
    # contador de millones de años
    s = pop(t, E["t_contador"] - 0.1, 0.35)
    if s > 0:
        n = int(round(400 * e_out(prog(t, E["t_contador"], E["t_contador_fin"] - E["t_contador"] + 0.25))))
        componer(fr, cartel(f"+{n}", "MILLONES DE AÑOS", (120, 228, 255), (8, 42, 84), 560, 100),
                 540, 628, escala=s)
    encabezado(fr, t, 1, E["tiburon_badge"])
    titulo(fr, t, TITULOS["tiburon"]["titulo"], t0 + 0.15)
    pildora(fr, t, TITULOS["tiburon"]["subtitulo"], (0, 118, 178), E["t_antiguos"])
    return fr


def escena_flamenco(t):
    fr = FONDOS["flamenco"].copy()
    t0 = ESC["flamenco"]["escena_ini"]
    c = Capa(0, 560, W, H - 560)
    # brillos del agua
    for i in range(9):
        x = (i * 137 + 40 * t) % (W + 100) - 50
        y = LAGUNA + 40 + i * 42
        c.elipse(x, y, 40 + 14 * math.sin(t * 2 + i), 4, fill=(230, 250, 250, 120))
    # juncos que se mecen
    for bx, alto, fase in [(40, 520, 0.0), (95, 420, 1.1), (990, 480, 0.6), (1045, 380, 1.8)]:
        pts = [(bx + math.sin(t * 1.4 + fase) * 22 * (j / 20) ** 1.5, H + 10 - alto * j / 20) for j in range(21)]
        c.linea(pts, (46, 120, 70), 10)
        c.elipse(pts[-3][0], pts[-3][1] + 10, 11, 34, fill=(120, 76, 40))
    tv = E["f_vuelven"]
    # nido, huevo y pichón gris
    nido = 1 - prog(t, tv, 0.3)
    if nido > 0:
        c.elipse(560, 1305, 190 * nido, 56 * nido, fill=(128, 92, 62))
        c.elipse(560, 1294, 150 * nido, 32 * nido, fill=(98, 68, 44))
    tn = E["f_nacen"]
    if t < tn:
        tiembla = 9 * math.sin(t * 38) * prog(t, tn - 0.5, 0.3)
        componer_huevo(c, 560, 1196, tiembla, 1.0)
    elif t < tv + 0.1:
        p = prog(t, tn, 0.5)
        if p < 1:  # cáscaras que salen volando
            componer_huevo(c, 560 - 150 * p, 1196 - 260 * p + 380 * p * p, -200 * p, 1 - p, mitad="arriba")
        pichon(c, 560, 1180 + 6 * math.sin(t * 6), t, 1.3 * e_back(prog(t, tn, 0.4)))
    # flamenco adulto que se va poniendo rosado
    llegadas = [_llegada(E, i) for i in range(len(BOCADOS))]
    rosa = sum(e_out(prog(t, ti, 0.35)) for ti in llegadas) / len(llegadas)
    boca = (0, 0)
    if t >= tv:
        s = e_back(prog(t, tv, 0.45))
        boca = flamenco(c, 560, 1010 + 5 * math.sin(t * 2.2), t, s, rosa)
        c.elipse(566, 1342, 60 * s, 10 * s, borde=(240, 255, 255, 200), grosor=4)
    # camarones y algas volando al pico
    for i, (tipo, x0) in enumerate(BOCADOS):
        u = prog(t, llegadas[i] - 0.55, 0.55)
        if 0 < u < 1 and t >= tv:
            x = lerp(x0, boca[0], u)
            y = lerp(LAGUNA + 60, boca[1], u) - 260 * 4 * u * (1 - u)
            (camaron if tipo == "camaron" else alga_bocado)(c, x, y, u * 9, 1.3)
    c.pegar_en(fr)
    # poof de la transformación
    p = prog(t, tv - 0.05, 0.55)
    if 0 < p < 1:
        c = Capa(260, 820, 600, 520)
        for i in range(9):
            a = i * 2 * math.pi / 9
            r = 70 + 90 * e_out(p)
            c.circulo(560 + r * math.cos(a), 1090 + r * 0.8 * math.sin(a), (90 - 30 * p),
                      fill=(255, 255, 255, int(235 * (1 - p))))
        c.circulo(560, 1090, 110 * (1 - p) + 20, fill=(255, 255, 255, int(235 * (1 - p))))
        c.pegar_en(fr)
    chispas(fr, t, llegadas[-1] + 0.1, 600, 900, n=22, seed=6,
            colores=((255, 120, 172), (255, 255, 255), (255, 200, 225)), vel=(300, 750), grav=500)
    encabezado(fr, t, 2, E["flamenco_badge"])
    titulo(fr, t, TITULOS["flamenco"]["titulo"], t0 + 0.15, color=(255, 190, 220))
    pildora(fr, t, "NACEN GRISES", (120, 120, 134), E["f_grises"], hasta=E["f_rosados"])
    pildora(fr, t, "¡ROSADOS POR LO QUE COMEN!", (236, 64, 132), E["f_rosados"] + 0.1)
    return fr


def componer_huevo(c, x, y, rot, alpha, mitad=None, k=1.3):
    """Huevo (o su cáscara de arriba) con manchitas."""
    a = math.radians(rot)
    col = (250, 245, 232, int(255 * alpha))
    borde = (130, 110, 90, int(255 * alpha))

    def r(px_, py_):
        px_, py_ = px_ * k, py_ * k
        return (x + px_ * math.cos(a) - py_ * math.sin(a), y + px_ * math.sin(a) + py_ * math.cos(a))

    if mitad == "arriba":
        pts = [r(58 * math.cos(u), 74 * math.sin(u)) for u in np.linspace(math.pi, 2 * math.pi, 20)]
        pts += [r(58 - 116 * i / 8, (10 if i % 2 else -6)) for i in range(9)]
    else:
        pts = [r(58 * math.cos(u), 74 * math.sin(u) * (1.0 if math.sin(u) > 0 else 1.08))
               for u in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    c.poligono(pts, fill=col, borde=borde, grosor=4)
    for px_, py_, rr in [(-18, -30, 7), (16, -8, 5), (-6, 22, 6), (24, 30, 4)]:
        if mitad != "arriba" or py_ < 0:
            c.circulo(*r(px_, py_), rr * k, fill=(200, 186, 160, int(255 * alpha)))


def escena_banana(t):
    fr = FONDOS["banana"].copy()
    t0 = ESC["banana"]["escena_ini"]
    tr, tq = E["b_radiactivas"], E["b_tranqui"]
    calma = e_in_out(prog(t, tq, 0.5))
    pulso = 0.5 + 0.5 * math.sin(t * 7)
    if calma < 1:
        componer(fr, spr_resplandor(430, (80, 255, 120)), 540, 980,
                 alpha=(0.35 + 0.35 * pulso * prog(t, tr - 0.2, 0.4)) * (1 - calma))
    if calma > 0:
        componer(fr, spr_resplandor(430, (255, 210, 90)), 540, 980, alpha=0.45 * calma)
    # símbolo de radiación girando detrás
    s = pop(t, tr, 0.45) * (1 - e_out(prog(t, tq, 0.4)))
    if s > 0.01:
        c = Capa(240, 660, 600, 600)
        trebol(c, 540, 960, 280 * s, t * 0.35)
        im = c.imagen()
        componer(fr, im, 540, 960, alpha=0.9)
    # banana
    c = Capa(120, 560, 840, 700)
    ent = e_back(prog(t, t0 + 0.1, 0.5))
    if ent > 0:
        brillo = (0.4 + 0.6 * pulso) * prog(t, tr, 0.3) * (1 - calma)
        banana(c, 540, 1010 + 10 * math.sin(t * 2.4), t, 1.4 * ent, lentes=prog(t, tq, 0.35), brillo=brillo)
    c.pegar_en(fr)
    # contador Geiger y el potasio (se van cuando dice "tranqui")
    fuera = 1 - e_out(prog(t, tq + 0.15, 0.3))
    s = pop(t, tr + 0.1, 0.4) * fuera
    if s > 0.01:
        c = Capa(120, 610, 220, 180)
        contador_geiger(c, 230, 700, t, calma)
        componer(fr, c.imagen(), 230, 700, escala=s, rot=6)
        componer(fr, texto("GEIGER", "negra", 30, borde=5), 230, 800, escala=s)
    s = pop(t, E["b_potasio"], 0.4) * fuera
    if s > 0.01:
        componer(fr, _elemento_potasio(), 850, 700, escala=s, rot=-6)
    # lluvia de bananas: millones
    tm = E["b_millones"]
    if t >= tm:
        rng = np.random.default_rng(10)
        for i in range(34):
            x = rng.uniform(40, W - 40)
            v = rng.uniform(650, 1100)
            y = -80 + v * (t - tm - rng.uniform(0, 0.8))
            if -80 < y < H + 80:
                componer(fr, spr_banana(int(rng.integers(70, 120))), x, y, rot=(t - tm) * rng.uniform(-200, 200))
        s = pop(t, tm, 0.3)
        componer(fr, cartel("¡MILLONES!", None, (255, 214, 10), (60, 40, 0), 560, 110), 540, 660, escala=s,
                 rot=-3)
    encabezado(fr, t, 3, E["banana_badge"])
    titulo(fr, t, TITULOS["banana"]["titulo"], t0 + 0.15, color=(255, 232, 90))
    pildora(fr, t, TITULOS["banana"]["subtitulo"], (36, 160, 78), tr, hasta=tq)
    pildora(fr, t, "TRANQUI: NO HACEN MAL", (230, 130, 0), tq + 0.1)
    return fr


# ======================================================= íconos del cierre
def _icono_tiburon(c, x, y, s, t):
    tiburon(c, x + 10 * s, y + 8 * s, t, 0.3 * s, 1)


def _icono_flamenco(c, x, y, s, t):
    flamenco(c, x - 14 * s, y + 4 * s, t, 0.27 * s, 1.0)


def _icono_banana(c, x, y, s, t):
    banana(c, x, y + 14 * s, t, 0.36 * s, lentes=1.0)


ICONOS = [_icono_tiburon, _icono_flamenco, _icono_banana]
ESCENAS = {"tiburon": escena_tiburon, "flamenco": escena_flamenco, "banana": escena_banana}
