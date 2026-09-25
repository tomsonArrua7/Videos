"""Episodio 7: más curiosidades de películas (voz de Tomás, Argentina).

Las imágenes usan objetos y guiños genéricos (un proyector, un pez payaso
cualquiera, varitas y una batería), nunca personajes o logos con derechos de autor.
"""
import math

import numpy as np

from dibujo import (H, W, Capa, a_imagen, cartel, chispas, componer, e_back, e_out, elipse_rotada, encabezado,
                    gradiente, lerp, onda, parpadeo, pildora, pop, prog, rayos_luz, resplandor, spr_estrella,
                    spr_resplandor, texto, titulo, viñeta)

SLUG = "peliculas_2"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
GANCHO_ETIQUETA = "DE PELÍCULAS 2"
PALABRAS_CIERRE = ("abajo", "seguinos")

# Guion escrito para el oído. "Los sables" se escuchaba "los hables": en singular
# ("del sable") se entiende perfecto.
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Otras tres curiosidades de películas que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE PELÍCULAS 2",
    },
    {
        "id": "sable",
        "texto": "Uno: el sonido del sable de luz de {Star Wars|Estár Uórs} mezcla un proyector viejo y un televisor.",
        "pausa_despues": 0.5,   # lugar para que se encienda el sable
        "titulo": "STAR WARS",
        "subtitulo": "¿DE DÓNDE SALE ESE SONIDO?",
    },
    {
        "id": "nemo",
        "texto": "Dos: en la vida real, el papá de Nemo se habría convertido en hembra. "
                 "¡Los peces payaso pueden cambiar de sexo!",
        "titulo": "BUSCANDO A NEMO",
        "subtitulo": "LOS PECES PAYASO CAMBIAN DE SEXO",
    },
    {
        "id": "varitas",
        "texto": "Tres: Daniel Radcliffe rompió unas ochenta varitas filmando Harry Potter. "
                 "¡Las usaba como palillos de batería!",
        "titulo": "HARRY POTTER",
        "subtitulo": "¡LAS USABA COMO PALILLOS!",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"sable": (80, 150, 255), "nemo": (255, 140, 40),
          "varitas": (150, 90, 200), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS, EXTRA = {}, {}, {}, {}
SABLE = (90, 160, 255)
NARANJA, NEGRO_P = (255, 128, 30), (30, 20, 20)
PISO_V = 1420


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "s_sonido": L.palabra("sable", "sonido"),
        "s_proyector": L.palabra("sable", "proyector"),
        "s_televisor": L.palabra("sable", "televisor"),
        "s_enciende": L.fin_palabra("sable", "televisor") + 0.05,
        "n_papa": L.palabra("nemo", "papá"),
        "n_hembra": L.palabra("nemo", "hembra"),
        "n_payaso": L.palabra("nemo", "payaso"),
        "v_rompio": L.palabra("varitas", "rompió"),
        "v_ochenta": L.palabra("varitas", "ochenta"),
        "v_varitas": L.fin_palabra("varitas", "varitas"),
        "v_palillos": L.palabra("varitas", "palillos"),
    }


def _golpes(E):
    """Golpes de los palillos sobre el redoblante (alternados, cada 0,2 s)."""
    t, fin, out = E["v_palillos"] + 0.1, E["cierre_ini"] - 0.1, []
    while t < fin:
        out.append(t)
        t += 0.2
    return out


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    fx = [(E["s_proyector"], S.pop(700, 300), 0.22), (E["s_proyector"] + 0.1, S.proyector(1.2), 0.12),
          (E["s_televisor"], S.zapping_sfx(), 0.18), (E["s_enciende"], S.sable_sfx(1.1), 0.34),
          (E["n_papa"], S.pop(800, 300), 0.25), (E["n_hembra"], S.poof(), 0.35),
          (E["n_hembra"] + 0.1, S.brillo_sfx(), 0.25), (E["n_payaso"], S.pop(600, 250), 0.22)]
    fx += [(E["nemo_ini"] + 0.3 + 0.4 * i, S.bloop(), 0.10) for i in range(3)]
    fx += [(E["v_rompio"], S.quiebre(), 0.40)]
    t = E["v_ochenta"]
    while t < E["v_varitas"]:
        fx.append((t, S.tic(), 0.14))
        t += 0.06
    fx += [(E["v_ochenta"] + 0.15 * i, S.quiebre(), 0.12) for i in range(5)]
    fx += [(g, S.redoblante(), 0.22) for g in _golpes(E)]
    return fx


