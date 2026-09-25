"""Animación del video vertical (1080x1920, 30 fps) y exportación final.

Todo se dibuja con código (Pillow + numpy): fondos, personajes, textos,
subtítulos karaoke y transiciones. Los tiempos salen de build/timeline.json,
así cada animación cae justo con la palabra que dice la voz.

Uso:
    python animacion.py                 -> output/curiosidades_30s.mp4
    python animacion.py --previa 1 5.5  -> build/previa/*.png (cuadros sueltos)
"""
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from guion import BLOQUES
from tiempos import BUILD, RAIZ, Linea, _norm, eventos

W, H, FPS = 1080, 1920, 30
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SALIDA = os.path.join(RAIZ, "output", "curiosidades_30s.mp4")
FUENTES = {
    "titulo": "LuckiestGuy-Regular.ttf",
    "negra": "Montserrat-Black.ttf",
}
TITULOS = {b["id"]: b for b in BLOQUES}
TINTA = (24, 16, 48)
ACENTO = {"pulpo": (0, 180, 216), "miel": (255, 183, 3),
          "venus": (123, 44, 191), "cierre": (255, 0, 110)}

L = Linea()
E = eventos(L)
ORDEN = [b["id"] for b in L.bloques]
ESC = {b["id"]: b for b in L.bloques}


# ================================================================ utilidades
@lru_cache(None)
def F(nombre, tam):
    return ImageFont.truetype(os.path.join(RAIZ, "assets", "fonts", FUENTES[nombre]), tam)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, dur):
    return clamp((t - t0) / dur)


def lerp(a, b, x):
    return a + (b - a) * x


def e_out(x):
    return 1 - (1 - clamp(x)) ** 3


def e_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def e_back(x, s=1.9):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def pop(t, t0, dur=0.35):
    """Escala de 'aparición con rebote': 0 antes de t0, 1 al terminar."""
    return 0.0 if t < t0 else e_back(prog(t, t0, dur))


def mezcla(c1, c2, x):
    return tuple(int(round(lerp(a, b, clamp(x)))) for a, b in zip(c1, c2))


def componer(base, im, cx, cy, escala=1.0, alpha=1.0, rot=0.0):
    """Pega `im` centrada en (cx, cy) con escala/rotación/opacidad, recortando bordes."""
    if escala <= 0.01 or alpha <= 0.01:
        return
    if abs(escala - 1) > 1e-3:
        im = im.resize((max(1, round(im.width * escala)), max(1, round(im.height * escala))),
                       Image.BICUBIC)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point([int(v * alpha) for v in range(256)]))
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(im.width, base.width - x), min(im.height, base.height - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    base.alpha_composite(im, (x + sx0, y + sy0), (sx0, sy0, sx1, sy1))


class Capa:
    """Lienzo sobremuestreado (antialias) sobre una región del cuadro."""

    def __init__(self, x0, y0, w, h, ss=2):
        self.x0, self.y0, self.w, self.h, self.ss = x0, y0, w, h, ss
        self.im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def p(self, x, y):
        return ((x - self.x0) * self.ss, (y - self.y0) * self.ss)

    def g(self, v):
        return max(1, int(round(v * self.ss)))

    def elipse(self, cx, cy, rx, ry, fill=None, borde=None, grosor=0):
        if rx <= 0 or ry <= 0:
            return
        a, b = self.p(cx - rx, cy - ry)
        c, d = self.p(cx + rx, cy + ry)
        self.d.ellipse([a, b, c, d], fill=fill, outline=borde,
                       width=self.g(grosor) if borde else 0)

    def circulo(self, cx, cy, r, **kw):
        self.elipse(cx, cy, r, r, **kw)

    def poligono(self, pts, fill=None, borde=None, grosor=0):
        self.d.polygon([self.p(x, y) for x, y in pts], fill=fill, outline=borde,
                       width=self.g(grosor) if borde else 1)

    def linea(self, pts, color, grosor, puntas=True):
        P = [self.p(x, y) for x, y in pts]
        g = self.g(grosor)
        self.d.line(P, fill=color, width=g, joint="curve")
        if puntas:
            for x, y in (P[0], P[-1]):
                self.d.ellipse([x - g / 2, y - g / 2, x + g / 2, y + g / 2], fill=color)

    def tubo(self, pts, radios, color):
        for (x, y), r in zip(pts, radios):
            self.circulo(x, y, r, fill=color)

    def rrect(self, x0, y0, x1, y1, r, fill=None, borde=None, grosor=0):
        a, b = self.p(x0, y0)
        c, d = self.p(x1, y1)
        self.d.rounded_rectangle([a, b, c, d], radius=r * self.ss, fill=fill, outline=borde,
                                 width=self.g(grosor) if borde else 0)

    def arco(self, cx, cy, rx, ry, a0, a1, color, grosor):
        a, b = self.p(cx - rx, cy - ry)
        c, d = self.p(cx + rx, cy + ry)
        self.d.arc([a, b, c, d], a0, a1, fill=color, width=self.g(grosor))

    def imagen(self):
        return self.im.resize((self.w, self.h), Image.BOX)

    def pegar_en(self, fr):
        fr.alpha_composite(self.imagen(), (self.x0, self.y0))


@lru_cache(maxsize=512)
def texto(txt, fuente, tam, color=(255, 255, 255), borde=0, color_borde=TINTA, sombra=0):
    """Texto con contorno y sombra, recortado a su tamaño."""
    f = F(fuente, tam)
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), txt, font=f, stroke_width=borde)
    pad = borde + 6
    im = Image.new("RGBA", (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad + sombra), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = (pad - bb[0], pad - bb[1])
    if sombra:
        d.text((o[0], o[1] + sombra), txt, font=f, fill=(10, 5, 30, 150),
               stroke_width=borde, stroke_fill=(10, 5, 30, 150))
    d.text(o, txt, font=f, fill=color, stroke_width=borde, stroke_fill=color_borde)
    return im


def texto_ajustado(txt, fuente, tam, ancho_max, **kw):
    while tam > 20:
        im = texto(txt, fuente, tam, **kw)
        if im.width <= ancho_max:
            return im
        tam -= 4
    return im


# ============================================================ fondos (numpy)
def gradiente(stops):
    y = np.linspace(0, 1, H)
    img = np.zeros((H, W, 3), np.float32)
    for ch in range(3):
        img[:, :, ch] = np.interp(y, [p for p, _ in stops], [c[ch] for _, c in stops])[:, None]
    return img


def resplandor(img, cx, cy, r, color, fuerza):
    yy, xx = np.ogrid[:H, :W]
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / r ** 2))[..., None] * fuerza
    img += (np.array(color, np.float32) - img) * g


