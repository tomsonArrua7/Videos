"""Genera el video completo: voz -> música/efectos -> animación + exportación.

    pip install -r requirements.txt
    python hacer_video.py

Resultado: output/curiosidades_30s.mp4 y output/portada.png
"""
import os
import subprocess
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")

for paso, script in [("Voz (Edge TTS)", "voz.py"), ("Música y efectos", "sonido.py"),
                     ("Animación y exportación", "animacion.py")]:
    print(f"\n== {paso} ==", flush=True)
    subprocess.run([sys.executable, script], cwd=SRC, check=True)
