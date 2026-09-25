"""Episodio 11: quiz de películas — cinco preguntas sobre escenas muy conocidas.

Las piezas del quiz (tarjeta, opciones, reloj, gancho) están en quiz.py; acá van las preguntas
y los dibujos. Todo es genérico: no se dibujan personajes con derechos de autor.
Voz: grabaciones/ep11.* (o Tomás si falta).
"""
import math

import numpy as np
from PIL import Image

import quiz
from dibujo import (H, W, Capa, a_imagen, clamp, componer, corazon, e_back, e_in_out, gradiente, lerp, pop, prog,
                    rect_rot, resplandor, spr_brillo, spr_estrella, spr_resplandor, texto, viñeta)
from quiz import signo

SLUG = "quiz_peliculas"
DURACION = 58.0                       # cinco preguntas con 3 s para pensar cada una
GRABACION = "grabaciones/ep11"
VOZ = "es-AR-TomasNeural"             # solo si falta la grabación
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
PALABRAS_CIERRE = ("abajo", "seguinos")
CIERRE_TITULO = ("¿CUÁNTAS", "ACERTASTE?")

# "[3s]" = tiempo para pensar. Los nombres en inglés llevan {cómo se ve|cómo se dice} por si se
# usa la voz sintética; con la grabación no hace falta.
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Cinco preguntas de películas, tres segundos cada una! ¿Cuántas acertás?",
        "titulo": "5 PREGUNTAS",
    },
    {
        "id": "q1",
        "texto": "Uno: en {Avengers|Avéngers}, ¿cómo hace Thanos para borrar a la mitad del universo? [3s] "
                 "¡Con un chasquido de dedos! Tenía las seis gemas en el guante.",
        "titulo": "EL CHASQUIDO",
        "pregunta": "En Avengers, ¿cómo hace Thanos para borrar a la mitad del universo?",
        "opciones": ["UN GRITO", "UN CHASQUIDO", "UN RAYO"],
        "correcta": 1,
    },
    {
        "id": "q2",
        "texto": "Dos: en {Forrest Gump|Fórest Gamp}, ¿a qué se parece la vida según su mamá? [3s] "
                 "¡A una caja de chocolates! Nunca sabés lo que te va a tocar.",
        "titulo": "LA VIDA",
        "pregunta": "En Forrest Gump, ¿a qué se parece la vida según su mamá?",
        "opciones": ["UNA CAJA DE CHOCOLATES", "UNA MONTAÑA RUSA", "UN PARTIDO DE FÚTBOL"],
        "correcta": 0,
    },
    {
        "id": "q3",
        "texto": "Tres: en {Toy Story|Tói Estóri}, ¿qué nombre tiene escrito {Woody|Gúdi} en la bota? [3s] "
                 "¡{Andy|Ándi}! El nombre de su dueño.",
        "titulo": "LA BOTA",
        "pregunta": "En Toy Story, ¿qué nombre tiene escrito Woody en la bota?",
        "opciones": ["BUZZ", "SID", "ANDY"],
        "correcta": 2,
    },
    {
        "id": "q4",
        "texto": "Cuatro: en {Ratatouille|Ratatúi}, ¿cómo maneja la rata Remy al cocinero? [3s] "
                 "¡Le tira del pelo! Escondida abajo del gorro.",
        "titulo": "LA RATA COCINERA",
        "pregunta": "En Ratatouille, ¿cómo maneja la rata Remy al cocinero?",
        "opciones": ["LE HABLA AL OÍDO", "LE TIRA DEL PELO", "CON UN CONTROL"],
        "correcta": 1,
    },
    {
        "id": "q5",
        "texto": "Cinco: en Mi pobre angelito, ¿a qué ciudad viaja la familia cuando se olvida de Kevin? [3s] "
                 "¡A París! Y Kevin pasa la Navidad solo en casa.",
        "titulo": "EL VIAJE",
        "pregunta": "En Mi pobre angelito, ¿a qué ciudad viaja la familia cuando se olvida de Kevin?",
        "opciones": ["LONDRES", "ROMA", "PARÍS"],
        "correcta": 2,
    },
    {
        "id": "cierre",
        "texto": "¿Cuántas acertaste? Comentalo abajo y seguinos para más.",
        "titulo": "¿CUÁNTAS ACERTASTE?",
    },
]

