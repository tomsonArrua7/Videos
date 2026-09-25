"""Episodio 10: quiz "¿Cuánto sabés?" — tres preguntas con opciones, cuenta regresiva y respuesta.

El primer episodio interactivo: las piezas comunes (tarjeta, opciones, reloj, gancho) están en
quiz.py; acá van las preguntas y los dibujos. Voz: grabaciones/ep10.* (o Tomás si falta).
"""
import math

import numpy as np

import quiz
from dibujo import (H, W, Capa, a_imagen, cartel, componer, e_back, e_in_out, gradiente, lerp, pop, prog,
                    resplandor, spr_estrella, spr_resplandor, texto, viñeta)

SLUG = "quiz"
DURACION = 38.0                       # las tres cuentas regresivas suman 9 s
GRABACION = "grabaciones/ep10"
VOZ = "es-AR-TomasNeural"             # solo si falta la grabación
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
PALABRAS_CIERRE = ("abajo", "seguinos")
CIERRE_TITULO = ("¿CUÁNTAS", "ACERTASTE?")

# Se lee la pregunta, "[3s]" deja tres segundos para pensar (con el reloj en pantalla) y
# después la respuesta. Las opciones no se leen: están en pantalla.
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres preguntas, tres segundos cada una! ¿Cuántas acertás?",
        "titulo": "3 PREGUNTAS",
    },
    {
        "id": "p1",
        "texto": "Uno: ¿qué animal tiene huellas digitales casi iguales a las nuestras? [3s] "
                 "¡El koala! Son tan parecidas que podrían confundir a la policía.",
        "titulo": "HUELLAS",
        "pregunta": "¿Qué animal tiene huellas digitales casi iguales a las nuestras?",
        "opciones": ["PERRO", "DELFÍN", "KOALA"],
        "correcta": 2,
    },
    {
        "id": "p2",
        "texto": "Dos: ¿cuánto tarda la luz del Sol en llegar a la Tierra? [3s] "
                 "¡Ocho minutos! Siempre vemos el Sol de hace ocho minutos.",
        "titulo": "LA LUZ DEL SOL",
        "pregunta": "¿Cuánto tarda la luz del Sol en llegar a la Tierra?",
        "opciones": ["8 SEGUNDOS", "8 MINUTOS", "8 HORAS"],
        "correcta": 1,
    },
    {
        "id": "p3",
        "texto": "Tres: ¿cuánto pesa una nube común? [3s] ¡Unas quinientas toneladas! Lo mismo que cien elefantes.",
        "titulo": "UNA NUBE",
        "pregunta": "¿Cuánto pesa una nube común?",
        "opciones": ["500 TONELADAS", "50 KILOS", "1 KILO"],
        "correcta": 0,
    },
    {
        "id": "cierre",
        "texto": "¿Cuántas acertaste? Comentalo abajo y seguinos para más.",
        "titulo": "¿CUÁNTAS ACERTASTE?",
    },
]

PREGUNTAS = ["p1", "p2", "p3"]
ACENTO = {"p1": (60, 180, 110), "p2": (255, 160, 30), "p3": (70, 150, 250), "cierre": (255, 0, 110)}
POR_ID = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        **quiz.eventos(L, PREGUNTAS),
        "gq_tres": L.palabra("gancho", "tres"),
        "gq_preguntas": L.palabra("gancho", "preguntas"),
        "gq_segundos": L.palabra("gancho", "segundos"),
        "gq_acertas": L.palabra("gancho", "acertás"),
        "k_parecidas": L.palabra("p1", "parecidas"),
        "k_policia": L.palabra("p1", "policía"),
        "l_siempre": L.palabra("p2", "siempre"),
        "l_hace": L.palabra("p2", "hace"),
        "n_toneladas": L.palabra("p3", "toneladas"),
        "n_elefantes": L.palabra("p3", "elefantes"),
    }


