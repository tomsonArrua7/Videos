"""Episodio 9: curiosidades de tu cuerpo — el primero pensado para voz humana.

Si existe grabaciones/ep09.<m4a|mp3|ogg|wav...>, voz.py usa esa grabación
(limpia y sincronizada por grabacion.py). Si no, usa la voz de Tomás.
"""
import math

import numpy as np
from PIL import Image, ImageFilter

from dibujo import (H, W, Capa, a_imagen, cartel, chispas, componer, e_back, e_in_out, e_out, encabezado,
                    gradiente, lerp, mezcla, pildora, pop, prog, resplandor, spr_estrella, tachar, texto,
                    titulo, viñeta)

SLUG = "cuerpo_humano"
DURACION = 30.0
GRABACION = "grabaciones/ep09"      # tu voz (cualquier extensión de audio)
VOZ = "es-AR-TomasNeural"            # solo si falta la grabación
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
GANCHO_ETIQUETA = "DE TU CUERPO"
PALABRAS_CIERRE = ("abajo", "seguinos")

# Escrito para leer en voz alta: frases cortas, sin nombres en inglés y con los
# números en palabras. Cada bloque se lee de un tirón; entre bloques, una pausa.
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades de tu cuerpo que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE TU CUERPO",
    },
    {
        "id": "altura",
        "texto": "Uno: a la mañana sos más alto que a la noche. "
                 "¡Durante el día, la columna se achica hasta un centímetro!",
        "titulo": "MÁS ALTO A LA MAÑANA",
        "subtitulo": "A LA MAÑANA SOS MÁS ALTO",
    },
    {
        "id": "huesos",
        "texto": "Dos: los bebés nacen con unos trescientos huesos. ¡Con los años se unen y quedan doscientos seis!",
        "titulo": "HUESOS",
        "subtitulo": "¡LOS HUESOS SE UNEN!",
    },
    {
        "id": "brillo",
        "texto": "Tres: tu cuerpo brilla en la oscuridad, pero con una luz mil veces más débil "
                 "de lo que pueden ver tus ojos.",
        "titulo": "BRILLÁS EN LA OSCURIDAD",
        "subtitulo": "¡TU CUERPO BRILLA!",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"altura": (255, 180, 60), "huesos": (120, 190, 255),
          "brillo": (120, 255, 170), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
HUESO, HUESO_B = (250, 244, 228), (160, 140, 110)


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "a_manana": L.palabra("altura", "mañana"),
        "a_noche": L.palabra("altura", "noche"),
        "a_columna": L.palabra("altura", "columna"),
        "a_achica": L.palabra("altura", "achica"),
        "a_centimetro": L.palabra("altura", "centímetro"),
        "h_trescientos": L.palabra("huesos", "trescientos"),
        "h_unen": L.palabra("huesos", "unen"),
        "h_doscientos": L.palabra("huesos", "doscientos"),
        "h_fin": L.fin_palabra("huesos", "seis"),
        "b_brilla": L.palabra("brillo", "brilla"),
        "b_mil": L.palabra("brillo", "mil"),
        "b_ojos": L.palabra("brillo", "ojos"),
    }


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    fx = [(E["a_manana"] - 0.2, S.pajaritos(1.3), 0.10), (E["a_noche"], S.grillos(1.6), 0.08),
          (E["a_achica"], S.subida(0.5, 500, 220), 0.20), (E["a_centimetro"] + 0.2, S.ding(), 0.22),
          (E["h_trescientos"], S.pop(900, 400), 0.28)]
    for i in range(12):
        fx.append((E["h_unen"] + i * (E["h_fin"] - E["h_unen"]) / 12, S.pop(1200 - 30 * i, 500, 0.06), 0.10))
    fx += [(E["h_fin"], S.ding(), 0.22),
           (E["b_brilla"], S.brillo_sfx(), 0.25), (E["b_mil"], S.pop(700, 300), 0.22),
           (E["b_ojos"], S.error_(), 0.15)]
    return fx


def sacudidas(E):
    return []