def viñeta(img, fuerza=0.45):
    yy, xx = np.ogrid[:H, :W]
    d = np.sqrt(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    img *= (1 - fuerza * np.clip(d - 0.55, 0, 1) ** 1.5)[..., None]


def a_imagen(arr, seed=0):
    ruido = np.random.default_rng(seed).uniform(-1.5, 1.5, arr.shape[:2])[..., None]
    return Image.fromarray(np.clip(arr + ruido, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def fondo_gancho():
    a = gradiente([(0, (58, 12, 163)), (0.55, (114, 9, 183)), (1, (247, 37, 133))])
    resplandor(a, 540, 1050, 650, (255, 140, 230), 0.35)
    viñeta(a)
    return a_imagen(a, 1)


def fondo_pulpo():
    a = gradiente([(0, (0, 190, 225)), (0.35, (0, 119, 182)), (1, (3, 10, 80))])
    resplandor(a, 540, -150, 900, (200, 245, 255), 0.5)
    viñeta(a)
    return a_imagen(a, 2)


def fondo_miel():
    a = gradiente([(0, (255, 94, 58)), (0.32, (255, 149, 0)), (0.6, (255, 210, 110)), (1, (255, 220, 140))])
    resplandor(a, 860, 640, 420, (255, 245, 205), 0.65)
    img = a_imagen(a, 3)
    c = Capa(700, 480, 320, 320)
    c.circulo(860, 640, 98, fill=(255, 248, 225))
    c.pegar_en(img)
    return img


def dunas():
    c = Capa(0, 1000, W, H - 1000)
    for base, amp, fase, col in [(1110, 26, 0.0, (244, 184, 96)), (1150, 34, 1.7, (230, 158, 66)),
                                 (1230, 40, 3.1, (214, 136, 48))]:
        pts = [(x, base + amp * math.sin(x / 170 + fase)) for x in range(-20, W + 40, 20)]
        c.poligono(pts + [(W + 40, H), (-20, H)], fill=col)
    # rugosidad de la arena
    rng = np.random.default_rng(5)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(1240, H)
        c.elipse(x, y, rng.uniform(8, 26), 3, fill=(200, 122, 40))
    return c.imagen(), c.y0


def fondo_venus():
    a = gradiente([(0, (8, 6, 30)), (0.5, (22, 12, 64)), (1, (48, 20, 96))])
    resplandor(a, 180, 520, 420, (120, 60, 200), 0.35)
    resplandor(a, 930, 1350, 480, (40, 90, 200), 0.3)
    resplandor(a, 600, 1750, 320, (200, 60, 160), 0.25)
    img = a_imagen(a, 4)
    rng = np.random.default_rng(11)
    for _ in range(140):
        componer(img, spr_estrella(int(rng.integers(3, 9))), rng.uniform(0, W), rng.uniform(0, H),
                 alpha=rng.uniform(0.3, 0.9))
    return img


def fondo_cierre():
    a = gradiente([(0, (255, 0, 110)), (0.5, (131, 56, 236)), (1, (58, 134, 255))])
    resplandor(a, 540, 800, 600, (255, 190, 240), 0.3)
    viñeta(a)
    return a_imagen(a, 5)


def rayos_luz():
    """Rayos de luz bajo el agua (se precalculan borrosos y luego se mecen)."""
    capa = Image.new("RGBA", (W + 300, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for x, ancho, alfa in [(150, 90, 40), (420, 140, 34), (700, 80, 42), (980, 120, 30), (1250, 90, 36)]:
        d.polygon([(x, -10), (x + ancho, -10), (x + ancho * 2.4 - 260, H * 0.85), (x - 260, H * 0.85)],
                  fill=(220, 250, 255, alfa))
    return capa.filter(ImageFilter.GaussianBlur(28))


# ================================================================== sprites
@lru_cache(None)
def spr_estrella(tam):
    s = tam * 8
    yy, xx = np.mgrid[-s:s + 1, -s:s + 1].astype(np.float32)
    d = np.sqrt(xx ** 2 + yy ** 2) / tam
    a = np.exp(-d ** 2 * 1.2) + 0.35 * np.exp(-d * 0.9)
    a += 0.6 * np.exp(-(np.abs(xx) / (tam * 0.25))) * np.exp(-np.abs(yy) / (tam * 3))
    a += 0.6 * np.exp(-(np.abs(yy) / (tam * 0.25))) * np.exp(-np.abs(xx) / (tam * 3))
    a = np.clip(a / a.max(), 0, 1)
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = (255, 250, 235)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


@lru_cache(None)
def spr_burbuja(r):
    c = Capa(0, 0, 2 * r + 8, 2 * r + 8, ss=4)
    m = r + 4
    c.circulo(m, m, r, fill=(220, 245, 255, 40), borde=(230, 250, 255, 190), grosor=max(1.5, r / 7))
    c.arco(m, m, r * 0.62, r * 0.62, 200, 260, (255, 255, 255, 230), max(1.5, r / 6))
    return c.imagen()


@lru_cache(None)
def spr_brillo(tam, color=(255, 250, 220)):
    c = Capa(0, 0, 2 * tam + 4, 2 * tam + 4, ss=4)
    m = tam + 2
    pts = []
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        r = tam if i % 2 == 0 else tam * 0.28
        pts.append((m + r * math.cos(a), m + r * math.sin(a)))
    c.poligono(pts, fill=color + (255,))
    return c.imagen()


@lru_cache(None)
def spr_resplandor(r, color):
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1].astype(np.float32)
    a = np.exp(-((xx ** 2 + yy ** 2) / (r * 0.45) ** 2))
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = color
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


FONDOS = {}
EXTRA = {}


def preparar():
    FONDOS.update(gancho=fondo_gancho(), pulpo=fondo_pulpo(), miel=fondo_miel(),
                  venus=fondo_venus(), cierre=fondo_cierre())
    EXTRA["rayos"] = rayos_luz()
    EXTRA["dunas"] = dunas()


# ======================================================= elementos comunes
def rayos_sol(fr, cx, cy, ang, n=14, color=(255, 255, 255, 24)):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    R = 2600
    for i in range(n):
        a0 = ang + i * 2 * math.pi / n
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=color)
    fr.alpha_composite(capa)


_rng = np.random.default_rng(21)
CONFETI = [dict(x=_rng.uniform(0, W), y=_rng.uniform(-H, 0), v=_rng.uniform(260, 520),
                a=_rng.uniform(20, 60), f=_rng.uniform(1, 3), ph=_rng.uniform(0, 6.3),
                giro=_rng.uniform(-6, 6), tam=_rng.uniform(14, 26),
                col=[(255, 214, 10), (0, 245, 212), (255, 255, 255), (255, 84, 0), (58, 134, 255),
                     (255, 0, 110)][i % 6])
           for i in range(46)]


def confeti(fr, t, t0, alpha=1.0):
    if t < t0:
        return
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    dt = t - t0
    for p in CONFETI:
        y = (p["y"] + p["v"] * dt) % (H + 1200) - 100
        if y < -60:
            continue
        x = p["x"] + p["a"] * math.sin(p["f"] * t + p["ph"])
        ang = p["giro"] * t
        w, h = p["tam"], p["tam"] * 0.55 * abs(math.cos(p["f"] * 2 * t + p["ph"]))
        ca, sa = math.cos(ang), math.sin(ang)
        pts = [(x + ca * dx - sa * dy, y + sa * dx + ca * dy)
               for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
        d.polygon(pts, fill=p["col"] + (int(230 * alpha),))
    fr.alpha_composite(capa)


def encabezado(fr, t, numero, t0):
    """Píldora '¿SABÍAS QUE...?' con el número de la curiosidad."""
    s = pop(t, t0, 0.4)
    if s <= 0:
        return
    im = _pildora_encabezado(numero)
    componer(fr, im, W / 2, 190 + 3 * math.sin(t * 2.5), escala=s)


@lru_cache(None)
def _pildora_encabezado(numero):
    txt = texto("¿SABÍAS QUE...?", "negra", 44, color=TINTA)
    w, h = txt.width + 150, 96
    c = Capa(0, 0, w + 10, h + 16, ss=3)
    c.rrect(5, 11, w + 5, h + 11, h / 2, fill=(10, 5, 30, 90))
    c.rrect(5, 5, w + 5, h + 5, h / 2, fill=(255, 255, 255))
    c.circulo(5 + h / 2, 5 + h / 2, h / 2 - 8, fill=(255, 214, 10), borde=TINTA, grosor=4)
    im = c.imagen()
    n = texto(str(numero), "titulo", 60, color=TINTA)
    im.alpha_composite(n, (int(5 + h / 2 - n.width / 2), int(5 + h / 2 - n.height / 2 + 2)))
    im.alpha_composite(txt, (int(h + 12), int(5 + h / 2 - txt.height / 2)))
    return im


def titulo(fr, t, txt, t0, y=340, tam=150, color=(255, 255, 255)):
    s = pop(t, t0, 0.45)
    if s <= 0:
        return
    im = texto_ajustado(txt, "titulo", tam, 1000, color=color, borde=13, sombra=12)
    componer(fr, im, W / 2, y + 5 * math.sin(t * 2.2), escala=s)


@lru_cache(None)
def _pildora(txt, color, tam=50):
    tx = texto(txt, "negra", tam, color=(255, 255, 255), borde=0)
    if tx.width > 900:
        return _pildora(txt, color, tam - 4)
    w, h = tx.width + 70, tx.height + 34
    c = Capa(0, 0, w + 10, h + 14, ss=3)
    c.rrect(5, 11, w + 5, h + 11, 28, fill=(10, 5, 30, 110))
    c.rrect(5, 5, w + 5, h + 5, 28, fill=color, borde=(255, 255, 255), grosor=5)
    im = c.imagen()
    im.alpha_composite(tx, (int(5 + w / 2 - tx.width / 2), int(5 + h / 2 - tx.height / 2)))
    return im


def pildora(fr, t, txt, color, t0, y=470, rot=-2.0):
    s = pop(t, t0, 0.4)
    if s > 0:
        componer(fr, _pildora(txt, color), W / 2, y, escala=s, rot=rot)


# ================================================================ personajes
def corazon_pts(cx, cy, tam, n=64):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * tam / 16, cy - y * tam / 16))
    return pts


def corazon(c, cx, cy, tam, color):
    c.poligono(corazon_pts(cx, cy, tam), fill=color, borde=(40, 8, 30), grosor=max(3, tam / 9))
    c.elipse(cx - tam * 0.45, cy - tam * 0.38, tam * 0.2, tam * 0.13, fill=(255, 255, 255, 230))


def latido(t, fase=0.0):
    x = ((t + fase) % 0.9) / 0.9
    return 1 + 0.16 * math.exp(-((x - 0.06) / 0.05) ** 2) + 0.10 * math.exp(-((x - 0.24) / 0.05) ** 2)


def parpadeo(t, periodo=2.7, fase=0.0):
    ph = (t + fase) % periodo
    return abs(1 - 2 * ph / 0.16) if ph < 0.16 else 1.0


def pulpo(c, cx, cy, t, k=1.0, sorpresa=False):
    ROSA, BORDE, CLARO, OSC = (255, 111, 145), (110, 18, 58), (255, 178, 196), (236, 78, 118)
    tent = []
    for i in range(8):
        u = (i - 3.5) / 3.5
        bx, by = cx + u * 118 * k, cy + 105 * k
        ang = math.radians(90 - u * 64)
        dx, dy = math.cos(ang), math.sin(ang)
        px, py = -dy, dx
        largo = (235 + 40 * (1 - abs(u))) * k
        pts, rad = [], []
        for j in range(36):
            s = j / 35
            onda = math.sin(s * 5.2 - t * 4.0 + i * 0.9) * 24 * k * s
            rizo = (s ** 3) * 60 * k * (-1 if u >= 0 else 1)
            off = onda + rizo
            pts.append((bx + dx * largo * s + px * off, by + dy * largo * s + py * off))
            rad.append((31 - 23 * s) * k)
        tent.append((pts, rad))
    for pts, rad in tent:
        c.tubo(pts, [r + 6 * k for r in rad], BORDE)
    for pts, rad in tent:
        c.tubo(pts, rad, ROSA)
        for j in range(8, 33, 5):
            x, y = pts[j]
            c.circulo(x, y + rad[j] * 0.3, rad[j] * 0.36, fill=CLARO)
    # cabeza
    c.elipse(cx, cy, 190 * k + 7 * k, 178 * k + 7 * k, fill=BORDE)
    c.elipse(cx, cy, 190 * k, 178 * k, fill=ROSA)
    c.elipse(cx, cy + 118 * k, 150 * k, 44 * k, fill=ROSA)
    c.elipse(cx - 72 * k, cy - 98 * k, 58 * k, 32 * k, fill=CLARO)
    for sx, sy, sr in [(62, -112, 17), (114, -48, 12), (-128, -24, 10), (18, -146, 9)]:
        c.circulo(cx + sx * k, cy + sy * k, sr * k, fill=OSC)
    # cara
    abre = parpadeo(t, fase=0.6)
    for s in (-1, 1):
        ex, ey = cx + s * 70 * k, cy + 26 * k
        if abre < 0.25:
            c.linea([(ex - 30 * k, ey), (ex + 30 * k, ey)], BORDE, 8 * k)
        else:
            ry = 48 * k * (1.15 if sorpresa else 1.0)
            c.elipse(ex, ey, 40 * k, ry * abre, fill=(255, 255, 255), borde=BORDE, grosor=6 * k)
            pr = (16 if sorpresa else 24) * k
            c.elipse(ex + 5 * k, ey + 8 * k, pr, pr * min(1, abre * 1.2), fill=(30, 18, 40))
            c.circulo(ex + 13 * k, ey - 4 * k, 8 * k, fill=(255, 255, 255))
    for s in (-1, 1):
        c.elipse(cx + s * 122 * k, cy + 80 * k, 26 * k, 14 * k, fill=(255, 78, 120))
    if sorpresa:
        c.elipse(cx, cy + 92 * k, 17 * k, 21 * k, fill=BORDE)
    else:
        c.arco(cx, cy + 66 * k, 30 * k, 24 * k, 25, 155, BORDE, 7 * k)


def vasija(c, cx, cy, t, k=1.0):
    TERRA, OSC, BORDE, CLARO = (205, 108, 60), (160, 74, 40), (86, 36, 16), (236, 156, 102)
    MIEL, MIEL_C, MIEL_B = (247, 179, 43), (255, 226, 140), (176, 100, 6)
    top = cy - 215 * k
    # cuello
    c.rrect(cx - 98 * k, top, cx + 98 * k, cy - 110 * k, 18 * k, fill=TERRA, borde=BORDE, grosor=6 * k)
    c.rrect(cx - 60 * k, top + 10 * k, cx - 35 * k, cy - 125 * k, 10 * k, fill=CLARO)
    # cuerpo con sombreado
    c.elipse(cx, cy, 185 * k, 168 * k, fill=BORDE)
    c.elipse(cx, cy, 179 * k, 162 * k, fill=OSC)
    c.elipse(cx - 20 * k, cy - 10 * k, 154 * k, 148 * k, fill=TERRA)
    c.elipse(cx - 92 * k, cy - 62 * k, 26 * k, 48 * k, fill=CLARO)
    # banda egipcia
    y0, y1 = cy - 18 * k, cy + 34 * k

    def xw(y):
        return 179 * k * math.sqrt(max(0.0, 1 - ((y - cy) / (162 * k)) ** 2))

    ys = [y0 + (y1 - y0) * i / 6 for i in range(7)]
    banda = [(cx - xw(y), y) for y in ys] + [(cx + xw(y), y) for y in reversed(ys)]
    c.poligono(banda, fill=(29, 78, 137))
    n = 9
    for i in range(n):
        f0 = -math.pi / 2 + math.pi * i / n
        f1 = -math.pi / 2 + math.pi * (i + 1) / n
        xa, xb = cx + xw(y1) * math.sin(f0), cx + xw(y1) * math.sin(f1)
        c.poligono([(xa, y1 - 3 * k), (xb, y1 - 3 * k), ((xa + xb) / 2, y0 + 5 * k)], fill=(244, 197, 66))
    # boca
    c.elipse(cx, top, 128 * k, 32 * k, fill=TERRA, borde=BORDE, grosor=6 * k)
    # miel desbordando
    c.elipse(cx, top - 6 * k, 116 * k, 28 * k, fill=MIEL_B)
    c.elipse(cx, top - 20 * k, 88 * k, 36 * k, fill=MIEL_B)
    for i, (dx, lmin, lmax, per) in enumerate([(-78, 40, 120, 2.3), (-30, 60, 175, 2.9),
                                              (28, 30, 95, 2.0), (74, 50, 150, 2.6)]):
        ph = ((t + i * 0.7) % per) / per
        largo = lerp(lmin, lmax, e_in_out(min(1.0, ph / 0.78))) * k
        x = cx + dx * k
        pts = [(x + 3 * k * math.sin(j), top + largo * j / 14) for j in range(15)]
        c.tubo(pts, [15 * k] * 15, MIEL_B)
        c.circulo(pts[-1][0], pts[-1][1] + 4 * k, 20 * k, fill=MIEL_B)
        c.tubo(pts, [11 * k] * 15, MIEL)
        c.circulo(pts[-1][0], pts[-1][1] + 4 * k, 16 * k, fill=MIEL)
        c.circulo(pts[-1][0] - 5 * k, pts[-1][1], 4.5 * k, fill=MIEL_C)
        if ph > 0.78:  # gota que se desprende
            a = (ph - 0.78) * per
            gy = pts[-1][1] + 4 * k + 900 * a * a * k
            c.circulo(x, gy, 13 * k * (1 - 0.3 * a), fill=MIEL_B)
            c.circulo(x, gy, 10 * k * (1 - 0.3 * a), fill=MIEL)
    c.elipse(cx, top - 6 * k, 110 * k, 23 * k, fill=MIEL)
    c.elipse(cx, top - 20 * k, 82 * k, 30 * k, fill=MIEL)
    c.elipse(cx - 30 * k, top - 32 * k, 26 * k, 10 * k, fill=MIEL_C)


def abeja(c, x, y, t, k=1.0, dir_=1):
    D = (38, 26, 18)
    aleteo = 0.35 + 0.65 * abs(math.sin(t * 38))
    for dx in (-10, 8):
        c.elipse(x + dx * k * dir_, y - 30 * k, 18 * k, 28 * k * aleteo, fill=(225, 245, 255),
                 borde=(70, 90, 120), grosor=3 * k)
    c.poligono([(x - 36 * k * dir_, y - 5 * k), (x - 52 * k * dir_, y), (x - 36 * k * dir_, y + 6 * k)], fill=D)
    c.elipse(x, y, 38 * k, 26 * k, fill=(255, 205, 40), borde=D, grosor=4 * k)
    for dx in (-12, 6):
        c.elipse(x + dx * k * dir_, y, 6 * k, 22 * k, fill=D)
    c.circulo(x + 36 * k * dir_, y - 4 * k, 16 * k, fill=D)
    c.circulo(x + 41 * k * dir_, y - 8 * k, 5 * k, fill=(255, 255, 255))
    for da in (-1, 1):
        c.linea([(x + 40 * k * dir_, y - 16 * k), (x + (48 + 6 * da) * k * dir_, y - 34 * k)], D, 3 * k)


def piramide(c, ax, by, ancho, alto):
    ay = by - alto
    bl, br, ridge = (ax - ancho / 2, by), (ax + ancho / 2, by), (ax + ancho * 0.14, by)
    c.poligono([(ax, ay), bl, ridge], fill=(240, 180, 84))
    c.poligono([(ax, ay), ridge, br], fill=(186, 112, 40))
    for i in range(1, 7):
        f = i / 7
        y = ay + alto * f
        c.linea([(ax + (bl[0] - ax) * f, y), (ax + (ridge[0] - ax) * f, y)], (205, 140, 60), 3, False)
        c.linea([(ax + (ridge[0] - ax) * f, y), (ax + (br[0] - ax) * f, y)], (150, 86, 28), 3, False)
    c.poligono([(ax, ay), bl, br], borde=(110, 60, 18), grosor=5)
    c.linea([(ax, ay), ridge], (110, 60, 18), 4)


def sprite_venus(r, t, dormido=True):
    """Venus con nubes que giran lentísimo y cara de sueño."""
    ss = 2
    tam = int(2 * r + 16)
    c = Capa(0, 0, tam, tam, ss=ss)
    m = tam / 2
    c.circulo(m, m, r, fill=(232, 168, 88))
    off = (t * 9) % 120
    for j, (yy, col, gro) in enumerate([(-0.62, (246, 208, 138), 0.12), (-0.3, (205, 128, 58), 0.10),
                                        (0.02, (250, 214, 150), 0.14), (0.36, (210, 138, 64), 0.1),
                                        (0.66, (246, 204, 130), 0.1)]):
        pts = [(x, m + yy * r + math.sin((x + off + j * 37) / (r * 0.28)) * r * 0.06)
               for x in np.linspace(m - r - 20, m + r + 20, 30)]
        c.linea(pts, col, gro * r * 2, puntas=False)
    base = c.im
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse([(m + r * 0.1) * ss, (m - r * 0.7) * ss, (m + r * 2.0) * ss,
                                    (m + r * 1.6) * ss], fill=(90, 30, 40, 95))
    base.alpha_composite(sombra)
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).ellipse([(m - r) * ss, (m - r) * ss, (m + r) * ss, (m + r) * ss], fill=255)
    base.putalpha(Image.fromarray(np.minimum(np.array(base.getchannel("A")), np.array(mask))))
    c.im = base
    c.d = ImageDraw.Draw(c.im)
    c.circulo(m, m, r, borde=(120, 56, 24), grosor=max(3, r / 16))
    k = r / 100
    BORDE = (90, 40, 20)
    if dormido:
        for s in (-1, 1):
            c.arco(m + s * 36 * k, m + 2 * k, 20 * k, 14 * k, 10, 170, BORDE, 6 * k)
        c.elipse(m, m + 42 * k, 12 * k, 8 * k, fill=BORDE)
    else:
        for s in (-1, 1):
            c.circulo(m + s * 36 * k, m, 10 * k, fill=BORDE)
        c.arco(m, m + 28 * k, 18 * k, 12 * k, 20, 160, BORDE, 6 * k)
    for s in (-1, 1):
        c.elipse(m + s * 62 * k, m + 26 * k, 14 * k, 8 * k, fill=(240, 120, 110))
    return c.imagen()


def cara_emoji(c, cx, cy, r, t, explota):
    """Carita 🤯: sorprendida y, al llegar 'cabeza', con la tapa volada."""
    AM, OSC, BORDE = (255, 204, 51), (242, 160, 28), (122, 66, 8)
    c.circulo(cx, cy, r + 8, fill=BORDE)
    c.circulo(cx, cy, r, fill=OSC)
    c.circulo(cx - 6, cy - 14, r - 10, fill=AM)
    c.elipse(cx - r * 0.42, cy - r * 0.5, r * 0.22, r * 0.12, fill=(255, 236, 150))
    for s in (-1, 1):
        ex, ey = cx + s * r * 0.36, cy - r * 0.02
        c.elipse(ex, ey, r * 0.17, r * 0.22, fill=(255, 255, 255), borde=BORDE, grosor=5)
        c.circulo(ex, ey + r * 0.02, r * 0.065, fill=(30, 18, 30))
        c.arco(ex, ey - r * 0.28, r * 0.16, r * 0.09, 200, 340, BORDE, 8)
    c.elipse(cx, cy + r * 0.48, r * 0.17, r * 0.22, fill=(110, 36, 22))
    c.elipse(cx, cy + r * 0.58, r * 0.11, r * 0.09, fill=(222, 88, 90))
    if not explota:
        return
    corte = cy - r * 0.42
    ancho = math.sqrt(r * r - (cy - corte) ** 2) + 10
    dientes = [(cx - ancho - 12 + i * (2 * ancho + 24) / 12,
                corte + (14 if i % 2 else -10)) for i in range(13)]
    c.poligono([(cx - r - 20, cy - r - 30), (cx + r + 20, cy - r - 30)] + dientes[::-1],
               fill=(0, 0, 0, 0))
    c.elipse(cx, corte + 2, ancho - 4, r * 0.16, fill=(210, 112, 18), borde=BORDE, grosor=6)
    c.elipse(cx, corte + 4, ancho - 26, r * 0.1, fill=(110, 40, 8))


# ================================================================== escenas
def escena_gancho(t):
    fr = FONDOS["gancho"].copy()
    rayos_sol(fr, 540, 1080, t * 0.35, n=16, color=(255, 255, 255, 22))
    confeti(fr, t, 0.2, alpha=0.9)
    tb = E["g_boom"]
    # carita
    s = pop(t, E["g_cara"], 0.4)
    if s > 0:
        c = Capa(120, 520, 840, 880)
        cx, cy, r = 540, 1080, 205 * s
        temblor = clamp((t - E["g_cara"] - 0.3) / max(0.1, tb - E["g_cara"] - 0.3)) if t < tb else 0
        cx += math.sin(t * 95) * 7 * temblor
        explota = t >= tb
        cara_emoji(c, cx, cy, r, t, explota)
        if explota:
            p = e_out(prog(t, tb, 0.55))
            corte = cy - r * 0.42
            sube = (t - tb) * 30
            nube = [(-70, -80, 58), (70, -85, 60), (0, -120, 70), (-120, -150, 62), (120, -155, 64),
                    (-50, -200, 74), (60, -210, 76), (0, -250, 70), (-130, -230, 50), (135, -235, 52)]
            tallo = [(0, -10, 50), (-12, -40, 46), (10, -65, 44)]
            for capa_col, extra in (((122, 50, 8), 9), ((255, 120, 40), 0)):
                for dx, dy, rr in tallo + nube:
                    wob = 1 + 0.05 * math.sin(t * 9 + dx)
                    c.circulo(cx + dx * p, corte + (dy * p - sube), (rr * p * wob) + extra, fill=capa_col)
            for dx, dy, rr in nube:
                wob = 1 + 0.05 * math.sin(t * 9 + dx)
                c.circulo(cx + dx * p - 8, corte + (dy * p - sube) - 10, rr * p * wob * 0.72,
                          fill=(255, 196, 60))
            for dx, dy, rr in nube[5:]:
                c.circulo(cx + dx * p - 16, corte + (dy * p - sube) - 22, rr * p * 0.35, fill=(255, 240, 170))
        c.pegar_en(fr)
        if t >= tb:
            # rayos de explosión y chispas
            p = prog(t, tb, 0.45)
            if p < 1:
                capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                d = ImageDraw.Draw(capa)
                ox, oy = 540, 1080 - 205 * 0.42 - 120
                for i in range(14):
                    a = i * 2 * math.pi / 14 + 0.2
                    r0, r1 = 180 + 500 * p, 260 + 700 * e_out(p)
                    d.line([(ox + r0 * math.cos(a), oy + r0 * math.sin(a)),
                            (ox + r1 * math.cos(a), oy + r1 * math.sin(a))],
                           fill=(255, 245, 180, int(255 * (1 - p))), width=int(16 * (1 - p)) + 2)
                fr.alpha_composite(capa)
            rng = np.random.default_rng(3)
            dt = t - tb
            for i in range(26):
                a = rng.uniform(-math.pi, 0)
                v = rng.uniform(500, 1100)
                x = 540 + math.cos(a) * v * dt
                y = 1080 - 120 + math.sin(a) * v * dt + 900 * dt * dt
                if dt < 1.2:
                    componer(fr, spr_brillo(int(rng.integers(12, 26)),
                                            [(255, 240, 150), (255, 150, 60), (255, 255, 255)][i % 3]),
                             x, y, rot=dt * 300, alpha=clamp(1.3 - dt))
    # textos
    s3 = 0 if t < E["g_tres"] else lerp(2.6, 1.0, e_out(prog(t, E["g_tres"], 0.22)))
    if s3 > 0:
        rot = 8 * math.sin((t - E["g_tres"]) * 18) * math.exp(-(t - E["g_tres"]) * 5)
        componer(fr, texto("3", "titulo", 400, color=(255, 214, 10), borde=18, sombra=16),
                 540, 420 + 6 * math.sin(t * 2.4), escala=s3, rot=rot,
                 alpha=clamp((t - E["g_tres"]) / 0.08))
    s = pop(t, E["g_curio"], 0.4)
    if s > 0:
        im = texto_ajustado("CURIOSIDADES", "titulo", 140, 1000, borde=13, sombra=12)
        componer(fr, im, 540, 680 + 4 * math.sin(t * 2.2 + 1), escala=s)
    # destello de la explosión
    if tb <= t < tb + 0.18:
        fl = Image.new("RGBA", (W, H), (255, 250, 230, int(200 * (1 - prog(t, tb, 0.18)))))
        fr.alpha_composite(fl)
    return fr


def escena_pulpo(t):
    fr = FONDOS["pulpo"].copy()
    ray = EXTRA["rayos"]
    ox = int(150 + 60 * math.sin(t * 0.7))
    fr.alpha_composite(ray, (0, 0), (ox, 0, ox + W, H))
    rng = np.random.default_rng(8)
    for _ in range(26):
        r = int(rng.integers(6, 22))
        x0, y0, v = rng.uniform(0, W), rng.uniform(0, H + 200), rng.uniform(90, 220)
        y = (y0 - v * t) % (H + 200) - 60
        x = x0 + 18 * math.sin(t * 2 + x0)
        componer(fr, spr_burbuja(r), x, y)
    t0 = ESC["pulpo"]["escena_ini"]
    c = Capa(0, 470, W, H - 470)
    # algas
    for bx, alto, fase, col in [(70, 640, 0, (24, 150, 96)), (170, 420, 1.3, (40, 180, 110)),
                                (1010, 580, 2.1, (24, 150, 96)), (905, 360, 0.7, (40, 180, 110))]:
        pts = [(bx + math.sin(t * 1.6 + fase + j * 0.35) * 26 * (j / 30), H + 20 - alto * j / 30)
               for j in range(31)]
        c.tubo(pts, [30 - 20 * j / 30 + 5 for j in range(31)], (8, 70, 60))
        c.tubo(pts, [30 - 20 * j / 30 for j in range(31)], col)
    # pulpo
    ent = e_back(prog(t, t0, 0.65), 1.4)
    cy = 960 + (1 - ent) * 950 + 12 * math.sin(t * 2.2)
    sorpresa = E["p_azul"] <= t < E["p_azul"] + 0.9
    pulpo(c, 540, cy, t, 1.0, sorpresa)
    # corazones
    azul = e_in_out(prog(t, E["p_azul"], 0.35))
    col = mezcla((255, 59, 92), (58, 134, 255), azul)
    for i, (hx, hy) in enumerate([(290, 650), (540, 590), (790, 650)]):
        s = pop(t, E["p_corazones"] + 0.13 * i, 0.35)
        if s <= 0:
            continue
        tam = 62 * s * latido(t, i * 0.3)
        hy += 8 * math.sin(t * 2 + i)
        corazon(c, hx, hy, tam, col)
        if azul > 0:
            for kk in range(7):
                ts = E["p_azul"] + 0.12 + 0.5 * kk + 0.17 * i
                a = t - ts
                if 0 < a < 0.9:
                    gy = hy + tam * 0.95 + 0.5 * 1300 * a * a
                    rr = 11 * (1 - a * 0.5)
                    c.poligono([(hx - rr * 0.95, gy), (hx, gy - rr * 2.3), (hx + rr * 0.95, gy)],
                               fill=(58, 134, 255))
                    c.circulo(hx, gy + 2, rr, fill=(58, 134, 255))
    c.pegar_en(fr)
    encabezado(fr, t, 1, E["pulpo_badge"])
    titulo(fr, t, TITULOS["pulpo"]["titulo"], t0 + 0.15)
    pildora(fr, t, TITULOS["pulpo"]["subtitulo"], (58, 134, 255), E["p_azul"])
    return fr


def escena_miel(t):
    fr = FONDOS["miel"].copy()
    t0 = ESC["miel"]["escena_ini"]
    # pirámides que asoman detrás de las dunas
    sube = (1 - e_out(prog(t, E["m_piramides"], 0.8))) * 420
    if t >= E["m_piramides"] - 0.05:
        c = Capa(0, 760, W, 520)
        piramide(c, 235, 1160 + sube, 460, 340)
        piramide(c, 880, 1160 + sube * 1.1, 330, 245)
        c.pegar_en(fr)
    dun, dy = EXTRA["dunas"]
    fr.alpha_composite(dun, (0, dy))
    # polvito dorado
    rng = np.random.default_rng(9)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for _ in range(40):
        x0, y0, v = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(20, 60)
        x = (x0 + v * t) % W
        y = y0 + 20 * math.sin(t + x0)
        r = rng.uniform(2, 5)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 245, 200, 150))
    fr.alpha_composite(capa)
    # vasija + abeja
    s = pop(t, t0 + 0.15, 0.5)
    c = Capa(0, 560, W, 760)
    if s > 0:
        vasija(c, 540, 1070 + 4 * math.sin(t * 2), t, 1.0 * s)
    if t > t0 + 0.4:
        th = (t - t0) * 2.1
        bx = 540 + 340 * math.sin(th)
        by = 790 + 70 * math.sin(2 * th)
        abeja(c, bx, by, t, 1.0, 1 if math.cos(th) >= 0 else -1)
    c.pegar_en(fr)
    # contador de años
    s = pop(t, E["m_contador"] - 0.1, 0.35)
    if s > 0:
        n = int(round(3000 * e_out(prog(t, E["m_contador"], E["m_contador_fin"] - E["m_contador"] + 0.25)), -1))
        componer(fr, _cartel_anios(n), 540, 640, escala=s)
    # sello
    if t >= E["m_comer"]:
        p = prog(t, E["m_comer"], 0.2)
        esc = lerp(2.4, 1.0, e_out(p))
        componer(fr, _sello(), 540, 1070, escala=esc, rot=-9, alpha=clamp(p * 3))
        if p >= 1:
            for i in range(8):
                a = i * 2 * math.pi / 8 + 0.3
                tw = 0.5 + 0.5 * math.sin(t * 7 + i * 1.7)
                componer(fr, spr_brillo(22), 540 + 360 * math.cos(a), 1070 + 170 * math.sin(a),
                         escala=0.6 + 0.6 * tw, alpha=0.4 + 0.6 * tw)
    encabezado(fr, t, 2, E["miel_badge"])
    titulo(fr, t, TITULOS["miel"]["titulo"], t0 + 0.15, color=(255, 236, 160))
    pildora(fr, t, "NUNCA SE ECHA A PERDER", (214, 110, 0), E["m_nunca"])
    return fr


