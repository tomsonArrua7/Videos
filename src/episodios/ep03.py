"""Episodio 3: las nutrias, el rayo y los árboles (voz de Elena, Argentina)."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from dibujo import (H, W, Capa, _pildora, a_imagen, chispas, clamp, componer, corazon,
                    e_back, e_in_out, e_out, encabezado, gradiente, latido, lerp, pildora, pop, prog,
                    resplandor, sello, spr_estrella, texto, titulo, viñeta)

SLUG = "nutrias_rayo_arboles"
DURACION = 30.0
VOZ = "es-AR-ElenaNeural"
VOZ_TONO = "+0Hz"
VOZ_VELOCIDAD_MIN = 0
GANCHO_ETIQUETA = "PARTE 3"
PALABRAS_CIERRE = ("abajo", "seguinos")

BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades más que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "PARTE 3",
    },
    {
        "id": "nutrias",
        "texto": "Uno: las nutrias marinas duermen tomadas de la mano, para que la corriente no las separe.",
        "titulo": "NUTRIAS",
        "subtitulo": "DUERMEN DE LA MANO",
    },
    {
        "id": "rayo",
        "texto": "Dos: un rayo es cinco veces más caliente que la superficie del Sol. "
                 "¡Llega a unos treinta mil grados!",
        "titulo": "RAYOS",
        "subtitulo": "5 VECES MÁS CALIENTES QUE EL SOL",
    },
    {
        "id": "arboles",
        "texto": "Tres: en la Tierra hay más árboles que estrellas en nuestra galaxia. "
                 "¡Unos tres billones de árboles!",
        "titulo": "ÁRBOLES",
        "subtitulo": "MÁS ÁRBOLES QUE ESTRELLAS",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"nutrias": (0, 168, 190), "rayo": (255, 222, 60),
          "arboles": (60, 190, 90), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS, EXTRA = {}, {}, {}, {}
SUELO = 1420            # donde pega el rayo


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "n_duermen": L.palabra("nutrias", "duermen"),
        "n_mano": L.palabra("nutrias", "mano"),
        "n_corriente": L.palabra("nutrias", "corriente"),
        "r_rayo": L.palabra("rayo", "rayo"),
        "r_cinco": L.palabra("rayo", "cinco"),
        "r_caliente": L.palabra("rayo", "caliente"),
        "r_sol": L.palabra("rayo", "sol"),
        "r_treinta": L.palabra("rayo", "treinta"),
        "r_grados": L.fin_palabra("rayo", "grados"),
        "a_mas": L.palabra("arboles", "más"),
        "a_arboles": L.palabra("arboles", "árboles"),
        "a_estrellas": L.palabra("arboles", "estrellas"),
        "a_galaxia": L.palabra("arboles", "galaxia"),
        "a_billones": L.palabra("arboles", "billones"),
        "a_fin": L.fin_palabra("arboles", "árboles", 2),
        # cuando el contador de árboles ya pasó al de estrellas
        "a_veces": L.palabra("arboles", "billones") + 0.45,
    }


# ángulos (en grados, -90 = arriba) de los árboles que brotan sobre la Tierra
ARBOLES_1 = [-165 + 12.5 * i for i in range(13)]
ARBOLES_2 = [-158.75 + 12.5 * i for i in range(12)]


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    fx = [(E["n_duermen"], S.pop(600, 300), 0.20),
          (E["n_mano"], S.pop(900, 400), 0.35),
          (E["n_mano"] + 0.1, S.brillo_sfx(), 0.30),
          (E["n_corriente"] - 0.1, S.whoosh(0.9, 250, 1400), 0.22)]
    ini, fin = E["rayo_ini"], E["arboles_ini"]
    fx += [(ini - 0.2, S.lluvia(fin - ini + 0.3), 0.10),
           (E["r_rayo"] - 0.05, S.trueno(), 0.45),
           (E["r_cinco"], S.golpe(), 0.45),
           (E["r_caliente"], S.subida(0.8, 300, 1500), 0.22),
           (E["r_sol"], S.subida(0.35, 300, 500), 0.20),
           (E["r_treinta"] - 0.05, S.trueno(), 0.36)]
    t = E["r_treinta"]
    while t < E["r_grados"]:
        fx.append((t, S.tic(), 0.14))
        t += 0.06
    fx += [(E["a_arboles"] + 0.05 * i, S.pop(500 + 60 * i, 300 + 30 * i, 0.08), 0.14)
           for i in range(len(ARBOLES_1))]
    fx += [(E["a_mas"], S.pop(600, 250), 0.25),
           (E["a_galaxia"], S.bloop(), 0.30)]
    for t0, t1 in ((E["a_estrellas"], E["a_estrellas"] + 0.8), (E["a_billones"], E["a_fin"])):
        t = t0
        while t < t1:
            fx.append((t, S.tic(), 0.14))
            t += 0.06
    fx += [(E["a_billones"] + 0.05 * i, S.pop(700 + 50 * i, 350, 0.08), 0.10) for i in range(len(ARBOLES_2))]
    fx += [(E["a_veces"], S.golpe(), 0.45), (E["a_veces"] + 0.05, S.ding(), 0.25)]
    return fx


def sacudidas(E):
    return [(E["r_rayo"], 16, 0.35), (E["r_treinta"], 12, 0.3), (E["a_veces"], 6, 0.2)]


# ==================================================================== fondos
def fondo_nutrias():
    """Mar de noche visto desde arriba, con el reflejo de la luna."""
    a = gradiente([(0, (16, 46, 104)), (0.5, (10, 38, 88)), (1, (4, 20, 56))])
    resplandor(a, 850, 560, 260, (150, 190, 240), 0.45)
    viñeta(a, 0.4)
    img = a_imagen(a, 9)
    rng = np.random.default_rng(13)
    for _ in range(40):
        componer(img, spr_estrella(int(rng.integers(3, 6))), rng.uniform(0, W), rng.uniform(0, H),
                 alpha=rng.uniform(0.15, 0.4))
    return img


def fondo_rayo():
    a = gradiente([(0, (20, 18, 40)), (0.45, (36, 34, 64)), (0.72, (52, 50, 86)), (1, (30, 28, 50))])
    img = a_imagen(a, 10)
    c = Capa(0, 360, W, 360)
    rng = np.random.default_rng(3)
    for capa_, col in ((0, (58, 56, 88)), (1, (76, 74, 110))):
        for _ in range(22):
            x, y, r = rng.uniform(-60, W + 60), rng.uniform(420, 600) - capa_ * 20, rng.uniform(60, 120)
            c.circulo(x, y + capa_ * 6, r * (1 - 0.15 * capa_), fill=col)
    c.pegar_en(img)
    c = Capa(0, SUELO - 80, W, H - SUELO + 80)
    pts = [(x, SUELO + 26 * math.sin(x / 150) + 14 * math.sin(x / 47)) for x in range(-20, W + 40, 20)]
    c.poligono(pts + [(W + 40, H), (-20, H)], fill=(22, 20, 36))
    c.pegar_en(img)
    return img


def fondo_arboles():
    a = gradiente([(0, (8, 10, 36)), (0.5, (22, 18, 66)), (1, (40, 22, 88))])
    for i in range(9):  # la Vía Láctea cruzando en diagonal
        resplandor(a, -100 + i * 160, 1500 - i * 150, 210, (120, 110, 190), 0.28)
    img = a_imagen(a, 11)
    rng = np.random.default_rng(14)
    for _ in range(220):
        u = rng.uniform(0, 1)
        x, y = -100 + u * 1300 + rng.normal(0, 110), 1500 - u * 1220 + rng.normal(0, 110)
        componer(img, spr_estrella(int(rng.integers(2, 5))), x, y, alpha=rng.uniform(0.3, 0.9))
    for _ in range(90):
        componer(img, spr_estrella(int(rng.integers(3, 8))), rng.uniform(0, W), rng.uniform(0, H),
                 alpha=rng.uniform(0.3, 0.9))
    return img


def preparar():
    FONDOS.update(nutrias=fondo_nutrias(), rayo=fondo_rayo(), arboles=fondo_arboles())


# ================================================================ personajes
MARRON, MARRON_OSC, PANZA, CARA, BORDE_N = (140, 94, 58), (100, 64, 40), (206, 162, 114), (234, 208, 172), (58, 34, 18)


def nutria(c, x, y, t, k=1.0, lado=1, mano=None, fase=0.0):
    """Nutria panza arriba vista desde arriba; estira un brazo hacia `mano`."""
    cola = [(x + 8 * k * math.sin(t * 1.5 + fase + i * 0.4), y + 150 * k + 100 * k * i / 10) for i in range(11)]
    c.tubo(cola, [(28 - 14 * i / 10) * k + 5 * k for i in range(11)], BORDE_N)
    c.tubo(cola, [(28 - 14 * i / 10) * k for i in range(11)], MARRON_OSC)
    for s in (-1, 1):
        c.elipse(x + s * 50 * k, y + 160 * k, 21 * k, 32 * k, fill=MARRON_OSC, borde=BORDE_N, grosor=4 * k)
    c.elipse(x, y + 30 * k, 90 * k, 144 * k, fill=MARRON, borde=BORDE_N, grosor=6 * k)
    c.elipse(x, y + 24 * k, 60 * k, 110 * k, fill=PANZA)
    c.elipse(x - lado * 30 * k, y - 32 * k, 18 * k, 15 * k, fill=MARRON_OSC, borde=BORDE_N, grosor=3 * k)
    hx, hy = x, y - 128 * k
    for s in (-1, 1):
        c.circulo(hx + s * 50 * k, hy - 40 * k, 15 * k, fill=MARRON_OSC, borde=BORDE_N, grosor=4 * k)
    c.circulo(hx, hy, 66 * k, fill=MARRON, borde=BORDE_N, grosor=6 * k)
    c.elipse(hx, hy + 12 * k, 54 * k, 44 * k, fill=CARA)
    for s in (-1, 1):
        c.arco(hx + s * 25 * k, hy - 8 * k, 13 * k, 10 * k, 20, 160, BORDE_N, 4.5 * k)
        c.elipse(hx + s * 40 * k, hy + 16 * k, 11 * k, 6 * k, fill=(240, 150, 140))
        for dy in (-1, 1):
            c.linea([(hx + s * 20 * k, hy + 20 * k + dy * 4 * k), (hx + s * 52 * k, hy + 14 * k + dy * 11 * k)],
                    BORDE_N, 2 * k, puntas=False)
    c.elipse(hx, hy + 12 * k, 13 * k, 9 * k, fill=(50, 30, 25))
    for s in (-1, 1):
        c.arco(hx + s * 7 * k, hy + 22 * k, 7 * k, 6 * k, 0, 180, BORDE_N, 3 * k)
    if mano is not None:
        hombro = (x + lado * 62 * k, y - 38 * k)
        c.linea([hombro, mano], BORDE_N, 36 * k)
        c.linea([hombro, mano], MARRON, 27 * k)


def patitas(c, m, k=1.0):
    for dx in (-9, 9):
        c.circulo(m[0] + dx * k, m[1], 19 * k, fill=MARRON_OSC, borde=BORDE_N, grosor=3.5 * k)


def rayo_pts(seed, x0, y0, x1, y1, n=11, amp=46):
    rng = np.random.default_rng(seed)
    pts = [(x0, y0)]
    for i in range(1, n):
        u = i / n
        pts.append((lerp(x0, x1, u) + rng.uniform(-amp, amp), lerp(y0, y1, u) + rng.uniform(-12, 12)))
    pts.append((x1, y1))
    ramas = []
    for j in (3, 6):
        bx, by = pts[j]
        rama = [(bx, by)]
        lado = 1 if rng.uniform() > 0.5 else -1
        for m in range(1, 5):
            rama.append((bx + lado * m * rng.uniform(25, 45), by + m * rng.uniform(35, 55)))
        ramas.append(rama)
    return pts, ramas


def dibujar_rayo(c, pts, ramas, alpha=1.0):
    a = int(255 * alpha)
    for trazo, g in [(pts, 1.0)] + [(r, 0.55) for r in ramas]:
        c.linea(trazo, (150, 180, 255, int(a * 0.45)), 30 * g)
        c.linea(trazo, (255, 245, 170, a), 13 * g)
        c.linea(trazo, (255, 255, 255, a), 5 * g)


def icono_rayo(c, x, y, k=1.0, color=(255, 222, 60)):
    pts = [(-10, -60), (32, -60), (10, -12), (34, -12), (-22, 64), (-4, 6), (-28, 6)]
    c.poligono([(x + px * k, y + py * k) for px, py in pts], fill=color, borde=(60, 40, 0), grosor=4 * k)


def icono_sol(c, x, y, k=1.0, t=0.0):
    for i in range(10):
        a = i * math.pi / 5 + t * 0.5
        c.poligono([(x + 34 * k * math.cos(a - 0.2), y + 34 * k * math.sin(a - 0.2)),
                    (x + 54 * k * math.cos(a), y + 54 * k * math.sin(a)),
                    (x + 34 * k * math.cos(a + 0.2), y + 34 * k * math.sin(a + 0.2))], fill=(255, 196, 40))
    c.circulo(x, y, 36 * k, fill=(255, 170, 30), borde=(150, 70, 0), grosor=4 * k)
    c.circulo(x - 2 * k, y - 2 * k, 28 * k, fill=(255, 214, 70))


def termometro(c, x, y_top, y_bot, frac, color):
    blanco, vidrio = (255, 255, 255), (255, 255, 255, 50)
    c.rrect(x - 34, y_top - 34, x + 34, y_bot + 10, 34, fill=vidrio, borde=blanco, grosor=6)
    c.circulo(x, y_bot + 44, 58, fill=vidrio, borde=blanco, grosor=6)
    c.circulo(x, y_bot + 44, 44, fill=color)
    alto = (y_bot - y_top) * frac
    c.rrect(x - 20, y_bot - alto, x + 20, y_bot + 30, 20, fill=color)
    c.rrect(x - 12, y_bot - alto + 8, x - 4, y_bot + 10, 4, fill=(255, 255, 255, 120))
    for i in range(1, 9):
        yy = y_bot - (y_bot - y_top) * i / 9
        c.linea([(x + 34, yy), (x + 50, yy)], blanco, 4, puntas=False)


def arbolito(c, x, y, ang, k=1.0):
    ux, uy = math.cos(ang), math.sin(ang)
    c.linea([(x - ux * 6 * k, y - uy * 6 * k), (x + ux * 30 * k, y + uy * 30 * k)], (96, 60, 34), 11 * k)
    cx, cy = x + ux * 50 * k, y + uy * 50 * k
    c.circulo(cx, cy, 27 * k, fill=(20, 84, 44))
    c.circulo(cx, cy, 23 * k, fill=(76, 186, 86))
    c.circulo(cx - 7 * k, cy - 7 * k, 8 * k, fill=(140, 226, 140))


def sprite_tierra(r, t, cara=True):
    """Planeta Tierra con continentes que giran y cara feliz."""
    ss = 2
    tam = int(2 * r + 16)
    c = Capa(0, 0, tam, tam, ss=ss)
    m = tam / 2
    c.circulo(m, m, r, fill=(46, 126, 224))
    periodo = 2.4 * r
    off = (t * 16) % periodo
    manchas = [(-0.7, -0.35, 0.34, 0.24), (-0.55, 0.1, 0.22, 0.3), (-0.1, 0.35, 0.3, 0.32),
               (0.4, -0.3, 0.32, 0.22), (0.55, 0.05, 0.2, 0.2), (0.95, 0.3, 0.26, 0.24)]
    for u, v, rx, ry in manchas:
        x = m - 1.2 * r + ((u + 1.2) * r + off) % periodo
        for dup in (-periodo, 0, periodo):
            for dx, dy, e in ((0, 0, 1.0), (0.18, 0.1, 0.7), (-0.15, -0.08, 0.6)):
                c.elipse(x + dup + dx * r, m + (v + dy) * r, rx * e * r, ry * e * r, fill=(88, 186, 92))
    c.elipse(m, m - r * 0.97, r * 0.5, r * 0.16, fill=(240, 248, 255))
    c.elipse(m, m + r * 0.99, r * 0.45, r * 0.14, fill=(240, 248, 255))
    base = c.im
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse([(m + r * 0.15) * ss, (m - r * 0.6) * ss, (m + r * 2.0) * ss,
                                    (m + r * 1.6) * ss], fill=(10, 20, 70, 80))
    base.alpha_composite(sombra)
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).ellipse([(m - r) * ss, (m - r) * ss, (m + r) * ss, (m + r) * ss], fill=255)
    base.putalpha(Image.fromarray(np.minimum(np.array(base.getchannel("A")), np.array(mask))))
    c.im = base
    c.d = ImageDraw.Draw(c.im)
    c.circulo(m, m, r, borde=(18, 50, 110), grosor=max(3, r / 18))
    if cara:
        k = r / 100
        B = (20, 40, 80)
        for s in (-1, 1):
            c.circulo(m + s * 30 * k, m - 4 * k, 12 * k, fill=(255, 255, 255), borde=B, grosor=3 * k)
            c.circulo(m + s * 30 * k + 2 * k, m - 2 * k, 6.5 * k, fill=B)
            c.elipse(m + s * 54 * k, m + 22 * k, 12 * k, 7 * k, fill=(255, 140, 150))
        c.arco(m, m + 16 * k, 20 * k, 16 * k, 20, 160, B, 5 * k)
    return c.imagen()


@lru_cache(None)
def _galaxia_redonda(r):
    rng = np.random.default_rng(5)
    n = 2 * r + 1
    brazos = np.zeros((n, n), np.float32)
    for brazo in range(2):
        for _ in range(4200):
            s = rng.uniform(0.06, 1.0)
            ang = brazo * math.pi + 5.2 * s + rng.normal(0, 0.3 * (1.1 - s))
            x = int(r + r * 0.95 * s * math.cos(ang) + rng.normal(0, 3))
            y = int(r + r * 0.95 * s * math.sin(ang) + rng.normal(0, 3))
            if 0 <= x < n and 0 <= y < n:
                brazos[y, x] += rng.uniform(0.3, 1.0)
    borroso = np.asarray(Image.fromarray(np.clip(brazos * 70, 0, 255).astype(np.uint8), "L")
                         .filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1].astype(np.float32)
    d = np.sqrt(xx ** 2 + yy ** 2) / r
    nucleo = np.exp(-(d / 0.16) ** 2) + 0.35 * np.exp(-(d / 0.45) ** 2)
    puntos = np.clip(brazos * 0.8, 0, 1)
    a = np.clip(nucleo + 3.2 * borroso + 0.7 * puntos, 0, 1) * np.clip(1.1 - d, 0, 1)
    peso_n = np.clip(nucleo / (nucleo + borroso + 1e-6), 0, 1)[..., None]
    rgb = peso_n * np.array([255, 238, 200]) + (1 - peso_n) * np.array([170, 160, 255])
    rgba = np.dstack([rgb, a * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def spr_galaxia(r, ang):
    im = _galaxia_redonda(r).rotate(ang, resample=Image.BICUBIC)
    return im.resize((im.width, int(im.height * 0.55)), Image.BICUBIC)


def _numero(v):
    return f"{v:,}".replace(",", ".")


@lru_cache(maxsize=800)
def _fila(etiqueta, valor, color, icono):
    w, h = 920, 118
    c = Capa(0, 0, w + 12, h + 16, ss=3)
    c.rrect(6, 14, w + 6, h + 14, 30, fill=(0, 0, 20, 120))
    c.rrect(6, 6, w + 6, h + 6, 30, fill=(14, 14, 44), borde=color, grosor=5)
    c.circulo(6 + 64, 6 + h / 2, 44, fill=(34, 34, 80))
    if icono == "arbol":
        arbolito(c, 6 + 64, 6 + h / 2 + 30, -math.pi / 2, 0.95)
    im = c.imagen()
    if icono == "galaxia":
        g = spr_galaxia(44, 30)
        im.alpha_composite(g, (int(6 + 64 - g.width / 2), int(6 + h / 2 - g.height / 2)))
    et = texto(etiqueta, "negra", 30, color=(210, 210, 240))
    num = texto(valor, "titulo", 62, color=color)
    im.alpha_composite(et, (140, 14))
    im.alpha_composite(num, (136, int(h - num.height + 10)))
    return im


def fila(fr, t, y, etiqueta, final, t0, dur, color, icono):
    s = e_back(prog(t, t0 - 0.1, 0.35))
    if s <= 0:
        return
    p = e_out(prog(t, t0, dur))
    v = final * p
    cifras = max(0, len(str(int(final))) - 3)
    v = int(round(v / 10 ** cifras)) * 10 ** cifras
    componer(fr, _fila(etiqueta, _numero(v), color, icono), W / 2, y, escala=s)


# =================================================================== escenas
def escena_nutrias(t):
    fr = FONDOS["nutrias"].copy()
    t0 = ESC["nutrias"]["escena_ini"]
    tc = E["n_corriente"]
    # reflejo de la luna que titila
    c = Capa(0, 480, W, H - 480)
    for i in range(14):
        y = 560 + i * 34
        ancho = (60 - i * 2.5) * (0.7 + 0.3 * math.sin(t * 3 + i * 1.7))
        c.elipse(850 + 16 * math.sin(t * 1.2 + i), y, ancho, 5, fill=(200, 220, 255, 150))
    # corriente: rayitas que pasan
    fuerza = prog(t, tc - 0.2, 0.3) * (1 - prog(t, tc + 1.4, 0.5))
    if fuerza > 0:
        rng = np.random.default_rng(2)
        for _ in range(20):
            y = rng.uniform(620, 1480)
            x = (rng.uniform(0, W) + 900 * (t - tc)) % (W + 300) - 150
            c.linea([(x - 110, y), (x, y + 6 * math.sin(x / 40))], (200, 235, 255, int(160 * fuerza)), 5)
    # algas flotando
    for j, (y0, fase) in enumerate([(700, 0.0), (1330, 1.6), (1420, 3.0)]):
        pts = [(x, y0 + 22 * math.sin(x / 70 + t * 1.2 + fase)) for x in range(-40, W + 60, 30)]
        c.linea(pts, (22, 86, 50), 18)
        for x, y in pts[1::3]:
            c.elipse(x, y + 10, 16, 8, fill=(40, 130, 70))
    # las dos nutrias, dormidas y de la mano
    deriva = 60 * e_in_out(prog(t, tc, 1.2))
    ent = e_out(prog(t, t0, 0.8))
    ya = 1010 + 8 * math.sin(t * 1.4)
    yb = 1010 + 8 * math.sin(t * 1.4 + 1.3)
    K = 1.12
    xa, xb = 360 + deriva - (1 - ent) * 600, 720 + deriva + (1 - ent) * 600
    for x, y in ((xa, ya), (xb, yb)):
        r = 150 + 40 * ((t * 0.6) % 1)
        c.elipse(x, y + 20, r * 0.9 * K, r * 1.4 * K, borde=(170, 210, 255, int(90 * (1 - (t * 0.6) % 1))), grosor=4)
    tm = E["n_mano"]
    junta = e_back(prog(t, tm - 0.15, 0.45))
    mano = (lerp(xa + 30 * K, (xa + xb) / 2, junta), lerp(ya - 30 * K, (ya + yb) / 2 - 20, junta))
    mano_b = (lerp(xb - 30 * K, (xa + xb) / 2, junta), lerp(yb - 30 * K, (ya + yb) / 2 - 20, junta))
    nutria(c, xa, ya, t, K, 1, mano, 0.0)
    nutria(c, xb, yb, t, K, -1, mano_b, 1.3)
    patitas(c, mano, K)
    patitas(c, mano_b, K)
    s = pop(t, tm, 0.4)
    if s > 0:
        corazon(c, (xa + xb) / 2, (ya + yb) / 2 - 120 - 10 * math.sin(t * 3), 48 * s * latido(t), (255, 90, 124))
    c.pegar_en(fr)
    # zzz
    if t >= E["n_duermen"]:
        for hx, hy in ((xa, ya - 128 * K), (xb, yb - 128 * K)):
            for i in range(3):
                ph = ((t * 0.55) + i / 3) % 1
                componer(fr, texto("z", "titulo", 36 + 12 * i, color=(255, 255, 255), borde=5),
                         hx + 30 + 50 * ph, hy - 90 - 110 * ph, alpha=math.sin(math.pi * ph))
    encabezado(fr, t, 1, E["nutrias_badge"])
    titulo(fr, t, TITULOS["nutrias"]["titulo"], t0 + 0.15, color=(180, 240, 255))
    pildora(fr, t, TITULOS["nutrias"]["subtitulo"], (0, 140, 170), tm, hasta=tc)
    pildora(fr, t, "¡ASÍ NO SE SEPARAN!", (230, 80, 120), tc + 0.1)
    return fr


def escena_rayo(t):
    fr = FONDOS["rayo"].copy()
    t0 = ESC["rayo"]["escena_ini"]
    golpes = [(E["r_rayo"] - 0.05, 7, 250), (E["r_treinta"] - 0.05, 11, 380)]
    # lluvia
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    rng = np.random.default_rng(1)
    for _ in range(80):
        x0, y0, v = rng.uniform(-200, W), rng.uniform(0, H), rng.uniform(1400, 2000)
        y = (y0 + v * t) % (H + 100) - 50
        x = (x0 + 0.2 * v * t) % (W + 200) - 100
        d.line([(x, y), (x + 9, y + 44)], fill=(190, 200, 255, 90), width=3)
    fr.alpha_composite(capa)
    # rayos que caen
    for ts, seed, xs in golpes:
        dt = t - ts
        if 0 <= dt < 0.4 and not (0.07 < dt < 0.12):
            c = Capa(0, 520, W, SUELO - 500)
            pts, ramas = rayo_pts(seed, xs - 60, 560, xs, SUELO)
            dibujar_rayo(c, pts, ramas, alpha=clamp((0.4 - dt) / 0.15))
            c.pegar_en(fr)
        chispas(fr, t, ts, xs, SUELO, n=18, seed=seed, colores=((255, 245, 170), (255, 255, 255)),
                vel=(250, 650), grav=900, dur=0.9, arriba=True)
    # termómetros: Sol contra rayo
    ent = e_out(prog(t, t0 + 0.3, 0.5))
    if ent > 0:
        c = Capa(480, 560, 560, 880)
        f_rayo = e_out(prog(t, E["r_caliente"], 0.8))
        f_sol = 0.19 * e_out(prog(t, E["r_sol"], 0.5))
        brillo = 0.5 + 0.5 * math.sin(t * 12)
        termometro(c, 600, 790 + (1 - ent) * 600, 1250 + (1 - ent) * 600, f_sol, (255, 140, 40))
        termometro(c, 900, 790 + (1 - ent) * 600, 1250 + (1 - ent) * 600, f_rayo,
                   (255, int(220 + 30 * brillo), int(60 + 120 * brillo * f_rayo)))
        icono_sol(c, 600, 700 + (1 - ent) * 600, 0.9, t)
        icono_rayo(c, 900, 700 + (1 - ent) * 600, 0.9)
        c.pegar_en(fr)
        if f_sol > 0.01:
            componer(fr, texto("5.500 °C", "negra", 40, borde=6), 600, 600, alpha=clamp(f_sol * 8))
        s = pop(t, E["r_treinta"], 0.3)
        if s > 0:
            n = int(round(30000 * e_out(prog(t, E["r_treinta"], E["r_grados"] - E["r_treinta"] + 0.2)), -2))
            componer(fr, texto(f"{_numero(n)} °C", "negra", 44, color=(255, 236, 90), borde=6), 900, 600,
                     escala=s)
    s = e_back(prog(t, E["r_cinco"], 0.3))
    if s > 0:
        componer(fr, sello("×5", (230, 40, 70), 84), 750, 1000, escala=s * (1 + 0.04 * math.sin(t * 8)),
                 rot=-10)
    # fogonazo del rayo
    for ts, _, _ in golpes:
        if ts <= t < ts + 0.25:
            fr.alpha_composite(Image.new("RGBA", (W, H), (235, 240, 255, int(170 * (1 - prog(t, ts, 0.25))))))
    encabezado(fr, t, 2, E["rayo_badge"])
    titulo(fr, t, TITULOS["rayo"]["titulo"], t0 + 0.15, color=(255, 236, 110))
    pildora(fr, t, TITULOS["rayo"]["subtitulo"], (200, 120, 0), E["r_caliente"])
    return fr


def escena_arboles(t):
    fr = FONDOS["arboles"].copy()
    t0 = ESC["arboles"]["escena_ini"]
    rng = np.random.default_rng(15)
    for i in range(30):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        tw = 0.5 + 0.5 * math.sin(t * rng.uniform(2, 5) + i)
        componer(fr, spr_estrella(int(rng.integers(4, 9))), x, y, alpha=0.25 + 0.75 * tw)
    # galaxia girando (se enciende al decir "estrellas")
    luz = 0.45 + 0.55 * e_out(prog(t, E["a_estrellas"], 0.5))
    pulso = 1 + 0.08 * math.exp(-max(0.0, t - E["a_galaxia"]) * 4) if t >= E["a_galaxia"] else 1
    componer(fr, spr_galaxia(175, -t * 14), 820, 700, escala=pulso * e_out(prog(t, t0, 0.6)), alpha=luz)
    # la Tierra con árboles que brotan
    ex, ey, r = 390, 905, 170
    s_t = e_back(prog(t, t0 + 0.1, 0.5))
    if s_t > 0:
        c = Capa(100, 600, 580, 560)
        for lista, t_ini, k in ((ARBOLES_1, E["a_arboles"], 1.0), (ARBOLES_2, E["a_billones"], 0.8)):
            for i, ang in enumerate(lista):
                s = e_back(prog(t, t_ini + 0.05 * i, 0.3))
                if s > 0:
                    a = math.radians(ang)
                    arbolito(c, ex + (r * s_t - 4) * math.cos(a), ey + (r * s_t - 4) * math.sin(a), a,
                             k * s * s_t)
        c.pegar_en(fr)
        componer(fr, sprite_tierra(int(r * s_t), t), ex, ey)
    fila(fr, t, 1180, "ESTRELLAS EN LA VÍA LÁCTEA", 400_000_000_000, E["a_estrellas"], 0.8,
         (190, 180, 255), "galaxia")
    fila(fr, t, 1320, "ÁRBOLES EN LA TIERRA", 3_000_000_000_000, E["a_billones"],
         max(0.4, E["a_fin"] - E["a_billones"]), (120, 230, 120), "arbol")
    s = e_back(prog(t, E["a_veces"], 0.35))
    if s > 0:
        componer(fr, _pildora("¡MÁS DE 7 VECES!", (40, 160, 70), 40), 800, 960, escala=s, rot=-7)
    encabezado(fr, t, 3, E["arboles_badge"])
    titulo(fr, t, TITULOS["arboles"]["titulo"], t0 + 0.15, color=(160, 240, 150))
    pildora(fr, t, TITULOS["arboles"]["subtitulo"], (40, 150, 70), E["a_mas"])
    return fr


# ======================================================= íconos del cierre
def _icono_nutrias(c, x, y, s, t):
    k = 0.27 * s
    m = (x, y - 16 * s)
    nutria(c, x - 46 * s, y + 6 * s, t, k, 1, m)
    nutria(c, x + 46 * s, y + 6 * s, t, k, -1, m, 1.3)
    patitas(c, m, k)


def _icono_rayo(c, x, y, s, t):
    icono_rayo(c, x, y, 1.35 * s)


def _icono_arboles(c, x, y, s, t):
    r = 62 * s
    for ang in ARBOLES_1[::2]:
        a = math.radians(ang)
        arbolito(c, x + (r - 3) * math.cos(a), y + 14 * s + (r - 3) * math.sin(a), a, 0.55 * s)
    return [(sprite_tierra(int(r), t), x, y + 14 * s)]


ICONOS = [_icono_nutrias, _icono_rayo, _icono_arboles]
ESCENAS = {"nutrias": escena_nutrias, "rayo": escena_rayo, "arboles": escena_arboles}