# ==================================================================== fondos
def fondo_dia():
    a = gradiente([(0, (110, 190, 250)), (0.6, (200, 232, 255)), (0.72, (160, 210, 120)), (1, (110, 170, 80))])
    resplandor(a, 220, 620, 260, (255, 250, 210), 0.6)
    return a_imagen(a, 70)


def fondo_noche():
    a = gradiente([(0, (10, 16, 50)), (0.6, (34, 44, 100)), (0.72, (30, 60, 50)), (1, (18, 40, 30))])
    resplandor(a, 860, 620, 240, (190, 200, 255), 0.35)
    img = a_imagen(a, 71)
    rng = np.random.default_rng(72)
    for _ in range(80):
        componer(img, spr_estrella(int(rng.integers(2, 6))), rng.uniform(0, W), rng.uniform(0, 1300),
                 alpha=rng.uniform(0.3, 0.9))
    return img


def fondo_huesos():
    a = gradiente([(0, (206, 226, 255)), (0.6, (236, 222, 250)), (1, (250, 214, 232))])
    img = a_imagen(a, 73)
    c = Capa(0, 0, W, H, ss=1)
    rng = np.random.default_rng(74)
    for _ in range(40):
        c.circulo(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(10, 40), fill=(255, 255, 255, 60))
    c.pegar_en(img)
    return img


def fondo_brillo():
    a = gradiente([(0, (6, 8, 20)), (0.5, (10, 14, 30)), (1, (4, 6, 14))])
    viñeta(a, 0.6)
    return a_imagen(a, 75)


def preparar():
    FONDOS.update(dia=fondo_dia(), noche=fondo_noche(), huesos=fondo_huesos(), brillo=fondo_brillo())


# ================================================================ elementos
def silueta(c, x, y, k, fill, borde=None, grosor=0, estira=1.0):
    """Persona genérica de frente; (x, y) = cintura. `estira` achica el torso (columna)."""
    torso = 270 * k * estira
    cab = (x, y - torso - 92 * k)
    for s in (-1, 1):   # piernas y brazos
        c.linea([(x + s * 40 * k, y), (x + s * 48 * k, y + 330 * k)], fill if not borde else borde, 62 * k + grosor)
        c.linea([(x + s * 104 * k, y - torso + 24 * k), (x + s * 132 * k, y - 20 * k)], fill if not borde else borde,
                46 * k + grosor)
    if borde:
        for s in (-1, 1):
            c.linea([(x + s * 40 * k, y), (x + s * 48 * k, y + 330 * k)], fill, 62 * k - grosor)
            c.linea([(x + s * 104 * k, y - torso + 24 * k), (x + s * 132 * k, y - 20 * k)], fill, 46 * k - grosor)
    c.poligono([(x - 120 * k, y - torso), (x + 120 * k, y - torso), (x + 86 * k, y + 20 * k), (x - 86 * k, y + 20 * k)],
               fill=fill, borde=borde, grosor=grosor)
    c.rrect(x - 30 * k, y - torso - 40 * k, x + 30 * k, y - torso + 10 * k, 12 * k, fill=fill)
    c.circulo(*cab, 78 * k, fill=fill, borde=borde, grosor=grosor)
    return cab


def columna(c, x, y_base, k, apriete):
    """Vértebras con discos rosados que se aplastan (`apriete` 0..1). Devuelve la altura de la cima."""
    y = y_base
    for i in range(8):
        disco = (20 - 11 * apriete) * k
        y -= disco
        c.elipse(x, y + disco / 2, 46 * k, disco / 2 + 2, fill=(255, 150, 176), borde=(200, 90, 120), grosor=2)
        alto = 26 * k
        y -= alto
        c.rrect(x - 52 * k, y, x + 52 * k, y + alto, 10 * k, fill=HUESO, borde=HUESO_B, grosor=3)
        c.circulo(x + 58 * k, y + alto / 2, 9 * k, fill=HUESO, borde=HUESO_B, grosor=2)
        c.circulo(x - 58 * k, y + alto / 2, 9 * k, fill=HUESO, borde=HUESO_B, grosor=2)
    return y