def sacudidas(E):
    return [(E["s_enciende"] + 0.1, 8, 0.25), (E["v_rompio"], 6, 0.2)]


# ==================================================================== fondos
def fondo_sable():
    a = gradiente([(0, (6, 8, 26)), (0.5, (14, 12, 46)), (1, (8, 6, 24))])
    resplandor(a, 260, 600, 380, (70, 40, 140), 0.35)
    resplandor(a, 860, 1400, 420, (30, 70, 160), 0.3)
    img = a_imagen(a, 50)
    rng = np.random.default_rng(51)
    for _ in range(160):
        componer(img, spr_estrella(int(rng.integers(2, 7))), rng.uniform(0, W), rng.uniform(0, H),
                 alpha=rng.uniform(0.3, 0.9))
    return img


def fondo_nemo():
    a = gradiente([(0, (40, 170, 220)), (0.4, (20, 120, 190)), (1, (6, 44, 104))])
    viñeta(a, 0.4)
    img = a_imagen(a, 52)
    c = Capa(0, 1200, W, H - 1200)
    c.poligono([(x, 1500 + 30 * math.sin(x / 90)) for x in range(-20, W + 40, 20)] + [(W + 40, H), (-20, H)],
               fill=(226, 196, 140))
    for x, alto, col in ((120, 260, (255, 110, 120)), (190, 180, (255, 170, 80)), (930, 300, (170, 110, 230)),
                         (1010, 200, (255, 120, 170))):
        for j, ang in enumerate((-0.4, 0.0, 0.35)):
            pts = [(x + math.sin(ang) * alto * u + 18 * math.sin(u * 5 + j), 1560 - math.cos(ang) * alto * u)
                   for u in np.linspace(0, 1, 12)]
            c.tubo(pts, [16 - 8 * u for u in np.linspace(0, 1, 12)], col)
    c.elipse(300, 1560, 90, 55, fill=(200, 150, 100))
    for i in range(5):
        c.arco(300, 1560, 70 - i * 12, 40 - i * 7, 190, 350, (160, 110, 70), 4)
    c.pegar_en(img)
    return img


def fondo_varitas():
    a = gradiente([(0, (44, 32, 66)), (PISO_V / H - 0.001, (30, 22, 46)), (PISO_V / H, (92, 60, 40)),
                   (1, (60, 38, 24))])
    viñeta(a, 0.5)
    img = a_imagen(a, 53)
    c = Capa(0, 0, W, H)
    for fila_, y in enumerate(range(80, PISO_V, 70)):
        c.linea([(0, y), (W, y)], (60, 48, 84), 4, puntas=False)
        for x in range(-70 + 70 * (fila_ % 2), W, 140):
            c.linea([(x, y), (x, y + 70)], (60, 48, 84), 4, puntas=False)
    for y in range(PISO_V + 60, H, 80):
        c.linea([(0, y), (W, y)], (74, 46, 30), 4, puntas=False)
    for x in (110, 970):  # soportes de las antorchas
        c.rrect(x - 14, 820, x + 14, 960, 6, fill=(70, 60, 60))
        c.poligono([(x - 36, 800), (x + 36, 800), (x + 20, 840), (x - 20, 840)], fill=(90, 80, 80))
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(sable=fondo_sable(), nemo=fondo_nemo(), varitas=fondo_varitas())
    EXTRA["rayos"] = rayos_luz()


# ================================================================ elementos
def proyector(c, x, y, t, k=1.0):
    B = (20, 20, 26)
    for dx in (-62, 62):
        cx, cy = x + dx * k, y - 112 * k
        c.circulo(cx, cy, 60 * k, fill=(50, 50, 62), borde=B, grosor=5 * k)
        for i in range(5):
            a = t * 5 + i * 2 * math.pi / 5
            c.circulo(cx + 32 * k * math.cos(a), cy + 32 * k * math.sin(a), 11 * k, fill=(20, 20, 26))
        c.circulo(cx, cy, 10 * k, fill=(160, 160, 170))
    c.linea([(x - 62 * k, y - 52 * k), (x - 30 * k, y - 40 * k)], (30, 30, 36), 5 * k)
    c.rrect(x - 115 * k, y - 50 * k, x + 110 * k, y + 70 * k, 16 * k, fill=(70, 72, 84), borde=B, grosor=6 * k)
    for i in range(4):
        c.linea([(x - 90 * k, y - 20 * k + i * 22 * k), (x - 20 * k, y - 20 * k + i * 22 * k)], (40, 40, 50), 5 * k)
    c.rrect(x + 104 * k, y - 26 * k, x + 150 * k, y + 34 * k, 10 * k, fill=(50, 50, 60), borde=B, grosor=4 * k)
    c.circulo(x + 150 * k, y + 4 * k, 24 * k, fill=(220, 240, 255), borde=B, grosor=4 * k)
    return (x + 160 * k, y + 4 * k)


