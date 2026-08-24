# -*- coding: utf-8 -*-
"""
Copy de los 10 carruseles de La Fiore (@la_fiore.cl).

Convenciones de marcado:
  *texto*   -> resaltado (dorado)
  **texto** -> negrita + dorado en subtitulos

Linea editorial:
  El contenido ensena a cuidar el resultado en casa y dice cuando volver.
  Nunca se corrige ni se critica a la clienta o al cliente: "EN CASA" es una
  indicacion, no un reproche. "EN EL SALON" es lo que hacemos nosotros.

Los servicios nombrados salen del catalogo real del salon
(insumos/services_report_354962_1787606199.xlsx).
"""

SETS = [
    # ---------------------------------------------------------------- SET 01
    {
        "id": 1,
        "num": "01",
        "seccion": "Manicure",
        "publico": "unas",
        "portada": {
            "titulo": "Tu esmaltado *no se cae*. Tu uña *crece*.",
            "sub": "Por qué el retiro tiene fecha y qué hacer entre una sesión y **la siguiente**.",
        },
        "paginas": [
            {
                "ante": "El plazo",
                "titulo": "Tres semanas, *ni una más*",
                "casa": "Anota la fecha del retiro el mismo día.",
                "casa_icono": "calendario_marca",
                "salon": "Retiramos y revisamos la uña natural.",
                "salon_icono": "una_retiro_pro",
                "dato_a": "El esmalte queda firme.",
                "dato_b": "La uña se corre.",
            },
            {
                "ante": "La cutícula",
                "titulo": "Aceite, *no tijera*",
                "casa": "Una gota de aceite cada noche, un minuto.",
                "casa_icono": "aceite_cuticula",
                "salon": "Retiro profesional sin herir el borde.",
                "salon_icono": "una_cuticula",
                "dato_a": "La cutícula es un sello.",
                "dato_b": "No es un adorno.",
            },
            {
                "ante": "Si se levanta",
                "titulo": "Nunca *a tirones*",
                "casa": "Si una se despega, no la sigas: avísanos.",
                "casa_icono": "una_tiron",
                "salon": "Retiro con torno y lima, capa por capa.",
                "salon_icono": "una_lima",
                "dato_a": "Un tirón se lleva",
                "dato_b": "tres capas de uña.",
            },
            {
                "ante": "Entre sesiones",
                "titulo": "La mano *también cuenta*",
                "casa": "Crema después de cada lavado de manos.",
                "casa_icono": "crema_manos",
                "salon": "Embellecimiento cuando la piel está seca.",
                "salon_icono": "spa_manos",
                "dato_a": "Uña impecable",
                "dato_b": "con mano cuidada.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 3 semanas",
            "detalle": "Esmaltado permanente, francesa y degradé. "
                       "El **retiro con embellecimiento** deja la uña lista para la siguiente.",
            "cta": "Agenda tu retiro",
            "sub": "Por mensaje directo o en la agenda online. El aceite de cutícula lo tienes acá.",
        },
    },

    # ---------------------------------------------------------------- SET 02
    {
        "id": 2,
        "num": "02",
        "seccion": "Color",
        "publico": "cabello",
        "portada": {
            "titulo": "Tu color *no se destiñe*. Se *lava*.",
            "sub": "Cuatro cuidados que le suman semanas a tu **tintura o tu balayage**.",
        },
        "paginas": [
            {
                "ante": "El agua",
                "titulo": "Tibia, *nunca hirviendo*",
                "casa": "Lava con agua tibia y cierra con agua fría.",
                "casa_icono": "agua_tibia",
                "salon": "Sellamos el color al terminar el servicio.",
                "salon_icono": "enjuague_frio",
                "dato_a": "El calor abre la cutícula.",
                "dato_b": "El frío la cierra.",
            },
            {
                "ante": "El shampoo",
                "titulo": "Uno *para cabello con color*",
                "casa": "Revisa que diga apto para cabello teñido.",
                "casa_icono": "shampoo_duda",
                "salon": "Te decimos cuál le sirve al tuyo.",
                "salon_icono": "shampoo_indicado",
                "dato_a": "Shampoo cualquiera",
                "dato_b": "se lleva el color bueno.",
            },
            {
                "ante": "El calor",
                "titulo": "Protector *siempre*",
                "casa": "Nada de plancha sobre el pelo sin protector.",
                "casa_icono": "plancha_calor",
                "salon": "Trabajamos a 180°, no más.",
                "salon_icono": "protector_termico",
                "dato_a": "El color no se va.",
                "dato_b": "Se quema.",
            },
            {
                "ante": "La raíz",
                "titulo": "Retoque *con fecha*",
                "casa": "Marca la cuarta semana en el calendario.",
                "casa_icono": "raiz_avisa",
                "salon": "Retoque de crecimiento y ajuste de tono.",
                "salon_icono": "calendario_retoque",
                "dato_a": "La raíz avisa temprano.",
                "dato_b": "Adelántate.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 4 a 6 semanas",
            "detalle": "Retoque de crecimiento, baño de color y tintura. "
                       "Para **balayage y babylights**, el contorno estira mucho más el trabajo.",
            "cta": "Agenda tu retoque",
            "sub": "Trabajamos con Alfaparf y Framesi. El shampoo que te indicamos está en el salón.",
        },
    },

    # ---------------------------------------------------------------- SET 03
    {
        "id": 3,
        "num": "03",
        "seccion": "Barbería",
        "publico": "barba",
        "portada": {
            "titulo": "Tu barba no crece mal. Crece *sin forma*.",
            "sub": "Lo que hace un perfilado con **toallas temperadas** y cómo sostenerlo en casa.",
        },
        "paginas": [
            {
                "ante": "El lavado",
                "titulo": "La barba *va aparte*",
                "casa": "Shampoo de barba dos o tres veces por semana.",
                "casa_icono": "shampoo_pelo_barba",
                "salon": "Lavado de barba con toallas temperadas.",
                "salon_icono": "shampoo_barba",
                "dato_a": "El shampoo de pelo",
                "dato_b": "reseca la barba.",
            },
            {
                "ante": "El aceite",
                "titulo": "Va en la *piel*",
                "casa": "Unas gotas en la piel, no solo en el pelo.",
                "casa_icono": "aceite_barba",
                "salon": "Te mostramos cuánto es suficiente.",
                "salon_icono": "rostro_barba_ok",
                "dato_a": "La picazón no es la barba.",
                "dato_b": "Es la piel.",
            },
            {
                "ante": "El peine",
                "titulo": "Siempre *hacia abajo*",
                "casa": "Peine de madera, siempre en el mismo sentido.",
                "casa_icono": "peine_barba",
                "salon": "Perfilado que ordena el crecimiento.",
                "salon_icono": "navaja_perfila",
                "dato_a": "La forma se entrena.",
                "dato_b": "No se espera.",
            },
            {
                "ante": "El límite",
                "titulo": "El cuello *no se toca*",
                "casa": "Deja el cuello y el pómulo para el salón.",
                "casa_icono": "maquina_cuello",
                "salon": "Perfilado con navaja y toallas temperadas.",
                "salon_icono": "navaja_cuello",
                "dato_a": "Un cuello mal marcado",
                "dato_b": "se nota tres semanas.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 2 a 3 semanas",
            "detalle": "Perfilado de barba con toallas temperadas y afeitado al ras. "
                       "El **Servicio Presidencial** junta corte, barba y ritual completo.",
            "cta": "Agenda tu perfilado",
            "sub": "Línea Sir Fausto para barba disponible en el salón.",
        },
    },

    # ---------------------------------------------------------------- SET 04
    {
        "id": 4,
        "num": "04",
        "seccion": "Barbería",
        "publico": "corte",
        "portada": {
            "titulo": "El degradado *vive tres semanas*. Después es otro corte.",
            "sub": "Cómo estirar la línea de tu corte sin que pierda **el diseño**.",
        },
        "paginas": [
            {
                "ante": "El plazo",
                "titulo": "Tres o cuatro *semanas*",
                "casa": "Deja agendada la próxima antes de salir.",
                "casa_icono": "calendario_agenda",
                "salon": "Mantenemos la línea y el diseño original.",
                "salon_icono": "maquina_fade",
                "dato_a": "El degradado se corre",
                "dato_b": "de a un milímetro.",
            },
            {
                "ante": "El lavado",
                "titulo": "No *todos los días*",
                "casa": "Tres veces por semana es suficiente.",
                "casa_icono": "lavado_diario",
                "salon": "Te decimos qué necesita tu cuero cabelludo.",
                "salon_icono": "lavado_justo",
                "dato_a": "Lavar de más",
                "dato_b": "no es lavar mejor.",
            },
            {
                "ante": "El secado",
                "titulo": "Aire *tibio*",
                "casa": "Secador tibio y a distancia de un palmo.",
                "casa_icono": "secador_calor",
                "salon": "Peinado y producto según tu tipo de pelo.",
                "salon_icono": "secador_tibio",
                "dato_a": "El calor seco",
                "dato_b": "quiebra la punta.",
            },
            {
                "ante": "El producto",
                "titulo": "Menos *de lo que crees*",
                "casa": "Del tamaño de una arveja, en pelo seco.",
                "casa_icono": "producto_exceso",
                "salon": "Elegimos entre cera, pomada o polvo.",
                "salon_icono": "producto_justo",
                "dato_a": "El exceso pesa.",
                "dato_b": "Y el pelo cae.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 3 a 4 semanas",
            "detalle": "Corte clásico, corte con tijeras, undercut y diseño. "
                       "Si el tuyo es **degradado**, la tercera semana es el momento justo.",
            "cta": "Agenda tu corte",
            "sub": "También corte de niño, adulto mayor y perfilado de cejas masculino.",
        },
    },

    # ---------------------------------------------------------------- SET 05
    {
        "id": 5,
        "num": "05",
        "seccion": "Pedicure",
        "publico": "pies",
        "portada": {
            "titulo": "Tus pies aguantan *todo el día*. Diez minutos *a la semana*.",
            "sub": "La rutina corta que evita la grieta y la uña que **se entierra**.",
        },
        "paginas": [
            {
                "ante": "El corte",
                "titulo": "Recto, *nunca en punta*",
                "casa": "Corta recto y deja el borde a ras del dedo.",
                "casa_icono": "una_pie_punta",
                "salon": "Corte y perfilado sin dañar el lecho.",
                "salon_icono": "una_pie_recta",
                "dato_a": "La uña en punta",
                "dato_b": "se entierra sola.",
            },
            {
                "ante": "El talón",
                "titulo": "La lima va *en seco*",
                "casa": "Lima suave sobre talón seco, nunca mojado.",
                "casa_icono": "lima_seco",
                "salon": "Rebaje de durezas con técnica y medida.",
                "salon_icono": "pie_lima",
                "dato_a": "El talón mojado",
                "dato_b": "se lima de más.",
            },
            {
                "ante": "La crema",
                "titulo": "De *noche*",
                "casa": "Crema con urea en los talones antes de dormir.",
                "casa_icono": "crema_noche",
                "salon": "Pedicure spa cuando la piel ya está dura.",
                "salon_icono": "spa_pies",
                "dato_a": "La grieta duele después.",
                "dato_b": "Adelántate.",
            },
            {
                "ante": "El calzado",
                "titulo": "Déjalos *respirar*",
                "casa": "Alterna zapatos y seca bien entre los dedos.",
                "casa_icono": "pie_encerrado",
                "salon": "Revisamos qué te está apretando y dónde.",
                "salon_icono": "pie_revision",
                "dato_a": "El pie húmedo",
                "dato_b": "no alcanza a recuperarse.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 4 a 6 semanas",
            "detalle": "Pedicure spa y pedicure en seco. "
                       "Y si los pies vienen cansados, la **reflexología podal** se hace en la misma visita.",
            "cta": "Agenda tu pedicure",
            "sub": "Sala exclusiva de pedicure, con cabina de masajes al lado.",
        },
    },

    # ---------------------------------------------------------------- SET 06
    {
        "id": 6,
        "num": "06",
        "seccion": "Cosmetología",
        "publico": "piel",
        "portada": {
            "titulo": "Una limpieza facial *no es un lujo*. Es mantención.",
            "sub": "Qué hacer los días de después para que el resultado **te dure**.",
        },
        "paginas": [
            {
                "ante": "Las 48 horas",
                "titulo": "Sol *no*, protector *sí*",
                "casa": "Protector solar aunque el día esté nublado.",
                "casa_icono": "sol_sin_proteccion",
                "salon": "Te indicamos qué usar esos dos días.",
                "salon_icono": "protector_solar",
                "dato_a": "La piel recién limpia",
                "dato_b": "está recién abierta.",
            },
            {
                "ante": "La tentación",
                "titulo": "No *extraigas* en casa",
                "casa": "Deja la extracción para la cabina. Siempre.",
                "casa_icono": "piel_aprieta",
                "salon": "Extracción con técnica, vapor y asepsia.",
                "salon_icono": "piel_extraccion",
                "dato_a": "Un poro forzado",
                "dato_b": "deja marca un año.",
            },
            {
                "ante": "Cada noche",
                "titulo": "Limpia *antes de dormir*",
                "casa": "Desmaquilla siempre, aunque llegues tarde.",
                "casa_icono": "desmaquilla",
                "salon": "Ajustamos la rutina a tu tipo de piel.",
                "salon_icono": "rutina_piel",
                "dato_a": "Ocho horas de maquillaje",
                "dato_b": "son ocho horas de poro.",
            },
            {
                "ante": "El plazo",
                "titulo": "Una vez *al mes*",
                "casa": "Marca la fecha y no esperes el brote.",
                "casa_icono": "calendario_mes",
                "salon": "Limpieza profunda según lo que pida tu piel.",
                "salon_icono": "piel_limpia",
                "dato_a": "La piel se ordena",
                "dato_b": "con constancia.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 4 a 6 semanas",
            "detalle": "Limpieza facial profunda, anti-age, piel sensible, acné y rosácea. "
                       "También **dermaneedling** cuando la piel ya está preparada.",
            "cta": "Agenda tu limpieza",
            "sub": "Antes elegimos juntos el protocolo según tu tipo de piel.",
        },
    },

    # ---------------------------------------------------------------- SET 07
    {
        "id": 7,
        "num": "07",
        "seccion": "Cabello",
        "publico": "cabello",
        "portada": {
            "titulo": "El pelo largo *se logra con tijera*. Suena raro y es así.",
            "sub": "Cómo cortar la punta abierta antes de que **suba por el largo**.",
        },
        "paginas": [
            {
                "ante": "El despunte",
                "titulo": "Cada *tres meses*",
                "casa": "Marca la fecha aunque lo veas bien.",
                "casa_icono": "calendario_despunte",
                "salon": "Cortamos solo lo quebrado, no el largo.",
                "salon_icono": "tijera_despunte",
                "dato_a": "La punta abierta",
                "dato_b": "sube por el pelo.",
            },
            {
                "ante": "La toalla",
                "titulo": "Presiona, *no restriegues*",
                "casa": "Envuelve y aprieta suave. Nada de frotar.",
                "casa_icono": "toalla_frota",
                "salon": "Te enseñamos el secado que no maltrata.",
                "salon_icono": "toalla_presiona",
                "dato_a": "El pelo mojado",
                "dato_b": "se quiebra solo.",
            },
            {
                "ante": "El tratamiento",
                "titulo": "Mascarilla *semanal*",
                "casa": "De medios a puntas, diez minutos y enjuaga.",
                "casa_icono": "mascarilla_semanal",
                "salon": "Hidratación, botox capilar o células madre.",
                "salon_icono": "masaje_capilar",
                "dato_a": "Hidratar no es reparar.",
                "dato_b": "Van los dos juntos.",
            },
            {
                "ante": "El peine",
                "titulo": "Desenreda *desde abajo*",
                "casa": "Parte por las puntas y sube de a poco.",
                "casa_icono": "peine_arriba",
                "salon": "Revisamos si el quiebre es corte o químico.",
                "salon_icono": "peine_abajo",
                "dato_a": "El tirón desde arriba",
                "dato_b": "arrastra todo el largo.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 8 a 12 semanas",
            "detalle": "Despunte, corte y tratamiento. "
                       "Para cabello muy trabajado, **Olaplex** y la laminación biomimética.",
            "cta": "Agenda tu despunte",
            "sub": "Si tienes color, hazlo coincidir con el retoque y ahorras una visita.",
        },
    },

    # ---------------------------------------------------------------- SET 08
    {
        "id": 8,
        "num": "08",
        "seccion": "Manicure",
        "publico": "unas",
        "portada": {
            "titulo": "El relleno *no es opcional*. Es lo que sostiene la uña.",
            "sub": "Soft gel y kapping: por qué el peso **se corre** a la tercera semana.",
        },
        "paginas": [
            {
                "ante": "El plazo",
                "titulo": "Cada *tres semanas*",
                "casa": "Agenda el relleno el mismo día del servicio.",
                "casa_icono": "calendario_relleno",
                "salon": "Rebalance y revisión del molde completo.",
                "salon_icono": "una_rebalance",
                "dato_a": "La uña crece.",
                "dato_b": "El peso se corre.",
            },
            {
                "ante": "El golpe",
                "titulo": "No abras nada *con la uña*",
                "casa": "Usa la yema del dedo, nunca el borde libre.",
                "casa_icono": "una_golpe",
                "salon": "Arreglamos una uña suelta en cinco minutos.",
                "salon_icono": "una_repara",
                "dato_a": "La uña no es herramienta.",
                "dato_b": "Es uña.",
            },
            {
                "ante": "Si se levanta",
                "titulo": "Avísanos *el mismo día*",
                "casa": "No la pegues ni la limes por tu cuenta.",
                "casa_icono": "una_levante",
                "salon": "Retiro y revisión del lecho ungueal.",
                "salon_icono": "una_revision",
                "dato_a": "Bajo un levante",
                "dato_b": "entra humedad.",
            },
            {
                "ante": "El descanso",
                "titulo": "Pídelo *sin miedo*",
                "casa": "Cuenta cuántos meses llevas seguidos.",
                "casa_icono": "una_descanso",
                "salon": "Te decimos cuándo conviene parar y cuánto.",
                "salon_icono": "una_natural",
                "dato_a": "Descansar no es perder.",
                "dato_b": "Es cuidar.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 3 semanas",
            "detalle": "Soft gel, kapping con hard gel y técnica híbrida. "
                       "El **retiro de uña artificial con embellecimiento** deja la mano lista.",
            "cta": "Agenda tu relleno",
            "sub": "También hacemos arreglo de una sola uña, si es lo único que necesitas.",
        },
    },

    # ---------------------------------------------------------------- SET 09
    {
        "id": 9,
        "num": "09",
        "seccion": "Cejas y pestañas",
        "publico": "mirada",
        "portada": {
            "titulo": "Tu mirada se arma con *dos milímetros*.",
            "sub": "Por eso el perfilado con **visajismo** no se improvisa frente al espejo.",
        },
        "paginas": [
            {
                "ante": "Las cejas",
                "titulo": "Guarda *la pinza*",
                "casa": "Deja crecer dos semanas antes de tu hora.",
                "casa_icono": "pinza_casa",
                "salon": "Perfilado con visajismo, según tu rostro.",
                "salon_icono": "ceja_perfilado",
                "dato_a": "La pinza en casa",
                "dato_b": "borra el diseño.",
            },
            {
                "ante": "Las pestañas",
                "titulo": "Sin *frotar*",
                "casa": "Seca dando toques suaves, nunca frotando.",
                "casa_icono": "pestana_frota",
                "salon": "Relleno antes de que se vea despoblada.",
                "salon_icono": "pestana_relleno",
                "dato_a": "Una pestaña arrancada",
                "dato_b": "demora dos meses.",
            },
            {
                "ante": "La depilación",
                "titulo": "Cera, *no máquina*",
                "casa": "Deja el vello del largo de un grano de arroz.",
                "casa_icono": "maquina_vello",
                "salon": "Cera con la piel preparada y calmante final.",
                "salon_icono": "cera_profesional",
                "dato_a": "La máquina corta.",
                "dato_b": "La cera saca de raíz.",
            },
            {
                "ante": "El día después",
                "titulo": "24 horas *sin calor*",
                "casa": "Ese día, nada de sol, piscina ni sauna.",
                "casa_icono": "sol_despues",
                "salon": "Te damos la calmante antes de que salgas.",
                "salon_icono": "calmante",
                "dato_a": "El poro recién abierto",
                "dato_b": "se irrita con nada.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 3 a 4 semanas",
            "detalle": "Perfilado con visajismo, laminado de cejas y lifting de pestañas. "
                       "Extensiones **clásica, efecto máscara y fibra tecnológica**.",
            "cta": "Agenda tu perfilado",
            "sub": "El relleno de extensiones se agenda antes, no cuando ya se vació.",
        },
    },

    # ---------------------------------------------------------------- SET 10
    {
        "id": 10,
        "num": "10",
        "seccion": "Masajes",
        "publico": "masaje",
        "portada": {
            "titulo": "La contractura *no llegó ayer*.",
            "sub": "Qué hacer las horas siguientes para que el masaje **no se pierda**.",
        },
        "paginas": [
            {
                "ante": "Al salir",
                "titulo": "Toma *agua*",
                "casa": "Dos vasos al salir y sigue tomando el día.",
                "casa_icono": "dos_vasos",
                "salon": "Cerramos la sesión con maniobras suaves.",
                "salon_icono": "masaje_cierre",
                "dato_a": "El músculo trabajado",
                "dato_b": "pide agua.",
            },
            {
                "ante": "En casa",
                "titulo": "Calor *seco*, diez minutos",
                "casa": "Guatero diez minutos y descansa. No más.",
                "casa_icono": "calor_guatero",
                "salon": "Te indicamos dónde aplicarlo y cuándo.",
                "salon_icono": "calor_indicado",
                "dato_a": "El calor relaja.",
                "dato_b": "No repara solo.",
            },
            {
                "ante": "En el día",
                "titulo": "Levántate *cada hora*",
                "casa": "Un minuto de pie por cada hora sentada.",
                "casa_icono": "sentado_hora",
                "salon": "Masaje descontracturante en la zona exacta.",
                "salon_icono": "masaje_localizado",
                "dato_a": "La postura suma",
                "dato_b": "todos los días.",
            },
            {
                "ante": "El plazo",
                "titulo": "No esperes *que duela*",
                "casa": "Agenda antes de que la molestia aparezca.",
                "casa_icono": "dolor_espera",
                "salon": "Sesiones espaciadas, no de emergencia.",
                "salon_icono": "calendario_mantencion",
                "dato_a": "Mantener cuesta menos",
                "dato_b": "que recuperar.",
            },
        ],
        "cierre": {
            "ante": "Tu próxima visita",
            "plazo": "Cada 3 a 4 semanas",
            "detalle": "Relajación, descontracturante, piedras calientes y deportivo. "
                       "También **drenaje linfático** y reflexología podal o corporal.",
            "cta": "Agenda tu masaje",
            "sub": "Cabina de masajes dentro del salón. Puedes juntarlo con tu pedicure.",
        },
    },
]


# --------------------------------------------------------------------------
# validaciones de linea editorial
# --------------------------------------------------------------------------

PALABRAS_PROHIBIDAS = ["OFICIO"]

MAX_CASA_SALON = 52
MAX_DATO = 34
MAX_TITULO_PORTADA = 78
MAX_CTA = 22

ICONOS_OBLIGATORIOS = ("casa_icono", "salon_icono")


def _todos_los_textos(s):
    yield s["portada"]["titulo"]
    yield s["portada"]["sub"]
    for p in s["paginas"]:
        for k in ("ante", "titulo", "casa", "salon", "dato_a", "dato_b"):
            yield p[k]
    for k in ("ante", "plazo", "detalle", "cta", "sub"):
        yield s["cierre"][k]


def validar():
    """Revisa reglas duras de contenido. Devuelve lista de errores."""
    import iconos

    errores = []
    vistos = set()
    for s in SETS:
        et = "SET %02d" % s["id"]
        if s["id"] in vistos:
            errores.append("%s: id repetido" % et)
        vistos.add(s["id"])

        for t in _todos_los_textos(s):
            for mala in PALABRAS_PROHIBIDAS:
                if mala.lower() in t.lower():
                    errores.append("%s: palabra prohibida '%s' en: %s" % (et, mala, t))

        if len(s["portada"]["titulo"]) > MAX_TITULO_PORTADA:
            errores.append("%s: titulo de portada con %d caracteres (max %d)"
                           % (et, len(s["portada"]["titulo"]), MAX_TITULO_PORTADA))

        if len(s["paginas"]) != 4:
            errores.append("%s: tiene %d paginas interiores, deben ser 4"
                           % (et, len(s["paginas"])))

        for i, p in enumerate(s["paginas"], start=2):
            for k in ("casa", "salon"):
                if len(p[k]) > MAX_CASA_SALON:
                    errores.append("%s l%d: '%s' tiene %d caracteres (max %d)"
                                   % (et, i, p[k], len(p[k]), MAX_CASA_SALON))
            for k in ("dato_a", "dato_b"):
                if len(p[k]) > MAX_DATO:
                    errores.append("%s l%d: dato '%s' tiene %d caracteres (max %d)"
                                   % (et, i, p[k], len(p[k]), MAX_DATO))
            for k in ICONOS_OBLIGATORIOS:
                if p[k] not in iconos.ICONOS:
                    errores.append("%s l%d: icono inexistente '%s'" % (et, i, p[k]))

        if len(s["cierre"]["cta"]) > MAX_CTA:
            errores.append("%s cierre: cta '%s' tiene %d caracteres (max %d)"
                           % (et, s["cierre"]["cta"], len(s["cierre"]["cta"]), MAX_CTA))
    return errores


def por_id(set_id):
    for s in SETS:
        if s["id"] == set_id:
            return s
    raise KeyError("set %s no existe" % set_id)


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "plantilla"))
    errs = validar()
    if errs:
        print("\n".join(errs))
        raise SystemExit(1)
    print("Contenido OK: %d sets, %d laminas." % (len(SETS), len(SETS) * 6))