def regla(c, x, y0, y1, marca):
    c.rrect(x - 40, y0 - 20, x + 40, y1 + 20, 10, fill=(250, 226, 150), borde=(140, 100, 40), grosor=4)
    for i, yy in enumerate(np.linspace(y0, y1, 31)):
        largo = 34 if i % 5 == 0 else 18
        c.linea([(x - 40, yy), (x - 40 + largo, yy)], (120, 80, 30), 3, puntas=False)
    c.poligono([(x + 44, marca), (x + 90, marca - 22), (x + 90, marca + 22)], fill=(230, 40, 60))


def hueso(c, x, y, k, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    a, b = (x - 34 * k * ca, y - 34 * k * sa), (x + 34 * k * ca, y + 34 * k * sa)
    for col, extra in ((HUESO_B, 3), (HUESO, 0)):
        c.linea([a, b], col, 18 * k + extra * 2)
        for px, py in (a, b):
            for s in (-1, 1):
                c.circulo(px - s * 9 * k * sa, py + s * 9 * k * ca, 11 * k + extra, fill=col)


def mamadera(c, x, y, k=1.0):
    B = (90, 90, 120)
    c.elipse(x, y - 118 * k, 18 * k, 26 * k, fill=(250, 200, 140), borde=B, grosor=3 * k)
    c.rrect(x - 42 * k, y - 104 * k, x + 42 * k, y - 76 * k, 8 * k, fill=(120, 180, 255), borde=B, grosor=3 * k)
    c.rrect(x - 50 * k, y - 80 * k, x + 50 * k, y + 90 * k, 26 * k, fill=(240, 248, 255), borde=B, grosor=4 * k)
    c.rrect(x - 44 * k, y - 10 * k, x + 44 * k, y + 84 * k, 22 * k, fill=(255, 255, 255))
    for i in range(4):
        c.linea([(x - 44 * k, y - 50 * k + i * 30 * k), (x - 20 * k, y - 50 * k + i * 30 * k)], B, 3 * k, puntas=False)


def ojo(c, x, y, k, t):
    B = (30, 30, 50)
    mira = 18 * math.sin(t * 1.3)
    c.poligono([(x - 110 * k + 220 * k * u, y - 62 * k * math.sin(math.pi * u)) for u in np.linspace(0, 1, 20)] +
               [(x + 110 * k - 220 * k * u, y + 62 * k * math.sin(math.pi * u)) for u in np.linspace(0, 1, 20)],
               fill=(255, 255, 255), borde=B, grosor=6 * k)
    c.circulo(x + mira * k, y, 44 * k, fill=(90, 150, 220), borde=B, grosor=4 * k)
    c.circulo(x + mira * k, y, 22 * k, fill=(10, 10, 20))
    c.circulo(x + mira * k + 12 * k, y - 12 * k, 8 * k, fill=(255, 255, 255))


# =================================================================== escenas
def escena_altura(t):
    t0 = ESC["altura"]["escena_ini"]
    noche = e_in_out(prog(t, E["a_noche"] - 0.2, 0.9))
    fr = Image.blend(FONDOS["dia"], FONDOS["noche"], noche) if 0 < noche < 1 else \
        (FONDOS["noche"] if noche >= 1 else FONDOS["dia"]).copy()
    c = Capa(0, 520, W, 1000)
    # el sol baja y sale la luna
    sx, sy = lerp(220, -120, noche), lerp(640, 900, noche)
    c.circulo(sx, sy, 80, fill=(255, 220, 90))
    mx, my = lerp(1200, 860, noche), lerp(900, 640, noche)
    c.circulo(mx, my, 66, fill=(236, 240, 255))
    c.circulo(mx + 26, my - 14, 58, fill=mezcla((236, 240, 255), (34, 44, 100), 0.9))
    # la persona (con la columna a la vista) se achica durante el día
    apriete = e_in_out(prog(t, E["a_columna"] - 0.2, E["a_centimetro"] - E["a_columna"] + 0.4))
    estira = 1 - 0.14 * apriete
    s = e_back(prog(t, t0 + 0.15, 0.5))
    if s > 0:
        cintura = 1260
        cab = silueta(c, 470, cintura, 0.9 * s, (140, 200, 250, 150), (60, 110, 170, 220), 5, estira)
        columna(c, 470, cintura - 16, 0.64 * s, apriete)
        # regla con la marca de la altura (cima de la cabeza)
        tope = cab[1] - 78 * 0.9 * s
        regla(c, 800, 720, 1380, tope)
        if t >= E["a_achica"]:  # dónde estaba la cabeza a la mañana
            tope0 = cintura - (270 + 92 + 78) * 0.9 * s
            for xx in range(380, 760, 28):
                c.linea([(xx, tope0), (xx + 14, tope0)], (255, 255, 255, 200), 5, puntas=False)
    c.pegar_en(fr)
    sm = pop(t, E["a_centimetro"], 0.35)
    if sm > 0:
        componer(fr, cartel("-1 CM", "AL FINAL DEL DÍA", (255, 90, 110), (60, 10, 20), 300, 90), 770, 640,
                 escala=sm, rot=6)
    encabezado(fr, t, 1, E["altura_badge"])
    titulo(fr, t, TITULOS["altura"]["titulo"], t0 + 0.15, tam=110, color=(255, 236, 150))
    pildora(fr, t, TITULOS["altura"]["subtitulo"], (230, 140, 20), E["a_manana"], hasta=E["a_achica"])
    pildora(fr, t, "¡LA COLUMNA SE ACHICA!", (200, 60, 90), E["a_achica"] + 0.05)
    return fr


def escena_huesos(t):
    fr = FONDOS["huesos"].copy()
    t0 = ESC["huesos"]["escena_ini"]
    tu, tf = E["h_unen"], E["h_fin"]
    rng = np.random.default_rng(5)
    n = 30
    pos = [(rng.uniform(170, 910), rng.uniform(800, 1340), rng.uniform(0, 6)) for _ in range(n)]
    fusion = e_in_out(prog(t, tu, tf - tu + 0.2))
    c = Capa(0, 560, W, 900)
    s = e_back(prog(t, t0 + 0.2, 0.5))
    for i, (x, y, a) in enumerate(pos):
        # los huesos se juntan de a pares: la mitad "se une" con su pareja
        pareja = pos[(i + 1) % n] if i % 2 == 0 else pos[i - 1]
        mx, my = (x + pareja[0]) / 2, (y + pareja[1]) / 2
        orden = (i // 2) / (n // 2)
        u = clamp_((fusion - orden * 0.6) / 0.4)
        if i % 2 == 1 and u >= 1:
            continue
        px, py = lerp(x, mx, u) + 8 * math.sin(t * 2 + i), lerp(y, my, u) + 8 * math.cos(t * 1.7 + i)
        hueso(c, px, py, (0.9 + 0.35 * (u if i % 2 == 0 else 0)) * s, a + t * 0.3 * (1 if i % 2 else -1))
    etapa = "ADULTO" if fusion > 0.5 else "BEBÉ"
    if etapa == "BEBÉ":
        mamadera(c, 170, 700, 0.8 * s)
    c.pegar_en(fr)
    sc = pop(t, E["h_trescientos"], 0.4)
    if sc > 0:
        nhuesos = int(round(lerp(300, 206, fusion)))
        componer(fr, cartel(f"{nhuesos} HUESOS", etapa, (255, 240, 150), (40, 70, 140), 480, 96), 580, 660,
                 escala=sc, rot=-2)
    encabezado(fr, t, 2, E["huesos_badge"])
    titulo(fr, t, TITULOS["huesos"]["titulo"], t0 + 0.15, color=(255, 255, 255))
    pildora(fr, t, TITULOS["huesos"]["subtitulo"], (60, 130, 220), tu, hasta=E["h_doscientos"])
    pildora(fr, t, "DE GRANDE QUEDAN 206", (130, 80, 200), E["h_doscientos"])
    return fr


def clamp_(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def escena_brillo(t):
    fr = FONDOS["brillo"].copy()
    t0 = ESC["brillo"]["escena_ini"]
    tb, tm, to = E["b_brilla"], E["b_mil"], E["b_ojos"]
    luz = e_out(prog(t, tb, 0.6))
    s = e_back(prog(t, t0 + 0.2, 0.5))
    x0, y0 = 380, 1090
    if luz > 0:  # resplandor (exagerado): más fuerte en la cara, como midió el estudio
        capa = Capa(80, 540, 600, 920, ss=1)
        silueta(capa, x0, y0, 0.8, (140, 255, 190, int(200 * luz)))
        capa.circulo(x0, y0 - 0.8 * 270 - 0.8 * 92, 110, fill=(200, 255, 220, int(230 * luz)))
        im = capa.imagen().filter(ImageFilter.GaussianBlur(26))
        fr.alpha_composite(im, (80, 540))
    c = Capa(80, 540, 600, 920)
    silueta(c, x0, y0, 0.8 * s, (18, 24, 40), mezcla((70, 80, 110), (180, 255, 210), luz), 4)
    c.pegar_en(fr)
    if luz > 0.5:
        componer(fr, texto("(EXAGERADO)", "negra", 26, color=(160, 220, 190)), x0, 1470 - 60)
    # el ojo que no llega a ver ese brillo
    so = pop(t, t0 + 0.4, 0.4)
    if so > 0:
        c = Capa(640, 700, 400, 260)
        ojo(c, 840, 830, 0.95 * so, t)
        tachar(c, 840, 830, 200, e_back(prog(t, to, 0.3)), 20)
        c.pegar_en(fr)
    # comparación: lo que ve el ojo contra tu brillo (mil veces menos)
    sb = e_out(prog(t, tm, 0.5))
    if sb > 0:
        c = Capa(620, 980, 440, 260)
        c.rrect(660, 1010, 660 + 360 * sb, 1050, 12, fill=(120, 200, 255))
        c.rrect(660, 1130, 664, 1170, 2, fill=(140, 255, 190))
        c.pegar_en(fr)
        componer(fr, texto("LO QUE VEN TUS OJOS", "negra", 26, color=(200, 230, 255)), 840, 990, alpha=sb)
        componer(fr, texto("TU BRILLO", "negra", 26, color=(170, 255, 200)), 740, 1110, alpha=sb)
        componer(fr, cartel("×1000", "MÁS DÉBIL", (140, 255, 190), (10, 40, 30), 240, 70), 850, 1200,
                 escala=pop(t, tm + 0.3, 0.35), rot=-5)
    if tb <= t < tb + 1.0:
        chispas(fr, t, tb, x0, 800, n=16, seed=3, colores=((160, 255, 200), (255, 255, 255)), vel=(150, 400),
                grav=100, dur=1.0)
    encabezado(fr, t, 3, E["brillo_badge"])
    titulo(fr, t, TITULOS["brillo"]["titulo"], t0 + 0.15, tam=110, color=(170, 255, 200))
    pildora(fr, t, TITULOS["brillo"]["subtitulo"], (30, 150, 90), tb, hasta=tm)
    pildora(fr, t, "MIL VECES MÁS DÉBIL DE LO VISIBLE", (40, 90, 170), tm + 0.05)
    return fr


# ======================================================= íconos del cierre
def _icono_altura(c, x, y, s, t):
    columna(c, x, y + 80 * s, 0.7 * s, 0.3)


def _icono_huesos(c, x, y, s, t):
    hueso(c, x, y, 1.7 * s, -0.6)


def _icono_brillo(c, x, y, s, t):
    c.circulo(x, y, 118 * s, fill=(14, 20, 36))
    c.circulo(x, y - 30 * s, 44 * s, fill=(18, 24, 40), borde=(170, 255, 200), grosor=5 * s)
    c.poligono([(x - 70 * s, y + 90 * s), (x - 60 * s, y + 30 * s), (x + 60 * s, y + 30 * s), (x + 70 * s, y + 90 * s)],
               fill=(18, 24, 40), borde=(170, 255, 200), grosor=5 * s)


ICONOS = [_icono_altura, _icono_huesos, _icono_brillo]
ESCENAS = {"altura": escena_altura, "huesos": escena_huesos, "brillo": escena_brillo}