def tele_chica(c, x, y, t, k=1.0):
    B = (40, 26, 16)
    for s in (-1, 1):
        c.linea([(x + s * 20 * k, y - 100 * k), (x + s * 70 * k, y - 170 * k)], (80, 80, 90), 5 * k)
    c.rrect(x - 130 * k, y - 100 * k, x + 130 * k, y + 100 * k, 24 * k, fill=(150, 98, 58), borde=B, grosor=6 * k)
    c.rrect(x - 110 * k, y - 80 * k, x + 60 * k, y + 80 * k, 24 * k, fill=(170, 170, 176))
    rng = np.random.default_rng(int(t * 20))
    for i in range(14):
        yy = y - 72 * k + i * 11 * k
        g = int(rng.integers(60, 230))
        c.linea([(x - 100 * k, yy), (x + 50 * k, yy)], (g, g, g), 7 * k, puntas=False)
    for i in range(2):
        c.circulo(x + 96 * k, y - 40 * k + i * 60 * k, 14 * k, fill=(210, 200, 180), borde=B, grosor=3 * k)
    return (x - 130 * k, y)


def sable(c, x, y, largo, ang, t, k=1.0):
    """Sable de luz genérico: mango metálico y hoja de energía; gira `ang` alrededor del mango."""
    ca, sa = math.cos(ang), math.sin(ang)

    def R(dx, dy):
        dx, dy = dx * k, dy * k
        return (x + dx * ca - dy * sa, y + dx * sa + dy * ca)

    if largo > 2:
        tip = R(0, -largo / k)
        vib = 1 + 0.06 * math.sin(t * 43)
        for col, g in ((SABLE + (60,), 70), (SABLE + (130,), 42), ((200, 230, 255), 22), ((255, 255, 255), 12)):
            c.linea([R(0, -8), tip], col, g * vib * k)
    c.poligono([R(-18, 0), R(18, 0), R(18, 130), R(-18, 130)], fill=(186, 190, 200), borde=(40, 40, 50), grosor=4 * k)
    for dy in (30, 52, 74, 96):
        c.poligono([R(-19, dy), R(19, dy), R(19, dy + 10), R(-19, dy + 10)], fill=(40, 40, 50))
    c.poligono([R(-24, -14), R(24, -14), R(24, 4), R(-24, 4)], fill=(150, 154, 166), borde=(40, 40, 50),
               grosor=4 * k)
    c.circulo(*R(0, 16), 6 * k, fill=(230, 60, 60))


def pez_payaso(c, x, y, t, k=1.0, dir_=1):
    """Pez payaso (la especie, no un personaje)."""
    def P(dx, dy):
        return (x + dir_ * dx * k, y + dy * k)

    cola = 10 * math.sin(t * 9)
    c.poligono([P(-78, 0), P(-126, -40 + cola), P(-110, 0), P(-126, 40 + cola)], fill=NARANJA, borde=NEGRO_P,
               grosor=5 * k)
    c.poligono([P(-50, -38), P(-14, -72), P(30, -44)], fill=NARANJA, borde=NEGRO_P, grosor=5 * k)
    c.poligono([P(-40, 40), P(-10, 66), P(20, 42)], fill=NARANJA, borde=NEGRO_P, grosor=5 * k)
    c.elipse(x, y, 92 * k, 52 * k, fill=NARANJA, borde=NEGRO_P, grosor=6 * k)
    for bx, ancho in ((48, 14), (-4, 18), (-60, 12)):
        arriba, abajo = [], []
        for u in np.linspace(-1, 1, 8):
            lx = bx + u * ancho
            h = 52 * math.sqrt(max(0.0, 1 - (lx / 92) ** 2)) - 3
            arriba.append(P(lx, -h))
            abajo.append(P(lx, h))
        c.poligono(arriba + abajo[::-1], fill=(255, 255, 255), borde=NEGRO_P, grosor=4 * k)
    c.elipse(*P(8, 14), 16 * k, 9 * k, fill=(255, 150, 60), borde=NEGRO_P, grosor=3 * k)
    ex, ey = P(64, -12)
    c.circulo(ex, ey, 11 * k, fill=(255, 255, 255), borde=NEGRO_P, grosor=3 * k)
    c.elipse(ex + dir_ * 2 * k, ey, 6 * k, 6 * k * parpadeo(t, 3.0), fill=(10, 10, 10))
    c.arco(*P(84, 10), 8 * k, 6 * k, 20 if dir_ > 0 else 200, 160 if dir_ > 0 else 340, NEGRO_P, 3 * k)


