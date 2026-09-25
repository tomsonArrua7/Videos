"""Episodio 12: quiz de series — cinco preguntas sobre series muy conocidas.

Las piezas del quiz están en quiz.py; acá van las preguntas y los dibujos. Todo es genérico:
un semáforo, una pared con letras, una máscara, una caja de zapatos y una mano que camina.
Voz: grabaciones/ep12.* (o Tomás si falta).
"""
import math

import numpy as np

import quiz
from dibujo import (W, Capa, a_imagen, bezier, cartel, clamp, componer, e_back, e_in_out, gradiente, lerp, pop, prog,
                    rect_rot, resplandor, spr_brillo, spr_estrella, spr_resplandor, tachar, texto, viñeta)
from quiz import signo

SLUG = "quiz_series"
DURACION = 58.0                       # cinco preguntas con 3 s para pensar cada una
GRABACION = "grabaciones/ep12"
VOZ = "es-AR-TomasNeural"             # solo si falta la grabación
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
PALABRAS_CIERRE = ("abajo", "seguinos")
CIERRE_TITULO = ("¿CUÁNTAS", "ACERTASTE?")

BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Cinco preguntas de series, tres segundos cada una! ¿Cuántas acertás?",
        "titulo": "5 PREGUNTAS",
    },
    {
        "id": "s1",
        "texto": "Uno: en El juego del calamar, ¿cuál es el primer juego? [3s] "
                 "¡Luz roja, luz verde! Si te movías en rojo, quedabas afuera.",
        "titulo": "EL PRIMER JUEGO",
        "pregunta": "En El juego del calamar, ¿cuál es el primer juego?",
        "opciones": ["LAS ESCONDIDAS", "LUZ ROJA, LUZ VERDE", "LA MANCHA"],
        "correcta": 1,
    },
    {
        "id": "s2",
        "texto": "Dos: en {Stranger Things|Estréinyer Zings}, ¿cómo le habla {Will|Uil} a su mamá desde el Mundo del "
                 "Revés? [3s] ¡Con luces de Navidad! Prendía una por cada letra.",
        "titulo": "LAS LUCES",
        "pregunta": "En Stranger Things, ¿cómo le habla Will a su mamá desde el Mundo del Revés?",
        "opciones": ["CON LUCES DE NAVIDAD", "CON UNA RADIO", "CON CARTAS"],
        "correcta": 0,
    },
    {
        "id": "s3",
        "texto": "Tres: en La casa de papel, ¿de quién es la cara de las máscaras? [3s] "
                 "¡De Dalí! El pintor del bigote famoso.",
        "titulo": "LA MÁSCARA",
        "pregunta": "En La casa de papel, ¿de quién es la cara de las máscaras?",
        "opciones": ["PICASSO", "EINSTEIN", "DALÍ"],
        "correcta": 2,
    },
    {
        "id": "s4",
        "texto": "Cuatro: en Casados con hijos, ¿de qué trabaja Pepe Argento? [3s] "
                 "¡Vende zapatos! Y siempre se queja de su trabajo.",
        "titulo": "EL TRABAJO",
        "pregunta": "En Casados con hijos, ¿de qué trabaja Pepe Argento?",
        "opciones": ["TAXISTA", "VENDEDOR DE ZAPATOS", "CARNICERO"],
        "correcta": 1,
    },
    {
        "id": "s5",
        "texto": "Cinco: en Merlina, ¿cómo se llama la mano que la acompaña? [3s] ¡Dedos! Una mano que camina sola.",
        "titulo": "LA MANO",
        "pregunta": "En Merlina, ¿cómo se llama la mano que la acompaña?",
        "opciones": ["DEDOS", "MANITO", "GARRA"],
        "correcta": 0,
    },
    {
        "id": "cierre",
        "texto": "¿Cuántas acertaste? Comentalo abajo y seguinos para más.",
        "titulo": "¿CUÁNTAS ACERTASTE?",
    },
]

