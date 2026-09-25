"""Kit de dibujo compartido por todos los episodios.

Utilidades de animación (easing, composición), lienzo con antialias, textos,
fondos con numpy, sprites y elementos de interfaz (títulos, píldoras, carteles).
"""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
TINTA = (24, 16, 48)
FUENTES = {
    "titulo": "LuckiestGuy-Regular.ttf",
    "negra": "Montserrat-Black.ttf",
}


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


def pildora(fr, t, txt, color, t0, y=470, rot=-2.0, hasta=None):
    """Píldora de subtítulo que aparece en t0 (y se encoge al llegar `hasta`)."""
    s = pop(t, t0, 0.4)
    if hasta is not None and t >= hasta:
        s *= 1 - e_out(prog(t, hasta, 0.18))
    if s > 0:
        componer(fr, _pildora(txt, color), W / 2, y, escala=s, rot=rot)


def con_alpha(im, alpha):
    im = im.copy()
    im.putalpha(im.getchannel("A").point([int(v * alpha) for v in range(256)]))
    return im


@lru_cache(maxsize=600)
def cartel(txt, sub=None, color=(255, 214, 10), fondo=(70, 30, 6), ancho=640, tam=104):
    """Cartel oscuro con borde de color (contadores tipo '+3.000 AÑOS')."""
    tx = texto(txt, "titulo", tam, color=color)
    st = texto(sub, "negra", 40, color=(255, 255, 255)) if sub else None
    h = 150 + (st.height - 6 if st else 0)
    c = Capa(0, 0, ancho + 12, h + 18, ss=3)
    c.rrect(6, 14, ancho + 6, h + 14, 34, fill=(20, 8, 0, 120))
    c.rrect(6, 6, ancho + 6, h + 6, 34, fill=fondo, borde=color, grosor=6)
    im = c.imagen()
    y_tx = 6 + 75 - tx.height / 2 + 4
    im.alpha_composite(tx, (int(6 + ancho / 2 - tx.width / 2), int(y_tx)))
    if st:
        im.alpha_composite(st, (int(6 + ancho / 2 - st.width / 2), int(y_tx + tx.height - 14)))
    return im


@lru_cache(None)
def sello(txt, fondo=(34, 170, 90), tam=100):
    """Sello rotundo tipo '¡COMESTIBLE!'."""
    tx = texto(txt, "titulo", tam, color=(255, 255, 255), borde=0)
    w, h = tx.width + 80, tx.height + 50
    claro = mezcla(fondo, (255, 255, 255), 0.7)
    c = Capa(0, 0, w + 20, h + 20, ss=3)
    c.rrect(10, 10, w + 10, h + 10, 30, fill=fondo, borde=(255, 255, 255), grosor=9)
    c.rrect(24, 24, w - 4, h - 4, 22, borde=claro, grosor=3)
    im = c.imagen()
    im.alpha_composite(tx, (int(10 + w / 2 - tx.width / 2), int(10 + h / 2 - tx.height / 2 + 4)))
    return im


def burbujas(fr, t, n=26, seed=8, y_min=-60):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        r = int(rng.integers(6, 22))
        x0, y0, v = rng.uniform(0, W), rng.uniform(0, H + 200), rng.uniform(90, 220)
        y = (y0 - v * t) % (H + 200) - 60
        if y < y_min:
            continue
        componer(fr, spr_burbuja(r), x0 + 18 * math.sin(t * 2 + x0), y)


def algas(c, t, lista):
    """Algas que se mecen: lista de (x_base, alto, fase, color)."""
    for bx, alto, fase, col in lista:
        pts = [(bx + math.sin(t * 1.6 + fase + j * 0.35) * 26 * (j / 30), H + 20 - alto * j / 30)
               for j in range(31)]
        oscuro = tuple(int(v * 0.45) for v in col)
        c.tubo(pts, [30 - 20 * j / 30 + 5 for j in range(31)], oscuro)
        c.tubo(pts, [30 - 20 * j / 30 for j in range(31)], col)


def estrellas_titilando(fr, t, n=24, seed=12):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        tw = 0.5 + 0.5 * math.sin(t * rng.uniform(2, 5) + i)
        componer(fr, spr_estrella(int(rng.integers(5, 10))), x, y, alpha=0.3 + 0.7 * tw)


def chispas(fr, t, t0, x0, y0, n=24, seed=3, colores=((255, 240, 150), (255, 150, 60), (255, 255, 255)),
            vel=(450, 1000), grav=800, dur=1.3, arriba=False):
    """Explosión de brillitos con gravedad."""
    dt = t - t0
    if not 0 <= dt < dur:
        return
    rng = np.random.default_rng(seed)
    for i in range(n):
        a = rng.uniform(-math.pi, 0) if arriba else rng.uniform(0, 2 * math.pi)
        v = rng.uniform(*vel)
        x = x0 + math.cos(a) * v * dt
        y = y0 + math.sin(a) * v * dt + grav * dt * dt
        componer(fr, spr_brillo(int(rng.integers(12, 26)), colores[i % len(colores)]),
                 x, y, rot=dt * 300, alpha=clamp((dur - dt) / 0.4))


def bezier(p0, p1, p2, p3, n=30):
    pts = []
    for i in range(n):
        u = i / (n - 1)
        a, b, c_, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        pts.append((a * p0[0] + b * p1[0] + c_ * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c_ * p2[1] + d * p3[1]))
    return pts


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