def anemona(c, x, y, t, k=1.0):
    for i in range(24):
        u = (i - 11.5) / 11.5
        base = (x + u * 150 * k, y)
        pts = [(base[0] + u * 60 * k * j / 8 + 14 * k * math.sin(t * 2.2 + i * 0.7 + j * 0.5),
                base[1] - 170 * k * (1 - abs(u) * 0.4) * j / 8) for j in range(9)]
        c.tubo(pts, [13 * k] * 9, (170, 60, 150))
        c.tubo(pts, [10 * k] * 9, (255, 130, 200))
        c.circulo(*pts[-1], 12 * k, fill=(255, 200, 230))
    c.elipse(x, y + 20 * k, 170 * k, 40 * k, fill=(150, 60, 140), borde=(90, 30, 90), grosor=5 * k)


def simbolo(c, x, y, k, tipo, color):
    """Símbolo de macho (flecha) o hembra (cruz), dibujado."""
    c.circulo(x, y, 24 * k, borde=color, grosor=8 * k)
    if tipo == "macho":
        c.linea([(x + 17 * k, y - 17 * k), (x + 44 * k, y - 44 * k)], color, 8 * k)
        c.linea([(x + 22 * k, y - 44 * k), (x + 44 * k, y - 44 * k), (x + 44 * k, y - 22 * k)], color, 8 * k)
    else:
        c.linea([(x, y + 24 * k), (x, y + 60 * k)], color, 8 * k)
        c.linea([(x - 16 * k, y + 44 * k), (x + 16 * k, y + 44 * k)], color, 8 * k)


def varita(c, x0, y0, x1, y1, k=1.0):
    """Varita de madera (genérica): de la empuñadura (x0, y0) a la punta (x1, y1)."""
    n = max(16, int(math.hypot(x1 - x0, y1 - y0) / 4))
    pts = [(lerp(x0, x1, u), lerp(y0, y1, u)) for u in np.linspace(0, 1, n)]
    rad = [(10 - 5 * u) * k for u in np.linspace(0, 1, n)]
    c.tubo(pts, [r + 3 * k for r in rad], (30, 16, 8))
    c.tubo(pts, rad, (110, 70, 40))
    for u in (0.08, 0.16, 0.26):
        c.circulo(lerp(x0, x1, u), lerp(y0, y1, u), 11 * k, fill=(80, 48, 26))
    c.circulo(x1, y1, 5 * k, fill=(240, 230, 200))


def tambor(c, x, y, k=1.0, golpe=0.0):
    ROJO, B, METAL = (196, 40, 52), (40, 12, 16), (200, 204, 214)
    for s in (-1, 1):
        c.linea([(x + s * 110 * k, y + 70 * k), (x + s * 150 * k, y + 250 * k)], (70, 70, 80), 8 * k)
    c.rrect(x - 180 * k, y - 36 * k, x + 180 * k, y + 80 * k, 12 * k, fill=ROJO, borde=B, grosor=6 * k)
    for i in range(7):
        lx = x - 150 * k + i * 50 * k
        c.rrect(lx - 8 * k, y - 10 * k, lx + 8 * k, y + 54 * k, 4 * k, fill=METAL, borde=B, grosor=2 * k)
    c.elipse(x, y + 80 * k, 180 * k, 30 * k, fill=METAL, borde=B, grosor=5 * k)
    c.elipse(x, y - 36 * k, 180 * k, (44 - 8 * golpe) * k, fill=METAL, borde=B, grosor=5 * k)
    c.elipse(x, y - 36 * k, 164 * k, (36 - 7 * golpe) * k, fill=(250, 248, 240) if golpe < 0.5 else (255, 255, 200))


