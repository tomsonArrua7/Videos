"""Línea de tiempo compartida entre animación y sonido.

Lee build/<episodio>/timeline.json (generado por voz.py) y expone los
momentos clave ("eventos") anclados a palabras de la narración, así la imagen
y los efectos de sonido caen justo cuando la voz dice cada cosa.
"""
import json
import os
import unicodedata

from episodio import BUILD, EP


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalnum() and unicodedata.category(c) != "Mn")


class Linea:
    def __init__(self, ruta=None):
        with open(ruta or os.path.join(BUILD, "timeline.json"), encoding="utf-8") as f:
            data = json.load(f)
        self.duracion = data["duracion"]
        self.bloques = data["bloques"]
        self.por_id = {b["id"]: b for b in self.bloques}

    def _buscar(self, bloque, palabra, n):
        b = self.por_id[bloque]
        hits = [w for w in b["palabras"] if _norm(w["w"]) == _norm(palabra)]
        if len(hits) < n:
            raise KeyError(f"'{palabra}' (#{n}) no aparece en el bloque '{bloque}'")
        return b, hits[n - 1]

    def palabra(self, bloque, palabra, n=1):
        """Segundo absoluto en que empieza la n-ésima aparición de `palabra`."""
        b, w = self._buscar(bloque, palabra, n)
        return b["inicio"] + w["t"]

    def fin_palabra(self, bloque, palabra, n=1):
        b, w = self._buscar(bloque, palabra, n)
        return b["inicio"] + w["t"] + w["d"]

    def escena_en(self, t):
        for b in self.bloques:
            if b["escena_ini"] <= t < b["escena_fin"]:
                return b
        return self.bloques[-1]

    def palabras_absolutas(self):
        """Todas las palabras con tiempo absoluto, agrupadas por bloque."""
        return [(b, [{**w, "t": b["inicio"] + w["t"]} for w in b["palabras"]])
                for b in self.bloques]


def eventos(L):
    """Momentos clave del video (en segundos) usados por imagen y sonido.

    Los del gancho y el cierre son iguales en todos los episodios; cada
    episodio suma los suyos en su función eventos().
    """
    E = {}
    for b in L.bloques[1:]:
        E[f"{b['id']}_ini"] = b["escena_ini"]
        E[f"{b['id']}_badge"] = b["escena_ini"] + 0.30

    E["g_tres"] = L.palabra("gancho", "tres")
    E["g_curio"] = L.palabra("gancho", "curiosidades")
    E["g_cara"] = E["g_curio"] + 0.40
    E["g_boom"] = L.palabra("gancho", "cabeza")

    comentar, seguir = getattr(EP, "PALABRAS_CIERRE", ("comentarios", "seguinos"))
    ultima = L.por_id["cierre"]["palabras"][-1]["w"]
    E["c_comentarios"] = L.palabra("cierre", comentar)
    E["c_seguinos"] = L.palabra("cierre", seguir)
    E["c_fin_voz"] = L.fin_palabra("cierre", ultima)
    E.update(EP.eventos(L))
    return E
