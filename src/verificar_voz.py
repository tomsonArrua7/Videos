"""Control de calidad de la voz: la escucha un reconocedor (Whisper) y la compara con el guion.

Si Whisper entiende cada palabra, sobre todo los nombres propios, la voz se
está pronunciando bien. Requiere `pip install faster-whisper` (opcional).

Uso:
    python verificar_voz.py ep04
        Transcribe cada bloque ya generado (build/ep04/voz) y marca lo que no se entendió.
    python verificar_voz.py ep04 --probar "Yúrasic Park" "Yurásic Park"
        Sintetiza cada variante con la voz del episodio y muestra cuál se entiende mejor.
"""
import asyncio
import difflib
import os
import re
import tempfile

from faster_whisper import WhisperModel

import voz
from episodio import BUILD, EP, argumentos
from tiempos import Linea, _norm

_modelo = None


def modelo():
    global _modelo
    if _modelo is None:
        _modelo = WhisperModel("small", device="cpu", compute_type="int8")
    return _modelo


def transcribir(ruta):
    segs, _ = modelo().transcribe(ruta, language="es", beam_size=5)
    segs = list(segs)
    texto = " ".join(s.text.strip() for s in segs)
    confianza = sum(s.avg_logprob for s in segs) / max(1, len(segs))
    return texto, confianza


_UNIDADES = ("cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince "
             "dieciséis diecisiete dieciocho diecinueve veinte veintiuno veintidós veintitrés veinticuatro "
             "veinticinco veintiséis veintisiete veintiocho veintinueve").split()
_DECENAS = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_CENTENAS = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos",
             6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def en_palabras(n):
    """Número a palabras en castellano (alcanza para lo que dice un guion)."""
    if n < 30:
        return _UNIDADES[n]
    if n < 100:
        d, u = divmod(n, 10)
        return _DECENAS[d] + (f" y {_UNIDADES[u]}" if u else "")
    if n == 100:
        return "cien"
    if n < 1000:
        c, r = divmod(n, 100)
        return _CENTENAS[c] + (" " + en_palabras(r) if r else "")
    if n < 1_000_000:
        m, r = divmod(n, 1000)
        return ("mil" if m == 1 else en_palabras(m) + " mil") + (" " + en_palabras(r) if r else "")
    return str(n)


def palabras(texto):
    # Whisper escribe los números con cifras ("42", "30.000"): los pasamos a palabras para comparar
    texto = re.sub(r"\d{1,3}(?:\.\d{3})+|\d+", lambda m: " " + en_palabras(int(m.group().replace(".", ""))) + " ", texto)
    return [w for w in (_norm(x) for x in texto.split()) if w]


def se_escucha(objetivo, oidas):
    """¿La palabra `objetivo` aparece (con tolerancia) entre las oídas?"""
    return any(difflib.SequenceMatcher(None, objetivo, w).ratio() >= 0.8 for w in oidas)


def verificar():
    L = Linea()
    total_ok = True
    informe = []
    for b in L.bloques:
        oido, conf = transcribir(b["audio"])
        esperado = palabras(b["texto"])
        oidas = palabras(oido)
        # las palabras cortas (de, la, y...) no suman: nos importan las que llevan significado
        faltan = [w for w in esperado if len(w) > 3 and not se_escucha(w, oidas)]
        _, _, pares = voz.separar(EP.BLOQUES[L.bloques.index(b)]["texto"])
        nombres = [_norm(m) for d, m in pares if m and d != m]
        nombres_mal = [w for w in nombres if w and not se_escucha(w, oidas)]
        estado = "OK " if not faltan else "REVISAR"
        total_ok &= not faltan
        informe += [f"[{estado}] {b['id']}  (confianza {conf:.2f})",
                    f"   guion : {b['texto']}",
                    f"   oído  : {oido}"]
        if nombres:
            informe.append(f"   nombres adaptados: {len(nombres) - len(nombres_mal)}/{len(nombres)} reconocidos"
                           + (f" (no: {', '.join(nombres_mal)})" if nombres_mal else ""))
        if faltan:
            informe.append(f"   no se entendió: {', '.join(faltan)}")
    texto = "\n".join(informe)
    print(texto)
    with open(os.path.join(BUILD, "verificacion_voz.txt"), "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    print("\nTodo se entiende." if total_ok else "\nHay palabras para revisar.")


def probar(variantes):
    with tempfile.TemporaryDirectory() as tmp:
        for i, v in enumerate(variantes):
            ruta = os.path.join(tmp, f"v{i}.mp3")
            asyncio.run(voz.sintetizar(v, ruta, "+0%"))
            oido, conf = transcribir(ruta)
            print(f"{v!r:40} -> {oido!r}  (confianza {conf:.2f})")


if __name__ == "__main__":
    args = argumentos()
    if args and args[0] == "--probar":
        probar(args[1:])
    else:
        verificar()