def platillo(c, x, y, k, t, golpe=0.0):
    c.linea([(x, y), (x, y + 360 * k)], (70, 70, 80), 8 * k)
    c.poligono(elipse_rotada(x, y, 130 * k, 20 * k, -10 + 6 * golpe * math.sin(t * 40)), fill=(226, 180, 60),
               borde=(120, 80, 20), grosor=4 * k)
    c.circulo(x, y, 12 * k, fill=(190, 150, 50))


def antorcha(c, x, y, t):
    for col, esc in (((255, 120, 30), 1.0), ((255, 210, 80), 0.6)):
        pts = [(x - 26 * esc, y), (x - 10 * esc, y - 60 * esc - 8 * math.sin(t * 13)),
               (x + 4 * esc, y - 90 * esc - 10 * math.sin(t * 17 + 1)), (x + 20 * esc, y - 50 * esc),
               (x + 26 * esc, y)]
        c.poligono(pts, fill=col)


# =================================================================== escenas
def escena_sable(t):
    fr = FONDOS["sable"].copy()
    t0 = ESC["sable"]["escena_ini"]
    te = E["s_enciende"]
    c = Capa(0, 560, W, 900)
    sp = pop(t, E["s_proyector"], 0.4)
    lente = (0, 0)
    if sp > 0:
        if t >= E["s_proyector"] + 0.2:
            c.poligono([(390, 804), (620, 700), (620, 900)], fill=(255, 250, 210, 40))
        lente = proyector(c, 230, 800, t, 0.95 * sp)
    st = pop(t, E["s_televisor"], 0.4)
    antena = (0, 0)
    if st > 0:
        antena = tele_chica(c, 860, 800, t, 0.95 * st)
    # los dos sonidos viajan y se juntan en el mango
    mango = (540, 1200)
    for p0, t_i, col in ((lente, E["s_proyector"], (255, 230, 150)), (antena, E["s_televisor"], (160, 220, 255))):
        v = e_out(prog(t, t_i + 0.2, 0.6)) * (1 - prog(t, te, 0.25))
        if v > 0:
            onda(c, p0, (mango[0], mango[1] - 20), t, col + (220,), 7, 16, 5, v)
    c.pegar_en(fr)
    # el sable: encendido desde el principio; cuando se juntan los sonidos, hace un "swing" y destella
    sm = e_back(prog(t, t0 + 0.2, 0.5))
    if sm > 0:
        largo = 480 * e_out(prog(t, t0 + 0.5, 0.4))
        swing = math.sin(math.pi * prog(t, te, 0.5)) if t >= te else 0.0
        ang = math.radians(8 * math.sin(t * 1.6) - 38 * swing)
        destello = 1 + 0.8 * swing
        if largo > 0:
            componer(fr, _brillo(), 540 + 240 * math.sin(ang), 1200 - largo / 2, escala=(0.6 + largo / 480) * destello,
                     alpha=min(1.0, 0.6 * destello))
        c = Capa(160, 620, 760, 820)
        sable(c, 540, 1200 + (1 - sm) * 200, largo, ang, t, 1.25)
        c.pegar_en(fr)
    s = e_back(prog(t, te + 0.15, 0.3)) * (1 - prog(t, te + 1.2, 0.2))
    if s > 0:
        componer(fr, texto("¡VZZZUM!", "titulo", 90, color=(200, 230, 255), borde=10, color_borde=(20, 40, 120)),
                 790, 1080, escala=s, rot=-10)
    encabezado(fr, t, 1, E["sable_badge"])
    titulo(fr, t, TITULOS["sable"]["titulo"], t0 + 0.15, color=(170, 210, 255))
    pildora(fr, t, TITULOS["sable"]["subtitulo"], (40, 80, 180), E["s_sonido"], hasta=te)
    pildora(fr, t, "¡PROYECTOR + TELEVISOR!", (30, 120, 220), te + 0.05)
    return fr


def _brillo():
    return spr_resplandor(300, SABLE)


