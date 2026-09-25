# Episodio 9: "Tres curiosidades de tu cuerpo que te van a volar la cabeza"

**Formato:** video vertical 9:16 (1080×1920) · 30 segundos · Shorts / Reels / TikTok
**Voz:** voz humana, grabada con el celular (`grabaciones/ep09.m4a`) y retocada por `src/grabacion.py`. Sin la grabación, el video usa `es-AR-TomasNeural`.
**Imágenes:** todo original (una silueta, una regla, huesos, un ojo); no hay personajes ni logos.

| Tiempo | Escena | Voz en off | Qué se ve | Sonido |
|---|---|---|---|---|
| 0:00 – 0:03 | **Gancho** | "¡Tres curiosidades de tu cuerpo que te van a volar la cabeza!" | El "3", "CURIOSIDADES", la etiqueta **DE TU CUERPO** y el emoji que explota 🤯 | Golpe, pops, explosión |
| 0:03 – 0:11 | **#1 Más alto a la mañana** | "Uno: a la mañana sos más alto que a la noche. ¡Durante el día, la columna se achica hasta un centímetro!" | Una silueta con la columna a la vista junto a una regla. El sol baja, sale la luna y el cielo se hace de noche. En "achica" se aprietan los discos de la columna, la silueta baja y aparece el cartel **-1 CM / AL FINAL DEL DÍA** | Pajaritos, grillos, bajada, "ding" |
| 0:11 – 0:18 | **#2 Huesos** | "Dos: los bebés nacen con unos trescientos huesos. ¡Con los años se unen y quedan doscientos seis!" | Una mamadera y una nube de huesos que flotan con el contador **300 HUESOS · BEBÉ**. En "se unen" los huesos se juntan de a pares y el contador baja hasta **206 HUESOS · ADULTO** | Pop, cascada de pops, "ding" |
| 0:18 – 0:25 | **#3 Brillás en la oscuridad** | "Tres: tu cuerpo brilla en la oscuridad, pero con una luz mil veces más débil de lo que pueden ver tus ojos." | Un cuarto oscuro y una silueta con un brillo verde (más fuerte en la cara) marcado **(EXAGERADO)**. En "mil" se comparan dos barras, **LO QUE VEN TUS OJOS** contra **TU BRILLO**, con el cartel **×1000 MÁS DÉBIL**. En "ojos" se tacha un ojo | Brillitos, pop, "error" |
| 0:25 – 0:30 | **Cierre** | "¿Cuál te sorprendió más? Contanos abajo y seguinos para más." | Las 3 curiosidades en tarjetas, "¡COMENTÁ ABAJO!" y el botón **SEGUIR → SIGUIENDO** | Clic + "ding", acorde final |

## Guion para grabar

Leé los cinco bloques **en un solo audio**, con uno o dos segundos de silencio entre bloque y bloque.
Las palabras en **negrita** son las que conviene remarcar.

> **1 · Gancho:** ¡**Tres** curiosidades de tu cuerpo que te van a **volar la cabeza**!
>
> **2 · Altura:** Uno: a la mañana sos **más alto** que a la noche. ¡Durante el día, la columna se **achica** hasta un **centímetro**!
>
> **3 · Huesos:** Dos: los bebés nacen con unos **trescientos** huesos. ¡Con los años se **unen** y quedan **doscientos seis**!
>
> **4 · Brillo:** Tres: tu cuerpo **brilla en la oscuridad**, pero con una luz **mil veces** más débil de lo que pueden ver tus ojos.
>
> **5 · Cierre:** ¿Cuál te **sorprendió** más? Contanos abajo y **seguinos** para más.

### Cómo grabar

1. **Lugar:** un cuarto callado y con cosas blandas (un dormitorio con ropa, cortinas o la cama).
   Evitá el baño y la cocina porque hacen eco. Apagá el ventilador o el aire si podés.
2. **Celular:** a 15–20 cm de la boca, un poco de costado para que las "p" no golpeen el micrófono.
   Ponelo en modo avión para que no entre una notificación.
3. **Prueba:** grabá 5 segundos, escuchalos con auriculares y fijate que no se oiga ruido fuerte ni saturación.
4. **Tono:** como si le contaras algo increíble a un amigo. Hablar sonriendo se nota en la voz.
   No hace falta apurarse: las pausas se recortan solas y, si el audio queda largo, se acelera
   hasta un 15 % sin cambiar el tono. Si los cinco bloques te llevan menos de ~32 segundos
   (sin contar las pausas del medio), el video queda en 30 justos.
