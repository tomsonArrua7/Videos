"""Episodio 4: curiosidades de películas (voz de Tomás, Argentina).

Las imágenes usan objetos y guiños genéricos (un dinosaurio propio, una
heladera, un boceto), nunca personajes o logos con derechos de autor.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageOps

from dibujo import (H, W, Capa, a_imagen, cartel, chispas, componer, e_back, e_in_out, e_out, elipse_rotada,
                    encabezado, gradiente, lerp, onda, parpadeo, pildora, pop, prog, resplandor,
                    spr_estrella, tachar, texto, titulo, viñeta)

SLUG = "peliculas"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
VOZ_FINAL = 0.75        # un poco menos de cola musical para que Tomás no tenga que apurarse
VOZ_PAUSA = 0.2
GANCHO_ETIQUETA = "DE PELÍCULAS"
PALABRAS_CIERRE = ("abajo", "seguinos")

# Guion escrito para el oído: frases cortas, números en palabras y los nombres
# en inglés adaptados solo donde la voz los pronunciaba mal ({se ve|se dice}).
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades de películas que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE PELÍCULAS",
    },
    {
        "id": "rugido",
        "texto": "Uno: el rugido del tiranosaurio de Jurassic Park mezcla sonidos de un elefante bebé, "
                 "un tigre y un caimán.",
        "pausa_despues": 0.6,   # lugar para que ruja el dinosaurio
        "titulo": "JURASSIC PARK",
        "subtitulo": "UN RUGIDO DE TRES ANIMALES",
    },
    {
        "id": "heladera",
        "texto": "Dos: en Volver al futuro, la máquina del tiempo iba a ser una heladera. "
                 "¡La cambiaron para que ningún chico se encerrara!",
        "titulo": "VOLVER AL FUTURO",
        "subtitulo": "¡IBA A SER UNA HELADERA!",
    },
    {
        "id": "dibujo",
        "texto": "Tres: las manos que dibujan a {Rose|Róus} en {Titanic|Titánic} son del director. "
                 "¡Y como es zurdo, dieron vuelta la imagen!",
        "titulo": "TITANIC",
        "subtitulo": "LAS MANOS DEL DIRECTOR",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"rugido": (80, 170, 70), "heladera": (255, 90, 160),
          "dibujo": (60, 140, 230), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS, EXTRA = {}, {}, {}, {}
HORIZONTE_80S = 1120
HORIZONTE_MAR = 860
ANIMALES = [("elefante", 690, (215, 225, 235)), ("tigre", 930, (255, 226, 180)), ("caimán", 1170, (205, 236, 190))]


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "r_mezcla": L.palabra("rugido", "mezcla"),
        "r_elefante": L.palabra("rugido", "elefante"),
        "r_tigre": L.palabra("rugido", "tigre"),
        "r_caiman": L.palabra("rugido", "caimán"),
        "r_ruge": L.fin_palabra("rugido", "caimán") + 0.08,
        "h_heladera": L.palabra("heladera", "heladera"),
        "h_cambiaron": L.palabra("heladera", "cambiaron"),
        "h_chico": L.palabra("heladera", "chico"),
        "d_manos": L.palabra("dibujo", "manos"),
        "d_director": L.palabra("dibujo", "director"),
        "d_zurdo": L.palabra("dibujo", "zurdo"),
        "d_imagen": L.palabra("dibujo", "imagen"),
    }


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    fx = [(E["r_elefante"], S.pop(900, 400), 0.25), (E["r_tigre"], S.pop(700, 300), 0.25),
          (E["r_caiman"], S.pop(500, 220), 0.25), (E["r_ruge"], S.rugido_sfx(), 0.42),
          (E["h_heladera"], S.chisporroteo(0.7), 0.20), (E["h_cambiaron"], S.error_(), 0.25),
          (E["h_cambiaron"] + 0.35, S.whoosh(0.5, 300, 1500), 0.25),
          (E["h_cambiaron"] + 0.5, S.whoosh(0.7, 200, 4000), 0.35),
          (E["h_chico"], S.pop(600, 250), 0.25),
          (E["d_director"], S.pop(900, 400), 0.30),
          (E["d_zurdo"] + 0.2, S.whoosh(0.5, 400, 2500), 0.25),
          (E["d_imagen"], S.ding(), 0.20)]
    t = E["d_manos"] - 0.3
    while t < E["d_zurdo"]:
        fx.append((t, S.marcador(0.3), 0.10))
        t += 0.45
    return fx


def sacudidas(E):
    return [(E["r_ruge"], 18, 0.5)]


# ==================================================================== fondos
def fondo_rugido():
    a = gradiente([(0, (20, 70, 44)), (0.6, (12, 48, 30)), (1, (8, 30, 20))])
    resplandor(a, 620, 520, 520, (120, 200, 120), 0.25)
    viñeta(a, 0.5)
    img = a_imagen(a, 20)
    c = Capa(0, 0, W, H)
    for x, y, ang, e, col in [(-30, 560, 25, 1.2, (16, 60, 32)), (1110, 640, 155, 1.3, (18, 70, 36)),
                              (-40, 1560, -20, 1.4, (14, 54, 28)), (1110, 1500, 200, 1.3, (16, 62, 32)),
                              (120, 1880, -50, 1.1, (20, 76, 38)), (960, 1880, 230, 1.2, (20, 76, 38))]:
        c.poligono(elipse_rotada(x, y, 230 * e, 70 * e, ang), fill=col)
        a_ = math.radians(ang)
        c.linea([(x - 200 * e * math.cos(a_), y - 200 * e * math.sin(a_)),
                 (x + 200 * e * math.cos(a_), y + 200 * e * math.sin(a_))], (30, 96, 48), 5)
    c.elipse(700, 1395, 330, 40, fill=(12, 26, 14))
    c.pegar_en(img)
    return img


def fondo_heladera():
    corte = HORIZONTE_80S / H
    a = gradiente([(0, (22, 6, 52)), (0.4, (70, 20, 100)), (corte, (230, 70, 130)), (corte + 0.001, (22, 6, 42)),
                   (1, (10, 2, 26))])
    # sol retro con franjas
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy, r = 540, 1000, 250
    dentro = ((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r) & (yy < HORIZONTE_80S)
    u = np.clip((yy - (cy - r)) / (2 * r), 0, 1)
    sol = np.stack([255 + 0 * u, 225 - 160 * u, 80 + 60 * u], -1)
    franja = (yy > 940) & (((yy - 940) % 34) < (4 + (yy - 940) / 22))
    m = dentro & ~franja
    a[m] = sol[m]
    img = a_imagen(a, 21)
    rng = np.random.default_rng(22)
    for _ in range(70):
        componer(img, spr_estrella(int(rng.integers(2, 6))), rng.uniform(0, W), rng.uniform(0, 800),
                 alpha=rng.uniform(0.3, 0.9))
    return img


def fondo_dibujo():
    corte = HORIZONTE_MAR / H
    a = gradiente([(0, (56, 38, 104)), (0.25, (190, 96, 120)), (corte, (255, 186, 120)),
                   (corte + 0.001, (60, 70, 130)), (0.75, (30, 36, 84)), (1, (16, 18, 50))])
    resplandor(a, 800, HORIZONTE_MAR, 240, (255, 230, 170), 0.6)
    img = a_imagen(a, 23)
    c = Capa(560, HORIZONTE_MAR - 120, 480, 520)
    pts = [(800 + 95 * math.cos(u), HORIZONTE_MAR - 95 * math.sin(u)) for u in np.linspace(0, math.pi, 30)]
    c.poligono(pts, fill=(255, 230, 170))
    for i in range(9):
        y = HORIZONTE_MAR + 18 + i * 36
        c.elipse(800, y, 110 - i * 9, 5, fill=(255, 210, 150, 170))
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(rugido=fondo_rugido(), heladera=fondo_heladera(), dibujo=fondo_dibujo())


# ================================================================ personajes
VERDE, VERDE_OSC, PANZA_T, BORDE_T = (96, 172, 84), (68, 132, 60), (216, 228, 152), (26, 56, 26)


def trex(c, x, y, t, k=1.0, boca=0.15):
    """Tiranosaurio de caricatura mirando a la izquierda; `boca` en radianes."""
    def P(dx, dy):
        return (x + dx * k, y + dy * k)

    cola = [P(120 + 220 * u, -10 + 70 * u ** 1.3 + 12 * math.sin(t * 2 + u * 3)) for u in np.linspace(0, 1, 22)]
    radios = [(72 - 58 * u) * k for u in np.linspace(0, 1, 22)]
    c.tubo(cola, [r + 6 * k for r in radios], BORDE_T)
    c.tubo(cola, radios, VERDE)
    # pata de atrás
    c.elipse(*P(55, 85), 68 * k, 88 * k, fill=VERDE_OSC, borde=BORDE_T, grosor=5 * k)
    c.linea([P(55, 130), P(45, 250)], BORDE_T, 46 * k)
    c.linea([P(55, 130), P(45, 250)], VERDE_OSC, 36 * k)
    c.elipse(*P(25, 262), 56 * k, 18 * k, fill=VERDE_OSC, borde=BORDE_T, grosor=5 * k)
    # cuerpo
    c.poligono(elipse_rotada(*P(0, 0), 185 * k, 122 * k, -18), fill=VERDE, borde=BORDE_T, grosor=6 * k)
    c.poligono(elipse_rotada(*P(-45, 42), 118 * k, 64 * k, -22), fill=PANZA_T)
    for i in range(5):
        c.elipse(*P(-60 + 45 * i, -95 + 14 * i), 16 * k, 9 * k, fill=VERDE_OSC)
    # cuello y cabeza
    c.tubo([P(-100 - 20 * u, -60 - 110 * u) for u in np.linspace(0, 1, 8)], [76 * k] * 8, BORDE_T)
    c.tubo([P(-100 - 20 * u, -60 - 110 * u) for u in np.linspace(0, 1, 8)], [70 * k] * 8, VERDE)
    hx, hy = -200, -190
    bisagra = P(hx + 40, hy + 10)
    ang = -boca

    def rot(dx, dy):
        px_, py_ = x + (hx + dx) * k - bisagra[0], y + (hy + dy) * k - bisagra[1]
        return (bisagra[0] + px_ * math.cos(ang) - py_ * math.sin(ang),
                bisagra[1] + px_ * math.sin(ang) + py_ * math.cos(ang))

    mandibula = [rot(40, 10), rot(-150, 22), rot(-128, 56), rot(30, 52)]
    arriba = [P(hx + 72, hy - 48), P(hx - 20, hy - 72), P(hx - 150, hy - 42), P(hx - 170, hy - 2),
              P(hx - 150, hy + 12), P(hx + 40, hy + 14)]
    c.poligono([P(hx + 40, hy + 12), P(hx - 150, hy + 12), rot(-150, 22), rot(40, 10)], fill=(150, 30, 44))
    for i in range(6):  # dientes de abajo
        u = (i + 0.5) / 6
        bx, by = rot(-140 + 170 * u, 20)
        c.poligono([(bx - 8 * k, by + 2), (bx + 8 * k, by + 2), (bx, by - 16 * k)], fill=(255, 255, 250))
    c.poligono(mandibula, fill=VERDE, borde=BORDE_T, grosor=5 * k)
    c.poligono(arriba, fill=VERDE, borde=BORDE_T, grosor=6 * k)
    for i in range(7):  # dientes de arriba
        u = (i + 0.5) / 7
        bx, by = P(hx - 148 + 180 * u, hy + 12)
        c.poligono([(bx - 8 * k, by - 2), (bx + 8 * k, by - 2), (bx, by + 18 * k)], fill=(255, 255, 250))
    ex, ey = P(hx - 8, hy - 34)
    c.circulo(ex, ey, 18 * k, fill=(255, 240, 120), borde=BORDE_T, grosor=4 * k)
    c.elipse(ex - 3 * k, ey + 1, 5 * k, 12 * k * parpadeo(t, 3.3, 0.7), fill=(20, 20, 20))
    c.linea([P(hx - 36, hy - 60), P(hx + 14, hy - 48)], BORDE_T, 9 * k)
    c.elipse(*P(hx - 146, hy - 30), 7 * k, 4 * k, fill=BORDE_T)
    # bracitos
    for dy in (0, 16):
        brazo = [P(-122, -6 + dy), P(-160, 26 + dy), P(-172, 40 + dy)]
        c.linea(brazo, BORDE_T, 22 * k)
        c.linea(brazo, VERDE_OSC, 15 * k)
    # pata de adelante
    c.elipse(*P(5, 92), 80 * k, 100 * k, fill=VERDE, borde=BORDE_T, grosor=6 * k)
    c.linea([P(0, 150), P(-12, 252)], BORDE_T, 52 * k)
    c.linea([P(0, 150), P(-12, 252)], VERDE, 42 * k)
    c.elipse(*P(-40, 266), 62 * k, 20 * k, fill=VERDE, borde=BORDE_T, grosor=5 * k)
    for i in range(3):
        c.poligono([P(-92 + 14 * i, 258), P(-106 + 14 * i, 268), P(-92 + 14 * i, 276)], fill=(240, 236, 220))
    return rot(-140, 34)  # punto de la boca, adonde llegan los sonidos


def elefante(c, x, y, k=1.0):
    G, B = (170, 172, 188), (60, 60, 80)
    for s in (-1, 1):
        c.elipse(x + s * 44 * k, y - 8 * k, 30 * k, 38 * k, fill=G, borde=B, grosor=4 * k)
        c.elipse(x + s * 46 * k, y - 6 * k, 18 * k, 25 * k, fill=(236, 176, 188))
    c.circulo(x, y - 6 * k, 42 * k, fill=G, borde=B, grosor=4 * k)
    trompa = [(x, y + 12 * k), (x + 2 * k, y + 36 * k), (x + 10 * k, y + 54 * k), (x + 24 * k, y + 58 * k)]
    c.linea(trompa, B, 24 * k)
    c.linea(trompa, G, 17 * k)
    for s in (-1, 1):
        c.circulo(x + s * 16 * k, y - 14 * k, 6 * k, fill=(30, 30, 40))
        c.elipse(x + s * 28 * k, y + 6 * k, 8 * k, 5 * k, fill=(240, 150, 160))


def tigre(c, x, y, k=1.0):
    N, B = (245, 150, 40), (60, 30, 10)
    for s in (-1, 1):
        c.circulo(x + s * 32 * k, y - 38 * k, 15 * k, fill=N, borde=B, grosor=4 * k)
    c.circulo(x, y, 46 * k, fill=N, borde=B, grosor=4 * k)
    for s in (-1, 1):
        for i in range(2):
            c.linea([(x + s * 46 * k, y - 4 * k + i * 16 * k), (x + s * 26 * k, y - 2 * k + i * 14 * k)], B, 6 * k)
    for dx in (-10, 0, 10):
        c.linea([(x + dx * k, y - 44 * k), (x + dx * 0.7 * k, y - 28 * k)], B, 5 * k)
    c.elipse(x, y + 18 * k, 28 * k, 18 * k, fill=(255, 245, 230))
    c.poligono([(x - 8 * k, y + 6 * k), (x + 8 * k, y + 6 * k), (x, y + 15 * k)], fill=(60, 30, 30))
    for s in (-1, 1):
        c.elipse(x + s * 17 * k, y - 10 * k, 8 * k, 9 * k, fill=(140, 200, 80))
        c.elipse(x + s * 17 * k, y - 10 * k, 3 * k, 8 * k, fill=(20, 20, 20))


def caiman(c, x, y, k=1.0):
    V, B = (96, 150, 80), (30, 60, 30)
    for s in (-1, 1):
        c.circulo(x + 18 * k + s * 16 * k, y - 22 * k, 13 * k, fill=V, borde=B, grosor=3 * k)
        c.circulo(x + 18 * k + s * 16 * k, y - 24 * k, 6 * k, fill=(250, 230, 90))
        c.elipse(x + 18 * k + s * 16 * k, y - 24 * k, 2 * k, 5 * k, fill=(20, 20, 20))
    c.rrect(x - 56 * k, y - 18 * k, x + 50 * k, y + 22 * k, 18 * k, fill=V, borde=B, grosor=4 * k)
    c.linea([(x - 52 * k, y + 4 * k), (x + 44 * k, y + 4 * k)], B, 3 * k)
    for i in range(7):
        bx = x - 46 * k + i * 13 * k
        c.poligono([(bx - 4 * k, y + 3 * k), (bx + 4 * k, y + 3 * k), (bx, y + 11 * k)], fill=(255, 255, 250))
    for s in (-1, 1):
        c.circulo(x - 48 * k, y - 8 * k + s * 5 * k, 2.5 * k, fill=B)


def heladera(c, x, y, t, k=1.0, chispa=0.0):
    MENTA, B = (168, 224, 204), (36, 70, 70)

    def P(dx, dy):
        return (x + dx * k, y + dy * k)

    for s in (-1, 1):
        c.rrect(*P(s * 110 - 18, 262), *P(s * 110 + 18, 300), 6 * k, fill=(60, 70, 80))
    c.rrect(*P(-150, -290), *P(150, 280), 56 * k, fill=MENTA, borde=B, grosor=7 * k)
    c.linea([P(-146, -120), P(146, -120)], B, 5 * k)
    c.rrect(*P(-128, -270), *P(-100, -150), 10 * k, fill=(214, 244, 232))
    for y0, y1 in ((-260, -150), (-90, 60)):
        c.rrect(*P(112, y0), *P(130, y1), 8 * k, fill=(200, 205, 215), borde=B, grosor=3 * k)
    # "máquina del tiempo casera": reloj, cables y lucecitas
    for col, pts in (((220, 50, 60), [(-60, 10), (-150, 30), (-190, 120)]),
                     ((60, 120, 230), [(60, 10), (150, 60), (185, 160)])):
        c.linea([P(*p) for p in pts], B, 16 * k)
        c.linea([P(*p) for p in pts], col, 10 * k)
    c.circulo(*P(0, 10), 72 * k, fill=(250, 250, 245), borde=B, grosor=6 * k)
    for i in range(12):
        a = i * math.pi / 6
        c.linea([P(58 * math.cos(a), 10 + 58 * math.sin(a)), P(66 * math.cos(a), 10 + 66 * math.sin(a))], B, 4 * k,
                puntas=False)
    for largo, vel in ((42, 6.0), (56, 36.0)):
        a = t * vel - math.pi / 2
        c.linea([P(0, 10), P(largo * math.cos(a), 10 + largo * math.sin(a))], B, 6 * k)
    for i in range(4):
        prendida = (int(t * 6) + i) % 4 == 0 or chispa > 0
        c.circulo(*P(-60 + 40 * i, 150), 11 * k, fill=(255, 80, 80) if prendida else (120, 40, 40), borde=B,
                  grosor=3 * k)
    c.rrect(*P(-70, 185), *P(70, 235), 10 * k, fill=(20, 30, 20), borde=B, grosor=4 * k)


def auto(c, x, y, t, k=1.0):
    """Auto deportivo plateado de los 80 mirando a la izquierda."""
    ACERO, OSC, B = (206, 212, 222), (150, 156, 172), (40, 44, 60)

    def P(dx, dy):
        return (x + dx * k, y + dy * k)

    c.poligono([P(-235, 40), P(-228, 2), P(-100, -30), P(-12, -88), P(126, -88), P(236, -30), P(240, 40)],
               fill=ACERO, borde=B, grosor=6 * k)
    c.poligono([P(-230, 18), P(240, 18), P(240, 40), P(-235, 40)], fill=OSC)
    c.poligono([P(-80, -30), P(-8, -76), P(58, -76), P(58, -30)], fill=(40, 52, 84), borde=B, grosor=4 * k)
    c.poligono([P(72, -76), P(120, -76), P(170, -30), P(72, -30)], fill=(40, 52, 84), borde=B, grosor=4 * k)
    c.linea([P(-50, -34), P(-12, -64)], (160, 190, 240), 6 * k)
    for i in range(5):
        c.linea([P(180 + 10 * i, -20), P(180 + 10 * i, 10)], B, 4 * k, puntas=False)
    c.rrect(*P(-232, -2), *P(-205, 16), 5 * k, fill=(255, 240, 150))
    for wx in (-140, 150):
        cx_, cy_ = P(wx, 46)
        c.circulo(cx_, cy_, 44 * k, fill=(24, 24, 30))
        c.circulo(cx_, cy_, 22 * k, fill=(170, 175, 190))
        for i in range(5):
            a = -t * 18 + i * 2 * math.pi / 5
            c.linea([(cx_, cy_), (cx_ + 20 * k * math.cos(a), cy_ + 20 * k * math.sin(a))], (90, 95, 110), 4 * k)


def fuego(c, x0, y0, x1, t, k=1.0):
    """Estela de fuego sobre el piso (de x0 a x1)."""
    for col, g in (((255, 110, 30), 30), ((255, 200, 60), 16), ((255, 250, 210), 6)):
        pts = [(x, y0 + 5 * math.sin(x / 23 + t * 25) * (1 if g > 10 else 0.5))
               for x in np.linspace(x0, x1, 30)]
        c.linea(pts, col, g * k)


def barco(c, x, y, k=1.0):
    """Silueta de un transatlántico de 1912 (cuatro chimeneas)."""
    S = (34, 22, 46)
    c.poligono([(x - 180 * k, y - 16 * k), (x + 190 * k, y - 16 * k), (x + 170 * k, y + 14 * k),
                (x - 164 * k, y + 14 * k)], fill=S)
    c.rrect(x - 140 * k, y - 34 * k, x + 140 * k, y - 14 * k, 4 * k, fill=S)
    for i in range(4):
        fx = x - 90 * k + i * 58 * k
        c.poligono([(fx - 12 * k, y - 34 * k), (fx + 12 * k, y - 34 * k), (fx + 15 * k, y - 78 * k),
                    (fx - 9 * k, y - 78 * k)], fill=S)
        c.poligono([(fx - 10 * k, y - 70 * k), (fx + 14 * k, y - 70 * k), (fx + 15 * k, y - 78 * k),
                    (fx - 9 * k, y - 78 * k)], fill=(70, 50, 60))
    for mx in (-170, 176):
        c.linea([(x + mx * k, y - 16 * k), (x + mx * k * 0.95, y - 100 * k)], S, 3 * k, puntas=False)
    for i in range(14):
        c.circulo(x - 150 * k + i * 22 * k, y - 3 * k, 2.2 * k, fill=(255, 220, 140))


# Trazos del boceto (coordenadas en la hoja, 0..1): un retrato simple
def _trazos():
    tr = []
    ola = 0.012
    # cara (sin la parte de arriba, que tapa el pelo)
    tr.append([(0.5 + 0.13 * math.cos(u), 0.4 + 0.19 * math.sin(u)) for u in np.linspace(-0.2, math.pi + 0.2, 18)])
    # pelo: la cúpula y dos cascadas onduladas a los costados
    tr.append([(0.5 + 0.16 * math.cos(u), 0.36 - 0.2 * math.sin(u)) for u in np.linspace(0, math.pi, 16)])
    for s in (-1, 1):
        for j in range(3):
            base = 0.5 + s * (0.16 + 0.03 * j)
            tr.append([(base + s * 0.05 * u + ola * math.sin(14 * u + j), 0.36 + 0.42 * u) for u in np.linspace(0, 1, 16)])
    # cejas, ojos cerrados, nariz y boca
    for s in (-1, 1):
        tr.append([(0.5 + s * 0.055 + 0.03 * math.cos(u), 0.35 - 0.012 * math.sin(u)) for u in np.linspace(0, math.pi, 8)])
        tr.append([(0.5 + s * 0.055 + 0.03 * math.cos(u), 0.4 + 0.012 * math.sin(u)) for u in np.linspace(0, math.pi, 8)])
    tr.append([(0.5, 0.42), (0.49, 0.47), (0.505, 0.48)])
    tr.append([(0.47 + 0.06 * u, 0.53 + 0.012 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 8)])
    tr.append([(0.475 + 0.05 * u, 0.535 + 0.02 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 8)])
    # cuello, hombros y collar con dije de corazón
    for s in (-1, 1):
        tr.append([(0.5 + s * 0.06, 0.58), (0.5 + s * 0.07, 0.7), (0.5 + s * 0.34, 0.8)])
    tr.append([(0.5 + 0.1 * math.cos(u), 0.68 + 0.08 * math.sin(u)) for u in np.linspace(0.3, math.pi - 0.3, 12)])
    corazon_ = []
    for u in np.linspace(0, 2 * math.pi, 18):
        hx = 16 * math.sin(u) ** 3
        hy = 13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u)
        corazon_.append((0.5 + hx * 0.0022, 0.78 - hy * 0.0026))
    tr.append(corazon_)
    return tr


TRAZOS = _trazos()


def hoja(t, avance, w=600, h=440, con_mano=True):
    """Hoja con el boceto dibujado hasta `avance` (0..1) y la mano zurda con el lápiz."""
    c = Capa(0, 0, w + 300, h + 260, ss=2)
    ox, oy = 150, 130
    c.rrect(ox + 10, oy + 14, ox + w + 10, oy + h + 14, 14, fill=(10, 5, 20, 110))
    c.rrect(ox, oy, ox + w, oy + h, 14, fill=(250, 246, 234), borde=(180, 170, 150), grosor=3)
    total = sum(len(s) - 1 for s in TRAZOS)
    resto = avance * total
    punta = None
    for s in TRAZOS:
        pts = [(ox + px * w, oy + py * h) for px, py in s]
        seg = len(pts) - 1
        if resto <= 0:
            break
        n = min(seg, resto)
        entero = int(n)
        visibles = pts[:entero + 1]
        if n > entero and entero < seg:
            f = n - entero
            a, b = pts[entero], pts[entero + 1]
            visibles.append((lerp(a[0], b[0], f), lerp(a[1], b[1], f)))
        if len(visibles) > 1:
            c.linea(visibles, (64, 60, 72), 5)
        punta = visibles[-1]
        resto -= seg
    if con_mano and punta is not None:
        px, py = punta
        PIEL, B = (242, 204, 172), (90, 60, 40)
        # manga y puño de la camisa (entra desde la izquierda: es la mano izquierda)
        c.linea([(px - 110, py - 70), (px - 290, py + 30)], (60, 70, 110), 96)
        c.linea([(px - 104, py - 72), (px - 126, py - 60)], (250, 250, 250), 100)
        # lápiz
        lx, ly = px - 70, py - 150
        c.linea([(px, py), (lx, ly)], (70, 45, 20), 24)
        c.linea([(px + 3, py - 6), (lx, ly)], (250, 200, 60), 17)
        c.linea([(lx + 4, ly + 9), (lx - 4, ly - 9)], (240, 140, 160), 18)
        c.poligono([(px, py), (px - 7, py - 20), (px + 9, py - 16)], fill=(236, 200, 150))
        c.poligono([(px, py), (px - 2.5, py - 7), (px + 3, py - 6)], fill=(50, 50, 55))
        # puño
        c.elipse(px - 72, py - 64, 58, 46, fill=PIEL, borde=B, grosor=4)
        for i in range(4):
            c.circulo(px - 30 - i * 17, py - 30 + i * 3, 15, fill=PIEL, borde=B, grosor=3)
        c.elipse(px - 34, py - 88, 26, 14, fill=PIEL, borde=B, grosor=3)
    return c.imagen()


# =================================================================== escenas
def escena_rugido(t):
    fr = FONDOS["rugido"].copy()
    t0 = ESC["rugido"]["escena_ini"]
    tr = E["r_ruge"]
    # el tiranosaurio (la boca se va abriendo mientras llegan los sonidos)
    ent = e_out(prog(t, t0, 0.7))
    boca = 0.12 + 0.04 * math.sin(t * 3) + 0.12 * prog(t, E["r_mezcla"], tr - E["r_mezcla"])
    if t >= tr:
        boca = lerp(0.62, 0.16, e_in_out(prog(t, tr + 0.7, 0.6))) * e_back(prog(t, tr, 0.2))
    c = Capa(260, 560, 820, 900)
    boca_pt = trex(c, 740 + (1 - ent) * 500, 1110, t, 1.0, boca)
    # sonidos que viajan desde cada animal hasta la boca
    apagado = 1 - prog(t, tr, 0.3)
    for (nombre, y, _), col in zip(ANIMALES, ((200, 205, 230), (255, 170, 60), (140, 220, 110))):
        ti = E[f"r_{nombre.replace('á', 'a')}"]
        v = e_out(prog(t, ti + 0.2, 0.6))
        if v > 0 and apagado > 0:
            onda(c, (292, y), boca_pt, t + y, col + (int(230 * apagado),), 8, 16, 5, v)
    c.pegar_en(fr)
    # medallones con los animales
    for nombre, y, fondo in ANIMALES:
        s = pop(t, E[f"r_{nombre.replace('á', 'a')}"], 0.4)
        if s <= 0:
            continue
        c = Capa(90, y - 110, 220, 220)
        c.circulo(200, y + 8, 92 * s, fill=(0, 0, 0, 90))
        c.circulo(200, y, 92 * s, fill=fondo, borde=(255, 255, 255), grosor=8 * s)
        {"elefante": elefante, "tigre": tigre, "caimán": caiman}[nombre](c, 200, y + 4 * s, s)
        c.pegar_en(fr)
        etiqueta = {"elefante": "ELEFANTE BEBÉ", "tigre": "TIGRE", "caimán": "CAIMÁN"}[nombre]
        componer(fr, texto(etiqueta, "negra", 30, borde=5), 200, y + 110, escala=s)
    # el rugido
    if t >= tr:
        p = prog(t, tr, 0.9)
        c = Capa(0, 520, 760, 760)
        for i in range(3):
            q = (p * 1.6 - i * 0.25)
            if 0 < q < 1:
                c.arco(boca_pt[0], boca_pt[1], 60 + 380 * q, 60 + 380 * q, 150, 250, (255, 250, 200, int(230 * (1 - q))),
                       10)
        c.pegar_en(fr)
        s = e_back(prog(t, tr, 0.25)) * (1 - prog(t, tr + 1.0, 0.25))
        componer(fr, texto("¡GROAAAR!", "titulo", 110, color=(255, 230, 80), borde=12, color_borde=(140, 20, 20)),
                 640, 640, escala=s, rot=8)
    encabezado(fr, t, 1, E["rugido_badge"])
    titulo(fr, t, TITULOS["rugido"]["titulo"], t0 + 0.15, color=(200, 255, 150))
    pildora(fr, t, TITULOS["rugido"]["subtitulo"], (50, 140, 60), E["r_mezcla"])
    return fr


def escena_heladera(t):
    fr = FONDOS["heladera"].copy()
    t0 = ESC["heladera"]["escena_ini"]
    tc = E["h_cambiaron"]
    # piso con grilla retro que avanza
    c = Capa(0, HORIZONTE_80S, W, H - HORIZONTE_80S)
    for i in range(14):
        d = ((i / 14) + t * 0.35) % 1
        y = HORIZONTE_80S + 800 * d ** 2.2
        c.linea([(0, y), (W, y)], (255, 60, 200, int(80 + 150 * d)), 3 + 3 * d, puntas=False)
    for j in range(-8, 9):
        c.linea([(540 + j * 26, HORIZONTE_80S), (540 + j * 190, H)], (255, 60, 200, 170), 3, puntas=False)
    llegada = e_out(prog(t, tc + 0.5, 0.6))
    if t >= tc + 0.5:
        cx = lerp(1500, 540, llegada)
        fuego(c, cx + 150, 1316, W + 60, t)
        fuego(c, cx - 140, 1316, W + 60, t + 0.4)
    c.pegar_en(fr)
    # la heladera "máquina del tiempo" (se va cuando la cambian)
    s = e_back(prog(t, t0 + 0.15, 0.5))
    sale = prog(t, tc + 0.35, 0.5)
    if s > 0 and sale < 1:
        c = Capa(0, 540, W, 800)
        chispa = prog(t, E["h_heladera"], 0.1) * (1 - prog(t, E["h_heladera"] + 0.8, 0.1))
        vibra = 5 * math.sin(t * 60) * chispa
        heladera(c, 540 - 900 * sale ** 2 + vibra, 940, t, 0.95 * s, chispa)
        tachar(c, 540 - 900 * sale ** 2, 900, 460, e_back(prog(t, tc, 0.3)), 30)
        c.pegar_en(fr)
        if chispa > 0:
            chispas(fr, t, E["h_heladera"], 540, 700, n=16, seed=5,
                    colores=((255, 255, 180), (160, 220, 255), (255, 255, 255)), vel=(250, 600), grav=600, dur=0.8)
    # el auto que la reemplazó
    if t >= tc + 0.5:
        c = Capa(0, 1080, W, 320)
        auto(c, lerp(1500, 540, llegada), 1270 + 3 * math.sin(t * 30) * (1 - llegada), t, 1.0)
        c.pegar_en(fr)
    encabezado(fr, t, 2, E["heladera_badge"])
    titulo(fr, t, TITULOS["heladera"]["titulo"], t0 + 0.15, tam=120, color=(255, 200, 90))
    pildora(fr, t, TITULOS["heladera"]["subtitulo"], (200, 40, 140), E["h_heladera"], hasta=E["h_chico"])
    pildora(fr, t, "¡PARA QUE LOS CHICOS NO SE ENCIERREN!", (230, 90, 30), E["h_chico"] + 0.05)
    return fr


def escena_dibujo(t):
    fr = FONDOS["dibujo"].copy()
    t0 = ESC["dibujo"]["escena_ini"]
    tz = E["d_zurdo"]
    # el barco cruzando el horizonte
    c = Capa(0, HORIZONTE_MAR - 120, W, 150)
    barco(c, lerp(150, 420, prog(t, t0, 8.0)), HORIZONTE_MAR - 6, 0.9)
    c.pegar_en(fr)
    # la hoja con el boceto: se dibuja con la mano zurda y después se espeja
    avance = e_in_out(prog(t, E["d_manos"] - 0.3, tz - E["d_manos"] + 0.4))
    s = e_back(prog(t, t0 + 0.2, 0.5))
    if s > 0:
        im = hoja(t, avance)
        giro = prog(t, tz + 0.25, 0.55)
        sx = math.cos(math.pi * e_in_out(giro))
        if sx < 0:
            im = ImageOps.mirror(im)
        ancho = max(2, int(im.width * abs(sx)))
        im = im.resize((ancho, im.height), Image.BICUBIC)
        componer(fr, im, 540, 1120, escala=s, rot=-3)
        if 0 < giro < 1:
            c = Capa(300, 1060, 480, 120)
            a_ = int(255 * math.sin(math.pi * giro))
            for col, g in (((20, 20, 50, a_), 26), ((255, 255, 255, a_), 14)):
                c.linea([(400, 1120), (680, 1120)], col, g)
                for x0, d in ((400, 1), (680, -1)):
                    c.poligono([(x0 - d * 12, 1120), (x0 + d * 40, 1120 - 34 - g / 2), (x0 + d * 40, 1120 + 34 + g / 2)],
                               fill=col)
            c.pegar_en(fr)
    # quién dibuja
    sd = pop(t, E["d_director"], 0.4)
    if sd > 0:
        componer(fr, cartel("JAMES CAMERON", "EL DIRECTOR", (130, 205, 255), (12, 30, 76), 560, 84),
                 540, 660, escala=sd, rot=-2)
    sz = pop(t, tz, 0.35)
    if sz > 0:
        lado = 250 if prog(t, tz + 0.25, 0.55) < 0.5 else 830
        componer(fr, texto("ES ZURDO", "titulo", 56, color=(255, 230, 90), borde=8), lado, 860, escala=sz, rot=-8)
    encabezado(fr, t, 3, E["dibujo_badge"])
    titulo(fr, t, TITULOS["dibujo"]["titulo"], t0 + 0.15, color=(170, 215, 255))
    pildora(fr, t, TITULOS["dibujo"]["subtitulo"], (40, 110, 200), E["d_manos"], hasta=E["d_imagen"] - 0.2)
    pildora(fr, t, "¡DIERON VUELTA LA IMAGEN!", (230, 70, 90), E["d_imagen"] - 0.15)
    return fr


# ======================================================= íconos del cierre
def _icono_rugido(c, x, y, s, t):
    trex(c, x + 38 * s, y + 18 * s, t, 0.27 * s, 0.35)


def _icono_heladera(c, x, y, s, t):
    heladera(c, x, y + 2 * s, t, 0.3 * s)


def _icono_dibujo(c, x, y, s, t):
    return [(_mini_hoja(), x, y)] if s > 0.05 else []


@lru_cache(None)
def _mini_hoja():
    im = hoja(0, 1.0, con_mano=False)
    return im.resize((int(im.width * 0.3), int(im.height * 0.3)), Image.LANCZOS)


ICONOS = [_icono_rugido, _icono_heladera, _icono_dibujo]
ESCENAS = {"rugido": escena_rugido, "heladera": escena_heladera, "dibujo": escena_dibujo}
