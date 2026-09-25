"""Episodio 1: el pulpo, la miel y Venus (voz de Tomás, Argentina)."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from dibujo import (TINTA, H, W, Capa, a_imagen, clamp, componer, corazon, e_back, e_in_out, e_out,
                    _pildora, encabezado, gradiente, latido, lerp, mezcla, parpadeo, pildora, pop, prog,
                    rayos_luz, resplandor, spr_brillo, spr_burbuja, spr_estrella, spr_resplandor,
                    texto, titulo, viñeta)

SLUG = "pulpo_miel_venus"
DURACION = 30.0
VOZ = "es-AR-TomasNeural"
VOZ_TONO = "+2Hz"
VOZ_VELOCIDAD_MIN = 4

BLOQUES = [
    {
        "id": "gancho",
        "texto": "¡Tres curiosidades que te van a volar la cabeza!",
        "titulo": "3 CURIOSIDADES",
        "subtitulo": "QUE TE VAN A VOLAR LA CABEZA",
    },
    {
        "id": "pulpo",
        "texto": "Uno: el pulpo tiene tres corazones... y encima, su sangre es azul.",
        "titulo": "3 CORAZONES",
        "subtitulo": "Y SANGRE AZUL",
    },
    {
        "id": "miel",
        "texto": "Dos: la miel nunca se echa a perder. Encontraron miel de más de "
                 "tres mil años en tumbas egipcias, ¡y todavía se podía comer!",
        "titulo": "MIEL ETERNA",
        "subtitulo": "+3000 AÑOS Y COMESTIBLE",
    },
    {
        "id": "venus",
        "texto": "Tres: Venus tarda más en girar sobre sí mismo que en darle la "
                 "vuelta al Sol. O sea, allá un día dura más que un año.",
        "titulo": "VENUS",
        "subtitulo": "UN DÍA DURA MÁS QUE UN AÑO",
    },
    {
        "id": "cierre",
        "texto": "¿Cuál te sorprendió más? Contanos en los comentarios y seguinos "
                 "para más curiosidades.",
        "titulo": "¿CUÁL TE SORPRENDIÓ MÁS?",
        "subtitulo": "SEGUINOS PARA MÁS",
    },
]

ACENTO = {"pulpo": (0, 180, 216), "miel": (255, 183, 3),
          "venus": (123, 44, 191), "cierre": (255, 0, 110)}
TITULOS = {b["id"]: b for b in BLOQUES}
E, ESC, FONDOS, EXTRA = {}, {}, {}, {}


def iniciar(eventos_, escenas):
    E.update(eventos_)
    ESC.update(escenas)


def eventos(L):
    return {
        "p_corazones": L.palabra("pulpo", "tres"),
        "p_azul": L.palabra("pulpo", "sangre"),
        "m_nunca": L.palabra("miel", "nunca"),
        "m_piramides": L.palabra("miel", "encontraron"),
        "m_contador": L.palabra("miel", "tres"),
        "m_contador_fin": L.fin_palabra("miel", "años"),
        "m_comer": L.palabra("miel", "comer"),
        "v_girar": L.palabra("venus", "girar"),
        "v_vuelta": L.palabra("venus", "vuelta"),
        "v_dia": L.palabra("venus", "día"),
        "v_anio": L.palabra("venus", "año"),
    }


def efectos(E, L, S):
    """Efectos de sonido propios del episodio: (segundo, señal, ganancia)."""
    fx = [(E["p_corazones"] + 0.13 * i, S.pop(800 + 200 * i, 300 + 60 * i), 0.35) for i in range(3)]
    fx += [(E["p_azul"], S.bloop(), 0.40),
           (E["m_nunca"], S.pop(600, 250), 0.25),
           (E["m_piramides"], S.golpe(), 0.30)]
    t = E["m_contador"]
    while t < E["m_contador_fin"]:
        fx.append((t, S.tic(), 0.16))
        t += 0.06
    fx += [(E["m_comer"], S.golpe(), 0.55), (E["m_comer"] + 0.05, S.ding(), 0.25),
           (E["v_girar"], S.pop(500, 900), 0.25), (E["v_vuelta"], S.pop(500, 900), 0.25),
           (E["v_dia"], S.pop(900, 300), 0.30), (E["v_anio"], S.golpe(), 0.50)]
    return fx


def sacudidas(E):
    return [(E["m_comer"], 16, 0.3), (E["v_anio"], 10, 0.25)]


def preparar():
    FONDOS.update(pulpo=fondo_pulpo(), miel=fondo_miel(), venus=fondo_venus())
    EXTRA["rayos"] = rayos_luz()
    EXTRA["dunas"] = dunas()


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


# ======================================================= íconos del cierre
def _icono_pulpo(c, x, y, s, t):
    pulpo(c, x, y - 32 * s, t, 0.3 * s)


def _icono_miel(c, x, y, s, t):
    vasija(c, x, y + 20 * s, t, 0.4 * s)


def _icono_venus(c, x, y, s, t):
    return [(sprite_venus(int(74 * s), t, dormido=False), x, y)]


ICONOS = [_icono_pulpo, _icono_miel, _icono_venus]
ESCENAS = {"pulpo": escena_pulpo, "miel": escena_miel, "venus": escena_venus}