@lru_cache(maxsize=400)
def _cartel_anios(n):
    tx = texto(f"+{n:,}".replace(",", ".") + " AÑOS", "titulo", 104, color=(255, 214, 10),
               borde=0)
    w, h = 640, 150
    c = Capa(0, 0, w + 12, h + 18, ss=3)
    c.rrect(6, 14, w + 6, h + 14, 34, fill=(40, 16, 0, 120))
    c.rrect(6, 6, w + 6, h + 6, 34, fill=(70, 30, 6), borde=(255, 214, 10), grosor=6)
    im = c.imagen()
    im.alpha_composite(tx, (int(6 + w / 2 - tx.width / 2), int(6 + h / 2 - tx.height / 2 + 4)))
    return im


@lru_cache(None)
def _sello():
    tx = texto("¡COMESTIBLE!", "titulo", 100, color=(255, 255, 255), borde=0)
    w, h = tx.width + 80, tx.height + 50
    c = Capa(0, 0, w + 20, h + 20, ss=3)
    c.rrect(10, 10, w + 10, h + 10, 30, fill=(34, 170, 90), borde=(255, 255, 255), grosor=9)
    c.rrect(24, 24, w - 4, h - 4, 22, borde=(200, 255, 220), grosor=3)
    im = c.imagen()
    im.alpha_composite(tx, (int(10 + w / 2 - tx.width / 2), int(10 + h / 2 - tx.height / 2 + 4)))
    return im