PREGUNTAS = ["q1", "q2", "q3", "q4", "q5"]
ACENTO = {"q1": (150, 80, 255), "q2": (200, 110, 50), "q3": (255, 160, 30), "q4": (235, 70, 80),
          "q5": (30, 170, 120), "cierre": (255, 0, 110)}
POR_ID = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
TINTA = (24, 16, 48)


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        **quiz.eventos(L, PREGUNTAS),
        **quiz.eventos_gancho(L, "cinco", "películas"),
        "q1_gemas": L.palabra("q1", "gemas"),
        "q2_tocar": L.palabra("q2", "tocar"),
        "q3_dueno": L.palabra("q3", "dueño"),
        "q4_gorro": L.palabra("q4", "gorro"),
        "q5_kevin": L.palabra("q5", "Kevin", 2),
        "q5_navidad": L.palabra("q5", "Navidad"),
        "q5_solo": L.palabra("q5", "solo"),
    }


def efectos(E, L, S):
    fx = quiz.efectos(E, S, PREGUNTAS) + quiz.efectos_gancho(E, S)
    tr = {q: E[f"{q}_revela"] for q in PREGUNTAS}
    fx += [(tr["q1"] - 0.02, S.clic(), 0.9), (tr["q1"] + 0.15, S.whoosh(1.0, 3000, 200), 0.18)]
    for i in range(6):
        fx.append((E["q1_gemas"] + 0.1 * i, S.pop(900 + 120 * i, 500, 0.08), 0.18))
    fx += [(tr["q2"] + 0.05, S.pop(500, 200, 0.15), 0.3), (E["q2_tocar"], S.pop(1200, 700), 0.3),
           (tr["q3"] + 0.05, S.marcador(0.5), 0.25), (E["q3_dueno"], S.brillo_sfx(), 0.18),
           (tr["q4"] + 0.05, S.whoosh(0.3, 800, 3000), 0.2), (E["q4_gorro"], S.pop(400, 150, 0.15), 0.3),
           (tr["q5"] + 0.05, S.whoosh(0.7, 300, 2500), 0.2), (E["q5_navidad"], S.brillo_sfx(), 0.22)]
    return fx


def sacudidas(E):
    return quiz.sacudidas_gancho(E) + [(E["q1_revela"], 16, 0.35)]


def momento_portada(E):
    return E["gq_acertas"] + 0.7


# ==================================================================== fondos
def fondo_gancho():
    a = gradiente([(0, (20, 16, 60)), (0.5, (120, 20, 90)), (1, (240, 120, 30))])
    resplandor(a, 540, 1000, 620, (255, 190, 120), 0.35)
    viñeta(a)
    return a_imagen(a, 90)


def fondo_cosmos():
    a = gradiente([(0, (14, 6, 40)), (0.6, (50, 20, 100)), (1, (90, 30, 120))])
    resplandor(a, 540, 700, 520, (200, 120, 255), 0.35)
    img = a_imagen(a, 91)
    rng = np.random.default_rng(92)
    for _ in range(100):
        componer(img, spr_estrella(int(rng.integers(2, 6))), rng.uniform(0, W), rng.uniform(0, H),
                 alpha=rng.uniform(0.3, 0.9))
    return img


def fondo_plaza():
    a = gradiente([(0, (120, 190, 245)), (0.62, (200, 232, 250)), (0.72, (140, 200, 110)), (1, (90, 160, 80))])
    resplandor(a, 850, 560, 300, (255, 250, 220), 0.5)
    return a_imagen(a, 93)


def fondo_cuarto():
    a = gradiente([(0, (110, 170, 235)), (0.74, (165, 205, 245)), (0.745, (190, 130, 75)), (1, (150, 95, 55))])
    img = a_imagen(a, 94)
    c = Capa(0, 0, W, H, ss=1)
    rng = np.random.default_rng(95)
    for _ in range(9):   # nubecitas del empapelado
        x, y = rng.uniform(40, W - 40), rng.uniform(80, 1350)
        for dx, dy, r in ((-40, 6, 30), (0, -10, 42), (42, 6, 30)):
            c.circulo(x + dx, y + dy, r, fill=(255, 255, 255, 80))
    for y in range(1440, H, 70):   # tablas del piso
        c.linea([(0, y), (W, y)], (120, 70, 40, 90), 3, puntas=False)
    c.pegar_en(img)
    return img