def _sirena(S, dur=1.1):
    t = S.tt(dur)
    f = np.where((t * 4).astype(int) % 2 == 0, 760.0, 980.0)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / S.SR)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f) / S.SR) * 0.6
    return S.filtro(y, "lowpass", 3000) * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.2)


def _trompeta(S, dur=0.6):
    """Barrito de elefante: un bronce que sube y se quiebra."""
    t = S.tt(dur)
    f = 330 * (1 + 0.5 * np.minimum(1, t / 0.25)) * (1 + 0.03 * np.sin(2 * np.pi * 22 * t))
    fase = 2 * np.pi * np.cumsum(f) / S.SR
    y = sum(np.sin(k * fase) / k for k in range(1, 9))
    return S.filtro(y, "bandpass", [300, 2600]) * np.minimum(1, t / 0.04) * np.exp(-np.maximum(0, t - 0.35) * 8)


def efectos(E, L, S):
    fx = quiz.efectos(E, S, PREGUNTAS)
    fx += [(E["gq_tres"], S.golpe(), 0.5), (E["gq_segundos"] - 0.1, S.pop(1000, 300), 0.3),
           (E["gq_acertas"], S.pop(600, 180), 0.4), (E["gq_acertas"] + 0.05, S.brillo_sfx(), 0.22)]
    for i in range(4):
        fx.append((E["gq_segundos"] + 0.15 + 0.3 * i, S.tictac(i % 2 == 0), 0.35))
    fx += [(E["k_parecidas"], S.pop(900, 350), 0.22), (E["k_policia"], _sirena(S), 0.07),
           (E["p2_revela"] + 0.35, S.brillo_sfx(), 0.18), (E["l_hace"], S.whoosh(0.4, 3000, 300), 0.12),
           (E["n_toneladas"], S.golpe(), 0.40), (E["n_elefantes"] + 0.1, _trompeta(S), 0.10)]
    return fx


def sacudidas(E):
    return [(E["gq_tres"], 10, 0.25), (E["gq_acertas"], 14, 0.3), (E["n_toneladas"], 12, 0.3)]


def momento_portada(E):
    return E["gq_acertas"] + 0.7


# ==================================================================== fondos
def _estrellas(img, n, seed, alto=H):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        componer(img, spr_estrella(int(rng.integers(2, 6))), rng.uniform(0, W), rng.uniform(0, alto),
                 alpha=rng.uniform(0.3, 0.9))


def fondo_gancho():
    a = gradiente([(0, (26, 20, 110)), (0.55, (98, 20, 170)), (1, (230, 30, 130))])
    resplandor(a, 540, 1000, 620, (255, 150, 230), 0.35)
    viñeta(a)
    return a_imagen(a, 80)


def fondo_eucalipto():
    a = gradiente([(0, (24, 96, 80)), (0.6, (70, 150, 110)), (1, (150, 205, 140))])
    resplandor(a, 540, 760, 500, (220, 255, 220), 0.3)
    viñeta(a, 0.35)
    img = a_imagen(a, 81)
    c = Capa(0, 0, W, H, ss=1)
    rng = np.random.default_rng(82)
    for _ in range(26):   # hojas de eucalipto, apenas marcadas
        x, y, ang = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, math.pi)
        dx, dy = math.cos(ang) * 60, math.sin(ang) * 60
        c.linea([(x - dx, y - dy), (x + dx, y + dy)], (255, 255, 255, 22), 34)
    c.pegar_en(img)
    return img


def fondo_espacio():
    a = gradiente([(0, (6, 8, 30)), (0.6, (22, 20, 70)), (1, (54, 24, 84))])
    resplandor(a, 190, 780, 420, (255, 170, 60), 0.35)
    img = a_imagen(a, 83)
    _estrellas(img, 110, 84)
    return img