def escena_venus(t):
    fr = FONDOS["venus"].copy()
    t0 = ESC["venus"]["escena_ini"]
    rng = np.random.default_rng(12)
    for i in range(24):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        tw = 0.5 + 0.5 * math.sin(t * rng.uniform(2, 5) + i)
        componer(fr, spr_estrella(int(rng.integers(5, 10))), x, y, alpha=0.3 + 0.7 * tw)
    cx, cy, rx, ry = 540, 800, 400, 150
    ent = e_out(prog(t, t0, 0.6))
    c = Capa(0, 480, W, 700)
    # órbita punteada (se vuelve dorada al decir "vuelta")
    oro = prog(t, E["v_vuelta"], 0.3)
    col_orb = mezcla((200, 190, 255), (255, 214, 10), oro) + (int(lerp(140, 255, oro)),)
    for a in range(0, 360, 10):
        c.arco(cx, cy, rx * ent, ry * ent, a + t * 12, a + 5 + t * 12, col_orb, 5 + 2 * oro)
    c.pegar_en(fr)
    # sol
    componer(fr, spr_resplandor(260, (255, 190, 60)), cx, cy, escala=ent * (1 + 0.04 * math.sin(t * 3)))
    c = Capa(cx - 170, cy - 170, 340, 340)
    for i in range(12):
        a = i * math.pi / 6 + t * 0.6
        r0, r1 = 112 * ent, 150 * ent
        c.poligono([(cx + r0 * math.cos(a - 0.14), cy + r0 * math.sin(a - 0.14)),
                    (cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                    (cx + r0 * math.cos(a + 0.14), cy + r0 * math.sin(a + 0.14))], fill=(255, 196, 40))
    c.circulo(cx, cy, 104 * ent, fill=(255, 150, 20))
    c.circulo(cx - 6, cy - 6, 94 * ent, fill=(255, 212, 60))
    c.circulo(cx - 36 * ent, cy - 38 * ent, 22 * ent, fill=(255, 240, 160))
    c.pegar_en(fr)
    # Venus sobre su órbita
    th = math.radians(18 + (t - t0) * 7)
    vx, vy = cx + rx * math.cos(th), cy + ry * math.sin(th)
    rv = 104 * (0.88 + 0.12 * math.sin(th)) * e_back(prog(t, t0 + 0.2, 0.5))
    if rv > 2:
        componer(fr, sprite_venus(int(rv), t), vx, vy)
        # zzz
        for i in range(3):
            ph = ((t * 0.6) + i / 3) % 1
            componer(fr, texto("z", "titulo", 40 + 14 * i, color=(255, 255, 255), borde=5),
                     vx + rv * 0.7 + 60 * ph + 10 * i, vy - rv * 0.8 - 120 * ph, alpha=math.sin(math.pi * ph))
        # flecha de giro sobre sí mismo
        s = pop(t, E["v_girar"], 0.4)
        if s > 0:
            c = Capa(int(vx - rv - 70), int(vy - rv - 70), int(2 * rv + 140), int(2 * rv + 140))
            R = (rv + 32) * s
            a0 = 200 + (t - E["v_girar"]) * 25
            c.arco(vx, vy, R, R * 0.42, a0, a0 + 250, (255, 255, 255), 8)
            ae = math.radians(a0 + 250)
            px, py = vx + R * math.cos(ae), vy + R * 0.42 * math.sin(ae)
            tx, ty = -math.sin(ae) * R, math.cos(ae) * R * 0.42
            nn = math.hypot(tx, ty) or 1
            tx, ty = tx / nn, ty / nn
            c.poligono([(px + tx * 26, py + ty * 26), (px - ty * 17, py + tx * 17),
                        (px + ty * 17, py - tx * 17)], fill=(255, 255, 255))
            c.pegar_en(fr)
    # barras comparativas
    barra(fr, t, 1150, "GIRAR SOBRE SÍ MISMO", "1 DÍA EN VENUS", E["v_dia"], 243, (255, 140, 66), E["v_girar"])
    barra(fr, t, 1290, "DAR LA VUELTA AL SOL", "1 AÑO EN VENUS", E["v_anio"], 225, (255, 214, 10),
          E["v_vuelta"])
    s = pop(t, E["v_anio"] + 0.05, 0.35)
    if s > 0:
        componer(fr, _pildora("¡MÁS LARGO!", (230, 40, 70), 40), 820, 1128, escala=s, rot=6)
    encabezado(fr, t, 3, E["venus_badge"])
    titulo(fr, t, TITULOS["venus"]["titulo"], t0 + 0.15, color=(255, 200, 120))
    pildora(fr, t, TITULOS["venus"]["subtitulo"], (123, 44, 191), E["v_dia"])
    return fr


def barra(fr, t, y, etiqueta, etiqueta2, t_cambio, dias, color, t0):
    s = e_out(prog(t, t0, 0.35))
    if s <= 0:
        return
    x0, total = 110, 860
    fill = total * dias / 250 * e_out(prog(t, t0 + 0.1, 0.8))
    c = Capa(0, y - 20, W, 130)
    c.rrect(x0, y + 32, x0 + total, y + 102, 35, fill=(255, 255, 255, 45), borde=(255, 255, 255, 90),
            grosor=3)
    if fill > 40:
        brillo = 0.5 + 0.5 * math.sin((t - t_cambio) * 12) if t >= t_cambio else 0
        col = mezcla(color, (255, 255, 255), 0.35 * brillo * clamp(1.5 - (t - t_cambio)))
        c.rrect(x0 + 4, y + 36, x0 + fill - 4, y + 98, 31, fill=col)
        c.rrect(x0 + 22, y + 44, x0 + fill - 22, y + 56, 6, fill=(255, 255, 255, 110))
    im = c.imagen()
    im.putalpha(im.getchannel("A").point([int(v * s) for v in range(256)]))
    fr.alpha_composite(im, (0, y - 20))
    cambio = t >= t_cambio
    et = texto(etiqueta2 if cambio else etiqueta, "negra", 42, borde=6, sombra=4)
    esc = 1 + 0.25 * math.exp(-(t - t_cambio) * 8) if cambio else 1
    componer(fr, et, x0 + et.width * esc / 2 - 4, y + 2, escala=esc, alpha=s)
    if fill > 300:
        v = texto(f"{dias} días", "negra", 44, color=TINTA)
        componer(fr, v, x0 + fill - v.width / 2 - 26, y + 67, alpha=clamp((fill - 300) / 100))


def escena_cierre(t):
    fr = FONDOS["cierre"].copy()
    t0 = ESC["cierre"]["escena_ini"]
    rayos_sol(fr, 540, 800, -t * 0.3, n=18, color=(255, 255, 255, 20))
    confeti(fr, t, t0, alpha=0.8)
    titulo(fr, t, "¿CUÁL TE", t0 + 0.1, y=320, tam=130)
    titulo(fr, t, "SORPRENDIÓ MÁS?", t0 + 0.22, y=460, tam=130, color=(255, 230, 90))
    aros = [(0, 180, 216), (255, 183, 3), (123, 44, 191)]
    for i, x in enumerate((200, 540, 880)):
        s = pop(t, t0 + 0.35 + 0.15 * i, 0.45)
        if s <= 0:
            continue
        y = 790 + 12 * math.sin(t * 3 - i * 0.9)
        c = Capa(int(x - 170), int(y - 170), 340, 350)
        r = 132 * s
        c.circulo(x, y + 12, r, fill=(20, 0, 60, 90))
        c.circulo(x, y, r, fill=(255, 255, 255), borde=aros[i], grosor=12 * s)
        if i == 0:
            pulpo(c, x, y - 32 * s, t, 0.3 * s)
        elif i == 1:
            vasija(c, x, y + 20 * s, t, 0.4 * s)
        c.circulo(x + 96 * s, y - 96 * s, 34 * s, fill=TINTA, borde=(255, 255, 255), grosor=4 * s)
        c.pegar_en(fr)
        if i == 2:
            componer(fr, sprite_venus(int(74 * s), t, dormido=False), x, y)
        componer(fr, texto(str(i + 1), "titulo", 44), x + 96 * s, y - 94 * s, escala=s)
    # comentario
    s = pop(t, E["c_comentarios"] - 0.1, 0.4)
    if s > 0:
        componer(fr, _pildora_comentario(), 540, 1075, escala=s, rot=-2)
    # botón seguir + cursor
    tb = E["c_seguinos"]
    s = pop(t, tb - 0.45, 0.4)
    if s > 0:
        clic = tb + 0.25
        hecho = t >= clic
        squish = 1 - 0.1 * math.sin(math.pi * prog(t, clic - 0.06, 0.18)) if t >= clic - 0.06 else 1
        componer(fr, _boton(hecho), 540, 1240, escala=s * squish * (1 + 0.03 * math.sin(t * 6)))
        if hecho:
            p = prog(t, clic, 0.5)
            if p < 1:
                c = Capa(240, 1000, 600, 480)
                rr = 60 + 260 * e_out(p)
                c.circulo(620, 1250, rr, borde=(255, 255, 255, int(255 * (1 - p))), grosor=10 * (1 - p) + 2)
                c.pegar_en(fr)
            rng = np.random.default_rng(4)
            dt = t - clic
            for i in range(22):
                a = rng.uniform(0, 2 * math.pi)
                v = rng.uniform(350, 900)
                x = 540 + math.cos(a) * v * dt
                y = 1240 + math.sin(a) * v * dt + 700 * dt * dt
                if dt < 1.4:
                    componer(fr, spr_brillo(int(rng.integers(12, 24)),
                                            [(255, 214, 10), (255, 255, 255), (0, 245, 212)][i % 3]),
                             x, y, rot=dt * 200, alpha=clamp(1.5 - dt))
        pc = e_in_out(prog(t, tb - 0.35, 0.5))
        px, py = lerp(980, 640, pc), lerp(1760, 1262, pc)
        if t >= clic - 0.05:
            px, py = 640, 1262
        pres = 0.85 if clic - 0.05 <= t < clic + 0.12 else 1.0
        if pc > 0:
            componer(fr, _cursor(), px + 22, py + 30, escala=pres,
                     alpha=clamp(1 - (t - clic - 1.2) / 0.3))
    return fr


@lru_cache(None)
def _pildora_comentario():
    tx = texto("¡COMENTÁ ABAJO!", "negra", 48, color=TINTA)
    w, h = tx.width + 150, 110
    c = Capa(0, 0, w + 12, h + 16, ss=3)
    c.rrect(6, 14, w + 6, h + 14, 55, fill=(20, 0, 60, 90))
    c.rrect(6, 6, w + 6, h + 6, 55, fill=(255, 255, 255))
    bx, by = 6 + 62, 6 + h / 2
    c.rrect(bx - 36, by - 28, bx + 36, by + 22, 16, fill=(131, 56, 236))
    c.poligono([(bx - 16, by + 18), (bx - 26, by + 38), (bx + 2, by + 20)], fill=(131, 56, 236))
    for dx in (-18, 0, 18):
        c.circulo(bx + dx, by - 3, 6, fill=(255, 255, 255))
    im = c.imagen()
    im.alpha_composite(tx, (int(bx + 50), int(by - tx.height / 2)))
    return im


@lru_cache(None)
def _boton(hecho):
    txt = "SIGUIENDO" if hecho else "SEGUIR"
    fondo = (70, 64, 90) if hecho else (255, 20, 70)
    tx = texto(txt, "negra", 62, color=(255, 255, 255))
    w, h = max(470, tx.width + 190), 132
    c = Capa(0, 0, w + 12, h + 18, ss=3)
    c.rrect(6, 16, w + 6, h + 16, 66, fill=(20, 0, 50, 110))
    c.rrect(6, 6, w + 6, h + 6, 66, fill=fondo, borde=(255, 255, 255), grosor=6)
    ix, iy = 6 + 72, 6 + h / 2
    if hecho:
        c.linea([(ix - 24, iy + 2), (ix - 6, iy + 20), (ix + 26, iy - 18)], (255, 255, 255), 12)
    else:
        c.poligono([(ix - 26, iy + 16), (ix - 18, iy - 8), (ix - 12, iy - 22), (ix, iy - 28),
                    (ix + 12, iy - 22), (ix + 18, iy - 8), (ix + 26, iy + 16)], fill=(255, 255, 255))
        c.circulo(ix, iy + 22, 8, fill=(255, 255, 255))
    im = c.imagen()
    im.alpha_composite(tx, (int(ix + 50), int(iy - tx.height / 2)))
    return im


@lru_cache(None)
def _cursor():
    c = Capa(0, 0, 70, 90, ss=4)
    pts = [(6, 4), (6, 66), (22, 52), (34, 80), (46, 74), (34, 48), (56, 48)]
    c.poligono(pts, fill=(255, 255, 255), borde=TINTA, grosor=5)
    return c.imagen()


ESCENAS = {"gancho": escena_gancho, "pulpo": escena_pulpo, "miel": escena_miel,
           "venus": escena_venus, "cierre": escena_cierre}


# =============================================================== subtítulos
def ancho_frase(palabras):
    f = F("negra", 96)
    return sum(f.getbbox(w.upper(), stroke_width=10)[2] for w in palabras) + 22 * (len(palabras) - 1)


def _cortes_por_puntuacion(texto_bloque, palabras):
    """Marca las palabras que en el guion terminan en coma, punto, etc."""
    tokens = texto_bloque.split()
    cortes, j = [], 0
    for w in palabras:
        corte = False
        while j < len(tokens):
            tok = tokens[j]
            j += 1
            if _norm(tok) == _norm(w["w"]):
                corte = tok[-1] in ",.:;!?…"
                break
        cortes.append(corte)
    return cortes


def armar_frases():
    frases = []
    for b, ws in L.palabras_absolutas():
        cortes = _cortes_por_puntuacion(b["texto"], ws)
        actual, grupo = [], []
        for i, w in enumerate(ws):
            if actual:
                prev = actual[-1]
                pausa = w["t"] - (prev["t"] + prev["d"])
                ancho = ancho_frase([x["w"] for x in actual] + [w["w"]])
                if cortes[i - 1] or pausa > 0.35 or len(actual) >= 4 or ancho > 940:
                    grupo.append(actual)
                    actual = []
            actual.append(w)
        if actual:
            grupo.append(actual)
        # Las frases cortísimas (< 0,3 s) parpadean: se suman a la vecina.
        fin_con_pausa = {id(w) for w, c in zip(ws, cortes) if c}
        i = 0
        while i < len(grupo):
            dur = (grupo[i + 1][0]["t"] if i + 1 < len(grupo) else 99) - grupo[i][0]["t"]
            if dur < 0.3 and len(grupo) > 1:
                prev_ok = (i > 0 and id(grupo[i - 1][-1]) not in fin_con_pausa and
                           ancho_frase([x["w"] for x in grupo[i - 1] + grupo[i]]) <= 940)
                if prev_ok:
                    grupo[i - 1] += grupo.pop(i)
                    continue
                if i + 1 < len(grupo) and id(grupo[i][-1]) not in fin_con_pausa:
                    grupo[i] += grupo.pop(i + 1)
                    continue
            i += 1
        for i, g in enumerate(grupo):
            ini = g[0]["t"] - 0.05
            if i + 1 < len(grupo):
                fin = grupo[i + 1][0]["t"] - 0.05
            else:
                fin = min(g[-1]["t"] + g[-1]["d"] + 0.35, b["escena_fin"] - 0.02)
            frases.append({"ini": ini, "fin": fin, "palabras": g})
    return frases


FRASES = armar_frases()


@lru_cache(maxsize=256)
def _img_frase(palabras, activa):
    fn, fa = F("negra", 84), F("negra", 96)
    borde, esp = 10, 22
    medidas = []
    for i, w in enumerate(palabras):
        f = fa if i == activa else fn
        bb = f.getbbox(w, stroke_width=borde)
        medidas.append((w, f, bb[2] - bb[0], bb))
    lineas, act, ancho = [], [], 0
    for m in medidas:
        extra = m[2] + (esp if act else 0)
        if act and ancho + extra > 980:
            lineas.append(act)
            act, ancho = [], 0
            extra = m[2]
        act.append(m)
        ancho += extra
    lineas.append(act)
    alto_l = 118
    im = Image.new("RGBA", (1040, alto_l * len(lineas) + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for li, linea in enumerate(lineas):
        total = sum(m[2] for m in linea) + esp * (len(linea) - 1)
        x = (im.width - total) / 2
        yb = 15 + li * alto_l + alto_l * 0.78
        for w, f, ancho_w, bb in linea:
            es_activa = f is fa
            col = (255, 225, 60) if es_activa else (255, 255, 255)
            d.text((x - bb[0], yb + 8), w, font=f, fill=(10, 5, 30, 140), anchor="ls",
                   stroke_width=borde, stroke_fill=(10, 5, 30, 140))
            d.text((x - bb[0], yb), w, font=f, fill=col, anchor="ls", stroke_width=borde,
                   stroke_fill=(12, 8, 26))
            x += ancho_w + esp
    return im


def subtitulos(fr, t):
    for fz in FRASES:
        if fz["ini"] <= t < fz["fin"]:
            ws = fz["palabras"]
            activa = 0
            for i, w in enumerate(ws):
                if t >= w["t"] - 0.03:
                    activa = i
            im = _img_frase(tuple(w["w"].upper() for w in ws), activa)
            s = lerp(0.75, 1.0, e_back(prog(t, fz["ini"], 0.16)))
            componer(fr, im, W / 2, 1500, escala=s)
            return


# ============================================================ composición
def barrido(a, b, t, T, color):
    """Transición: una franja diagonal cruza la pantalla y revela la escena nueva."""
    x = prog(t, T - TR / 2, TR)
    cx = lerp(-1.0 * W, 2.0 * W, e_in_out(x))
    s, bw = 280, 1720
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(-10, -10), (cx - bw / 2 + s, -10), (cx - bw / 2 - s, H + 10),
                                  (-10, H + 10)], fill=255)
    out = Image.composite(b, a, mask)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    def franja(x0, x1, col):
        d.polygon([(cx + x0 + s, -10), (cx + x1 + s, -10), (cx + x1 - s, H + 10), (cx + x0 - s, H + 10)],
                  fill=col)

    oscuro = tuple(int(v * 0.6) for v in color)
    franja(-bw / 2, -bw / 2 + 90, oscuro + (255,))
    franja(-bw / 2 + 90, bw / 2 - 50, color + (255,))
    franja(bw / 2 - 50, bw / 2, (255, 255, 255, 255))
    out.alpha_composite(capa)
    return out


TR = 0.5


def sacudida(t):
    dx = dy = 0.0
    for t0, amp, dur in [(E["g_tres"], 10, 0.25), (E["g_boom"], 30, 0.55), (E["m_comer"], 16, 0.3),
                         (E["v_anio"], 10, 0.25), (E["c_seguinos"] + 0.25, 6, 0.2)]:
        if 0 <= t - t0 < dur:
            k = amp * (1 - (t - t0) / dur) ** 2
            dx += k * math.sin(t * 97 + 1.3)
            dy += k * math.cos(t * 83 + 0.7)
    return dx, dy


def cuadro(t):
    b = L.escena_en(t)
    fr = None
    for i, sig in enumerate(L.bloques[1:], start=1):
        T = sig["escena_ini"]
        if abs(t - T) < TR / 2:
            fr = barrido(ESCENAS[ORDEN[i - 1]](t), ESCENAS[ORDEN[i]](t), t, T, ACENTO[ORDEN[i]])
            break
    if fr is None:
        fr = ESCENAS[b["id"]](t)
    subtitulos(fr, t)
    # barra de progreso
    d = ImageDraw.Draw(fr)
    d.rectangle([0, 0, W, 12], fill=(0, 0, 0, 90))
    fr2 = Image.new("RGBA", (W, 14), (0, 0, 0, 0))
    ImageDraw.Draw(fr2).rectangle([0, 0, int(W * t / L.duracion), 12], fill=(255, 255, 255, 230))
    fr.alpha_composite(fr2)
    dx, dy = sacudida(t)
    if abs(dx) + abs(dy) > 0.5:
        z = 1.04
        big = fr.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox, oy = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
        fr = big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return fr.convert("RGB")


def _render(i):
    return cuadro(i / FPS).tobytes()


def exportar():
    n = int(round(L.duracion * FPS))
    audio = os.path.join(BUILD, "audio_final.wav")
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    cmd = [FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", SALIDA]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for i, datos in enumerate(pool.imap(_render, range(n), chunksize=4)):
            proc.stdin.write(datos)
            if i % 60 == 0:
                print(f"  cuadro {i}/{n}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg falló al codificar el video")
    print("video listo:", SALIDA)


def previa(tiempos):
    carpeta = os.path.join(BUILD, "previa")
    os.makedirs(carpeta, exist_ok=True)
    for t in tiempos:
        ruta = os.path.join(carpeta, f"t{t:05.2f}.png")
        cuadro(t).save(ruta)
        print(ruta)


def portada():
    """Imagen de portada (miniatura) sin subtítulos: el gancho con la cabeza explotando."""
    ruta = os.path.join(os.path.dirname(SALIDA), "portada.png")
    escena_gancho(E["g_boom"] + 0.5).convert("RGB").save(ruta)
    print("portada lista:", ruta)


preparar()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--previa":
        previa([float(x) for x in sys.argv[2:]])
    else:
        exportar()
        portada()
