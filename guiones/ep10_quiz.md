# Episodio 10: quiz "¿Cuánto sabés?"

**Formato:** video vertical 9:16 (1080×1920) · 38 segundos · Shorts / Reels / TikTok. Es el primer episodio interactivo.
**Voz:** voz humana grabada con el celular (`grabaciones/ep10.m4a`) y retocada por `src/grabacion.py`.
**Imágenes:** todo original (una huella, un koala, el Sol y la Tierra, una nube, un elefante).

## Cómo funciona un quiz

Cada pregunta sigue el mismo ritmo:

1. La voz hace la pregunta; arriba queda la tarjeta con el texto y aparecen las opciones **A, B y C**.
2. **Tres segundos para pensar:** un reloj cuenta 3-2-1 con tic-tac y el aro pasa de verde a rojo.
3. La voz responde: la opción correcta se pone verde con un tilde y brillitos, las otras se apagan y aparece un dibujo con el dato.

En el guion, `[3s]` marca el silencio entre la pregunta y la respuesta (`src/quiz.py` arma la escena).

| Tiempo | Escena | Voz en off | Opciones | Qué se ve al responder |
|---|---|---|---|---|
| 0:00 – 0:04 | **Gancho** | "¡Tres preguntas, tres segundos cada una! ¿Cuántas acertás?" | — | **3 PREGUNTAS**, la etiqueta **3 SEGUNDOS CADA UNA** y un cronómetro con un "?" que late |
| 0:04 – 0:14 | **Pregunta 1** | "Uno: ¿qué animal tiene huellas digitales casi iguales a las nuestras? … ¡El koala! Son tan parecidas que podrían confundir a la policía." | A) Perro · B) Delfín · **C) Koala** | Una lupa recorre una huella; aparece el koala con **=** y **CASI IDÉNTICAS**; en "policía", luces y sirena roja y azul |
| 0:14 – 0:24 | **Pregunta 2** | "Dos: ¿cuánto tarda la luz del Sol en llegar a la Tierra? … ¡Ocho minutos! Siempre vemos el Sol de hace ocho minutos." | A) 8 segundos · **B) 8 minutos** · C) 8 horas | Un pulso de luz viaja del Sol a la Tierra y llega con la respuesta: **8 MIN 20 S** y **HACE 8 MIN** debajo del Sol |
| 0:24 – 0:33 | **Pregunta 3** | "Tres: ¿cuánto pesa una nube común? … ¡Unas quinientas toneladas! Lo mismo que cien elefantes." | **A) 500 toneladas** · B) 50 kilos · C) 1 kilo | Una nube con cara y la etiqueta **¿KILOS?**; con la respuesta se sorprende, cae **500 TONELADAS** y aparece un elefante **×100** |
| 0:33 – 0:38 | **Cierre** | "¿Cuántas acertaste? Comentalo abajo y seguinos para más." | — | Tarjetas de las 3 preguntas, **¿CUÁNTAS ACERTASTE?**, "¡COMENTÁ ABAJO!" y **SEGUIR → SIGUIENDO** |

Las respuestas quedan una en cada letra (C, B, A) y las preguntas van de fácil a difícil.

## La grabación

- **Audio:** 41,8 s de celular a −20 LUFS, sin saturar. "¿Cuántas acertaste?" estaba repetido y se usó la última toma.
- **Ruido de fondo:** de −47,4 a −55,5 dBFS.
- **Ubicación:** las ocho partes (el gancho, cada pregunta y respuesta por separado y el cierre) al 100 %.
- **Pausas:** se acortaron 2,3 s de pausas largas dentro de las frases.
- **Velocidad:** +8 %, sin cambiar el tono.
- **Whisper:** entiende todo. Solo duda con el "Tres" de la tercera pregunta, corto y pegado a "¿cuánto" (en el audio original también, al 50 %); en pantalla dicen "TRES" y "PREGUNTA 3 DE 3".

## Datos verificados

- **Koala:** sus huellas digitales tienen crestas, lazos y espirales como las nuestras. Maciej Henneberg (Universidad de Adelaida, 1996) mostró que ni con microscopio es fácil distinguirlas, y que podrían confundirse en la escena de un crimen. Perros y delfines no tienen huellas digitales.
- **Luz del Sol:** recorre unos 150 millones de kilómetros en unos 8 minutos y 20 segundos. Vemos el Sol como era hace ese tiempo.
- **Nube:** un cúmulo común ocupa cerca de 1 km³ con medio gramo de agua por metro cúbico, o sea unas 500 toneladas (el cálculo que difunde el Servicio Geológico de EE. UU.). Un elefante pesa unas 5 toneladas: son unos 100 elefantes. Flota porque ese peso está repartido en gotitas diminutas sostenidas por el aire que sube.

## Texto sugerido para la publicación

> 🧠 ¿Cuánto sabés? Tres preguntas, tres segundos cada una: 🐨 huellas digitales, ☀️ la luz del Sol y ☁️ el peso de una nube. ¿Cuántas acertaste? Comentalo 👇
>
> #quiz #curiosidades #trivia #sabiasque #shorts