def fondo_cielo():
    a = gradiente([(0, (60, 140, 230)), (0.6, (140, 200, 255)), (1, (220, 238, 255))])
    resplandor(a, 850, 380, 360, (255, 250, 220), 0.4)
    img = a_imagen(a, 85)
    c = Capa(0, 0, W, H, ss=1)
    for x, y, k in ((150, 560, 0.45), (930, 1250, 0.5), (120, 1500, 0.4)):
        nube(c, x, y, k, (255, 255, 255, 70), (255, 255, 255, 0), cara=False)
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(gancho=fondo_gancho(), eucalipto=fondo_eucalipto(), espacio=fondo_espacio(),
                  cielo=fondo_cielo())


# ================================================================ dibujos
def huella(c, x, y, k, color=(150, 96, 66)):
    """Huella digital: arcos con cortes, cerrados arriba y abiertos abajo."""
    for i in range(9):
        rx, ry = (18 + i * 17) * k, (26 + i * 21) * k
        a0 = 150 + (i * 37) % 30
        a1 = 390 - (i * 23) % 40
        c.arco(x, y, rx, ry, a0, a1, color, 8 * k)
    for i in range(4):   # líneas de abajo
        yy = y + (60 + i * 26) * k
        c.arco(x, yy - 40 * k, (70 + i * 26) * k, 60 * k, 40, 140, color, 8 * k)


def lupa(c, x, y, k):
    B = (40, 40, 60)
    c.linea([(x + 58 * k, y + 58 * k), (x + 120 * k, y + 120 * k)], B, 26 * k)
    c.circulo(x, y, 82 * k, fill=(220, 240, 255, 90), borde=B, grosor=14 * k)
    c.arco(x, y, 60 * k, 60 * k, 200, 250, (255, 255, 255, 200), 8 * k)


def koala(c, x, y, k, t):
    G, B, CL = (150, 152, 168), (62, 62, 80), (226, 222, 232)
    for s in (-1, 1):
        c.circulo(x + s * 122 * k, y - 84 * k, 74 * k, fill=G, borde=B, grosor=6 * k)
        c.circulo(x + s * 122 * k, y - 80 * k, 46 * k, fill=CL)
    c.circulo(x, y, 138 * k, fill=G, borde=B, grosor=6 * k)
    c.elipse(x, y + 58 * k, 96 * k, 60 * k, fill=(176, 178, 192))
    parpadea = (t % 3.3) < 0.13
    for s in (-1, 1):
        ex, ey = x + s * 56 * k, y - 22 * k
        if parpadea:
            c.linea([(ex - 13 * k, ey), (ex + 13 * k, ey)], (25, 20, 30), 6 * k)
        else:
            c.circulo(ex, ey, 14 * k, fill=(25, 20, 30))
            c.circulo(ex + 4 * k, ey - 5 * k, 4.5 * k, fill=(255, 255, 255))
    c.elipse(x, y + 24 * k, 40 * k, 54 * k, fill=(46, 40, 58))
    c.elipse(x - 12 * k, y + 2 * k, 10 * k, 15 * k, fill=(112, 106, 130))
    c.arco(x, y + 82 * k, 22 * k, 13 * k, 20, 160, (70, 58, 80), 5 * k)


def sirena(c, x, y, k, t):
    rojo = (t * 6) % 2 < 1
    c.rrect(x - 60 * k, y + 20 * k, x + 60 * k, y + 44 * k, 8 * k, fill=(60, 60, 80))
    c.elipse(x, y + 20 * k, 50 * k, 56 * k, fill=(240, 50, 60) if rojo else (50, 110, 255))
    c.rrect(x - 50 * k, y + 20 * k, x + 50 * k, y + 30 * k, 2, fill=(60, 60, 80))
    c.elipse(x - 16 * k, y - 4 * k, 10 * k, 18 * k, fill=(255, 255, 255, 170))


