"""Guion del video: lo que dice la voz y lo que se ve en cada escena.

Es la única fuente de verdad del texto; guion.md lo describe para humanos.
"""

DURACION = 30.0                 # segundos
VOZ = "es-AR-TomasNeural"       # voz neuronal de Microsoft Edge (gratuita)

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