def escena_nemo(t):
    fr = FONDOS["nemo"].copy()
    t0 = ESC["nemo"]["escena_ini"]
    th = E["n_hembra"]
    ray = EXTRA["rayos"]
    ox = int(150 + 60 * math.sin(t * 0.7))
    fr.alpha_composite(ray, (0, 0), (ox, 0, ox + W, H))
    c = Capa(0, 560, W, 1000)
    anemona(c, 540, 1350, t, 1.2)
    # el papá (macho) que se convierte en hembra (y crece: en los peces payaso la hembra es la más grande)
    cambio = e_out(prog(t, th, 0.6))
    k = lerp(0.95, 1.3, cambio)
    ent = e_out(prog(t, t0 + 0.1, 0.8))
    px = lerp(-200, 470, ent) + 40 * math.sin(t * 0.9)
    py = 960 + 20 * math.sin(t * 1.6)
    dir_ = 1 if math.cos(t * 0.9) >= -0.3 else -1
    pez_payaso(c, px, py, t, k, dir_)
    # un pececito chico (el hijo) jugando en la anémona
    nx, ny = 700 + 80 * math.sin(t * 1.3), 1130 + 30 * math.sin(t * 2.1)
    pez_payaso(c, nx, ny, t + 0.5, 0.5, 1 if math.cos(t * 1.3) >= 0 else -1)
    c.pegar_en(fr)
    # etiqueta con el símbolo: macho -> hembra
    s = pop(t, E["n_papa"], 0.4)
    if s > 0:
        tipo = "hembra" if t >= th + 0.25 else "macho"
        color = (255, 110, 170) if tipo == "hembra" else (90, 160, 255)
        c = Capa(560, 700, 460, 200)
        c.rrect(640, 740, 1000, 850, 30, fill=(10, 20, 50, 200), borde=color, grosor=6)
        simbolo(c, 700, 800 if tipo == "macho" else 780, 0.9, tipo, color)
        c.pegar_en(fr)
        componer(fr, texto("HEMBRA" if tipo == "hembra" else "MACHO", "titulo", 60, color=color), 865, 797,
                 escala=s)
        componer(fr, texto("EL PAPÁ", "negra", 30, borde=5), 820, 720, escala=s)
    if th <= t < th + 0.6:
        chispas(fr, t, th, px, py, n=24, seed=8, colores=((255, 255, 255), (255, 200, 120), (255, 150, 200)),
                vel=(250, 600), grav=200, dur=0.8)
    componer(fr, texto("NEMO", "negra", 26, borde=4), nx, ny - 60, alpha=0.9)
    encabezado(fr, t, 2, E["nemo_badge"])
    titulo(fr, t, TITULOS["nemo"]["titulo"], t0 + 0.15, tam=130, color=(255, 190, 120))
    pildora(fr, t, TITULOS["nemo"]["subtitulo"], (230, 100, 30), E["n_payaso"])
    return fr