def fondo_cocina():
    a = gradiente([(0, (255, 244, 225)), (0.75, (250, 232, 205)), (0.755, (150, 90, 60)), (1, (120, 70, 45))])
    img = a_imagen(a, 96)
    c = Capa(0, 0, W, H, ss=1)
    for x in range(0, W, 108):
        c.linea([(x, 0), (x, 1440)], (220, 200, 175, 150), 3, puntas=False)
    for y in range(0, 1440, 108):
        c.linea([(0, y), (W, y)], (220, 200, 175, 150), 3, puntas=False)
    c.pegar_en(img)
    return img


def fondo_noche():
    a = gradiente([(0, (8, 16, 44)), (0.62, (26, 44, 96)), (0.72, (200, 215, 240)), (1, (235, 242, 252))])
    resplandor(a, 800, 520, 220, (230, 235, 255), 0.35)
    img = a_imagen(a, 97)
    rng = np.random.default_rng(98)
    for _ in range(60):
        componer(img, spr_estrella(int(rng.integers(2, 5))), rng.uniform(0, W), rng.uniform(0, 1150),
                 alpha=rng.uniform(0.3, 0.8))
    return img


def preparar():
    FONDOS.update(gancho=fondo_gancho(), cosmos=fondo_cosmos(), plaza=fondo_plaza(), cuarto=fondo_cuarto(),
                  cocina=fondo_cocina(), noche=fondo_noche())


# ================================================================ utilidades
def estallido(fr, x, y, s, palabra, color=(255, 220, 60)):
    c = Capa(int(x - 260), int(y - 200), 520, 400)
    pts = []
    for i in range(28):
        r = (190 if i % 2 == 0 else 120) * s
        a = i * math.pi / 14
        pts.append((x + math.cos(a) * r * 1.25, y + math.sin(a) * r * 0.85))
    c.poligono(pts, fill=color, borde=TINTA, grosor=8)
    c.pegar_en(fr)
    componer(fr, texto(palabra, "titulo", 96, color=TINTA), x, y + 6, escala=s, rot=-6)


# ============================================================ 1 · el chasquido
def figura(c, x, y, k, color):
    c.circulo(x, y - 64 * k, 25 * k, fill=color)
    c.rrect(x - 32 * k, y - 34 * k, x + 32 * k, y + 42 * k, 24 * k, fill=color)


GEMAS = [(150, 60, 220), (40, 120, 255), (230, 40, 60), (255, 140, 20), (40, 200, 90), (255, 220, 40)]


def gema(c, x, y, k, col):
    pts = [(x, y - 30 * k), (x + 24 * k, y - 12 * k), (x + 18 * k, y + 22 * k), (x - 18 * k, y + 22 * k),
           (x - 24 * k, y - 12 * k)]
    c.poligono(pts, fill=col, borde=(255, 255, 255), grosor=4 * k)
    c.poligono([(x - 8 * k, y - 18 * k), (x + 2 * k, y - 22 * k), (x - 2 * k, y - 4 * k)], fill=(255, 255, 255, 170))


def dibujo_chasquido(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 500, W, 520)
    for i, x in enumerate((190, 330, 470, 610, 750, 890)):
        y = 925 + 5 * math.sin(t * 2 + i)
        col = (236, 230, 255)
        ini = tr + 0.2 + 0.1 * i
        if i % 2 == 1 and t >= ini:   # la mitad se hace polvo
            p = prog(t, ini, 0.9)
            if p < 1:
                figura(c, x, y, s, col + (int(255 * (1 - p)),))
            rng = np.random.default_rng(i)
            for j in range(40):
                x0, y0 = x + rng.uniform(-32, 32), y + rng.uniform(-88, 42)
                d = t - ini - rng.uniform(0, 0.6)
                if d <= 0:
                    x1, y1, a = x0, y0, 255
                else:
                    x1 = x0 + d * rng.uniform(80, 240)
                    y1 = y0 - d * rng.uniform(20, 100) + 8 * math.sin(d * 6 + j)
                    a = int(230 * clamp(1 - d / 1.3))
                if a > 0 and (d > 0 or p > 0.2):
                    c.circulo(x1, y1, rng.uniform(3, 6), fill=(214, 180, 140, a))
        else:
            figura(c, x, y, s, col)
    tg = E["q1_gemas"]
    for i, col in enumerate(GEMAS):
        sg = e_back(prog(t, tg + 0.1 * i, 0.35))
        if sg > 0:
            a = math.radians(205 + i * 26)
            gema(c, 540 + math.cos(a) * 260, 800 + math.sin(a) * 200 + 4 * math.sin(t * 3 + i), 1.3 * sg, col)
    c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 700, 150)
    sb = pop(t, tr - 0.05, 0.25) * (1 - prog(t, tr + 1.3, 0.3))
    if sb > 0.01:
        estallido(fr, 540, 690, sb, "¡CHAS!")


