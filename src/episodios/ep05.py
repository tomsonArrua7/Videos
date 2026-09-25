"""Episodio 5: curiosidades de series (voz de Tomás, Argentina).

Las imágenes usan objetos y guiños genéricos (un barril, una página de guion,
una fuente), nunca personajes o logos con derechos de autor.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

from dibujo import (TINTA, H, W, Capa, a_imagen, cartel, chispas, componer, e_back, e_out, encabezado,
                    gradiente, lerp, parpadeo, pildora, pop, prog, resplandor, sello, tachar, texto, tilde,
                    titulo, viñeta)

SLUG = "series"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
GANCHO_ETIQUETA = "DE SERIES"
PALABRAS_CIERRE = ("abajo", "seguinos")

# Guion escrito para el oído (ver episodio 4): frases cortas, números en
# palabras y nombres en inglés adaptados donde Whisper no los entendía.
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades de series que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE SERIES",
    },
    {
        "id": "chavo",
        "texto": "Uno: Chespirito tenía cuarenta y dos años cuando creó al Chavo. "
                 "¡Un nene de ocho años!",
        "titulo": "EL CHAVO DEL 8",
        "subtitulo": "¡34 AÑOS DE DIFERENCIA!",
    },
    {
        "id": "breaking",
        "texto": "Dos: en {Breaking Bad|Bréikin Bad}, {Jesse Pinkman|Yési Pínc man} iba a morir en la "
                 "primera temporada. ¡Pero el actor era tan bueno que lo dejaron hasta el final!",
        "titulo": "BREAKING BAD",
        "subtitulo": "JESSE IBA A MORIR",
    },
    {
        "id": "fuente",
        "texto": "Tres: la famosa fuente de {Friends|Fréns} no está en Nueva York. "
                 "¡Está en un estudio de California!",
        "titulo": "FRIENDS",
        "subtitulo": "¡ES UN SET DE FILMACIÓN!",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"chavo": (230, 150, 60), "breaking": (60, 170, 90),
          "fuente": (80, 170, 230), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
PARED, PISO = 640, 1380
DESIERTO = 1000


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "c_cuarenta": L.palabra("chavo", "cuarenta"),
        "c_anios": L.fin_palabra("chavo", "años"),
        "c_chavo": L.palabra("chavo", "chavo"),
        "c_nene": L.palabra("chavo", "nene"),
        "c_ocho": L.palabra("chavo", "ocho"),
        "b_jesse": L.palabra("breaking", "jesse"),
        "b_morir": L.palabra("breaking", "morir"),
        "b_actor": L.palabra("breaking", "actor"),
        "b_dejaron": L.palabra("breaking", "dejaron"),
        "b_final": L.palabra("breaking", "final"),
        "f_fuente": L.palabra("fuente", "fuente"),
        "f_york": L.palabra("fuente", "york"),
        "f_estudio": L.palabra("fuente", "estudio"),
        "f_california": L.palabra("fuente", "california"),
    }


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    fx = [(E["c_cuarenta"] - 0.1, S.pop(900, 400), 0.30), (E["c_chavo"], S.pop(600, 900), 0.20),
          (E["c_ocho"], S.pop(1000, 500), 0.30), (E["c_nene"] + 0.5, S.ding(), 0.22)]
    t = E["c_cuarenta"]
    while t < E["c_anios"]:
        fx.append((t, S.tic(), 0.15))
        t += 0.06
    fx += [(E["b_morir"], S.marcador(0.45), 0.22), (E["b_actor"], S.brillo_sfx(), 0.22),
           (E["b_dejaron"], S.marcador(0.35), 0.22), (E["b_dejaron"] + 0.35, S.golpe(), 0.45),
           (E["b_final"], S.pop(600, 250), 0.22)]
    ini, fin = E["fuente_ini"], E["cierre_ini"]
    fx += [(ini, S.lluvia(fin - ini), 0.06),
           (E["f_york"], S.pop(700, 300), 0.25), (E["f_york"] + 0.35, S.error_(), 0.25),
           (E["f_estudio"], S.golpe(), 0.30), (E["f_estudio"] + 0.02, S.clic(), 0.45),
           (E["f_california"], S.pop(800, 400), 0.25), (E["f_california"] + 0.3, S.ding(), 0.22)]
    return fx


def sacudidas(E):
    return [(E["b_dejaron"] + 0.35, 10, 0.25)]


# ==================================================================== fondos
def fondo_chavo():
    a = gradiente([(0, (120, 190, 240)), (PARED / H - 0.001, (196, 228, 246)), (PARED / H, (222, 176, 110)),
                   (PISO / H - 0.001, (206, 158, 94)), (PISO / H, (176, 168, 150)), (1, (140, 132, 116))])
    viñeta(a, 0.35)
    img = a_imagen(a, 30)
    c = Capa(0, PARED - 30, W, H - PARED + 30)
    c.rrect(-20, PARED - 30, W + 20, PARED + 16, 8, fill=(170, 80, 50))
    for x in range(-20, W + 40, 44):
        c.arco(x, PARED - 8, 22, 18, 180, 360, (130, 56, 36), 4)
    for fila_, y in enumerate(range(PARED + 50, PISO, 60)):
        c.linea([(0, y), (W, y)], (200, 150, 90), 3, puntas=False)
        for x in range(-60 + 60 * (fila_ % 2), W, 120):
            c.linea([(x, y), (x, y + 60)], (200, 150, 90), 3, puntas=False)
    for x, num in ((230, "71"), (850, "72")):
        c.rrect(x - 110, PISO - 420, x + 110, PISO, 10, fill=(120, 70, 40), borde=(70, 40, 20), grosor=6)
        c.rrect(x - 70, PISO - 360, x + 70, PISO - 250, 6, fill=(170, 210, 230), borde=(70, 40, 20), grosor=5)
        c.circulo(x + 80, PISO - 200, 10, fill=(230, 190, 80))
    for y in range(PISO + 40, H, 90):
        c.linea([(0, y), (W, y)], (150, 142, 126), 3, puntas=False)
    c.pegar_en(img)
    for x, num in ((230, "71"), (850, "72")):
        componer(img, texto(num, "negra", 40, color=(250, 230, 180)), x, PISO - 390)
    return img


def fondo_breaking():
    a = gradiente([(0, (110, 180, 232)), (DESIERTO / H - 0.001, (250, 224, 176)), (DESIERTO / H, (232, 190, 124)),
                   (1, (196, 146, 84))])
    resplandor(a, 860, 560, 300, (255, 250, 220), 0.45)
    img = a_imagen(a, 31)
    c = Capa(0, 760, W, H - 760)
    for x0, x1, alto, col in ((-40, 330, 150, (196, 116, 76)), (600, 960, 110, (206, 128, 84)),
                              (880, 1140, 180, (184, 104, 70))):
        c.poligono([(x0, DESIERTO + 2), (x0 + 40, DESIERTO - alto), (x1 - 40, DESIERTO - alto), (x1, DESIERTO + 2)],
                   fill=col)
        c.poligono([(x1 - 40, DESIERTO - alto), (x1, DESIERTO + 2), (x1 - 70, DESIERTO + 2), (x1 - 90, DESIERTO - alto)],
                   fill=tuple(int(v * 0.8) for v in col))
    # casa rodante a lo lejos
    c.rrect(440, DESIERTO - 44, 560, DESIERTO - 6, 8, fill=(240, 236, 226), borde=(120, 110, 100), grosor=3)
    c.rrect(450, DESIERTO - 36, 480, DESIERTO - 22, 3, fill=(120, 150, 170))
    for wx in (465, 535):
        c.circulo(wx, DESIERTO - 4, 7, fill=(40, 40, 40))
    for cx, cy, e in ((90, 1480, 1.0), (1010, 1560, 1.2), (180, 1780, 0.8)):
        V = (70, 140, 80)
        c.rrect(cx - 24 * e, cy - 200 * e, cx + 24 * e, cy + 60 * e, 24 * e, fill=V, borde=(30, 80, 40), grosor=4)
        for s in (-1, 1):
            c.linea([(cx + s * 20 * e, cy - 40 * e), (cx + s * 70 * e, cy - 50 * e), (cx + s * 70 * e, cy - 120 * e)],
                    (30, 80, 40), 36 * e)
            c.linea([(cx + s * 20 * e, cy - 40 * e), (cx + s * 70 * e, cy - 50 * e), (cx + s * 70 * e, cy - 120 * e)],
                    V, 28 * e)
    c.pegar_en(img)
    return img


def fondo_fuente():
    a = gradiente([(0, (110, 176, 240)), (0.5, (196, 226, 250)), (0.62, (210, 204, 190)), (1, (170, 160, 146))])
    img = a_imagen(a, 32)
    c = Capa(0, 780, W, 440)
    # fachadas de estudio (edificios de mentira)
    for x0, ancho, alto, col in ((-20, 260, 380, (168, 86, 64)), (230, 220, 300, (150, 110, 90)),
                                 (840, 260, 360, (160, 80, 70)), (640, 220, 260, (176, 120, 90))):
        c.rrect(x0, 1190 - alto, x0 + ancho, 1190, 4, fill=col)
        for fy in range(1190 - alto + 30, 1170, 70):
            for fx in range(x0 + 25, x0 + ancho - 40, 60):
                c.rrect(fx, fy, fx + 34, fy + 44, 3, fill=(90, 110, 140))
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(chavo=fondo_chavo(), breaking=fondo_breaking(), fuente=fondo_fuente())


# ================================================================ elementos
def barril(c, x, y, t, k=1.0, espia=0.0):
    """Barril de madera con alguien que espía desde adentro."""
    MADERA, OSC, AROS, B = (176, 116, 62), (140, 88, 44), (90, 96, 110), (70, 40, 20)

    def P(dx, dy):
        return (x + dx * k, y + dy * k)

    ancho = [128 + 16 * math.sin(math.pi * u) for u in np.linspace(0, 1, 20)]
    lados = [P(-a, -170 + 340 * i / 19) for i, a in enumerate(ancho)]
    lados += [P(a, -170 + 340 * i / 19) for i, a in reversed(list(enumerate(ancho)))]
    c.poligono(lados, fill=MADERA, borde=B, grosor=6 * k)
    for dx in (-96, -48, 0, 48, 96):
        c.linea([P(dx * 0.95, -165), P(dx * 1.08, 0), P(dx * 0.95, 165)], OSC, 5 * k)
    for dy in (-110, 110):
        c.arco(*P(0, dy - 14), 142 * k, 30 * k, 10, 170, AROS, 16 * k)
    c.elipse(*P(0, -170), 128 * k, 30 * k, fill=(40, 24, 14), borde=B, grosor=6 * k)
    # ojitos que espían desde adentro
    if espia > 0:
        mira = 10 * math.sin(t * 1.7)
        abre = parpadeo(t, 2.4)
        for s in (-1, 1):
            ex, ey = P(s * 28 + mira, -178 - 14 * espia)
            c.elipse(ex, ey, 17 * k, 15 * k * espia * abre, fill=(255, 255, 255), borde=B, grosor=3 * k)
            c.elipse(ex + mira * 0.4 * k, ey + 3 * k, 7 * k, 7 * k * espia * abre, fill=(30, 20, 20))
    # tapa levantada
    c.elipse(*P(-30, -206 - 20 * espia), 120 * k, 24 * k, fill=MADERA, borde=B, grosor=6 * k)
    c.linea([P(-130, -206 - 20 * espia), P(70, -206 - 20 * espia)], OSC, 4 * k)


@lru_cache(maxsize=64)
def pagina_guion(tachado, marca, quedan):
    """Página de guion con la línea 'JESSE MUERE.' (tachado y marca: 0..10 en décimos)."""
    w, h = 560, 700
    c = Capa(0, 0, w + 20, h + 24, ss=2)
    c.rrect(10, 18, w + 10, h + 18, 10, fill=(20, 10, 0, 110))
    c.rrect(10, 10, w + 10, h + 10, 10, fill=(252, 250, 244), borde=(190, 180, 160), grosor=3)
    for i, (y, largo) in enumerate([(200, 0.8), (240, 0.65), (280, 0.75), (430, 0.7), (470, 0.55),
                                    (560, 0.8), (600, 0.6), (640, 0.7)]):
        c.rrect(60, y, 60 + (w - 100) * largo, y + 14, 6, fill=(200, 200, 206))
    if marca:
        c.rrect(56, 322, 56 + 420 * marca / 10, 392, 14, fill=(255, 236, 110))
    if tachado:
        c.linea([(52, 360), (52 + 440 * tachado / 10, 350)], (220, 30, 40), 14)
    im = c.imagen()
    for txt, fuente, tam, color, pos in (("GUION · TEMPORADA 1", "negra", 30, TINTA, (60, 60)),
                                         ("EPISODIO 7 (FINAL)", "negra", 24, (120, 120, 130), (60, 110)),
                                         ("JESSE:", "negra", 28, TINTA, (60, 160))):
        im.alpha_composite(texto(txt, fuente, tam, color=color), pos)
    if quedan:
        im.alpha_composite(texto("JESSE MUERE.", "titulo", 64, color=(200, 20, 40)), (66, 318))
    return im


def fuente_agua(c, x, y, t, k=1.0):
    PIEDRA, OSC, AGUA, B = (200, 198, 206), (150, 148, 160), (96, 176, 232), (80, 80, 100)

    def P(dx, dy):
        return (x + dx * k, y + dy * k)

    c.elipse(*P(0, 90), 330 * k, 70 * k, fill=OSC, borde=B, grosor=6 * k)
    c.elipse(*P(0, 76), 300 * k, 54 * k, fill=AGUA)
    for i in range(3):  # ondas en el agua
        q = ((t * 0.7) + i / 3) % 1
        c.elipse(*P(0, 76), (90 + 200 * q) * k, (16 + 36 * q) * k, borde=(220, 240, 255, int(200 * (1 - q))),
                 grosor=3 * k)
    c.rrect(*P(-34, -150), *P(34, 76), 12 * k, fill=PIEDRA, borde=B, grosor=5 * k)
    for bowl_y, rx, ry in ((-150, 170, 34), (-290, 80, 18)):
        # cortina de agua que cae del borde
        for s in (-1, 1):
            for j in range(3):
                pts = []
                for u in np.linspace(0, 1, 12):
                    dx = s * (rx - 8 + 50 * u + 10 * j)
                    dy = bowl_y + 6 + (u ** 2) * (230 if bowl_y > -200 else 130)
                    pts.append(P(dx, dy))
                c.linea(pts, (170, 220, 255, 170), 6 * k)
        c.elipse(*P(0, bowl_y), rx * k, ry * k, fill=PIEDRA, borde=B, grosor=5 * k)
        c.elipse(*P(0, bowl_y - 4), (rx - 16) * k, (ry - 9) * k, fill=AGUA)
    c.rrect(*P(-16, -330), *P(16, -290), 6 * k, fill=PIEDRA, borde=B, grosor=4 * k)
    for i in range(14):  # chorro de arriba
        u = ((t * 1.3) + i / 14) % 1
        s = -1 if i % 2 else 1
        c.circulo(*P(s * 70 * u, -336 - 120 * u + 190 * u * u), 5 * k * (1 - 0.4 * u), fill=(190, 230, 255))


def cartel_lugar(c, x, y, s, icono, t):
    """Cartel en un poste; `icono` dibuja algo arriba del texto."""
    c.linea([(x, y + 40 * s), (x, y + 260 * s)], (110, 90, 70), 14 * s)
    c.rrect(x - 150 * s, y - 110 * s, x + 150 * s, y + 60 * s, 18 * s, fill=(250, 248, 240), borde=(60, 60, 80),
            grosor=6 * s)
    icono(c, x, y - 40 * s, s, t)


def icono_nueva_york(c, x, y, s, t):
    for dx, alto, ancho in ((-90, 70, 34), (-50, 110, 30), (-12, 80, 36), (26, 140, 24), (62, 90, 34)):
        c.rrect(x + dx * s, y + (40 - alto) * s, x + (dx + ancho) * s, y + 40 * s, 3 * s, fill=(80, 96, 130))
    c.poligono([(x + 38 * s, y - 100 * s), (x + 34 * s, y - 130 * s), (x + 30 * s, y - 100 * s)], fill=(80, 96, 130))


def icono_california(c, x, y, s, t):
    c.circulo(x + 60 * s, y - 40 * s, 30 * s, fill=(255, 196, 60))
    tronco = [(x - 20 * s, y + 40 * s), (x - 10 * s, y - 10 * s), (x + 4 * s, y - 60 * s)]
    c.linea(tronco, (140, 96, 50), 14 * s)
    for a in (-2.6, -2.0, -1.2, -0.5, 0.2):
        hx, hy = x + 4 * s, y - 60 * s
        ex, ey = hx + 64 * s * math.cos(a), hy + 40 * s * math.sin(a) + 20 * s
        c.linea([(hx, hy), ((hx + ex) / 2, (hy + ey) / 2 - 16 * s), (ex, ey)], (60, 150, 70), 12 * s)


def claqueta(c, x, y, s, abre):
    B = (20, 20, 24)
    c.rrect(x - 110 * s, y - 20 * s, x + 110 * s, y + 110 * s, 8 * s, fill=(30, 30, 36), borde=(240, 240, 240),
            grosor=4 * s)
    a = -math.radians(28 * abre)
    base = (x - 110 * s, y - 20 * s)
    pts = []
    for dx, dy in ((0, 0), (220, 0), (220, -34), (0, -34)):
        dx, dy = dx * s, dy * s
        pts.append((base[0] + dx * math.cos(a) - dy * math.sin(a), base[1] + dx * math.sin(a) + dy * math.cos(a)))
    c.poligono(pts, fill=(240, 240, 240), borde=B, grosor=3 * s)
    for i in range(5):
        u0, u1 = i / 5, i / 5 + 0.1
        q = [pts[0][0] + (pts[1][0] - pts[0][0]) * u0, pts[0][1] + (pts[1][1] - pts[0][1]) * u0]
        r = [pts[0][0] + (pts[1][0] - pts[0][0]) * u1, pts[0][1] + (pts[1][1] - pts[0][1]) * u1]
        c.poligono([tuple(q), tuple(r), (r[0] + (pts[3][0] - pts[0][0]), r[1] + (pts[3][1] - pts[0][1])),
                    (q[0] + (pts[3][0] - pts[0][0]), q[1] + (pts[3][1] - pts[0][1]))], fill=B)
    for i in range(3):
        c.rrect(x - 90 * s, y + (15 + 30 * i) * s, x + 90 * s, y + (22 + 30 * i) * s, 3 * s, fill=(200, 200, 210))


# =================================================================== escenas
def escena_chavo(t):
    fr = FONDOS["chavo"].copy()
    t0 = ESC["chavo"]["escena_ini"]
    c = Capa(300, 900, 480, 520)
    espia = e_out(prog(t, E["c_chavo"] - 0.2, 0.5))
    barril(c, 540, 1200 + 4 * math.sin(t * 2), t, 1.1 * e_back(prog(t, t0 + 0.2, 0.5)), espia)
    c.pegar_en(fr)
    s = pop(t, E["c_cuarenta"] - 0.1, 0.4)
    if s > 0:
        n = int(round(42 * e_out(prog(t, E["c_cuarenta"], E["c_anios"] - E["c_cuarenta"] + 0.2))))
        componer(fr, cartel(f"{n} AÑOS", "EL ACTOR", (255, 214, 10), (70, 30, 6), 420, 96), 285, 680, escala=s,
                 rot=-3)
    s = pop(t, E["c_ocho"], 0.4)
    if s > 0:
        componer(fr, cartel("8 AÑOS", "EL PERSONAJE", (120, 230, 140), (10, 60, 30), 420, 96), 800, 680,
                 escala=s, rot=3)
    encabezado(fr, t, 1, E["chavo_badge"])
    titulo(fr, t, TITULOS["chavo"]["titulo"], t0 + 0.15, color=(255, 236, 170))
    pildora(fr, t, TITULOS["chavo"]["subtitulo"], (200, 90, 30), E["c_nene"] + 0.35)
    return fr


def escena_breaking(t):
    fr = FONDOS["breaking"].copy()
    t0 = ESC["breaking"]["escena_ini"]
    marca = int(10 * e_out(prog(t, E["b_morir"], 0.4)))
    tachado = int(10 * e_out(prog(t, E["b_dejaron"], 0.35)))
    s = e_back(prog(t, t0 + 0.2, 0.5))
    if s > 0:
        componer(fr, pagina_guion(tachado, marca, t >= E["b_morir"] - 0.05), 540, 1070, escala=s, rot=-2)
    sa = pop(t, E["b_actor"], 0.4)
    if sa > 0:
        componer(fr, cartel("¡GRAN ACTUACIÓN!", None, (255, 214, 10), (40, 30, 10), 360, 56), 820, 690,
                 escala=sa * (1 + 0.04 * math.sin(t * 7)), rot=6)
        chispas(fr, t, E["b_actor"], 820, 690, n=14, seed=9, vel=(250, 550), grav=300, dur=0.9)
    if t >= E["b_dejaron"] + 0.35:
        p = prog(t, E["b_dejaron"] + 0.35, 0.22)
        componer(fr, sello("¡SE QUEDA!", (34, 150, 70), 96), 560, 1120, escala=lerp(2.2, 1.0, e_out(p)),
                 rot=-12, alpha=min(1.0, p * 3))
    encabezado(fr, t, 2, E["breaking_badge"])
    titulo(fr, t, TITULOS["breaking"]["titulo"], t0 + 0.15, color=(170, 240, 170))
    pildora(fr, t, TITULOS["breaking"]["subtitulo"], (180, 40, 50), E["b_morir"], hasta=E["b_final"] - 0.1)
    pildora(fr, t, "¡HASTA EL ÚLTIMO CAPÍTULO!", (30, 130, 70), E["b_final"])
    return fr


def escena_fuente(t):
    fr = FONDOS["fuente"].copy()
    t0 = ESC["fuente"]["escena_ini"]
    # reflectores del estudio
    luz = e_out(prog(t, E["f_estudio"], 0.4))
    c = Capa(0, 560, W, 1000)
    if luz > 0:
        for x, d in ((80, 1), (1000, -1)):
            c.poligono([(x, 1380), (x + d * 420, 1080), (x + d * 520, 1260)], fill=(255, 250, 200, int(70 * luz)))
    fuente_agua(c, 540, 1230, t, 1.15 * e_back(prog(t, t0 + 0.15, 0.5)))
    if luz > 0:
        for x, d in ((80, 1), (1000, -1)):
            c.linea([(x, 1540), (x, 1400)], (40, 40, 50), 10)
            c.linea([(x - 40, 1540), (x, 1460), (x + 40, 1540)], (40, 40, 50), 8)
            c.rrect(x - 40, 1340, x + 40, 1410, 12, fill=(50, 50, 60), borde=(20, 20, 30), grosor=4)
            c.circulo(x + d * 36, 1375, 26 * luz, fill=(255, 250, 210))
    c.pegar_en(fr)
    # carteles: Nueva York (no) y California (sí)
    s = pop(t, E["f_york"] - 0.1, 0.4)
    if s > 0:
        c = Capa(40, 520, 380, 440)
        cartel_lugar(c, 230, 690, s, icono_nueva_york, t)
        tachar(c, 230, 640, 230, e_back(prog(t, E["f_york"] + 0.35, 0.3)), 24)
        c.pegar_en(fr)
        componer(fr, texto("NUEVA YORK", "negra", 34, color=TINTA), 230, 725, escala=s)
    s = pop(t, E["f_california"], 0.4)
    if s > 0:
        c = Capa(660, 520, 380, 440)
        cartel_lugar(c, 850, 690, s, icono_california, t)
        tilde(c, 930, 610, 120, e_back(prog(t, E["f_california"] + 0.3, 0.3)), 22)
        c.pegar_en(fr)
        componer(fr, texto("CALIFORNIA", "negra", 34, color=TINTA), 850, 725, escala=s)
    s = pop(t, E["f_estudio"], 0.35)
    if s > 0:
        c = Capa(400, 740, 280, 260)
        claqueta(c, 540, 840, s, 1 - e_out(prog(t, E["f_estudio"] + 0.1, 0.15)))
        c.pegar_en(fr)
    encabezado(fr, t, 3, E["fuente_badge"])
    titulo(fr, t, TITULOS["fuente"]["titulo"], t0 + 0.15, color=(190, 230, 255))
    pildora(fr, t, TITULOS["fuente"]["subtitulo"], (40, 110, 200), E["f_estudio"])
    return fr


# ======================================================= íconos del cierre
def _icono_chavo(c, x, y, s, t):
    barril(c, x, y + 30 * s, t, 0.4 * s, 1.0)


def _icono_breaking(c, x, y, s, t):
    return [(_mini_pagina(), x, y)] if s > 0.05 else []


@lru_cache(None)
def _mini_pagina():
    im = pagina_guion(10, 10, True)
    return im.resize((int(im.width * 0.3), int(im.height * 0.3)), Image.LANCZOS)


def _icono_fuente(c, x, y, s, t):
    fuente_agua(c, x, y + 26 * s, t, 0.32 * s)


ICONOS = [_icono_chavo, _icono_breaking, _icono_fuente]
ESCENAS = {"chavo": escena_chavo, "breaking": escena_breaking, "fuente": escena_fuente}