PREGUNTAS = ["s1", "s2", "s3", "s4", "s5"]
ACENTO = {"s1": (240, 60, 130), "s2": (200, 40, 40), "s3": (215, 165, 30), "s4": (160, 100, 55),
          "s5": (110, 110, 140), "cierre": (255, 0, 110)}
POR_ID = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
TINTA = (24, 16, 48)


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        **quiz.eventos(L, PREGUNTAS),
        **quiz.eventos_gancho(L, "cinco", "series"),
        "s1_movias": L.palabra("s1", "movías"),
        "s1_afuera": L.palabra("s1", "afuera"),
        "s2_letra": L.palabra("s2", "letra"),
        "s3_pintor": L.palabra("s3", "pintor"),
        "s3_bigote": L.palabra("s3", "bigote"),
        "s4_queja": L.palabra("s4", "queja"),
        "s5_camina": L.palabra("s5", "camina"),
    }


def efectos(E, L, S):
    fx = quiz.efectos(E, S, PREGUNTAS) + quiz.efectos_gancho(E, S)
    tr = {q: E[f"{q}_revela"] for q in PREGUNTAS}
    fx += [(tr["s1"], S.error_(), 0.12), (E["s1_afuera"], S.poof(), 0.25)]
    for i in range(len(PALABRA_LUCES)):
        fx.append((tr["s2"] + 0.1 + 0.38 * i, S.pop(1300, 900, 0.07), 0.2))
    fx += [(tr["s3"] + 0.05, S.brillo_sfx(), 0.2), (E["s3_bigote"], S.subida(0.35, 500, 1200), 0.12),
           (tr["s4"] + 0.05, S.pop(500, 200, 0.15), 0.3), (E["s4_queja"], S.golpe(), 0.25)]
    for i in range(6):
        fx.append((E["s5_camina"] + 0.2 * i, S.tic(), 0.35))
    return fx


def sacudidas(E):
    return quiz.sacudidas_gancho(E) + [(E["s4_queja"], 10, 0.25)]


def momento_portada(E):
    return E["gq_acertas"] + 0.7


# ==================================================================== fondos
def fondo_gancho():
    a = gradiente([(0, (16, 30, 70)), (0.5, (30, 110, 140)), (1, (240, 60, 130))])
    resplandor(a, 540, 1000, 620, (160, 240, 255), 0.3)
    viñeta(a)
    return a_imagen(a, 100)


def fondo_patio():
    a = gradiente([(0, (250, 190, 210)), (0.62, (255, 222, 232)), (0.63, (226, 196, 150)), (1, (206, 170, 120))])
    img = a_imagen(a, 101)
    c = Capa(0, 0, W, 1920, ss=1)
    for x in range(-200, W + 200, 160):   # paredes pintadas con cielo
        c.circulo(x, 300, 60, fill=(255, 255, 255, 70))
    c.pegar_en(img)
    return img


def fondo_living():
    a = gradiente([(0, (70, 56, 40)), (0.7, (96, 78, 56)), (1, (60, 44, 30))])
    img = a_imagen(a, 102)
    c = Capa(0, 0, W, 1920, ss=1)
    for x in range(0, W, 90):   # empapelado de rayas
        c.linea([(x, 0), (x, 1920)], (120, 100, 70, 90), 20, puntas=False)
    c.pegar_en(img)
    return img


def fondo_boveda():
    a = gradiente([(0, (70, 8, 16)), (0.6, (130, 20, 30)), (1, (60, 6, 12))])
    resplandor(a, 540, 760, 520, (255, 120, 100), 0.3)
    viñeta(a, 0.5)
    return a_imagen(a, 103)


