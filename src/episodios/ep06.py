"""Episodio 6: curiosidades de dibujos animados (voz de Tomás, Argentina).

Las imágenes usan objetos y guiños genéricos (una tele, un pizarrón, una
etiqueta con nombre y un ratón gris cualquiera), nunca personajes o logos con
derechos de autor.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from dibujo import (H, W, Capa, a_imagen, cartel, chispas, componer, e_back, e_out, encabezado,
                    gradiente, lerp, parpadeo, pildora, pop, prog, resplandor, spr_burbuja, spr_resplandor, texto,
                    titulo, viñeta)

SLUG = "dibujos_animados"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 0
GANCHO_ETIQUETA = "DE DIBUJOS ANIMADOS"
PALABRAS_CIERRE = ("abajo", "seguinos")

# Guion escrito para el oído (ver episodio 4). "Zapping" se reemplazó por
# "cambiás de canal": se entiende siempre, lo diga quien lo diga.
BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades de dibujos animados que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "DE DIBUJOS ANIMADOS",
    },
    {
        "id": "amarillo",
        "texto": "Uno: los Simpson son amarillos a propósito: así te llaman la atención cuando cambiás de canal.",
        "titulo": "LOS SIMPSON",
        "subtitulo": "¡AMARILLOS A PROPÓSITO!",
    },
    {
        "id": "esponja",
        "texto": "Dos: el creador de Bob Esponja era profesor de biología marina. "
                 "¡Por eso sabía tanto del fondo del mar!",
        "titulo": "BOB ESPONJA",
        "subtitulo": "PROFESOR DE BIOLOGÍA MARINA",
    },
    {
        "id": "mortimer",
        "texto": "Tres: Mickey Mouse casi se llamó Mortimer. "
                 "¡Fue la esposa de {Walt Disney|Uólt Dísnei} la que eligió Mickey!",
        "titulo": "MICKEY MOUSE",
        "subtitulo": "¡CASI SE LLAMÓ MORTIMER!",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos abajo y seguinos para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"amarillo": (255, 214, 10), "esponja": (40, 180, 200),
          "mortimer": (210, 50, 60), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS = {}, {}, {}
PISO = 1400
AMARILLO = (255, 217, 15)


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "a_amarillos": L.palabra("amarillo", "amarillos"),
        "a_atencion": L.palabra("amarillo", "atención"),
        "a_cambias": L.palabra("amarillo", "cambiás"),
        "a_canal": L.fin_palabra("amarillo", "canal"),
        "e_creador": L.palabra("esponja", "creador"),
        "e_profesor": L.palabra("esponja", "profesor"),
        "e_fondo": L.palabra("esponja", "fondo"),
        "m_mortimer": L.palabra("mortimer", "mortimer"),
        "m_esposa": L.palabra("mortimer", "esposa"),
        "m_eligio": L.palabra("mortimer", "eligió"),
        "m_mickey": L.palabra("mortimer", "mickey", 2),
    }


def _cambios(E):
    """Momentos del zapping (un canal nuevo cada 0,14 s)."""
    t, fin, out = E["a_cambias"], E["a_canal"] + 0.1, []
    while t < fin:
        out.append(t)
        t += 0.14
    return out


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    ini = E["amarillo_ini"]
    fx = [(ini + 0.2, S.lluvia(max(0.5, E["a_amarillos"] - ini - 0.2)), 0.05),
          (E["a_amarillos"], S.ding(), 0.25), (E["a_atencion"], S.pop(700, 300), 0.25)]
    fx += [(tc, S.zapping_sfx(), 0.22) for tc in _cambios(E)]
    fx += [(E["a_canal"] + 0.2, S.ding(), 0.22),
           (E["e_creador"], S.pop(900, 400), 0.28),
           (E["e_profesor"], S.tiza(0.6), 0.20), (E["e_profesor"] + 0.7, S.tiza(0.5), 0.18),
           (E["e_fondo"] - 0.1, S.whoosh(0.8, 200, 1200), 0.30)]
    fx += [(E["e_fondo"] + 0.2 + 0.18 * i, S.bloop(), 0.18) for i in range(4)]
    ini_m, fin_m = E["mortimer_ini"], E["m_mickey"]
    fx += [(ini_m, S.proyector(fin_m - ini_m + 0.2), 0.10),
           (E["m_mortimer"], S.pop(700, 300), 0.25), (E["m_esposa"], S.pop(900, 400), 0.28),
           (E["m_eligio"], S.marcador(0.35), 0.25), (E["m_eligio"] + 0.35, S.marcador(0.3), 0.22),
           (E["m_mickey"], S.brillo_sfx(), 0.30), (E["m_mickey"] + 0.05, S.ding(), 0.22)]
    return fx


def sacudidas(E):
    return [(E["m_mickey"], 8, 0.25)]


# ==================================================================== fondos
def fondo_amarillo():
    a = gradiente([(0, (60, 52, 110)), (PISO / H - 0.001, (104, 86, 150)), (PISO / H, (132, 86, 54)),
                   (1, (96, 60, 36))])
    viñeta(a, 0.45)
    img = a_imagen(a, 40)
    c = Capa(0, 0, W, H)
    for x in range(0, W, 120):
        c.rrect(x + 50, 0, x + 70, PISO, 4, fill=(255, 255, 255, 14))
    for y in range(PISO + 50, H, 70):
        c.linea([(0, y), (W, y)], (110, 70, 42), 3, puntas=False)
    c.elipse(540, PISO + 40, 420, 60, fill=(170, 60, 70))
    c.elipse(540, PISO + 40, 380, 46, fill=(200, 80, 86))
    c.pegar_en(img)
    return img


def fondo_esponja():
    a = gradiente([(0, (236, 226, 196)), (0.72, (214, 200, 168)), (0.7201, (150, 100, 60)), (1, (120, 78, 46))])
    viñeta(a, 0.35)
    img = a_imagen(a, 41)
    c = Capa(0, 600, W, 700)
    c.rrect(110, 640, 970, 1220, 16, fill=(122, 80, 44))
    c.rrect(130, 660, 950, 1200, 8, fill=(38, 88, 68))
    c.rrect(160, 1200, 920, 1222, 6, fill=(150, 104, 60))
    for x in (260, 300, 340):
        c.rrect(x, 1188, x + 26, 1200, 3, fill=(245, 245, 240))
    c.pegar_en(img)
    return img


def fondo_mortimer():
    a = gradiente([(0, (60, 12, 20)), (0.5, (120, 20, 34)), (1, (50, 8, 14))])
    resplandor(a, 540, 950, 520, (255, 220, 150), 0.45)
    img = a_imagen(a, 42)
    c = Capa(0, 0, W, H)
    for lado in (-1, 1):  # telones de teatro
        x0 = 0 if lado < 0 else W
        for i in range(6):
            x = x0 - lado * (30 + i * 36)
            c.linea([(x, 0), (x + lado * 10 * math.sin(i), H)], (150, 20, 36) if i % 2 else (190, 34, 50), 40)
    c.rrect(-20, -20, W + 20, 150, 0, fill=(170, 26, 40))
    for x in range(0, W, 60):
        c.arco(x + 30, 150, 30, 26, 0, 180, (220, 170, 60), 6)
    c.rrect(0, PISO, W, H, 0, fill=(90, 50, 30))
    c.pegar_en(img)
    return img


def preparar():
    FONDOS.update(amarillo=fondo_amarillo(), esponja=fondo_esponja(), mortimer=fondo_mortimer())


# ================================================================ elementos
def tele(c, x, y, k=1.0):
    """Televisor de tubo; devuelve la caja de la pantalla (x0, y0, x1, y1)."""
    MADERA, B = (150, 98, 58), (60, 36, 20)

    def P(dx, dy):
        return (x + dx * k, y + dy * k)

    for s in (-1, 1):
        c.linea([P(s * 40, -225), P(s * 150, -370)], (60, 60, 70), 6 * k)
        c.circulo(*P(s * 150, -370), 12 * k, fill=(200, 200, 210), borde=(60, 60, 70), grosor=3 * k)
    c.elipse(*P(0, -225), 70 * k, 22 * k, fill=(70, 60, 60), borde=B, grosor=4 * k)
    for s in (-1, 1):
        c.rrect(*P(s * 210 - 16, 210), *P(s * 210 + 16, 262), 6 * k, fill=(90, 60, 36))
    c.rrect(*P(-290, -225), *P(290, 215), 40 * k, fill=MADERA, borde=B, grosor=7 * k)
    c.rrect(*P(-250, -190), *P(150, 180), 46 * k, fill=(28, 26, 34), borde=B, grosor=5 * k)
    for i in range(2):
        c.circulo(*P(222, -110 + i * 90), 26 * k, fill=(210, 200, 180), borde=B, grosor=4 * k)
        c.linea([P(222, -110 + i * 90), P(222 + 16, -120 + i * 90)], B, 5 * k)
    for i in range(5):
        c.linea([P(190, 60 + i * 22), P(254, 60 + i * 22)], B, 5 * k, puntas=False)
    return P(-228, -168) + P(128, 158)


def control_remoto(c, x, y, k, prendido):
    c.rrect(x - 42 * k, y - 110 * k, x + 42 * k, y + 110 * k, 26 * k, fill=(40, 40, 50), borde=(10, 10, 20), grosor=4 * k)
    c.circulo(x, y - 76 * k, 12 * k, fill=(255, 60, 60) if prendido else (140, 40, 40))
    for i in range(3):
        for j in range(3):
            c.circulo(x + (j - 1) * 24 * k, y - 30 * k + i * 26 * k, 8 * k, fill=(170, 170, 180))
    if prendido:
        for i in range(3):
            c.arco(x, y - 110 * k, (26 + 20 * i) * k, (26 + 20 * i) * k, 225, 315, (255, 240, 150, 220 - 60 * i), 5 * k)


def pantalla(t, canal, w, h):
    """Contenido de la pantalla: 0 estática, 1 barras de color, 2 sin señal, 3 amarillo, 4 verde."""
    if canal == 0:
        ruido = np.random.default_rng(int(t * 30)).integers(40, 230, (h // 6, w // 6), dtype=np.uint8)
        im = Image.fromarray(ruido, "L").resize((w, h), Image.NEAREST).convert("RGBA")
    elif canal == 1:
        im = Image.new("RGBA", (w, h))
        colores = [(192, 192, 192), (192, 192, 0), (0, 192, 192), (0, 192, 0), (192, 0, 192), (192, 0, 0), (0, 0, 192)]
        for i, col in enumerate(colores):
            im.paste(col + (255,), (i * w // 7, 0, (i + 1) * w // 7 + 1, h))
    elif canal == 2:
        im = Image.new("RGBA", (w, h), (20, 60, 200, 255))
        tx = texto("SIN SEÑAL", "negra", 34, color=(255, 255, 255))
        im.alpha_composite(tx, (w // 2 - tx.width // 2, h // 2 - tx.height // 2))
    elif canal == 4:
        im = Image.new("RGBA", (w, h), (40, 160, 80, 255))
    else:
        base = np.zeros((h, w, 3), np.float32) + AMARILLO
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt(((xx - w * 0.4) / w) ** 2 + ((yy - h * 0.35) / h) ** 2)
        base += (255 - base) * np.clip(0.5 - d, 0, 1)[..., None] * 0.9
        im = Image.fromarray(base.astype(np.uint8), "RGB").convert("RGBA")
    if canal != 3:
        tx = texto(f"CH {canal * 7 + 3:02d}", "negra", 26, color=(120, 255, 120))
        im.alpha_composite(tx, (16, 12))
    lineas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(0, h, 4):
        lineas.paste((0, 0, 0, 40), (0, y, w, y + 1))
    im.alpha_composite(lineas)
    return im


@lru_cache(None)
def _mascara_pantalla(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


def pez_mar(c, x, y, k, dir_, color, tiza=False):
    B = (255, 255, 255, 230) if tiza else (30, 40, 60)
    f = None if tiza else color
    c.poligono([(x - dir_ * 40 * k, y), (x - dir_ * 72 * k, y - 26 * k), (x - dir_ * 72 * k, y + 26 * k)],
               fill=f, borde=B, grosor=4 * k)
    c.elipse(x, y, 48 * k, 28 * k, fill=f, borde=B, grosor=4 * k)
    c.circulo(x + dir_ * 24 * k, y - 6 * k, 6 * k, fill=B)


def estrella_mar(c, x, y, k, color, tiza=False):
    B = (255, 255, 255, 230) if tiza else (120, 40, 20)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = (46 if i % 2 == 0 else 20) * k
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    c.poligono(pts, fill=None if tiza else color, borde=B, grosor=4 * k)
    if not tiza:
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            c.circulo(x + 24 * k * math.cos(a), y + 24 * k * math.sin(a), 4 * k, fill=(255, 220, 180))


def medusa(c, x, y, t, k, color, tiza=False):
    B = (255, 255, 255, 230) if tiza else (120, 60, 140)
    for i in range(5):
        pts = [(x + (-30 + 15 * i) * k + 6 * k * math.sin(t * 3 + j * 0.8 + i), y + (10 + 14 * j) * k) for j in range(7)]
        c.linea(pts, B, 4 * k)
    arco = [(x + 44 * k * math.cos(u), y - 36 * k * math.sin(u)) for u in np.linspace(0, math.pi, 20)]
    c.poligono(arco + [(x - 44 * k, y + 8 * k), (x + 44 * k, y + 8 * k)], fill=None if tiza else color, borde=B,
               grosor=4 * k)


def esponja_mar(c, x, y, k, color, tiza=False):
    """Esponja de mar natural (con forma de tubos)."""
    B = (255, 255, 255, 230) if tiza else (120, 80, 20)
    for dx, alto in ((-26, 70), (8, 96), (38, 60)):
        c.rrect(x + (dx - 15) * k, y - alto * k, x + (dx + 15) * k, y + 30 * k, 14 * k, fill=None if tiza else color,
                borde=B, grosor=4 * k)
        c.elipse(x + dx * k, y - alto * k + 8 * k, 8 * k, 4 * k, fill=B)


def etiqueta_nombre(nombre_tachado, nuevo, escritura):
    """Etiqueta 'HOLA, ME LLAMO' con el nombre; `escritura` 0..10 de la palabra nueva."""
    w, h = 640, 400
    c = Capa(0, 0, w + 20, h + 24, ss=2)
    c.rrect(10, 18, w + 10, h + 18, 34, fill=(0, 0, 0, 110))
    c.rrect(10, 10, w + 10, h + 10, 34, fill=(220, 40, 52), borde=(120, 10, 20), grosor=6)
    c.rrect(34, 150, w - 14, h - 14, 16, fill=(255, 255, 255))
    im = c.imagen()
    for txt, tam, y in (("HOLA", 60, 26), ("ME LLAMO", 34, 96)):
        tx = texto(txt, "titulo" if tam > 50 else "negra", tam, color=(255, 255, 255))
        im.alpha_composite(tx, (10 + w // 2 - tx.width // 2, y))
    tx = texto("MORTIMER", "titulo", 96, color=(40, 40, 60))
    im.alpha_composite(tx, (10 + w // 2 - tx.width // 2, 200 if not nuevo else 250))
    if nombre_tachado:
        c2 = Capa(0, 0, w + 20, h + 24, ss=2)
        yl = 300 if nuevo else 250
        c2.linea([(90, yl), (90 + (w - 160) * nombre_tachado / 10, yl - 10)], (230, 30, 40), 16)
        im.alpha_composite(c2.imagen())
    if nuevo and escritura:
        tx = texto("MICKEY", "titulo", 84, color=(30, 70, 200))
        corte = int(tx.width * escritura / 10)
        if corte > 0:
            im.alpha_composite(tx.crop((0, 0, corte, tx.height)), (10 + w // 2 - tx.width // 2, 158))
    return im


def raton(c, x, y, t, k=1.0):
    """Un ratón gris cualquiera que se asoma."""
    G, B = (150, 150, 160), (50, 50, 60)
    for s in (-1, 1):
        c.circulo(x + s * 58 * k, y - 50 * k, 40 * k, fill=G, borde=B, grosor=4 * k)
        c.circulo(x + s * 58 * k, y - 50 * k, 26 * k, fill=(240, 170, 180))
    c.elipse(x, y, 62 * k, 54 * k, fill=G, borde=B, grosor=4 * k)
    abre = parpadeo(t, 2.8, 0.9)
    for s in (-1, 1):
        c.elipse(x + s * 22 * k, y - 6 * k, 9 * k, 11 * k * abre, fill=(20, 20, 30))
        for dy in (-4, 6):
            c.linea([(x + s * 30 * k, y + 22 * k), (x + s * 80 * k, y + (18 + dy) * k)], B, 2.5 * k, puntas=False)
    c.elipse(x, y + 20 * k, 11 * k, 8 * k, fill=(240, 140, 160))


# =================================================================== escenas
def escena_amarillo(t):
    fr = FONDOS["amarillo"].copy()
    t0 = ESC["amarillo"]["escena_ini"]
    ta = E["a_amarillos"]
    cambios = _cambios(E)
    if t < ta:
        canal = 0
    elif cambios and cambios[0] <= t < cambios[-1] + 0.14:
        i = sum(1 for tc in cambios if tc <= t) - 1
        canal = [1, 2, 0, 4, 1, 2][i % 6] if i < len(cambios) - 1 else 3
    else:
        canal = 3
    brillo = 0.0 if canal != 3 else (0.7 + 0.3 * math.sin(t * 5))
    if brillo:
        componer(fr, spr_resplandor(430, AMARILLO), 540, 990, escala=1.1, alpha=brillo * 0.8)
    s = e_back(prog(t, t0 + 0.1, 0.5))
    c = Capa(200, 560, 680, 760)
    x0, y0, x1, y1 = tele(c, 540, 1010, s)
    c.pegar_en(fr)
    if s > 0.3:
        w, h = int(x1 - x0), int(y1 - y0)
        pant = pantalla(t, canal, w, h)
        pant.putalpha(_mascara_pantalla(w, h, int(40 * s)))
        fr.alpha_composite(pant, (int(x0), int(y0)))
    # ¡llama la atención!
    sa = pop(t, E["a_atencion"], 0.35)
    if sa > 0:
        c = Capa(100, 560, 880, 900)
        for i in range(10):
            a = i * 2 * math.pi / 10 + 0.3
            r0, r1 = 340 * sa, (400 + 30 * math.sin(t * 8 + i)) * sa
            c.linea([(540 + r0 * math.cos(a), 1000 + r0 * 0.8 * math.sin(a)),
                     (540 + r1 * math.cos(a), 1000 + r1 * 0.8 * math.sin(a))], AMARILLO + (230,), 12)
        c.pegar_en(fr)
    # control remoto haciendo zapping
    sr = pop(t, E["a_cambias"] - 0.2, 0.35)
    if sr > 0:
        c = Capa(840, 1000, 220, 330)
        prendido = any(tc <= t < tc + 0.07 for tc in cambios)
        control_remoto(c, 950, 1180, 0.9 * sr, prendido)
        c.pegar_en(fr)
    encabezado(fr, t, 1, E["amarillo_badge"])
    titulo(fr, t, TITULOS["amarillo"]["titulo"], t0 + 0.15, color=AMARILLO)
    pildora(fr, t, TITULOS["amarillo"]["subtitulo"], (220, 150, 0), ta, hasta=E["a_cambias"])
    pildora(fr, t, "PARA DESTACAR AL HACER ZAPPING", (120, 70, 190), E["a_cambias"] + 0.05)
    return fr


def escena_esponja(t):
    fr = FONDOS["esponja"].copy()
    t0 = ESC["esponja"]["escena_ini"]
    tp, tf = E["e_profesor"], E["e_fondo"]
    # dibujos de tiza en el pizarrón
    avance = e_out(prog(t, tp, 1.3))
    c = Capa(130, 660, 820, 540)
    if avance > 0:
        tiza_ = [(lambda: pez_mar(c, 300, 1000, 1.2, 1, None, True)),
                 (lambda: estrella_mar(c, 520, 1030, 1.2, None, True)),
                 (lambda: medusa(c, 720, 980, t, 1.2, None, True)),
                 (lambda: esponja_mar(c, 850, 1110, 1.1, None, True))]
        for i, dibujar in enumerate(tiza_):
            if avance > i / len(tiza_):
                dibujar()
    c.pegar_en(fr)
    if avance > 0:
        tx = texto("BIOLOGÍA MARINA", "titulo", 64, color=(255, 255, 255))
        ancho = int(tx.width * min(1.0, avance * 1.6))
        if ancho > 0:
            fr.alpha_composite(tx.crop((0, 0, ancho, tx.height)), (540 - tx.width // 2, 700))
    # el creador
    sc = pop(t, E["e_creador"], 0.4)
    if sc > 0:
        componer(fr, cartel("STEPHEN HILLENBURG", "EL CREADOR", (255, 230, 120), (20, 60, 70), 600, 70),
                 540, 620, escala=sc * (1 - e_out(prog(t, tf, 0.3))), rot=-2)
    # ¡el fondo del mar! el agua sube y los dibujos cobran vida
    sube = e_out(prog(t, tf - 0.1, 0.9))
    if sube > 0:
        nivel = lerp(H + 40, 500, sube)
        c = Capa(0, 0, W, H, ss=1)
        c.poligono([(x, nivel + 14 * math.sin(x / 60 + t * 4)) for x in range(-20, W + 40, 20)] + [(W + 40, H), (-20, H)],
                   fill=(30, 130, 200, 170))
        agua = c.imagen()
        fr.alpha_composite(agua)
        rng = np.random.default_rng(6)
        for _ in range(22):
            x0, v = rng.uniform(0, W), rng.uniform(120, 260)
            y = H - ((t - tf) * v + rng.uniform(0, H)) % (H - nivel + 1)
            if y > nivel + 20:
                componer(fr, spr_burbuja(int(rng.integers(6, 18))), x0 + 12 * math.sin(t * 2 + x0), y)
        vida = e_out(prog(t, tf + 0.3, 0.6))
        if vida > 0:
            c = Capa(0, 560, W, 900)
            pez_mar(c, lerp(300, 820, prog(t, tf + 0.3, 3.0)), 980 + 20 * math.sin(t * 3), 1.4 * vida, 1,
                    (255, 150, 60))
            pez_mar(c, lerp(900, 380, prog(t, tf + 0.5, 3.0)), 1180 + 16 * math.sin(t * 2.6), 1.1 * vida, -1,
                    (90, 200, 255))
            estrella_mar(c, 520, 1320 + 6 * math.sin(t * 2), 1.4 * vida, (255, 110, 90))
            medusa(c, 760, 860 + 20 * math.sin(t * 1.5), t, 1.3 * vida, (240, 160, 230))
            esponja_mar(c, 240, 1360, 1.3 * vida, (250, 200, 70))
            c.pegar_en(fr)
    encabezado(fr, t, 2, E["esponja_badge"])
    titulo(fr, t, TITULOS["esponja"]["titulo"], t0 + 0.15, color=(255, 236, 120))
    pildora(fr, t, TITULOS["esponja"]["subtitulo"], (30, 140, 160), tp, hasta=tf)
    pildora(fr, t, "¡SABÍA TODO DEL FONDO DEL MAR!", (20, 110, 190), tf + 0.1)
    return fr


def escena_mortimer(t):
    fr = FONDOS["mortimer"].copy()
    t0 = ESC["mortimer"]["escena_ini"]
    tm = E["m_mickey"]
    color = e_out(prog(t, tm - 0.05, 0.5))
    # ratón que se asoma y etiqueta con el nombre
    c = Capa(200, 700, 680, 400)
    asoma = e_back(prog(t, t0 + 0.4, 0.5))
    raton(c, 540 + 12 * math.sin(t * 1.3), 900 - 90 * asoma + 6 * math.sin(t * 3), t, 1.2)
    c.pegar_en(fr)
    s = e_back(prog(t, t0 + 0.15, 0.5))
    if s > 0:
        tachado = int(10 * e_out(prog(t, E["m_eligio"], 0.35)))
        escritura = int(10 * e_out(prog(t, E["m_eligio"] + 0.35, 0.5)))
        componer(fr, etiqueta_nombre(tachado, t >= E["m_eligio"], escritura), 540, 1120, escala=s,
                 rot=-3 + 2 * math.sin(t * 1.5))
    se = pop(t, E["m_esposa"], 0.4)
    if se > 0:
        componer(fr, cartel("LILLIAN DISNEY", "SU ESPOSA", (255, 214, 120), (60, 10, 20), 520, 70), 540, 640,
                 escala=se, rot=2)
    componer(fr, texto("1928", "negra", 40, color=(255, 240, 200), borde=5), 940, 1370, alpha=0.8)
    # película vieja en blanco y negro: se llena de color cuando nace el nombre
    if color < 1:
        rng = np.random.default_rng(int(t * 24))
        grano = Image.fromarray(rng.integers(0, 255, (H // 8, W // 8), dtype=np.uint8), "L").resize((W, H))
        bn = fr.convert("L")
        bn = Image.blend(bn, grano, 0.08).convert("RGBA")
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        for _ in range(3):
            x = rng.uniform(0, W)
            d.line([(x, 0), (x + rng.uniform(-20, 20), H)], fill=(255, 255, 255, 60), width=2)
        bn.alpha_composite(capa)
        titila = 0.9 + 0.1 * rng.uniform()
        bn = Image.eval(bn, lambda v: int(v * titila)) if titila < 0.99 else bn
        fr = Image.blend(bn, fr, color)
    chispas(fr, t, tm, 540, 1000, n=26, seed=4, colores=((255, 214, 10), (255, 255, 255), (80, 160, 255)),
            vel=(350, 850), grav=500, dur=1.2)
    encabezado(fr, t, 3, E["mortimer_badge"])
    titulo(fr, t, TITULOS["mortimer"]["titulo"], t0 + 0.15, color=(255, 230, 150))
    pildora(fr, t, TITULOS["mortimer"]["subtitulo"], (170, 30, 40), E["m_mortimer"], hasta=E["m_eligio"])
    pildora(fr, t, "¡EL NOMBRE LO ELIGIÓ SU ESPOSA!", (30, 80, 190), E["m_eligio"] + 0.05)
    return fr


# ======================================================= íconos del cierre
def _icono_amarillo(c, x, y, s, t):
    tele(c, x, y + 16 * s, 0.3 * s)
    return [(_mini_pantalla(), x - 15 * s, y + 13 * s)] if s > 0.3 else []


@lru_cache(None)
def _mini_pantalla():
    im = pantalla(0, 3, 107, 98)
    im.putalpha(_mascara_pantalla(107, 98, 12))
    return im


def _icono_esponja(c, x, y, s, t):
    c.circulo(x, y, 118 * s, fill=(60, 150, 210))
    pez_mar(c, x - 20 * s, y - 34 * s, 0.9 * s, 1, (255, 150, 60))
    estrella_mar(c, x + 40 * s, y + 40 * s, 0.9 * s, (255, 110, 90))
    esponja_mar(c, x - 50 * s, y + 60 * s, 0.7 * s, (250, 200, 70))


def _icono_mortimer(c, x, y, s, t):
    return [(_mini_etiqueta(), x, y + 6 * s)] if s > 0.05 else []


@lru_cache(None)
def _mini_etiqueta():
    im = etiqueta_nombre(10, True, 10)
    return im.resize((int(im.width * 0.33), int(im.height * 0.33)), Image.LANCZOS)


ICONOS = [_icono_amarillo, _icono_esponja, _icono_mortimer]
ESCENAS = {"amarillo": escena_amarillo, "esponja": escena_esponja, "mortimer": escena_mortimer}
