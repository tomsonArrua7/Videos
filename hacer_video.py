"""Genera episodios completos: voz -> música/efectos -> animación + exportación.

    pip install -r requirements.txt
    python hacer_video.py            # el último episodio
    python hacer_video.py ep01       # uno en particular
    python hacer_video.py todos      # todos

Resultado: output/epNN_<tema>.mp4 y output/epNN_portada.png
"""
import os
import re
import subprocess
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
EPISODIOS = sorted(f[:-3] for f in os.listdir(os.path.join(SRC, "episodios")) if re.fullmatch(r"ep\d+\.py", f))

pedidos = sys.argv[1:] or [EPISODIOS[-1]]
if pedidos == ["todos"]:
    pedidos = EPISODIOS
for ep in pedidos:
    if ep not in EPISODIOS:
        sys.exit(f"No existe '{ep}'. Episodios: {', '.join(EPISODIOS)}")
    for paso, script in [("Voz (Edge TTS)", "voz.py"), ("Música y efectos", "sonido.py"),
                         ("Animación y exportación", "animacion.py")]:
        print(f"\n== {ep} · {paso} ==", flush=True)
        subprocess.run([sys.executable, script], cwd=SRC, check=True, env={**os.environ, "EPISODIO": ep})