def fondo_zapateria():
    a = gradiente([(0, (250, 226, 190)), (0.74, (240, 210, 170)), (0.745, (130, 80, 50)), (1, (100, 60, 36))])
    img = a_imagen(a, 104)
    c = Capa(0, 0, W, 1920, ss=1)
    for y in (560, 1000, 1400):   # estantes con cajas
        c.rrect(0, y, W, y + 18, 4, fill=(150, 100, 60, 150))
        for i, x in enumerate(range(30, W, 150)):
            if (i + y // 100) % 3:
                col = [(220, 120, 60, 110), (80, 120, 180, 110), (200, 60, 70, 110)][i % 3]
                c.rrect(x, y - 80, x + 120, y, 6, fill=col)
    c.pegar_en(img)
    return img


def fondo_gotico():
    a = gradiente([(0, (16, 14, 26)), (0.6, (40, 36, 58)), (1, (20, 18, 30))])
    resplandor(a, 830, 560, 170, (230, 230, 255), 0.5)
    img = a_imagen(a, 105)
    rng = np.random.default_rng(106)
    for _ in range(50):
        componer(img, spr_estrella(int(rng.integers(2, 5))), rng.uniform(0, W), rng.uniform(0, 1300),
                 alpha=rng.uniform(0.2, 0.6))
    c = Capa(0, 0, W, 1920, ss=1)
    c.circulo(830, 560, 90, fill=(236, 236, 250))
    for i in range(12):   # piso a cuadros blanco y negro
        for j in range(4):
            if (i + j) % 2 == 0:
                c.rrect(i * 90, 1440 + j * 120, i * 90 + 90, 1440 + j * 120 + 120, 0, fill=(230, 230, 240, 60))
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(gancho=fondo_gancho(), patio=fondo_patio(), living=fondo_living(), boveda=fondo_boveda(),
                  zapateria=fondo_zapateria(), gotico=fondo_gotico())


# ================================================================ 1 · semáforo
def semaforo(c, x, y, k, rojo):
    c.rrect(x - 14 * k, y + 150 * k, x + 14 * k, y + 330 * k, 6 * k, fill=(70, 70, 80))
    c.rrect(x - 78 * k, y - 170 * k, x + 78 * k, y + 170 * k, 34 * k, fill=(40, 40, 50), borde=(20, 20, 26),
            grosor=6 * k)
    c.circulo(x, y - 78 * k, 56 * k, fill=(240, 50, 60) if rojo else (80, 30, 34))
    c.circulo(x, y + 78 * k, 56 * k, fill=(60, 220, 110) if not rojo else (26, 70, 40))


def jugador(c, x, y, k, color):
    c.circulo(x, y - 62 * k, 24 * k, fill=(250, 214, 180))
    c.rrect(x - 30 * k, y - 36 * k, x + 30 * k, y + 40 * k, 20 * k, fill=color)
    c.rrect(x - 26 * k, y + 30 * k, x + 26 * k, y + 70 * k, 10 * k, fill=color)
    c.rrect(x - 14 * k, y - 30 * k, x + 14 * k, y - 14 * k, 4 * k, fill=(255, 255, 255))


def dibujo_semaforo(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    rojo = t >= tr
    c = Capa(0, 480, W, 540)
    semaforo(c, 190, 700, 0.95 * s, rojo)
    tm, ta = E["s1_movias"], E["s1_afuera"]
    for i, x in enumerate((420, 560, 700, 840, 960)):
        mueve = not rojo or (i == 2 and tm <= t < ta)   # uno se mueve en rojo...
        paso = math.sin(t * 9 + i) if mueve else 0
        y = 900 + 8 * abs(paso)
        sale = e_in_out(prog(t, ta + 0.3, 0.6)) if i == 2 else 0   # ...y queda afuera
        if sale < 1:
            jugador(c, x + 4 * paso + 200 * sale, y, 0.95 * s * (1 - 0.3 * sale), (40, 130, 110))
        if i == 2 and t >= ta and sale < 1:
            tachar(c, x + 200 * sale, y - 20, 110, pop(t, ta, 0.25), 16)
    c.pegar_en(fr)
    if rojo:
        componer(fr, spr_resplandor(180, (255, 60, 70)), 190, 622, alpha=0.5 * (1 - prog(t, tr + 1.5, 0.5)))


# ============================================================ 2 · luces y letras
PALABRA_LUCES = "HOLA"
FILAS = ["ABCDEFGH", "IJKLMNOPQ", "RSTUVWXYZ"]
FOCOS = [(255, 70, 70), (255, 200, 60), (70, 210, 110), (80, 150, 255), (255, 120, 200)]


def dibujo_luces(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 500, W, 520)
    c.rrect(80, 560, 1000, 975, 18, fill=(236, 224, 196, int(255 * clamp(s))))
    # qué letra está prendida ahora
    k = int((t - tr - 0.1) / 0.38) if t >= tr + 0.1 else -1
    activa = PALABRA_LUCES[k] if 0 <= k < len(PALABRA_LUCES) else None
    todas = t >= tr + 0.1 + 0.38 * len(PALABRA_LUCES)
    pos = {}
    for f, fila in enumerate(FILAS):
        y = 640 + f * 125
        paso = 880 / len(fila)
        pts = [(100 + paso * (i + 0.5), y - 36 + 10 * math.sin(i * 1.3 + f)) for i in range(len(fila))]
        c.linea([(90, pts[0][1])] + pts + [(990, pts[-1][1])], (40, 50, 40), 4)
        for i, (px, py) in enumerate(pts):
            letra = fila[i]
            col = FOCOS[(i + f) % len(FOCOS)]
            prendida = letra == activa or (todas and (t * 3 + i + f) % 2 < 1)
            titila = t < tr and (t * 2.3 + i * 0.7 + f) % 5 < 0.12   # antes, alguna titila
            c.elipse(px, py + 8, 11, 15, fill=col if (prendida or titila) else tuple(v // 3 for v in col))
            pos[letra] = (px, py + 8, prendida)
    c.pegar_en(fr)
    for f, fila in enumerate(FILAS):
        for i, letra in enumerate(fila):
            px, py, prendida = pos[letra]
            if prendida:
                componer(fr, spr_resplandor(60, FOCOS[(i + f) % len(FOCOS)]), px, py, alpha=0.9)
            componer(fr, texto(letra, "titulo", 56, color=(40, 26, 22)), px, py + 58, escala=clamp(s))
    sl = pop(t, E["s2_letra"], 0.35)
    if sl > 0:
        componer(fr, cartel("H-O-L-A", None, (255, 236, 200), (120, 20, 20), 420, 100), 540, 770, escala=sl, rot=-3)


# ================================================================== 3 · máscara
def mascara(c, x, y, k, t, bigote):
    B = (140, 120, 110)
    c.elipse(x, y + 8 * k, 150 * k, 190 * k, fill=(20, 5, 10, 90))
    c.elipse(x, y, 150 * k, 190 * k, fill=(252, 246, 238), borde=B, grosor=5 * k)
    for s in (-1, 1):
        c.elipse(x + s * 58 * k, y - 40 * k, 34 * k, 22 * k, fill=(30, 20, 20))
        c.arco(x + s * 58 * k, y - 82 * k, 44 * k, 16 * k, 200, 340, (90, 60, 50), 8 * k)
        c.circulo(x + s * 86 * k, y + 50 * k, 26 * k, fill=(255, 170, 170, 150))
    c.poligono([(x, y - 20 * k), (x - 20 * k, y + 50 * k), (x + 16 * k, y + 52 * k)], fill=(236, 226, 214))
    c.arco(x, y + 88 * k, 64 * k, 36 * k, 15, 165, (150, 50, 50), 8 * k)
    # bigote enrulado: sube y se enrosca
    sube = 60 * bigote
    for s in (-1, 1):
        pts = bezier((x, y + 70 * k), (x + s * 60 * k, y + 76 * k), (x + s * 110 * k, y + 40 * k - sube * k),
                     (x + s * 120 * k, y - 30 * k - sube * k), 20)
        c.linea(pts, (40, 26, 20), 12 * k)
        ex, ey = pts[-1]
        c.arco(ex - s * 14 * k, ey, 14 * k, 14 * k, 180 if s > 0 else 0, 360 if s > 0 else 180, (40, 26, 20), 8 * k)


def billete(c, x, y, ang, k=1.0):
    c.poligono(rect_rot(x, y, 120 * k, 60 * k, ang), fill=(110, 170, 110), borde=(60, 110, 60), grosor=3)
    c.circulo(x, y, 14 * k, fill=(160, 210, 150))


def paleta(c, x, y, k):
    c.elipse(x, y, 90 * k, 66 * k, fill=(220, 180, 120), borde=(140, 100, 60), grosor=5 * k)
    c.circulo(x + 40 * k, y + 18 * k, 16 * k, fill=(120, 80, 40, 0), borde=(140, 100, 60), grosor=4 * k)
    for i, col in enumerate([(230, 50, 60), (60, 120, 230), (250, 210, 50), (60, 180, 90)]):
        a = math.radians(200 + i * 40)
        c.circulo(x + math.cos(a) * 55 * k, y + math.sin(a) * 34 * k, 13 * k, fill=col)
    c.linea([(x - 30 * k, y + 70 * k), (x + 70 * k, y - 60 * k)], (120, 70, 40), 10 * k)
    c.linea([(x + 60 * k, y - 48 * k), (x + 78 * k, y - 72 * k)], (40, 40, 40), 14 * k)


def dibujo_mascara(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 470, W, 550)
    rng = np.random.default_rng(12)
    for i in range(14):   # lluvia de billetes
        x0, v, a0 = rng.uniform(40, W - 40), rng.uniform(90, 160), rng.uniform(0, 6)
        y = 470 + ((rng.uniform(0, 550) + (t - ev["t0"]) * v) % 550)
        billete(c, x0 + 30 * math.sin(t + i), y, a0 + t * 0.8, 0.8)
    luz = e_in_out(prog(t, tr, 0.4))
    bg = E["s3_bigote"]
    bigote = e_back(prog(t, bg, 0.5)) if t >= bg else 0.3 * luz
    mascara(c, 540, 770, 1.0 * s, t, bigote)
    sp = e_back(prog(t, E["s3_pintor"], 0.4))
    if sp > 0:
        paleta(c, 860, 900, 0.9 * sp)
    c.pegar_en(fr)
    if luz < 1:   # antes de la respuesta, la máscara está en sombra
        c = Capa(380, 570, 320, 400)
        c.elipse(540, 770, 154, 194, fill=(30, 6, 12, int(235 * (1 - luz))))
        c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 770, 170)
    if t >= bg:
        for i, (x, y) in enumerate(((410, 740), (670, 740))):
            a = 0.5 + 0.5 * math.sin(t * 6 + i)
            componer(fr, spr_brillo(int(16 + 10 * a), (255, 240, 170)), x, y, alpha=a * clamp((t - bg) / 0.3))


# ================================================================ 4 · zapatos
def caja_zapatos(c, x, y, k, abre):
    c.rrect(x - 190 * k, y - 60 * k, x + 190 * k, y + 110 * k, 10 * k, fill=(230, 120, 50), borde=(140, 60, 20),
            grosor=6 * k)
    c.rrect(x - 170 * k, y - 40 * k, x + 170 * k, y + 90 * k, 6 * k, fill=(250, 236, 214))
    lx, ly, ang = x + 150 * abre * k, y - 70 * k - 170 * abre * k, -0.35 * abre
    c.poligono(rect_rot(lx, ly, 410 * k, 70 * k, ang), fill=(240, 140, 60), borde=(140, 60, 20), grosor=6 * k)


def zapato(c, x, y, k):
    M, B = (80, 44, 24), (40, 20, 10)
    c.poligono([(x - 150 * k, y + 40 * k), (x - 150 * k, y - 30 * k), (x - 90 * k, y - 60 * k), (x - 10 * k, y - 50 * k),
                (x + 60 * k, y - 20 * k), (x + 140 * k, y - 6 * k), (x + 160 * k, y + 20 * k), (x + 150 * k, y + 40 * k)],
               fill=M, borde=B, grosor=5 * k)
    c.rrect(x - 160 * k, y + 34 * k, x + 162 * k, y + 54 * k, 8 * k, fill=(40, 30, 26))
    c.rrect(x - 150 * k, y + 20 * k, x - 100 * k, y + 60 * k, 6 * k, fill=(40, 30, 26))
    for i in range(3):
        c.linea([(x - 10 * k + i * 22 * k, y - 48 * k + i * 8 * k), (x + 14 * k + i * 22 * k, y - 30 * k + i * 8 * k)],
                (230, 220, 200), 4 * k)
    c.arco(x + 40 * k, y - 14 * k, 60 * k, 20 * k, 200, 300, (160, 110, 80, 160), 5 * k)


def dibujo_zapatos(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    abre = e_in_out(prog(t, tr, 0.4))
    c = Capa(0, 480, W, 540)
    caja_zapatos(c, 540, 860, 1.0 * s, abre)
    sz = e_back(prog(t, tr + 0.15, 0.5))
    if sz > 0:
        zapato(c, 540, 820 - 90 * sz, 1.0 * sz)
    c.pegar_en(fr)
    if abre < 0.3:
        componer(fr, texto("?", "titulo", 110, color=(255, 255, 255), borde=9), 540, 795, escala=s,
                 alpha=1 - abre / 0.3)
    tq = E["s4_queja"]
    sq = pop(t, tq, 0.35)
    if sq > 0:   # la queja: un globo con insultos de historieta
        c = Capa(560, 470, 460, 260)
        c.elipse(790, 580, 190, 80, fill=(255, 255, 255), borde=TINTA, grosor=6)
        c.poligono([(700, 640), (650, 710), (760, 648)], fill=(255, 255, 255), borde=TINTA, grosor=6)
        c.elipse(790, 580, 184, 74, fill=(255, 255, 255))
        c.pegar_en(fr)
        componer(fr, texto("¡#@$%!", "titulo", 76, color=(220, 40, 50)), 790, 582, escala=sq,
                 rot=4 * math.sin((t - tq) * 20) * math.exp(-(t - tq) * 3))


# ============================================================ 5 · la mano
def mano(c, x, y, k, t, anda):
    """Mano parada sobre la punta de los dedos; `anda` mueve los dedos como patas."""
    P, B = (236, 228, 214), (120, 110, 100)
    for i, dx in enumerate((-48, -16, 16, 48)):
        fase = math.sin(t * 12 + i * 1.6) * anda
        rodilla = (x + dx * k + 10 * fase * k, y + 70 * k)
        punta = (x + dx * k + 26 * fase * k, y + 140 * k - 10 * max(0, fase) * k)
        c.linea([(x + dx * k, y + 20 * k), rodilla, punta], B, 34 * k)
        c.linea([(x + dx * k, y + 20 * k), rodilla, punta], P, 24 * k)
    c.rrect(x - 74 * k, y - 60 * k, x + 74 * k, y + 40 * k, 34 * k, fill=P, borde=B, grosor=5 * k)
    c.linea([(x - 70 * k, y - 10 * k), (x - 118 * k, y + 20 * k), (x - 130 * k, y + 70 * k)], B, 32 * k)
    c.linea([(x - 70 * k, y - 10 * k), (x - 118 * k, y + 20 * k), (x - 130 * k, y + 70 * k)], P, 22 * k)
    for i in range(4):   # costura
        c.linea([(x - 40 * k + i * 26 * k, y - 50 * k), (x - 30 * k + i * 26 * k, y - 30 * k)], (90, 80, 80), 4 * k)
    c.linea([(x - 50 * k, y - 40 * k), (x + 50 * k, y - 40 * k)], (90, 80, 80), 3 * k)


def dibujo_mano(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 480, W, 540)
    # un cofre que tiembla; con la respuesta sale la mano, baja al piso y camina sola
    tiembla = 5 * math.sin(t * 30) if t < tr and (t % 1.4) < 0.3 else 0
    cx, cy = 290 + tiembla, 900
    abre = e_in_out(prog(t, tr, 0.3))
    c.rrect(cx - 150 * s, cy - 40 * s, cx + 150 * s, cy + 80 * s, 14 * s, fill=(70, 50, 60), borde=(30, 20, 26),
            grosor=6 * s)
    c.poligono(rect_rot(cx - 20 * abre, cy - 60 * s - 60 * abre, 320 * s, 44 * s, -0.4 * abre), fill=(90, 66, 78),
               borde=(30, 20, 26), grosor=6 * s)
    sale = e_back(prog(t, tr + 0.1, 0.45))
    if sale > 0:
        camina = clamp((t - tr - 0.6) / 1.3)
        mx = lerp(cx, 820, e_in_out(camina))
        my = lerp(cy - 60, 690, sale) if camina <= 0 else lerp(690, 840, e_in_out(clamp(camina * 4))) \
            - 14 * abs(math.sin(t * 12)) * (camina < 1)
        mano(c, mx, my, 0.9 * sale, t, 1.0 if 0 < camina < 1 else 0.25)
    c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 600, 720, 150)


# ======================================================= íconos del cierre
def _icono_semaforo(c, x, y, s, t):
    semaforo(c, x, y - 10 * s, 0.42 * s, (t % 2) < 1)


def _icono_luces(c, x, y, s, t):
    pts = [(x - 80 * s + 40 * s * i, y - 10 * s + 14 * s * math.sin(i)) for i in range(5)]
    c.linea(pts, (40, 50, 40), 4 * s)
    for i, (px, py) in enumerate(pts):
        c.elipse(px, py + 16 * s, 12 * s, 18 * s, fill=FOCOS[i])


def _icono_mascara(c, x, y, s, t):
    mascara(c, x, y + 4 * s, 0.48 * s, t, 1.0)


def _icono_zapato(c, x, y, s, t):
    zapato(c, x, y, 0.5 * s)


def _icono_mano(c, x, y, s, t):
    mano(c, x + 6 * s, y - 30 * s, 0.55 * s, t, 0.6)


ICONOS = [_icono_semaforo, _icono_luces, _icono_mascara, _icono_zapato, _icono_mano]
ESCENAS = {
    "gancho": lambda t: quiz.escena_gancho(t, E, FONDOS, "DE SERIES", titulo="5 PREGUNTAS"),
    "s1": quiz.escena_pregunta("s1", 1, 5, "patio", dibujo_semaforo, ACENTO["s1"], E, ESC, POR_ID, FONDOS),
    "s2": quiz.escena_pregunta("s2", 2, 5, "living", dibujo_luces, ACENTO["s2"], E, ESC, POR_ID, FONDOS),
    "s3": quiz.escena_pregunta("s3", 3, 5, "boveda", dibujo_mascara, ACENTO["s3"], E, ESC, POR_ID, FONDOS),
    "s4": quiz.escena_pregunta("s4", 4, 5, "zapateria", dibujo_zapatos, ACENTO["s4"], E, ESC, POR_ID, FONDOS),
    "s5": quiz.escena_pregunta("s5", 5, 5, "gotico", dibujo_mano, ACENTO["s5"], E, ESC, POR_ID, FONDOS),
}
