"""Episodio 16: quiz de fútbol argentino — cinco clubes, cinco preguntas (voz de Tomás).

Camisetas genéricas con los colores de cada club (sin escudos ni logos), trofeos y un estadio.
"""
import math

import numpy as np

import quiz
from dibujo import (W, Capa, a_imagen, cartel, componer, e_back, gradiente, pop, prog, resplandor, viñeta)
from quiz import signo

SLUG = "quiz_futbol"
DURACION = 60.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
PALABRAS_CIERRE = ("abajo", "seguinos")
CIERRE_TITULO = ("¿CUÁNTAS", "ACERTASTE?")

BLOQUES = [
    {"id": "gancho", "texto": "¡Cinco preguntas de fútbol argentino, tres segundos cada una! ¿Cuántas acertás?",
     "titulo": "5 PREGUNTAS"},
    {"id": "f1", "texto": "Uno: ¿en qué club de Rosario jugó Messi de chico? [3s] "
                          "¡En {Newell's|Niúels}! Estuvo en las inferiores hasta los trece años.",
     "titulo": "MESSI", "pregunta": "¿En qué club de Rosario jugó Messi de chico?",
     "opciones": ["ROSARIO CENTRAL", "NEWELL'S", "TIRO FEDERAL"], "correcta": 1},
    {"id": "f2", "texto": "Dos: ¿cuál fue el primer club argentino campeón del mundo? [3s] "
                          "¡Racing! Le ganó al Celtic de Escocia en mil novecientos sesenta y siete.",
     "titulo": "CAMPEÓN DEL MUNDO", "pregunta": "¿Cuál fue el primer club argentino campeón del mundo?",
     "opciones": ["RACING", "BOCA", "ESTUDIANTES"], "correcta": 0},
    {"id": "f3", "texto": "Tres: ¿qué club ganó más Copas Libertadores? [3s] ¡Independiente! Tiene siete, más que nadie.",
     "titulo": "LIBERTADORES", "pregunta": "¿Qué club ganó más Copas Libertadores?",
     "opciones": ["BOCA", "RIVER", "INDEPENDIENTE"], "correcta": 2},
    {"id": "f4", "texto": "Cuatro: ¿qué club argentino tiene el estadio más grande? [3s] "
                          "¡River! El Monumental es el más grande de Sudamérica.",
     "titulo": "EL ESTADIO", "pregunta": "¿Qué club argentino tiene el estadio más grande?",
     "opciones": ["BOCA", "RIVER", "RACING"], "correcta": 1},
    {"id": "f5", "texto": "Cinco: ¿qué club argentino le ganó al {Milan|Mílan} en Tokio en mil novecientos noventa y "
                          "cuatro? [3s] ¡Vélez! Ese año fue campeón del mundo.",
     "titulo": "TOKIO 1994", "pregunta": "¿Qué club argentino le ganó al Milan en Tokio en 1994?",
     "opciones": ["BOCA", "INDEPENDIENTE", "VÉLEZ"], "correcta": 2},
    {"id": "cierre", "texto": "¿Cuántas acertaste? Comentalo abajo y seguinos para más.",
     "titulo": "¿CUÁNTAS ACERTASTE?"},
]

PREGUNTAS = ["f1", "f2", "f3", "f4", "f5"]
ACENTO = {"f1": (200, 30, 40), "f2": (90, 170, 230), "f3": (210, 30, 40), "f4": (230, 40, 50),
          "f5": (40, 80, 180), "cierre": (255, 0, 110)}
POR_ID = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
TINTA = (24, 16, 48)