def sol(c, x, y, r, t):
    for i in range(12):
        a = t * 0.4 + i * math.pi / 6
        p = [(x + math.cos(a) * r * 1.15, y + math.sin(a) * r * 1.15),
             (x + math.cos(a + 0.12) * r * 1.5, y + math.sin(a + 0.12) * r * 1.5),
             (x + math.cos(a + 0.24) * r * 1.15, y + math.sin(a + 0.24) * r * 1.15)]
        c.poligono(p, fill=(255, 200, 60))
    c.circulo(x, y, r, fill=(255, 180, 40))
    c.circulo(x - r * 0.12, y - r * 0.12, r * 0.82, fill=(255, 214, 80))


def tierra(c, x, y, r):
    c.circulo(x, y, r, fill=(50, 120, 230), borde=(200, 230, 255), grosor=4)
    for dx, dy, rr in ((-0.3, -0.3, 0.35), (0.25, 0.1, 0.42), (-0.2, 0.45, 0.25), (0.45, -0.45, 0.18)):
        c.circulo(x + dx * r, y + dy * r, rr * r, fill=(70, 180, 100))
    c.arco(x, y, r * 0.8, r * 0.8, 200, 250, (255, 255, 255, 170), r * 0.08)


def nube(c, x, y, k, color=(255, 255, 255), sombra=(196, 218, 245), cara=True, sorpresa=0.0):
    bolas = [(-150, 20, 80), (-80, -30, 100), (20, -62, 118), (122, -18, 96), (182, 26, 70), (40, 30, 96),
             (-60, 36, 88)]
    for dx, dy, r in bolas:
        c.circulo(x + dx * k, y + dy * k + 12 * k, r * k, fill=sombra)
    for dx, dy, r in bolas:
        c.circulo(x + dx * k, y + dy * k, r * k, fill=color)
    c.rrect(x - 205 * k, y + 8 * k, x + 225 * k, y + 96 * k, 44 * k, fill=color)
    if cara:
        ojo = 11 * k * (1 + 0.5 * sorpresa)
        for s in (-1, 1):
            c.circulo(x + 10 * k + s * 48 * k, y + 10 * k, ojo, fill=(40, 50, 80))
            c.circulo(x + 13 * k + s * 48 * k, y + 6 * k, ojo * 0.35, fill=(255, 255, 255))
        if sorpresa > 0.5:
            c.elipse(x + 10 * k, y + 52 * k, 14 * k, 18 * k, fill=(40, 50, 80))
        else:
            c.arco(x + 10 * k, y + 38 * k, 26 * k, 16 * k, 20, 160, (40, 50, 80), 6 * k)
        for s in (-1, 1):
            c.circulo(x + 10 * k + s * 88 * k, y + 40 * k, 16 * k, fill=(255, 170, 190, 150))


def elefante(c, x, y, k):
    """Elefante de costado, mirando a la izquierda; (x, y) = centro del cuerpo."""
    G, B, CL = (152, 162, 180), (70, 76, 98), (178, 188, 204)
    for dx in (-70, -30, 38, 78):
        c.rrect(x + (dx - 18) * k, y + 18 * k, x + (dx + 18) * k, y + 108 * k, 9 * k, fill=G, borde=B, grosor=5 * k)
    c.linea([(x + 110 * k, y - 16 * k), (x + 140 * k, y + 34 * k)], B, 7 * k)
    c.elipse(x + 6 * k, y, 118 * k, 80 * k, fill=G, borde=B, grosor=6 * k)
    trompa = [(x - 150 * k, y - 26 * k), (x - 176 * k, y + 22 * k), (x - 170 * k, y + 76 * k), (x - 146 * k, y + 96 * k)]
    c.linea(trompa, B, 40 * k)
    c.linea(trompa, G, 28 * k)
    c.circulo(x - 108 * k, y - 34 * k, 64 * k, fill=G, borde=B, grosor=6 * k)
    c.elipse(x - 70 * k, y - 26 * k, 42 * k, 56 * k, fill=CL, borde=B, grosor=5 * k)
    c.circulo(x - 132 * k, y - 50 * k, 8 * k, fill=(20, 20, 30))
    c.linea([(x - 150 * k, y + 2 * k), (x - 128 * k, y + 16 * k)], (250, 248, 240), 9 * k)