# ======================================================== 2 · caja de chocolates
CHOCOS = [(92, 46, 22), (70, 36, 16), (128, 74, 36)]


def caja_chocolates(c, x, y, k, salto, t):
    w, h = 400 * k, 250 * k
    c.rrect(x - w / 2, y - h / 2 + 12 * k, x + w / 2, y + h / 2 + 12 * k, 26 * k, fill=(10, 5, 30, 90))
    c.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 26 * k, fill=(120, 30, 50), borde=(70, 12, 24), grosor=8 * k)
    c.rrect(x - w / 2 + 22 * k, y - h / 2 + 22 * k, x + w / 2 - 22 * k, y + h / 2 - 22 * k, 16 * k,
            fill=(245, 226, 196))
    for fila in range(2):
        for col in range(4):
            cx = x - w / 2 + 22 * k + (col + 0.5) * (w - 44 * k) / 4
            cy = y - h / 2 + 22 * k + (fila + 0.5) * (h - 44 * k) / 2
            c.circulo(cx, cy + 4 * k, 38 * k, fill=(200, 160, 120))
            if fila == 0 and col == 1:
                cy -= 150 * salto * k
            c.circulo(cx, cy, 31 * k, fill=CHOCOS[(fila + col) % 3])
            c.arco(cx, cy, 20 * k, 20 * k, 200, 260, (255, 255, 255, 100), 5 * k)