5. **Errores:** si te trabás, hacé una pausa y **repetí el bloque entero**. Siempre se usa la última
   toma completa de cada bloque, así que no hace falta cortar ni empezar de nuevo.
6. **Formato:** sirve cualquier audio del celular (grabadora de voz `.m4a`, `.mp3`, un audio de WhatsApp `.opus`/`.ogg`, `.wav`...).

### Qué le hace el retoque a tu voz

Para usarla, `python hacer_video.py ep09` busca `grabaciones/ep09.*` y hace lo siguiente:

1. **Limpieza:** saca el zumbido grave y el ruido de fondo (una "compuerta espectral" que aprende el ruido de los silencios).
2. **Sincronía:** Whisper transcribe la grabación palabra por palabra y ubica cada bloque del guion, incluidas las repeticiones.
   Después, el comienzo y el final de cada palabra se ajustan con el nivel real del audio: Whisper suele adelantar
   los comienzos y cortar antes las "s" finales.
3. **Edición:** corta cada bloque, baja las respiraciones entre palabras y empareja el volumen de los cinco bloques.
4. **Tiempo:** si hace falta, acelera sin cambiar el tono (máximo 15 %). Los subtítulos karaoke y las animaciones siguen a tus palabras.
5. **Sonido:** después pasa por la misma cadena que la voz sintética (EQ, compresor, de-esser, limitador), la música baja sola cuando hablás y todo sale a −14 LUFS.

El informe queda en `build/ep09/grabacion_informe.txt`: ruido antes y después, velocidad y qué tan bien se reconoció cada bloque.

### Resultado con la grabación real

- **Audio:** 29,9 s de celular (AAC mono), a −17,5 LUFS y sin saturar. El ruido era un retumbe grave (100–300 Hz); arriba de 1 kHz la grabación estaba muy limpia.
- **Ruido de fondo:** de −44,8 a −54,5 dBFS. Se resta en potencia y no en amplitud: restar en amplitud bajaba más el ruido (−59 dBFS), pero se comía consonantes suaves y Whisper entendía peor que en el original (confianza media 0,89 contra 0,94). Así queda en 0,95.
- **Bloques:** los cinco se ubicaron al 100 %. Las pausas se recortaron y no hizo falta acelerar: la lectura dura 25 s.
- **Whisper:** entiende todo salvo "volar" en el gancho, que sale rápido y pegado ("van a volar" → "onar"). Pasa lo mismo con el audio original y con un modelo más grande, así que viene de la toma y no del retoque; en pantalla se lee "VOLAR LA CABEZA". "Se chica" y "que la noche" son elisiones naturales del habla y "seguidnos" es un sesgo de Whisper hacia el español de España.

También se probó con una grabación simulada con ruido, zumbido, eco y un bloque repetido: se quedó con la repetición correcta.

## Datos verificados

- **Más alto a la mañana:** durante el día, el peso del cuerpo comprime los discos que hay entre las vértebras y pierden algo de líquido. Por eso somos alrededor de un centímetro más bajos a la noche. Al dormir acostados se recuperan.
- **Huesos:** un recién nacido tiene cerca de 300 piezas óseas (según cómo se cuenten, entre 270 y 300), muchas todavía de cartílago. Con el crecimiento se fusionan (el cráneo, la pelvis, el sacro...) y un adulto tiene 206.
- **Brillamos:** en 2009, un estudio japonés (Kobayashi, Kikuchi y Okamura, del Instituto de Tecnología de Tohoku y la Universidad de Kioto, publicado en *PLoS ONE*) filmó con cámaras ultrasensibles que el cuerpo humano emite luz visible. Es una luz mil veces más débil de lo que el ojo puede percibir, más intensa en la cara y a media tarde. Viene de reacciones químicas del metabolismo. En el video el brillo está exagerado para que se vea.

## Texto sugerido para la publicación

> 🧠 Tres curiosidades de tu cuerpo: 📏 a la mañana sos más alto que a la noche, 🦴 los bebés nacen con unos 300 huesos y ✨ tu cuerpo brilla en la oscuridad. ¿Cuál no sabías? 👇
>
> #curiosidades #cuerpohumano #ciencia #sabiasque #shorts