def igual(fr, x, y, s):
    """Signo "=" dibujado (la tipografía de títulos no lo trae bien)."""
    if s <= 0:
        return
    c = Capa(int(x - 70), int(y - 60), 140, 120)
    for dy in (-20, 20):
        c.rrect(x - 44 * s, y + dy * s - 11 * s, x + 44 * s, y + dy * s + 11 * s, 9 * s, fill=(255, 255, 255),
                borde=(24, 16, 48), grosor=5 * s)
    c.pegar_en(fr)


# ============================================================ dibujos por pregunta
def dibujo_koala(fr, t, ev):
    tr = ev["revela"]
    mueve = e_in_out(prog(t, tr, 0.45))
    s = e_back(prog(t, ev["t0"] + 0.35, 0.5))
    if s <= 0:
        return
    c = Capa(0, 500, W, 520)
    hx, hk = lerp(540, 300, mueve), lerp(1.0, 0.72, mueve) * s
    c.circulo(hx, 770, 196 * hk, fill=(255, 246, 232), borde=(150, 96, 66), grosor=8 * hk)
    huella(c, hx, 770, hk)
    if t < tr:   # la lupa recorre la huella
        a = (t - ev["t0"]) * 1.6
        lupa(c, 540 + 90 * math.cos(a), 740 + 60 * math.sin(a), s)
    sk = e_back(prog(t, tr + 0.1, 0.5))
    if sk > 0:
        koala(c, 790, 780, 0.95 * sk, t)
    c.pegar_en(fr)
    si = pop(t, ev["revela"] + 0.35, 0.35)
    if si > 0:
        igual(fr, 548, 780, si)
    sc = pop(t, E["k_parecidas"], 0.35)
    if sc > 0:
        componer(fr, cartel("CASI IDÉNTICAS", None, (255, 255, 255), (30, 90, 60), 520, 70), 540, 590,
                 escala=sc, rot=-3)
    tp = E["k_policia"]
    if tp <= t < tp + 1.6:
        luz = spr_resplandor(420, (240, 50, 60) if (t * 6) % 2 < 1 else (50, 110, 255))
        alfa = 0.7 * (1 - prog(t, tp + 1.0, 0.6))
        componer(fr, luz, 60, 700, alpha=alfa)
        componer(fr, luz, W - 60, 700, alpha=alfa)
        c = Capa(700, 520, 180, 150)
        sirena(c, 790, 580, pop(t, tp, 0.3), t)
        c.pegar_en(fr)