def pluma(c, x, y, k, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(-5, 6):
        u = i / 5
        ancho = 26 * k * (1 - u * u) + 4 * k
        px, py = x + ca * u * 90 * k, y + sa * u * 90 * k
        c.linea([(px - sa * ancho, py + ca * ancho), (px + sa * ancho, py - ca * ancho)], (255, 255, 255, 220), 10 * k)
    c.linea([(x - ca * 110 * k, y - sa * 110 * k), (x + ca * 95 * k, y + sa * 95 * k)], (180, 180, 190), 4 * k)


def dibujo_chocolates(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 470, W, 550)
    fx = lerp(-150, W + 150, ((t - ev["t0"]) / 9) % 1)   # la pluma que vuela
    pluma(c, fx, 560 + 40 * math.sin(t * 1.3), 0.8, math.sin(t * 1.7) * 0.6)
    tt = E["q2_tocar"]
    salto = math.sin(math.pi * clamp((t - tt) / 0.7)) if t >= tt else 0
    caja_chocolates(c, 540, 820, 1.05 * s, salto, t)
    abre = e_in_out(prog(t, tr, 0.45))
    if abre < 1:   # tapa con moño; con la respuesta se levanta y sale volando
        lx, ly, ang = 540 + 380 * abre, 810 - 260 * abre, -0.5 * abre
        c.poligono(rect_rot(lx, ly, 430 * s, 270 * s, ang), fill=(200, 40, 70), borde=(110, 16, 36), grosor=8)
        c.poligono(rect_rot(lx, ly, 46 * s, 270 * s, ang), fill=(255, 205, 70))
        c.poligono(rect_rot(lx, ly, 430 * s, 46 * s, ang), fill=(255, 205, 70))
    c.pegar_en(fr)
    if abre < 0.3:
        componer(fr, texto("?", "titulo", 120, color=(255, 255, 255), borde=9), 540, 815, escala=s,
                 alpha=1 - abre / 0.3)
    if t >= tt:
        componer(fr, texto("?", "titulo", 80, color=(255, 214, 80), borde=7), 660, 640 - 30 * salto,
                 escala=pop(t, tt + 0.1, 0.3))


# ================================================================== 3 · la bota
CUERO, CUERO_B, SUELA = (150, 86, 42), (80, 44, 20), (238, 214, 172)


def bota(c, x, y, k, t):
    """Bota de vaquero vista desde abajo: la suela, el taco y una espuela."""
    c.elipse(x, y - 110 * k, 122 * k, 158 * k, fill=CUERO, borde=CUERO_B, grosor=8 * k)
    c.poligono([(x - 96 * k, y - 40 * k), (x + 96 * k, y - 40 * k), (x + 78 * k, y + 80 * k), (x - 78 * k, y + 80 * k)],
               fill=CUERO)
    c.rrect(x - 88 * k, y + 50 * k, x + 88 * k, y + 225 * k, 46 * k, fill=CUERO, borde=CUERO_B, grosor=8 * k)
    c.elipse(x, y - 112 * k, 100 * k, 136 * k, fill=SUELA)
    c.rrect(x - 68 * k, y + 70 * k, x + 68 * k, y + 205 * k, 36 * k, fill=(120, 70, 36))
    for i in range(3):
        c.linea([(x - 50 * k, y + (100 + 35 * i) * k), (x + 50 * k, y + (100 + 35 * i) * k)], (95, 52, 24), 5 * k)
    ex, ey = x + 120 * k, y + 150 * k   # espuela
    c.linea([(x + 86 * k, ey), (ex, ey)], (200, 200, 210), 8 * k)
    rot = t * 2
    c.poligono([(ex + math.cos(rot + i * math.pi / 5) * (30 if i % 2 == 0 else 13) * k,
                 ey + math.sin(rot + i * math.pi / 5) * (30 if i % 2 == 0 else 13) * k) for i in range(10)],
               fill=(255, 205, 70), borde=(150, 110, 20), grosor=3 * k)


def _escrito(txt, p):
    im = texto(txt, "titulo", 64, color=(28, 26, 40))
    if p >= 1:
        return im
    im = im.copy()
    a = np.array(im)
    a[:, int(im.width * p):, 3] = 0
    return Image.fromarray(a)


def dibujo_bota(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    c = Capa(0, 480, W, 540)
    y = 770 + 6 * math.sin(t * 1.8)
    bota(c, 540, y, 1.0 * s, t)
    c.pegar_en(fr)
    if t < tr:
        componer(fr, texto("???", "titulo", 90, color=(170, 140, 110)), 540, y - 112, escala=s, rot=-8)
    else:
        componer(fr, _escrito("ANDY", clamp((t - tr) / 0.55)), 540, y - 112, rot=-8)
    sc = pop(t, E["q3_dueno"], 0.35)
    if sc > 0:
        c = Capa(700, 470, 260, 220)
        corazon(c, 800, 580 + 6 * math.sin(t * 4), 90 * sc, (240, 60, 90))
        c.pegar_en(fr)


# ======================================================== 4 · la rata cocinera
PIEL, PIEL_B, PELO = (255, 214, 182), (120, 70, 50), (122, 72, 36)


def cocinero(c, x, y, k, t, levanta, tirones, cola):
    for s in (-1, 1):
        c.circulo(x + s * 120 * k, y + 12 * k, 28 * k, fill=PIEL, borde=PIEL_B, grosor=5 * k)
    c.circulo(x, y, 122 * k, fill=PIEL, borde=PIEL_B, grosor=6 * k)
    sorpresa = levanta > 0.2
    for s in (-1, 1):
        c.circulo(x + s * 44 * k, y - 6 * k, (15 if sorpresa else 11) * k, fill=(40, 30, 30))
        c.circulo(x + s * 44 * k + 4 * k, y - 10 * k, 4 * k, fill=(255, 255, 255))
    c.elipse(x, y + 30 * k, 24 * k, 19 * k, fill=(245, 168, 140))
    if sorpresa:
        c.elipse(x, y + 78 * k, 18 * k, 22 * k, fill=(150, 50, 50))
    else:
        c.arco(x, y + 62 * k, 34 * k, 18 * k, 20, 160, (150, 60, 50), 6 * k)
    # pelo: los mechones de los costados son las "riendas"
    for i, dx in enumerate((-58, -20, 20, 58)):
        tiro = 0
        if i in (0, 3):
            tiro = tirones * (1 + 0.5 * math.sin(t * 9 + i))
        c.linea([(x + dx * k, y - 104 * k), (x + dx * 1.15 * k, y - (128 + 60 * tiro) * k)], PELO, 20 * k)
    if levanta > 0:   # la rata, arriba de la cabeza
        rx, ry = x, y - 150 * k
        c.elipse(rx, ry, 58 * k, 34 * k, fill=(150, 150, 165), borde=(80, 80, 95), grosor=4 * k)
        c.circulo(rx - 50 * k, ry - 16 * k, 28 * k, fill=(150, 150, 165), borde=(80, 80, 95), grosor=4 * k)
        for s in (-1, 1):
            c.circulo(rx - 50 * k + s * 20 * k, ry - 40 * k, 13 * k, fill=(240, 170, 190), borde=(80, 80, 95),
                      grosor=3 * k)
        c.circulo(rx - 76 * k, ry - 12 * k, 6 * k, fill=(240, 120, 150))
        c.circulo(rx - 56 * k, ry - 22 * k, 5 * k, fill=(20, 20, 30))
        for dx in (-58, 58):   # las patitas agarran los mechones
            c.linea([(rx + (dx * 0.5) * k, ry + 6 * k), (x + dx * 1.15 * k, y - (128 + 60 * tirones) * k)],
                    (150, 150, 165), 9 * k)
    # gorro de cocinero (se levanta con la respuesta)
    gy = y - 120 * k - 120 * levanta * k
    ang = -0.25 * levanta
    c.poligono(rect_rot(x + 20 * levanta * k, gy, 200 * k, 60 * k, ang), fill=(255, 255, 255), borde=(170, 170, 185),
               grosor=5 * k)
    for dx, dy, r in ((-62, -78, 70), (0, -102, 82), (62, -78, 70)):
        ca, sa = math.cos(ang), math.sin(ang)
        c.circulo(x + 20 * levanta * k + (ca * dx - sa * dy) * k, gy + (sa * dx + ca * dy) * k, r * k,
                  fill=(255, 255, 255), borde=(170, 170, 185), grosor=5 * k)
    if cola > 0:   # la cola asoma debajo del gorro
        pts = [(x + 96 * k, y - 112 * k), (x + 132 * k, y - 80 * k), (x + 128 * k, y - 40 * k),
               (x + 150 * k, y - 15 * k)]
        c.linea(pts[:1 + int(3 * cola)], (240, 170, 190), 9 * k)


def dibujo_rata(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    tg = E["q4_gorro"]
    levanta = e_in_out(prog(t, tr, 0.35)) * (1 - e_in_out(prog(t, tg, 0.35)))
    tirones = clamp((t - tr) / 0.3) if t < tg + 0.2 else 1 - clamp((t - tg - 0.2) / 0.3)
    cola = clamp((t - tg - 0.3) / 0.3)
    temblor = 4 * math.sin(t * 22) if t < tr and (t % 1.6) < 0.25 else 0   # algo se mueve bajo el gorro
    c = Capa(0, 420, W, 600)
    cocinero(c, 540 + temblor, 850, 0.95 * s, t, levanta, tirones * (1 if t >= tr else 0), cola)
    c.pegar_en(fr)


# ============================================================ 5 · el viaje
def avion(c, x, y, k):
    c.elipse(x, y, 110 * k, 26 * k, fill=(250, 250, 255), borde=(110, 120, 150), grosor=4 * k)
    c.poligono([(x - 10 * k, y), (x + 30 * k, y), (x - 30 * k, y + 70 * k), (x - 60 * k, y + 70 * k)],
               fill=(220, 225, 240), borde=(110, 120, 150), grosor=3 * k)
    c.poligono([(x - 80 * k, y - 10 * k), (x - 100 * k, y - 60 * k), (x - 70 * k, y - 60 * k), (x - 50 * k, y - 10 * k)],
               fill=(220, 60, 70))
    c.linea([(x - 90 * k, y + 4 * k), (x + 90 * k, y + 4 * k)], (60, 120, 220), 6 * k)
    for i in range(5):
        c.circulo(x + (20 + 16 * i) * k - 40 * k, y - 6 * k, 5 * k, fill=(90, 150, 230))


def torre(c, x, y, k, t):
    """Torre de hierro de París (silueta genérica) con lucecitas."""
    T = (160, 170, 220)
    for s in (-1, 1):
        c.poligono([(x + s * 118 * k, y), (x + s * 74 * k, y), (x + s * 26 * k, y - 150 * k), (x + s * 54 * k, y - 150 * k)],
                   fill=T)
    c.rrect(x - 66 * k, y - 168 * k, x + 66 * k, y - 150 * k, 4 * k, fill=T)
    c.poligono([(x - 50 * k, y - 168 * k), (x + 50 * k, y - 168 * k), (x + 16 * k, y - 300 * k), (x - 16 * k, y - 300 * k)],
               fill=T)
    c.rrect(x - 28 * k, y - 312 * k, x + 28 * k, y - 300 * k, 3 * k, fill=T)
    c.poligono([(x - 16 * k, y - 312 * k), (x + 16 * k, y - 312 * k), (x + 4 * k, y - 400 * k), (x - 4 * k, y - 400 * k)],
               fill=T)
    c.linea([(x, y - 400 * k), (x, y - 435 * k)], T, 5 * k)
    for s in (-1, 1):   # arco entre las patas
        c.arco(x, y, 80 * k, 70 * k, 180 if s < 0 else 270, 270 if s < 0 else 360, T, 12 * k)
    rng = np.random.default_rng(3)
    for i in range(16):
        u = rng.uniform(0, 1)
        ly = y - u * 400 * k
        lx = x + rng.uniform(-1, 1) * (110 - 100 * u) * k
        if (t * 3 + i * 0.37) % 1 < 0.5:
            c.circulo(lx, ly, 4 * k, fill=(255, 240, 170))


def casa(c, x, y, k, t, luces, nene):
    c.rrect(x - 150 * k, y - 110 * k, x + 150 * k, y + 100 * k, 8 * k, fill=(170, 60, 50), borde=(90, 28, 24),
            grosor=6 * k)
    c.poligono([(x - 180 * k, y - 104 * k), (x, y - 240 * k), (x + 180 * k, y - 104 * k)], fill=(60, 44, 60),
               borde=(30, 20, 30), grosor=6 * k)
    c.poligono([(x - 150 * k, y - 126 * k), (x, y - 240 * k), (x + 150 * k, y - 126 * k), (x, y - 206 * k)],
               fill=(245, 248, 255))
    c.rrect(x + 50 * k, y - 190 * k, x + 90 * k, y - 120 * k, 4 * k, fill=(120, 60, 50))
    c.rrect(x - 30 * k, y + 10 * k, x + 30 * k, y + 100 * k, 6 * k, fill=(90, 40, 30))
    for wx in (-95, 95):
        c.rrect(x + (wx - 38) * k, y - 70 * k, x + (wx + 38) * k, y - 4 * k, 6 * k, fill=(255, 220, 120),
                borde=(90, 28, 24), grosor=5 * k)
        c.linea([(x + wx * k, y - 70 * k), (x + wx * k, y - 4 * k)], (90, 28, 24), 4 * k)
    if nene > 0:   # alguien solo en la ventana
        c.circulo(x - 95 * k, y - 40 * k, 12 * k * nene, fill=(60, 40, 40))
        c.elipse(x - 95 * k, y - 10 * k, 20 * k * nene, 14 * k * nene, fill=(60, 40, 40))
    if luces > 0:
        colores = [(255, 70, 70), (70, 220, 110), (255, 220, 60), (80, 150, 255)]
        for i in range(13):
            u = i / 12
            lx = lerp(x - 170 * k, x + 170 * k, u)
            ly = y - 104 * k - (240 - 104) * k * (1 - abs(2 * u - 1)) + 14 * k
            if i / 13 < luces:
                prendida = (t * 4 + i) % 2 < 1.4
                col = colores[i % 4] if prendida else tuple(v // 3 for v in colores[i % 4])
                c.circulo(lx, ly, 9 * k, fill=col)


def nieve(fr, t, fuerza):
    if fuerza <= 0:
        return
    c = Capa(0, 470, W, 560, ss=1)
    rng = np.random.default_rng(7)
    for i in range(int(60 * fuerza)):
        x0, v, r = rng.uniform(0, W), rng.uniform(40, 90), rng.uniform(3, 7)
        y = 470 + ((rng.uniform(0, 560) + t * v) % 560)
        c.circulo(x0 + 14 * math.sin(t + i), y, r, fill=(255, 255, 255, 200))
    c.pegar_en(fr)


def dibujo_viaje(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    nieve(fr, t, 0.4 + 0.6 * clamp((t - E["q5_navidad"]) / 0.5))
    c = Capa(0, 470, W, 550)
    st = e_back(prog(t, tr, 0.45))
    if st > 0:
        torre(c, 300, 960, 1.0 * st, t)
    sc = e_back(prog(t, E["q5_kevin"] - 0.1, 0.45))
    if sc > 0:
        casa(c, 780, 860, 0.95 * sc, t, clamp((t - E["q5_navidad"]) / 0.5), clamp((t - E["q5_solo"]) / 0.3))
    # el avión: da vueltas con un "?" hasta la respuesta; después se va hacia la torre
    if t < tr + 1.2:
        if t < tr:
            u = ((t - ev["t0"]) / 3.2) % 1
            ax, ay = lerp(-120, W + 120, u), 600 + 30 * math.sin(u * 6)
        else:
            p = e_in_out(prog(t, tr, 1.2))
            ax, ay = lerp(700, 330, p), lerp(560, 520, p)
        avion(c, ax, ay, 0.9 * s * (1 - 0.5 * (t >= tr) * prog(t, tr, 1.2)))
    c.pegar_en(fr)
    signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 800, 150)
    if st > 0:
        componer(fr, spr_resplandor(260, (255, 230, 150)), 300, 760, alpha=0.45 * st)
    if t >= E["q5_navidad"]:
        for i, (x, y) in enumerate(((640, 640), (930, 700), (780, 590))):
            a = 0.5 + 0.5 * math.sin(t * 5 + i)
            componer(fr, spr_brillo(int(16 + 10 * a), (255, 240, 170)), x, y, alpha=a)


# ======================================================= íconos del cierre
def _icono_gemas(c, x, y, s, t):
    for i, col in enumerate(GEMAS):
        a = math.radians(-90 + i * 60)
        gema(c, x + math.cos(a) * 62 * s, y + math.sin(a) * 62 * s, 1.0 * s, col)


def _icono_chocolate(c, x, y, s, t):
    c.circulo(x, y + 10 * s, 78 * s, fill=(200, 160, 120))
    c.circulo(x, y, 64 * s, fill=CHOCOS[0])
    c.arco(x, y, 42 * s, 42 * s, 200, 260, (255, 255, 255, 110), 9 * s)


def _icono_bota(c, x, y, s, t):
    bota(c, x - 10 * s, y + 10 * s, 0.42 * s, t)


def _icono_gorro(c, x, y, s, t):
    c.rrect(x - 70 * s, y + 20 * s, x + 70 * s, y + 70 * s, 8 * s, fill=(255, 255, 255), borde=(150, 150, 170),
            grosor=5 * s)
    for dx, dy, r in ((-44, -10, 48), (0, -34, 56), (44, -10, 48)):
        c.circulo(x + dx * s, y + dy * s, r * s, fill=(255, 255, 255), borde=(150, 150, 170), grosor=5 * s)


def _icono_torre(c, x, y, s, t):
    torre(c, x, y + 88 * s, 0.4 * s, t)


ICONOS = [_icono_gemas, _icono_chocolate, _icono_bota, _icono_gorro, _icono_torre]
ESCENAS = {
    "gancho": lambda t: quiz.escena_gancho(t, E, FONDOS, "DE PELÍCULAS", titulo="5 PREGUNTAS"),
    "q1": quiz.escena_pregunta("q1", 1, 5, "cosmos", dibujo_chasquido, ACENTO["q1"], E, ESC, POR_ID, FONDOS),
    "q2": quiz.escena_pregunta("q2", 2, 5, "plaza", dibujo_chocolates, ACENTO["q2"], E, ESC, POR_ID, FONDOS),
    "q3": quiz.escena_pregunta("q3", 3, 5, "cuarto", dibujo_bota, ACENTO["q3"], E, ESC, POR_ID, FONDOS),
    "q4": quiz.escena_pregunta("q4", 4, 5, "cocina", dibujo_rata, ACENTO["q4"], E, ESC, POR_ID, FONDOS),
    "q5": quiz.escena_pregunta("q5", 5, 5, "noche", dibujo_viaje, ACENTO["q5"], E, ESC, POR_ID, FONDOS),
}
