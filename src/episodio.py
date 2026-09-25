"""Elige qué episodio se genera.

Se indica con la variable de entorno EPISODIO o pasando el nombre como
argumento a cualquier script (por ejemplo `python animacion.py ep01`).
Cada episodio vive en src/episodios/epNN.py.
"""
import importlib
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "episodios")


def disponibles():
    return sorted(f[:-3] for f in os.listdir(CARPETA) if re.fullmatch(r"ep\d+\.py", f))


def _elegir():
    for arg in sys.argv[1:]:
        if re.fullmatch(r"ep\d+", arg):
            os.environ["EPISODIO"] = arg
    return os.environ.get("EPISODIO") or disponibles()[-1]


NOMBRE = _elegir()
if NOMBRE not in disponibles():
    sys.exit(f"No existe el episodio '{NOMBRE}'. Disponibles: {', '.join(disponibles())}")
EP = importlib.import_module(f"episodios.{NOMBRE}")
BUILD = os.path.join(RAIZ, "build", NOMBRE)
SALIDA_VIDEO = os.path.join(RAIZ, "output", f"{NOMBRE}_{EP.SLUG}.mp4")
SALIDA_PORTADA = os.path.join(RAIZ, "output", f"{NOMBRE}_portada.png")


def argumentos():
    """sys.argv sin el nombre del episodio."""
    return [a for a in sys.argv[1:] if not re.fullmatch(r"ep\d+", a)]
