"""Foto de perfil de la cuenta de quiz "trivias.fast".

Usa el mismo lenguaje que los quiz: el cronómetro con el "?" rosa del gancho, más líneas de
velocidad y un rayo. Todo lo importante queda dentro del círculo central, porque las redes
recortan la foto en redondo.

Salida: output/marca/trivias_fast_perfil.png (solo ícono, se lee aun chiquita)
        output/marca/trivias_fast_perfil_nombre.png (con "TRIVIAS.FAST", para verse más grande)
Uso:    python perfil.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

from dibujo import RAIZ, TINTA, Capa, componer, spr_brillo, texto
from quiz import cronometro

L = 1080                 # lado de la imagen
C = L / 2
CARPETA = os.path.join(RAIZ, "output", "marca")


def fondo():
    """Degradé radial rosa → violeta → azul, con rayos de sol suaves."""
    yy, xx = np.mgrid[:L, :L]
    d = np.clip(np.hypot(xx - C, yy - C * 0.9) / (L * 0.72), 0, 1)
    paradas = [(0, (255, 60, 150)), (0.45, (140, 30, 185)), (1, (28, 20, 100))]
    img = np.zeros((L, L, 3), np.float32)
    for ch in range(3):
        img[..., ch] = np.interp(d, [p for p, _ in paradas], [c[ch] for _, c in paradas])
    fr = Image.fromarray(img.astype(np.uint8)).convert("RGBA")
    capa = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    dr = ImageDraw.Draw(capa)
    for i in range(16):
        a0 = 0.2 + i * 2 * math.pi / 16
        a1 = a0 + math.pi / 16
        dr.polygon([(C, C), (C + 1600 * math.cos(a0), C + 1600 * math.sin(a0)),
                    (C + 1600 * math.cos(a1), C + 1600 * math.sin(a1))], fill=(255, 255, 255, 20))
    fr.alpha_composite(capa)
    return fr


def reloj(r):
    """Cronómetro con el "?" encima, en una imagen propia para poder inclinarlo."""
    lado = int(r * 2.9)
    c = Capa(0, 0, lado, lado, ss=3)
    x, y = lado / 2, lado / 2 + r * 0.18
    cronometro(c, x, y, r, 0, 1.05)
    im = c.imagen()
    q = texto("?", "titulo", int(r * 1.3), color=(255, 0, 110), borde=int(r * 0.05), color_borde=TINTA,
              sombra=int(r * 0.04))
    componer(im, q, x + r * 0.03, y + r * 0.06, rot=6)
    return im


def lineas_velocidad(fr, x, y, escala=1.0):
    """Estelas blancas a la izquierda: el reloj va rápido."""
    c = Capa(0, 0, L, L, ss=3)
    for dy, largo, grosor in ((-150, 170, 26), (-60, 250, 30), (35, 200, 28), (125, 140, 22)):
        yy = y + dy * escala
        c.linea([(x - largo * escala, yy), (x, yy)], (255, 255, 255, 235), grosor * escala)
    c.pegar_en(fr)


def rayo(fr, x, y, k):
    c = Capa(0, 0, L, L, ss=3)
    pts = [(x + 20 * k, y - 95 * k), (x - 48 * k, y + 12 * k), (x - 2 * k, y + 12 * k), (x - 22 * k, y + 95 * k),
           (x + 50 * k, y - 18 * k), (x + 4 * k, y - 18 * k)]
    c.poligono(pts, fill=(255, 214, 10), borde=TINTA, grosor=9 * k)
    c.pegar_en(fr)


def brillos(fr, puntos):
    for x, y, tam in puntos:
        componer(fr, spr_brillo(tam, (255, 250, 220)), x, y)


def solo_icono():
    fr = fondo()
    lineas_velocidad(fr, 285, 590, 0.8)
    componer(fr, reloj(272), 580, 560, rot=-10)
    rayo(fr, 800, 300, 1.0)
    brillos(fr, [(280, 300, 34), (840, 720, 28), (330, 830, 22)])
    return fr


def con_nombre():
    fr = fondo()
    lineas_velocidad(fr, 330, 460, 0.7)
    componer(fr, reloj(190), 560, 420, rot=-10)
    rayo(fr, 790, 230, 0.8)
    componer(fr, texto("TRIVIAS", "titulo", 158, color=(255, 255, 255), borde=13, color_borde=TINTA, sombra=12),
             C, 775, rot=-3)
    componer(fr, texto(".FAST", "titulo", 132, color=(255, 214, 10), borde=12, color_borde=TINTA, sombra=10),
             C + 20, 905, rot=-3)
    brillos(fr, [(230, 300, 28), (880, 560, 24)])
    return fr


def main():
    os.makedirs(CARPETA, exist_ok=True)
    for nombre, im in (("trivias_fast_perfil.png", solo_icono()), ("trivias_fast_perfil_nombre.png", con_nombre())):
        ruta = os.path.join(CARPETA, nombre)
        im.convert("RGB").save(ruta)
        print(ruta)


if __name__ == "__main__":
    main()