# Camiseta de cada respuesta (solo colores, sin escudos) y el cartel del dato
CLUBES = {
    "f1": ("mitades", (200, 30, 40), (20, 20, 24), "INFERIORES HASTA LOS 13"),
    "f2": ("bastones", (120, 190, 240), (255, 255, 255), "1967 · VS CELTIC"),
    "f3": ("lisa", (210, 30, 40), (255, 255, 255), "7 LIBERTADORES"),
    "f4": ("banda", (255, 255, 255), (230, 40, 50), "EL MÁS GRANDE DE SUDAMÉRICA"),
    "f5": ("v", (255, 255, 255), (40, 80, 180), "CAMPEÓN DEL MUNDO 1994"),
}


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {**quiz.eventos(L, PREGUNTAS), **quiz.eventos_gancho(L, "cinco", "fútbol")}


def efectos(E, L, S):
    fx = quiz.efectos(E, S, PREGUNTAS) + quiz.efectos_gancho(E, S)
    for q in PREGUNTAS:   # tribuna que festeja la respuesta
        fx += [(E[f"{q}_revela"] + 0.1, S.lluvia(1.2), 0.10), (E[f"{q}_revela"] + 0.7, S.pop(900, 400), 0.2)]
    return fx


def sacudidas(E):
    return quiz.sacudidas_gancho(E)


def momento_portada(E):
    return E["gq_acertas"] + 0.7


# ==================================================================== fondos
def fondo_gancho():
    a = gradiente([(0, (10, 40, 30)), (0.55, (30, 120, 70)), (1, (120, 190, 240))])
    resplandor(a, 540, 1000, 620, (200, 255, 210), 0.3)
    viñeta(a)
    return a_imagen(a, 160)


def fondo_cancha():
    a = gradiente([(0, (8, 12, 30)), (0.5, (20, 30, 60)), (0.51, (30, 120, 50)), (1, (20, 90, 40))])
    for x in (120, 960):
        resplandor(a, x, 300, 260, (255, 255, 230), 0.45)
    img = a_imagen(a, 161)
    c = Capa(0, 0, W, 1920, ss=1)
    for i in range(8):   # franjas del césped
        if i % 2 == 0:
            c.rrect(0, 980 + i * 120, W, 1100 + i * 120, 0, fill=(255, 255, 255, 18))
    for x in (120, 960):   # torres de luz
        c.linea([(x, 330), (x, 980)], (60, 60, 70), 10, puntas=False)
        c.rrect(x - 60, 270, x + 60, 330, 6, fill=(240, 240, 220))
    c.linea([(0, 980), (W, 980)], (255, 255, 255, 120), 6, puntas=False)
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(gancho=fondo_gancho(), cancha=fondo_cancha())


# ================================================================ dibujos
def camiseta(c, x, y, k, estilo, c1, c2):
    B = (30, 30, 40)
    cuerpo = [(x - 150 * k, y - 160 * k), (x - 60 * k, y - 190 * k), (x + 60 * k, y - 190 * k), (x + 150 * k, y - 160 * k),
              (x + 230 * k, y - 60 * k), (x + 160 * k, y), (x + 120 * k, y - 50 * k), (x + 120 * k, y + 190 * k),
              (x - 120 * k, y + 190 * k), (x - 120 * k, y - 50 * k), (x - 160 * k, y), (x - 230 * k, y - 60 * k)]
    c.poligono(cuerpo, fill=c1, borde=B, grosor=7 * k)
    if estilo == "mitades":
        c.poligono([(x, y - 190 * k), (x + 60 * k, y - 190 * k), (x + 150 * k, y - 160 * k), (x + 230 * k, y - 60 * k),
                    (x + 160 * k, y), (x + 120 * k, y - 50 * k), (x + 120 * k, y + 190 * k), (x, y + 190 * k)], fill=c2)
    elif estilo == "bastones":
        for dx in (-90, -30, 30, 90):
            c.rrect(x + (dx - 15) * k, y - 185 * k, x + (dx + 15) * k, y + 188 * k, 0, fill=c2)
    elif estilo == "banda":
        c.poligono([(x - 120 * k, y - 120 * k), (x - 60 * k, y - 175 * k), (x + 120 * k, y + 110 * k),
                    (x + 120 * k, y + 185 * k)], fill=c2)
    elif estilo == "v":
        c.poligono([(x - 120 * k, y - 175 * k), (x - 70 * k, y - 175 * k), (x, y - 40 * k), (x + 70 * k, y - 175 * k),
                    (x + 120 * k, y - 175 * k), (x, y + 30 * k)], fill=c2)
    c.poligono(cuerpo, borde=B, grosor=7 * k)
    c.arco(x, y - 190 * k, 60 * k, 40 * k, 0, 180, B, 8 * k)


