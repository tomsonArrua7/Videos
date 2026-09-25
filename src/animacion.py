"""Animación del video vertical (1080x1920, 30 fps) y exportación final.

Acá vive lo común a todos los episodios: el gancho (la carita que explota),
el cierre, los subtítulos karaoke, las transiciones y la exportación. Las
escenas de cada curiosidad están en src/episodios/epNN.py.

Uso:
    python animacion.py ep02                 -> output/ep02_<tema>.mp4 + portada
    python animacion.py ep02 --previa 1 5.5  -> build/ep02/previa/*.png
"""
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

from dibujo import (FPS, TINTA, H, W, Capa, F, _pildora, a_imagen, clamp, componer, confeti, e_back,
                    e_in_out, e_out, gradiente, lerp, pop, prog, rayos_sol, resplandor, spr_brillo,
                    texto, texto_ajustado, titulo, viñeta)
from episodio import BUILD, EP, SALIDA_PORTADA, SALIDA_VIDEO, argumentos
from tiempos import Linea, _norm, eventos

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
L = Linea()
E = eventos(L)
ORDEN = [b["id"] for b in L.bloques]
ESC = {b["id"]: b for b in L.bloques}
EP.iniciar(E, ESC)
FONDOS = {}


# ================================================================= escenas
def fondo_gancho():
    a = gradiente([(0, (58, 12, 163)), (0.55, (114, 9, 183)), (1, (247, 37, 133))])
    resplandor(a, 540, 1050, 650, (255, 140, 230), 0.35)
    viñeta(a)
    return a_imagen(a, 1)


def fondo_cierre():
    a = gradiente([(0, (255, 0, 110)), (0.5, (131, 56, 236)), (1, (58, 134, 255))])
    resplandor(a, 540, 800, 600, (255, 190, 240), 0.3)
    viñeta(a)
    return a_imagen(a, 5)


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
    etiqueta = getattr(EP, "GANCHO_ETIQUETA", None)
    s = pop(t, E["g_curio"] + 0.3, 0.4) if etiqueta else 0
    if s > 0:
        componer(fr, _pildora(etiqueta, (255, 0, 110), 46), 540, 795, escala=s, rot=-4)
    # destello de la explosión
    if tb <= t < tb + 0.18:
        fl = Image.new("RGBA", (W, H), (255, 250, 230, int(200 * (1 - prog(t, tb, 0.18)))))
        fr.alpha_composite(fl)
    return fr


def escena_cierre(t):
    fr = FONDOS["cierre"].copy()
    t0 = ESC["cierre"]["escena_ini"]
    rayos_sol(fr, 540, 800, -t * 0.3, n=18, color=(255, 255, 255, 20))
    confeti(fr, t, t0, alpha=0.8)
    titulo(fr, t, "¿CUÁL TE", t0 + 0.1, y=320, tam=130)
    titulo(fr, t, "SORPRENDIÓ MÁS?", t0 + 0.22, y=460, tam=130, color=(255, 230, 90))
    aros = [EP.ACENTO[i] for i in ORDEN[1:4]]
    for i, x in enumerate((200, 540, 880)):
        s = pop(t, t0 + 0.35 + 0.15 * i, 0.45)
        if s <= 0:
            continue
        y = 790 + 12 * math.sin(t * 3 - i * 0.9)
        c = Capa(int(x - 170), int(y - 170), 340, 350)
        r = 132 * s
        c.circulo(x, y + 12, r, fill=(20, 0, 60, 90))
        c.circulo(x, y, r, fill=(255, 255, 255), borde=aros[i], grosor=12 * s)
        sprites = EP.ICONOS[i](c, x, y, s, t) or []
        c.circulo(x + 96 * s, y - 96 * s, 34 * s, fill=TINTA, borde=(255, 255, 255), grosor=4 * s)
        c.pegar_en(fr)
        for im, ix, iy in sprites:
            componer(fr, im, ix, iy)
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
    for t0, amp, dur in [(E["g_tres"], 10, 0.25), (E["g_boom"], 30, 0.55),
                         (E["c_seguinos"] + 0.25, 6, 0.2)] + EP.sacudidas(E):
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
            fr = barrido(ESCENAS[ORDEN[i - 1]](t), ESCENAS[ORDEN[i]](t), t, T, EP.ACENTO[ORDEN[i]])
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
    os.makedirs(os.path.dirname(SALIDA_VIDEO), exist_ok=True)
    cmd = [FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", SALIDA_VIDEO]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for i, datos in enumerate(pool.imap(_render, range(n), chunksize=4)):
            proc.stdin.write(datos)
            if i % 60 == 0:
                print(f"  cuadro {i}/{n}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg falló al codificar el video")
    print("video listo:", SALIDA_VIDEO)


def previa(tiempos):
    carpeta = os.path.join(BUILD, "previa")
    os.makedirs(carpeta, exist_ok=True)
    for t in tiempos:
        ruta = os.path.join(carpeta, f"t{t:05.2f}.png")
        cuadro(t).save(ruta)
        print(ruta)


def portada():
    """Imagen de portada (miniatura) sin subtítulos: el gancho con la cabeza explotando."""
    escena_gancho(E["g_boom"] + 0.5).convert("RGB").save(SALIDA_PORTADA)
    print("portada lista:", SALIDA_PORTADA)


def preparar():
    FONDOS.update(gancho=fondo_gancho(), cierre=fondo_cierre())
    EP.preparar()


ESCENAS = {"gancho": escena_gancho, "cierre": escena_cierre, **EP.ESCENAS}
preparar()

if __name__ == "__main__":
    args = argumentos()
    if args and args[0] == "--previa":
        previa([float(x) for x in args[1:]])
    else:
        exportar()
        portada()
