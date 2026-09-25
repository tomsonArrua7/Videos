"""Línea de tiempo compartida entre animación y sonido.

Lee build/timeline.json (generado por voz.py) y expone los momentos clave
("eventos") anclados a palabras de la narración, así la imagen y los efectos
de sonido caen justo cuando la voz dice cada cosa.
"""
import json
import os
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(RAIZ, "build")


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
    """Momentos clave del video (en segundos) usados por imagen y sonido."""
    E = {}
    for b in L.bloques[1:]:
        E[f"{b['id']}_ini"] = b["escena_ini"]
        E[f"{b['id']}_badge"] = b["escena_ini"] + 0.30

    E["g_tres"] = L.palabra("gancho", "tres")
    E["g_curio"] = L.palabra("gancho", "curiosidades")
    E["g_cara"] = E["g_curio"] + 0.40
    E["g_boom"] = L.palabra("gancho", "cabeza")

    E["p_corazones"] = L.palabra("pulpo", "tres")
    E["p_azul"] = L.palabra("pulpo", "sangre")

    E["m_nunca"] = L.palabra("miel", "nunca")
    E["m_piramides"] = L.palabra("miel", "encontraron")
    E["m_contador"] = L.palabra("miel", "tres")
    E["m_contador_fin"] = L.fin_palabra("miel", "años")
    E["m_comer"] = L.palabra("miel", "comer")

    E["v_girar"] = L.palabra("venus", "girar")
    E["v_vuelta"] = L.palabra("venus", "vuelta")
    E["v_dia"] = L.palabra("venus", "día")
    E["v_anio"] = L.palabra("venus", "año")

    E["c_comentarios"] = L.palabra("cierre", "comentarios")
    E["c_seguinos"] = L.palabra("cierre", "seguinos")
    E["c_fin_voz"] = L.fin_palabra("cierre", "curiosidades")
    return E