def trofeo(c, x, y, k):
    G, B = (250, 200, 60), (150, 100, 20)
    c.rrect(x - 70 * k, y + 80 * k, x + 70 * k, y + 120 * k, 8 * k, fill=(90, 60, 30))
    c.rrect(x - 20 * k, y + 20 * k, x + 20 * k, y + 84 * k, 6 * k, fill=G, borde=B, grosor=4 * k)
    for s in (-1, 1):
        c.arco(x + s * 70 * k, y - 50 * k, 34 * k, 40 * k, 0, 360, B, 10 * k)
    c.poligono([(x - 80 * k, y - 110 * k), (x + 80 * k, y - 110 * k), (x + 50 * k, y + 10 * k), (x - 50 * k, y + 10 * k)],
               fill=G, borde=B, grosor=5 * k)
    c.arco(x - 30 * k, y - 60 * k, 20 * k, 40 * k, 150, 220, (255, 245, 200), 6 * k)


def pelota(c, x, y, r):
    c.circulo(x, y, r, fill=(255, 255, 255), borde=(30, 30, 40), grosor=r * 0.08)
    c.poligono([(x + math.cos(a) * r * 0.35, y + math.sin(a) * r * 0.35)
                for a in np.linspace(-math.pi / 2, 1.5 * math.pi, 6)[:-1]], fill=(30, 30, 40))


def dibujo_club(q):
    estilo, c1, c2, dato = CLUBES[q]

    def dibujo(fr, t, ev):
        tr = ev["revela"]
        s = e_back(prog(t, ev["t0"] + 0.3, 0.5))
        if s <= 0:
            return
        c = Capa(0, 460, W, 560)
        if t < tr:   # camiseta gris misteriosa
            camiseta(c, 540, 760, 0.95 * s, "lisa", (150, 150, 160), (150, 150, 160))
        else:
            sr = e_back(prog(t, tr, 0.4))
            camiseta(c, 540, 760, 0.95 * sr, estilo, c1, c2)
            st = e_back(prog(t, tr + 0.5, 0.4))
            if st > 0:
                if q == "f3":
                    for i in range(7):
                        trofeo(c, 150 + i * 130, 925, 0.38 * st)
                elif q in ("f2", "f5"):
                    trofeo(c, 850, 860, 0.8 * st)
                else:
                    pelota(c, 860, 900 - 60 * abs(math.sin((t - tr) * 5)), 50 * st)
        c.pegar_en(fr)
        signo(fr, t, ev["t0"] + 0.4, tr - 0.1, 540, 760, 160)
        sc = pop(t, tr + 0.6, 0.35)
        if sc > 0:
            componer(fr, cartel(dato, None, (255, 255, 255), (30, 40, 80), 520, 60), 540, 565, escala=sc, rot=-3)
    return dibujo


# ======================================================= íconos del cierre
def _icono(q):
    estilo, c1, c2, _ = CLUBES[q]
    return lambda c, x, y, s, t: camiseta(c, x, y + 10 * s, 0.42 * s, estilo, c1, c2)


ICONOS = [_icono(q) for q in PREGUNTAS]
ESCENAS = {
    "gancho": lambda t: quiz.escena_gancho(t, E, FONDOS, "FÚTBOL ARGENTINO", titulo="5 PREGUNTAS"),
    **{q: quiz.escena_pregunta(q, i + 1, 5, "cancha", dibujo_club(q), ACENTO[q], E, ESC, POR_ID, FONDOS)
       for i, q in enumerate(PREGUNTAS)},
}