def dibujo_luz(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    sx, tx, y = 200, 900, 780
    componer(fr, spr_resplandor(260, (255, 190, 80)), sx, y, alpha=0.7)
    c = Capa(0, 520, W, 480)
    for xx in range(sx + 150, tx - 80, 36):   # camino de la luz
        c.linea([(xx, y), (xx + 14, y)], (255, 240, 200, 150), 5, puntas=False)
    sol(c, sx, y, 100 * s, t)
    llega = e_in_out(prog(t, tr - 0.15, 0.4))
    tierra(c, tx, y, 64 * s * (1 + 0.12 * math.sin(math.pi * llega)))
    c.pegar_en(fr)
    # el pulso de luz viaja; con la respuesta, llega a la Tierra
    if t < tr + 0.3:
        u = ((t - ev["t0"]) / 2.4) % 1 if t < tr - 0.4 else lerp(((tr - 0.4 - ev["t0"]) / 2.4) % 1, 1, llega)
        px = lerp(sx + 120, tx - 70, u)
        componer(fr, spr_resplandor(70, (255, 250, 200)), px, y, alpha=0.9 * (1 - prog(t, tr + 0.1, 0.2)))
    if t >= tr:
        componer(fr, spr_resplandor(180, (255, 250, 210)), tx, y, alpha=0.8 * (1 - prog(t, tr + 0.2, 0.8)))
    sq = pop(t, ev["opc"], 0.3) * (1 - pop(t, tr - 0.05, 0.2))
    if sq > 0.01:
        componer(fr, texto("?", "titulo", 110, color=(255, 240, 180), borde=8), 550, 680, escala=sq)
    sc = pop(t, tr + 0.1, 0.35)
    if sc > 0:
        componer(fr, cartel("8 MIN 20 S", "DEL SOL A LA TIERRA", (255, 214, 80), (60, 30, 10), 460, 90), 550, 620,
                 escala=sc, rot=-3)
    sh = pop(t, E["l_hace"], 0.35)
    if sh > 0:
        componer(fr, cartel("HACE 8 MIN", None, (255, 255, 255), (120, 60, 10), 300, 56), sx, 935, escala=sh, rot=4)


def dibujo_nube(fr, t, ev):
    tr = ev["revela"]
    s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
    if s <= 0:
        return
    mueve = e_in_out(prog(t, tr, 0.45))
    nx, ny = lerp(540, 300, mueve), lerp(690, 700, mueve) + 10 * math.sin(t * 1.8)
    nk = lerp(1.05, 0.72, mueve) * s
    c = Capa(0, 460, W, 560)
    if t < tr:   # etiqueta colgando: ¿cuánto pesa?
        c.linea([(nx, ny + 90 * nk), (nx, ny + 150 * nk)], (60, 70, 100), 4)
    nube(c, nx, ny, nk, sorpresa=clamp01((t - tr) / 0.2))
    se = e_back(prog(t, E["n_elefantes"] - 0.15, 0.5))
    if se > 0:
        elefante(c, 810, 700, 0.9 * se)
    c.pegar_en(fr)
    if t < tr:
        componer(fr, cartel("¿KILOS?", None, (40, 60, 100), (255, 255, 255), 250, 60), nx, ny + 190 * nk,
                 escala=s, rot=4 * math.sin(t * 2))
    si = pop(t, E["n_elefantes"] - 0.05, 0.35)
    if si > 0:
        igual(fr, 555, 700, si)
        componer(fr, cartel("×100", None, (255, 255, 255), (70, 76, 98), 140, 46), 930, 590, escala=si, rot=6)
    sc = pop(t, E["n_toneladas"] - 0.05, 0.35)
    if sc > 0:
        componer(fr, cartel("500 TONELADAS", None, (255, 255, 255), (30, 70, 150), 520, 70), 540, 905,
                 escala=sc, rot=-2)


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


# ======================================================= íconos del cierre
def _icono_koala(c, x, y, s, t):
    koala(c, x, y + 14 * s, 0.6 * s, t)


def _icono_sol(c, x, y, s, t):
    sol(c, x, y, 62 * s, t)


def _icono_nube(c, x, y, s, t):
    nube(c, x - 6 * s, y - 6 * s, 0.42 * s, sombra=(170, 200, 240))


ICONOS = [_icono_koala, _icono_sol, _icono_nube]
ESCENAS = {
    "gancho": lambda t: quiz.escena_gancho(t, E, FONDOS, "3 SEGUNDOS CADA UNA"),
    "p1": quiz.escena_pregunta("p1", 1, 3, "eucalipto", dibujo_koala, ACENTO["p1"], E, ESC, POR_ID, FONDOS),
    "p2": quiz.escena_pregunta("p2", 2, 3, "espacio", dibujo_luz, ACENTO["p2"], E, ESC, POR_ID, FONDOS),
    "p3": quiz.escena_pregunta("p3", 3, 3, "cielo", dibujo_nube, ACENTO["p3"], E, ESC, POR_ID, FONDOS),
}