def escena_varitas(t):
    fr = FONDOS["varitas"].copy()
    t0 = ESC["varitas"]["escena_ini"]
    tr, to, tp = E["v_rompio"], E["v_ochenta"], E["v_palillos"]
    c = Capa(0, 560, W, H - 560)
    for x in (110, 970):
        antorcha(c, x, 800, t + x)
    # la pila de varitas rotas va creciendo
    rotas = int(80 * e_out(prog(t, to, E["v_varitas"] - to + 0.3))) if t >= to else (2 if t >= tr + 0.5 else 0)
    rng = np.random.default_rng(3)
    for i in range(rotas // 2):
        x, y = rng.uniform(200, 880), rng.uniform(1360, 1440) - i * 0.4
        a = rng.uniform(0, math.pi)
        largo = rng.uniform(40, 80)
        varita(c, x, y, x + largo * math.cos(a), y - largo * math.sin(a) * 0.4, 0.8)
    # batería
    golpes = _golpes(E)
    ultimo = max([g for g in golpes if g <= t], default=-9)
    golpe = max(0.0, 1 - (t - ultimo) / 0.12)
    sb = e_back(prog(t, tp - 0.3, 0.4))
    if sb > 0:
        platillo(c, 850, 1000, sb, t, golpe)
        tambor(c, 540, 1180, sb, golpe)
    # la varita mágica que se parte
    if t < tr + 0.6:
        s = e_back(prog(t, t0 + 0.2, 0.5))
        y = 980 + 10 * math.sin(t * 2.4)
        if t < tr:
            varita(c, 330, y + 120, 750, y - 90, 2.0 * s)
            for i in range(6):
                a = t * 3 + i * math.pi / 3
                c.circulo(750 + 34 * math.cos(a), y - 90 + 34 * math.sin(a), 6, fill=(255, 230, 150))
        else:
            p = prog(t, tr, 0.6)
            varita(c, 330 - 60 * p, y + 120 + 500 * p * p, 540 - 80 * p, y + 15 + 500 * p * p, 2.0)
            varita(c, 540 + 80 * p, y + 15 + 520 * p * p, 750 + 60 * p, y - 90 + 520 * p * p, 2.0)
    # pedazos de varitas que llueven mientras cuenta
    if to <= t < E["v_varitas"] + 0.8:
        rng2 = np.random.default_rng(12)
        for i in range(26):
            t_i = to + rng2.uniform(0, E["v_varitas"] - to + 0.3)
            dt = t - t_i
            if 0 <= dt < 0.8:
                x = rng2.uniform(220, 860)
                yy = 700 + 1300 * dt * dt
                a = rng2.uniform(0, 6) + dt * 8
                largo = rng2.uniform(50, 80)
                if yy < 1400:
                    varita(c, x, yy, x + largo * math.cos(a), yy + largo * math.sin(a), 1.0)
            else:
                rng2.uniform(), rng2.uniform(), rng2.uniform()
    # los palillos
    if t >= tp:
        for i, (bx, by, rx) in enumerate(((300, 1440, 470), (780, 1440, 610))):
            mios = [g for g in golpes[i::2] if g <= t]
            baja = max(0.0, 1 - (t - mios[-1]) / 0.12) if mios else 0
            varita(c, bx, by, rx, lerp(1000, 1130, baja), 1.1)
    c.pegar_en(fr)
    if tr <= t < tr + 0.8:
        chispas(fr, t, tr, 540, 970, n=18, seed=2, colores=((255, 230, 150), (200, 160, 255), (255, 255, 255)),
                vel=(250, 600), grav=600, dur=0.8)
    if golpe > 0.5 and t >= tp:
        componer(fr, texto("¡PAM!", "titulo", 60, color=(255, 230, 120), borde=8), 540 + (160 if int(ultimo * 5) % 2 else -160),
                 1030, escala=0.8 + 0.4 * golpe, rot=-8)
    # quién y cuántas
    s = pop(t, t0 + 0.5, 0.4) * (1 - e_out(prog(t, to - 0.1, 0.25)))
    if s > 0.01:
        componer(fr, cartel("DANIEL RADCLIFFE", "EL ACTOR", (255, 214, 120), (40, 20, 60), 560, 80), 540, 660,
                 escala=s, rot=-2)
    s = pop(t, to, 0.35)
    if s > 0:
        componer(fr, cartel(f"{rotas} VARITAS", "ROTAS", (255, 214, 10), (60, 20, 40), 520, 96), 540, 660,
                 escala=s, rot=2)
    encabezado(fr, t, 3, E["varitas_badge"])
    titulo(fr, t, TITULOS["varitas"]["titulo"], t0 + 0.15, color=(255, 215, 120))
    pildora(fr, t, TITULOS["varitas"]["subtitulo"], (120, 60, 180), tp)
    return fr


# ======================================================= íconos del cierre
def _icono_sable(c, x, y, s, t):
    sable(c, x - 30 * s, y + 50 * s, 130 * s, math.radians(35), t, 0.55 * s)


def _icono_nemo(c, x, y, s, t):
    pez_payaso(c, x + 6 * s, y, t, 0.85 * s, 1)


def _icono_varitas(c, x, y, s, t):
    varita(c, x - 70 * s, y + 70 * s, x + 70 * s, y - 70 * s, 1.2 * s)
    for i in range(5):
        a = i * 2 * math.pi / 5 + t
        c.circulo(x + 70 * s + 22 * s * math.cos(a), y - 70 * s + 22 * s * math.sin(a), 5 * s, fill=(255, 220, 120))


ICONOS = [_icono_sable, _icono_nemo, _icono_varitas]
ESCENAS = {"sable": escena_sable, "nemo": escena_nemo, "varitas": escena_varitas}
