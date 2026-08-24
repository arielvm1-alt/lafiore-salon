# -*- coding: utf-8 -*-
"""
Libreria de ilustraciones SVG propias para las laminas de La Fiore.

Sistema:
  - Todo se dibuja dentro de un viewBox de 240 x 180.
  - Trazo 5-7px, esquinas y puntas redondeadas, sin relleno salvo pelo y textos.
  - Color base TINTA #221F1F, acento DORADO #90651F.
  - Los textos cortos dentro del SVG van en Akzidenz Grotesk Bold Condensed.

Se construye por composicion: primitivas reutilizables + iconos compuestos.
"""

import math

TINTA = "#221F1F"
DORADO = "#90651F"

W, H = 240, 180


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def g(body, x=0.0, y=0.0, s=1.0):
    """Envuelve markup en un grupo trasladado/escalado."""
    return '<g transform="translate(%g,%g) scale(%g)">%s</g>' % (x, y, s, body)


def texto(t, x, y, size=30, color=TINTA, anchor="middle"):
    return (
        '<text x="%g" y="%g" text-anchor="%s" font-family="Akzidenz Cond" font-weight="700" '
        'font-size="%g" fill="%s" stroke="none" letter-spacing="0.04em">%s</text>'
        % (x, y, anchor, size, color, t)
    )


def linea(x1, y1, x2, y2, color=TINTA, w=6):
    return '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="%g"/>' % (x1, y1, x2, y2, color, w)


def circulo(cx, cy, r, color=TINTA, w=6, fill="none"):
    return '<circle cx="%g" cy="%g" r="%g" stroke="%s" stroke-width="%g" fill="%s"/>' % (
        cx, cy, r, color, w, fill)


def rect(x, y, w_, h_, r=8, color=TINTA, w=6, fill="none"):
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" stroke="%s" '
            'stroke-width="%g" fill="%s"/>' % (x, y, w_, h_, r, color, w, fill))


def path(d, color=TINTA, w=6, fill="none"):
    return '<path d="%s" stroke="%s" stroke-width="%g" fill="%s"/>' % (d, color, w, fill)


def flecha(x1, y1, x2, y2, color=TINTA, w=6, punta=14):
    a = math.atan2(y2 - y1, x2 - x1)
    p = [linea(x1, y1, x2, y2, color, w)]
    for s in (2.6, -2.6):
        p.append(linea(x2, y2, x2 + math.cos(a + s) * punta,
                       y2 + math.sin(a + s) * punta, color, w))
    return "".join(p)


def tachar(color=TINTA, x1=4, y1=4, x2=112, y2=104, w=8):
    """Barra diagonal para marcar 'esto no'."""
    return linea(x1, y1, x2, y2, color, w)


# --------------------------------------------------------------------------
# primitivas
# --------------------------------------------------------------------------

def persona(color=TINTA, pelo=TINTA, hombros=True):
    """Cabeza con pelo solido + hombros. Caja local: 0,0 -> 62,76."""
    p = ['<path d="M9,26 C9,7 22,-2 31,-2 C40,-2 53,7 53,26 '
         'C50,20 44,14 31,14 C18,14 12,20 9,26 Z" fill="%s" stroke="none"/>' % pelo]
    p.append(circulo(31, 26, 20, color))
    if hombros:
        p.append(path("M0,76 C0,55 13,45 31,45 C49,45 62,55 62,76", color))
    return "".join(p)


def rostro(color=TINTA, barba=None, gotas=None):
    """Rostro de frente con pelo. Caja local: 0,0 -> 76,100."""
    p = ['<path d="M10,34 C10,10 24,0 38,0 C52,0 66,10 66,34 '
         'C62,26 54,20 38,20 C22,20 14,26 10,34 Z" fill="%s" stroke="none"/>' % color]
    p.append(path("M12,32 L12,54 C12,74 24,88 38,88 C52,88 64,74 64,54 L64,32", color))
    p.append(circulo(27, 50, 3.5, color, 5, color))
    p.append(circulo(49, 50, 3.5, color, 5, color))
    if barba:
        p.append(path("M12,54 C12,80 24,96 38,96 C52,96 64,80 64,54", barba, 7))
        p.append(path("M25,70 C31,76 45,76 51,70", barba, 5))
    if gotas:
        p.append(g(gota(gotas, 0.34), 74, 24))
        p.append(g(gota(gotas, 0.26), 86, 52))
    return "".join(p)


def mano_unas(color=TINTA, acento=DORADO, esmalte=True):
    """Cuatro dedos con la una pintada, vista de manicure. Caja: 0,0 -> 100,98."""
    an = 22
    p = []
    for x, top in ((2, 22), (26, 6), (52, 10), (76, 26)):
        p.append(path("M%g,98 L%g,%g C%g,%g %g,%g %g,%g L%g,98"
                      % (x, x, top + 16, x, top, x + an, top, x + an, top + 16, x + an), color))
        p.append(path("M%g,%g C%g,%g %g,%g %g,%g L%g,%g C%g,%g %g,%g %g,%g Z"
                      % (x + 4, top + 19, x + 4, top + 8, x + an - 4, top + 8, x + an - 4, top + 19,
                         x + an - 4, top + 31, x + an - 4, top + 35, x + 4, top + 35, x + 4, top + 31),
                      acento, 4, acento if esmalte else "none"))
    return "".join(p)


def una(color=TINTA, acento=DORADO, cuticula=None, larga=False):
    """Dedo de frente con la lamina de la una. Caja local: 0,0 -> 64,112."""
    tope = 6 if larga else 20
    p = [path("M6,112 L6,44 C6,26 18,14 32,14 C46,14 58,26 58,44 L58,112", color)]
    p.append(path("M16,48 C16,%g 22,%g 32,%g C42,%g 48,%g 48,48 L48,64 "
                  "C48,69 43,71 32,71 C21,71 16,69 16,64 Z"
                  % (tope + 18, tope, tope, tope, tope + 18), acento, 6))
    if cuticula:
        p.append(path("M13,78 C21,86 43,86 51,78", cuticula, 7))
    return "".join(p)


def gota(color=TINTA, s=1.0):
    """Gota. Caja local: 0,0 -> 44,56 (antes de escalar)."""
    return g(path("M22,2 C22,2 42,26 42,38 C42,49 33,56 22,56 "
                  "C11,56 2,49 2,38 C2,26 22,2 22,2 Z", color), 0, 0, s)


def frasco(t="", color=TINTA, color_texto=None, pincel=False):
    """Frasco de producto. Caja local: 0,0 -> 62,100 (con pincel sube a -48)."""
    p = []
    if pincel:
        p.append(linea(31, -26, 31, 2, color, 7))
        p.append(path("M25,-46 C25,-54 37,-54 37,-46 L34,-26 L28,-26 Z", color, 5))
    p.append(rect(19, 0, 24, 16, 4, color, 5))
    p.append(path("M4,30 C4,22 12,16 20,16 L42,16 C50,16 58,22 58,30 L58,92 "
                  "C58,96 54,100 50,100 L12,100 C8,100 4,96 4,92 Z", color))
    p.append(linea(4, 44, 58, 44, color, 5))
    if t:
        p.append(texto(t, 31, 78, 26, color_texto or color))
    return "".join(p)


def tubo(t="", color=TINTA, color_texto=None):
    """Tubo de crema. Caja local: 0,0 -> 54,104."""
    p = [rect(16, 0, 22, 14, 3, color, 5)]
    p.append(path("M4,26 C4,20 10,14 16,14 L38,14 C44,14 50,20 50,26 L50,96 L4,96 Z", color))
    p.append(path("M4,96 L50,96 L44,104 L10,104 Z", color, 5))
    if t:
        p.append(texto(t, 27, 64, 24, color_texto or color))
    return "".join(p)


def calendario(t="", color=TINTA, color_texto=None):
    """Calendario. Caja local: 0,0 -> 88,84."""
    p = [rect(0, 8, 88, 76, 10, color)]
    p.append(linea(0, 30, 88, 30, color, 6))
    p.append(linea(22, 0, 22, 16, color, 6))
    p.append(linea(66, 0, 66, 16, color, 6))
    if t:
        p.append(texto(t, 44, 66, 30, color_texto or color))
    return "".join(p)


def reloj(color=TINTA):
    """Reloj. Caja local: 0,0 -> 72,72."""
    return circulo(36, 36, 32, color) + path("M36,18 L36,38 L52,46", color)


def bocadillo(t="", w_=104, h_=64, color=TINTA, size=30, color_texto=None, cola="izq"):
    """Bocadillo con cola. Caja local: 0,0 -> w_, h_+22."""
    p = [rect(0, 0, w_, h_, 14, color)]
    if cola == "izq":
        p.append(path("M22,%g L22,%g L52,%g" % (h_, h_ + 22, h_), color))
    else:
        p.append(path("M%g,%g L%g,%g L%g,%g"
                      % (w_ - 22, h_, w_ - 22, h_ + 22, w_ - 52, h_), color))
    if t:
        p.append(texto(t, w_ / 2.0, h_ / 2.0 + size * 0.34, size, color_texto or color))
    return "".join(p)


def sol(color=TINTA, r=18, rayos=8):
    """Sol / luz. Centrado en 0,0."""
    p = [circulo(0, 0, r, color)]
    for i in range(rayos):
        a = 2 * math.pi * i / rayos
        p.append(linea(math.cos(a) * (r + 9), math.sin(a) * (r + 9),
                       math.cos(a) * (r + 20), math.sin(a) * (r + 20), color, 5))
    return "".join(p)


def tijera(color=TINTA):
    """Tijera. Caja local: 0,0 -> 76,104."""
    p = [circulo(16, 88, 14, color), circulo(60, 88, 14, color)]
    p.append(path("M60,76 L20,10", color))
    p.append(path("M16,76 L56,10", color))
    p.append(circulo(38, 46, 4, color, 5, color))
    return "".join(p)


def navaja(color=TINTA):
    """Navaja de barbero abierta. Caja local: 0,0 -> 120,54."""
    p = [path("M4,44 L74,44 C82,44 88,38 88,30 L88,10 L14,10 C8,10 4,16 4,22 Z", color)]
    p.append(path("M88,26 L114,26", color, 7))
    p.append(circulo(114, 26, 5, color, 5, color))
    return "".join(p)


def peine(color=TINTA, dientes=9):
    """Peine. Caja local: 0,0 -> 106,52."""
    p = [path("M0,10 C0,4 4,0 10,0 L96,0 C102,0 106,4 106,10 L106,20 L0,20 Z", color)]
    for i in range(dientes):
        x = 8 + i * (90.0 / (dientes - 1))
        p.append(linea(x, 20, x, 50, color, 5))
    return "".join(p)


def maquina(color=TINTA):
    """Maquina de cortar. Caja local: 0,0 -> 90,86."""
    p = [path("M8,26 C8,18 14,12 22,12 L68,12 C76,12 82,18 82,26 L82,74 "
              "C82,80 78,84 72,84 L18,84 C12,84 8,80 8,74 Z", color)]
    p.append(path("M14,12 L14,2 L76,2 L76,12", color, 5))
    for i in range(6):
        p.append(linea(20 + i * 10, 2, 20 + i * 10, 12, color, 4))
    p.append(linea(20, 46, 70, 46, color, 5))
    return "".join(p)


def secador(color=TINTA, calor=None):
    """Secador de pelo. Caja local: 0,0 -> 112,88."""
    p = [path("M12,18 C4,18 0,26 0,34 C0,42 4,50 12,50 L64,50 C74,50 82,42 82,34 "
              "C82,26 74,18 64,18 Z", color)]
    p.append(path("M30,50 L30,80 C30,85 34,88 39,88 L52,88 C57,88 60,85 60,80 L60,50", color))
    if calor:
        for y in (22, 34, 46):
            p.append(linea(90, y, 110, y, calor, 5))
    return "".join(p)


def plancha(color=TINTA):
    """Plancha de pelo. Caja local: 0,0 -> 102,60."""
    p = [path("M6,18 L86,4 C94,2 100,6 100,14 L100,18 L6,30 Z", color)]
    p.append(path("M6,34 L100,22 L100,30 C100,38 94,44 86,46 L6,58 Z", color))
    return "".join(p)


def toalla(color=TINTA, vapor=None):
    """Toalla enrollada. Caja local: 0,0 -> 96,64 (con vapor sube a -14)."""
    p = [rect(0, 12, 96, 52, 20, color)]
    p.append(path("M24,12 C24,2 40,2 40,12", color, 5))
    p.append(linea(0, 34, 96, 34, color, 5))
    if vapor:
        for x in (26, 50, 74):
            p.append(path("M%g,6 C%g,-2 %g,-6 %g,-14" % (x, x + 9, x - 9, x), vapor, 5))
    return "".join(p)


def pie(color=TINTA, acento=DORADO, unas=True):
    """Huella de pie: planta y cinco dedos. Caja local: 0,0 -> 76,112."""
    c = acento if unas else color
    p = [path("M14,44 C14,31 29,24 44,29 C59,34 67,47 64,60 "
              "C61,72 51,76 45,84 C39,93 41,102 33,108 "
              "C24,114 12,107 10,96 C8,84 17,77 19,67 C21,57 14,54 14,44 Z", color)]
    for x, y, r in ((20, 15, 7), (35, 9, 6), (47, 11, 5.5), (57, 16, 5), (65, 23, 4.5)):
        p.append(circulo(x, y, r, c, 5, c if unas else "none"))
    return "".join(p)


def lima(color=TINTA):
    """Lima / pulidor de unas. Caja local: 0,0 -> 108,32."""
    p = [rect(2, 4, 88, 24, 12, color)]
    p.append(linea(92, 16, 106, 16, color, 6))
    for x in (22, 38, 54, 70):
        p.append(linea(x, 11, x, 21, color, 4))
    return "".join(p)


def mechon(color=TINTA, quebrado=False):
    """Mechon de pelo. Caja local: 0,0 -> 70,110."""
    p = []
    largo = 76 if quebrado else 104
    for x in (10, 32, 54):
        p.append(path("M%g,0 C%g,30 %g,50 %g,%g" % (x, x - 12, x + 12, x, largo), color))
    if quebrado:
        for x in (10, 32, 54):
            p.append(path("M%g,86 L%g,100 M%g,86 L%g,100"
                          % (x - 6, x - 13, x + 6, x + 13), color, 5))
    return "".join(p)


def piel(color=TINTA, acento=DORADO, puntos=True):
    """Circulo de piel con textura: sirve para poro / limpieza. Caja: 0,0 -> 96,96."""
    p = [circulo(48, 48, 44, color)]
    if puntos:
        for x, y in ((34, 36), (58, 32), (44, 58), (66, 56), (30, 62)):
            p.append(circulo(x, y, 4, acento, 4, acento))
    return "".join(p)


def ceja(color=TINTA, acento=None):
    """Ceja y ojo. Caja local: 0,0 -> 104,56."""
    p = [path("M4,20 C24,0 76,0 100,16", acento or color, 8)]
    p.append(path("M10,42 C28,28 74,28 94,42 C74,56 28,56 10,42 Z", color))
    p.append(circulo(52, 42, 8, color, 5, color))
    return "".join(p)


def pestana(color=TINTA, acento=DORADO):
    """Ojo con pestanas. Caja local: 0,0 -> 108,58."""
    p = [path("M6,40 C26,20 82,20 102,40 C82,56 26,56 6,40 Z", color)]
    p.append(circulo(54, 40, 9, color, 5, color))
    for x, dx in ((16, -8), (32, -5), (54, 0), (76, 5), (94, 8)):
        p.append(linea(x, 32 - abs(54 - x) * 0.10, x + dx, 8, acento, 5))
    return "".join(p)


def vaso_agua(color=TINTA, acento=DORADO):
    """Vaso con agua. Caja local: 0,0 -> 62,88."""
    p = [path("M4,4 L58,4 L50,84 C50,86 48,88 46,88 L16,88 C14,88 12,86 12,84 Z", color)]
    p.append(path("M9,38 L53,38", acento, 6))
    return "".join(p)


def espalda(color=TINTA, acento=DORADO, manos=True):
    """Torso de espaldas, con o sin manos de masaje. Caja local: 0,0 -> 110,104."""
    p = [circulo(55, 18, 16, color)]
    p.append(path("M18,104 C18,66 34,44 55,44 C76,44 92,66 92,104", color))
    if manos:
        p.append(path("M34,74 C34,62 46,60 50,70", acento, 5))
        p.append(path("M76,74 C76,62 64,60 60,70", acento, 5))
    return "".join(p)


def silla(color=TINTA):
    """Silla / persona sentada de perfil. Caja local: 0,0 -> 96,104."""
    p = [circulo(30, 16, 14, color)]
    p.append(path("M14,104 L14,56 C14,46 22,38 32,38 L54,38 L54,66 L86,66", color))
    p.append(linea(86, 66, 86, 104, color))
    return "".join(p)


def check_circulo(color=DORADO, r=32):
    return circulo(r, r, r - 3, color) + path(
        "M%g,%g L%g,%g L%g,%g" % (r * 0.52, r, r * 0.88, r * 1.36, r * 1.5, r * 0.62), color)


def equis_circulo(color=TINTA, r=32):
    d = r * 0.42
    return circulo(r, r, r - 3, color) + path(
        "M%g,%g L%g,%g M%g,%g L%g,%g"
        % (r - d, r - d, r + d, r + d, r + d, r - d, r - d, r + d), color)


def estrella_destello(color=DORADO, escala=1.0, destellos=True):
    p = [path("M48,4 L60,36 L94,38 L67,59 L77,92 L48,72 L19,92 L29,59 L2,38 L36,36 Z", color)]
    if destellos:
        p.append(linea(108, 12, 122, 12, color, 5))
        p.append(linea(115, 5, 115, 19, color, 5))
        p.append(linea(-24, 62, -12, 62, color, 5))
        p.append(linea(-18, 56, -18, 68, color, 5))
    return g("".join(p), 0, 0, escala)


# --------------------------------------------------------------------------
# marcas de los discos (van dentro del circulo de cada fila)
# --------------------------------------------------------------------------

MARCAS = {
    # casita
    "casa": '<path d="M5,20 L20,6 L35,20" stroke="%(c)s" stroke-width="3.4"/>'
            '<path d="M9.5,18 L9.5,33 L30.5,33 L30.5,18" stroke="%(c)s" stroke-width="3.4"/>',
    # destello de cuatro puntas
    "salon": '<path d="M20,4 C21.5,14 26,18.5 36,20 C26,21.5 21.5,26 20,36 '
             'C18.5,26 14,21.5 4,20 C14,18.5 18.5,14 20,4 Z" fill="%(c)s" stroke="none"/>',
    # rombo
    "dato": '<path d="M20,7 L33,20 L20,33 L7,20 Z" fill="%(c)s" stroke="none"/>',
}


def marca(nombre, color):
    """Devuelve el simbolo del disco como SVG independiente de la fuente."""
    if nombre not in MARCAS:
        raise KeyError("marca desconocida: %s" % nombre)
    return (
        '<svg class="disco-marca" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
        % (MARCAS[nombre] % {"c": color})
    )


# --------------------------------------------------------------------------
# iconos compuestos
# --------------------------------------------------------------------------

ICONOS = {}


def _reg(nombre):
    def deco(fn):
        ICONOS[nombre] = fn
        return fn
    return deco


# ------------------------------------------------------------ 01 y 08 · unas

@_reg("calendario_marca")
def _calendario_marca():
    return g(calendario("21", TINTA, DORADO), 76, 48, 1.15)


@_reg("una_retiro_pro")
def _una_retiro_pro():
    return g(una(TINTA, DORADO, cuticula=DORADO), 62, 38, 1.0) + g(lima(), 122, 108, 0.9)


@_reg("aceite_cuticula")
def _aceite_cuticula():
    return (g(frasco("", TINTA, pincel=True), 52, 76, 0.76) +
            g(gota(DORADO, 0.62), 132, 74) + g(gota(DORADO, 0.44), 168, 112))


@_reg("una_cuticula")
def _una_cuticula():
    return g(una(TINTA, TINTA, cuticula=DORADO), 88, 32, 1.0)


@_reg("una_tiron")
def _una_tiron():
    return (g(una(TINTA, DORADO), 82, 38, 1.0) +
            flecha(150, 116, 206, 62, TINTA, 6) + tachar(TINTA, 46, 30, 182, 152))


@_reg("una_lima")
def _una_lima():
    return g(una(TINTA, DORADO), 56, 38, 1.0) + g(lima(), 116, 88, 1.05)


@_reg("crema_manos")
def _crema_manos():
    return g(tubo("", TINTA), 34, 40, 0.86) + g(mano_unas(TINTA, TINTA, esmalte=False), 106, 50, 0.86)


@_reg("spa_manos")
def _spa_manos():
    return (g(mano_unas(TINTA, DORADO), 52, 46, 0.95) +
            g(gota(DORADO, 0.5), 172, 32) + g(gota(DORADO, 0.36), 198, 84))


@_reg("calendario_relleno")
def _calendario_relleno():
    return g(calendario("3", TINTA, DORADO), 40, 48, 1.05) + g(una(TINTA, DORADO), 152, 44, 0.86)


@_reg("una_rebalance")
def _una_rebalance():
    return g(una(TINTA, DORADO, larga=True), 60, 40, 0.95) + g(check_circulo(DORADO, 26), 146, 96)


@_reg("una_golpe")
def _una_golpe():
    return (g(una(TINTA, DORADO), 82, 38, 1.0) +
            linea(150, 52, 194, 34, TINTA, 5) + linea(154, 76, 200, 74, TINTA, 5) +
            tachar(TINTA, 46, 30, 182, 152))


@_reg("una_repara")
def _una_repara():
    return g(una(TINTA, DORADO), 56, 38, 1.0) + g(check_circulo(DORADO, 28), 132, 66)


@_reg("una_levante")
def _una_levante():
    return g(una(TINTA, DORADO), 96, 38, 1.0) + g(bocadillo("!", 62, 52, DORADO, 34, DORADO, "der"), 18, 26)


@_reg("una_revision")
def _una_revision():
    return (g(una(TINTA, TINTA, cuticula=DORADO), 52, 32, 1.0) +
            circulo(156, 74, 30, TINTA) + linea(178, 96, 202, 122, TINTA, 7))


@_reg("una_descanso")
def _una_descanso():
    return g(calendario("", TINTA), 40, 50, 1.05) + g(mano_unas(TINTA, TINTA, esmalte=False), 130, 52, 0.86)


@_reg("una_natural")
def _una_natural():
    return g(mano_unas(TINTA, DORADO, esmalte=False), 58, 44, 1.05) + g(estrella_destello(DORADO, 0.34), 172, 30)


# ------------------------------------------------------------ 02 y 07 · cabello

@_reg("agua_caliente")
def _agua_caliente():
    return g(secador(TINTA, DORADO), 62, 46, 0.9) + tachar(TINTA, 48, 26, 196, 150)


@_reg("agua_tibia")
def _agua_tibia():
    return g(gota(DORADO, 0.9), 56, 50) + g(gota(TINTA, 0.7), 118, 66) + g(gota(TINTA, 0.55), 168, 88)


@_reg("enjuague_frio")
def _enjuague_frio():
    return (g(mechon(TINTA), 52, 34, 0.95) +
            g(gota(DORADO, 0.66), 144, 44) + g(gota(DORADO, 0.5), 182, 92))


@_reg("shampoo_duda")
def _shampoo_duda():
    return g(frasco("", TINTA), 54, 40, 0.9) + g(bocadillo("?", 62, 54, TINTA, 36, TINTA, "izq"), 134, 32)


@_reg("shampoo_indicado")
def _shampoo_indicado():
    return g(frasco("", TINTA), 52, 40, 0.9) + g(check_circulo(DORADO, 28), 138, 62)


@_reg("plancha_calor")
def _plancha_calor():
    return (g(plancha(TINTA), 68, 62, 1.0) +
            linea(52, 40, 52, 22, DORADO, 5) + linea(96, 36, 96, 14, DORADO, 5) +
            linea(140, 40, 140, 22, DORADO, 5) + tachar(TINTA, 48, 26, 196, 150))


@_reg("protector_termico")
def _protector_termico():
    return (g(frasco("", TINTA), 42, 40, 0.9) + g(mechon(TINTA), 128, 36, 0.86) +
            g(check_circulo(DORADO, 24), 182, 116))


@_reg("raiz_avisa")
def _raiz_avisa():
    return g(persona(TINTA, DORADO), 76, 50, 1.35) + g(bocadillo("!", 56, 50, DORADO, 34, DORADO, "der"), 6, 26)


@_reg("calendario_retoque")
def _calendario_retoque():
    return g(calendario("4", TINTA, DORADO), 76, 48, 1.15)


@_reg("calendario_despunte")
def _calendario_despunte():
    return g(calendario("12", TINTA, DORADO), 40, 48, 1.05) + g(tijera(TINTA), 152, 40, 0.72)


@_reg("tijera_despunte")
def _tijera_despunte():
    return g(mechon(TINTA), 52, 34, 0.95) + g(tijera(TINTA), 136, 36, 0.82)


@_reg("punta_abierta")
def _punta_abierta():
    return g(mechon(TINTA, quebrado=True), 84, 34, 1.05)


@_reg("toalla_frota")
def _toalla_frota():
    return (g(toalla(TINTA), 72, 62, 1.0) + flecha(62, 40, 176, 40, TINTA, 5) +
            flecha(176, 152, 62, 152, TINTA, 5) + tachar(TINTA, 48, 26, 196, 150))


@_reg("toalla_presiona")
def _toalla_presiona():
    return g(toalla(TINTA, vapor=DORADO), 68, 76, 1.0) + g(check_circulo(DORADO, 22), 186, 128)


@_reg("mascarilla_semanal")
def _mascarilla_semanal():
    return (g(frasco("", TINTA), 44, 40, 0.9) + g(mechon(TINTA), 128, 36, 0.86) +
            g(gota(DORADO, 0.4), 184, 42))


@_reg("masaje_capilar")
def _masaje_capilar():
    return (g(persona(TINTA, TINTA), 88, 52, 1.3) +
            path("M64,76 C64,62 80,60 86,72", DORADO, 5) +
            path("M176,76 C176,62 160,60 154,72", DORADO, 5))


@_reg("peine_arriba")
def _peine_arriba():
    return (g(mechon(TINTA), 52, 34, 0.95) + g(peine(TINTA), 114, 40, 0.82) +
            flecha(158, 62, 158, 128, TINTA, 5) + tachar(TINTA, 48, 26, 196, 150))


@_reg("peine_abajo")
def _peine_abajo():
    return (g(mechon(TINTA), 52, 34, 0.95) + g(peine(TINTA), 114, 96, 0.82) +
            flecha(158, 128, 158, 66, DORADO, 5))


# ------------------------------------------------------------ 03 y 04 · barberia

@_reg("shampoo_pelo_barba")
def _shampoo_pelo_barba():
    return (g(frasco("", TINTA), 38, 40, 0.9) + g(rostro(TINTA, barba=TINTA), 126, 36, 0.86) +
            tachar(TINTA, 48, 26, 196, 150))


@_reg("shampoo_barba")
def _shampoo_barba():
    return g(frasco("", TINTA), 44, 40, 0.9) + g(rostro(TINTA, barba=DORADO), 130, 36, 0.86)


@_reg("toalla_caliente")
def _toalla_caliente():
    return g(toalla(TINTA, vapor=DORADO), 70, 78, 1.05)


@_reg("aceite_barba")
def _aceite_barba():
    return (g(frasco("", TINTA, pincel=True), 48, 78, 0.74) +
            g(gota(DORADO, 0.6), 124, 64) + g(gota(DORADO, 0.44), 164, 106))


@_reg("rostro_barba_ok")
def _rostro_barba_ok():
    return g(rostro(TINTA, barba=DORADO), 68, 36, 1.05) + g(check_circulo(DORADO, 24), 172, 116)


@_reg("barba_picazon")
def _barba_picazon():
    return (g(rostro(TINTA, barba=TINTA), 58, 36, 1.05) +
            linea(168, 54, 196, 44, TINTA, 5) + linea(170, 78, 200, 76, TINTA, 5) +
            linea(166, 102, 194, 110, TINTA, 5))


@_reg("peine_barba")
def _peine_barba():
    return (g(rostro(TINTA, barba=TINTA), 36, 36, 1.0) + g(peine(TINTA), 124, 60, 0.9) +
            flecha(172, 120, 172, 156, DORADO, 5, 10))


@_reg("navaja_perfila")
def _navaja_perfila():
    return g(rostro(TINTA, barba=DORADO), 30, 36, 1.0) + g(navaja(TINTA), 114, 78, 0.9)


@_reg("maquina_cuello")
def _maquina_cuello():
    return g(maquina(TINTA), 76, 48, 1.0) + tachar(TINTA, 48, 26, 196, 150)


@_reg("navaja_cuello")
def _navaja_cuello():
    return g(navaja(TINTA), 56, 64, 1.05) + g(check_circulo(DORADO, 24), 176, 114)


@_reg("calendario_agenda")
def _calendario_agenda():
    return g(calendario("3", TINTA, DORADO), 40, 48, 1.05) + g(check_circulo(DORADO, 26), 150, 74)


@_reg("maquina_fade")
def _maquina_fade():
    return g(maquina(TINTA), 32, 48, 0.95) + g(persona(TINTA, DORADO), 144, 52, 1.2)


@_reg("lavado_diario")
def _lavado_diario():
    return (g(frasco("", TINTA), 38, 40, 0.9) + g(calendario("7", TINTA, TINTA), 116, 48, 0.95) +
            tachar(TINTA, 48, 26, 196, 150))


@_reg("lavado_justo")
def _lavado_justo():
    return g(frasco("", TINTA), 44, 40, 0.9) + g(calendario("3", TINTA, DORADO), 122, 48, 0.95)


@_reg("secador_calor")
def _secador_calor():
    return g(secador(TINTA, TINTA), 44, 46, 0.95) + tachar(TINTA, 48, 26, 196, 150)


@_reg("secador_tibio")
def _secador_tibio():
    return g(secador(TINTA, DORADO), 40, 46, 0.95) + g(check_circulo(DORADO, 22), 186, 126)


@_reg("producto_exceso")
def _producto_exceso():
    return (g(frasco("", TINTA), 42, 40, 0.9) + circulo(158, 84, 34, TINTA) +
            tachar(TINTA, 48, 26, 196, 150))


@_reg("producto_justo")
def _producto_justo():
    return g(frasco("", TINTA), 50, 40, 0.9) + circulo(158, 90, 11, DORADO, 6, DORADO)


# ------------------------------------------------------------ 05 · pedicure

@_reg("una_pie_punta")
def _una_pie_punta():
    return g(pie(TINTA, TINTA, unas=True), 88, 34, 1.0) + tachar(TINTA, 52, 26, 190, 152)


@_reg("una_pie_recta")
def _una_pie_recta():
    return g(pie(TINTA, DORADO), 54, 34, 1.0) + g(lima(), 128, 96, 0.9)


@_reg("lima_seco")
def _lima_seco():
    return g(lima(), 62, 76, 1.2) + g(gota(TINTA, 0.5), 172, 40) + tachar(TINTA, 52, 26, 190, 152)


@_reg("pie_lima")
def _pie_lima():
    return g(pie(TINTA, DORADO), 42, 34, 1.0) + g(lima(), 116, 76, 1.0)


@_reg("crema_noche")
def _crema_noche():
    return g(tubo("", TINTA), 46, 40, 0.9) + g(pie(TINTA, TINTA, unas=False), 126, 36, 0.9)


@_reg("spa_pies")
def _spa_pies():
    return (g(pie(TINTA, DORADO), 50, 34, 1.0) +
            g(gota(DORADO, 0.52), 146, 44) + g(gota(DORADO, 0.4), 186, 92))


@_reg("pie_encerrado")
def _pie_encerrado():
    return (g(pie(TINTA, TINTA, unas=False), 88, 36, 1.0) + rect(60, 26, 124, 132, 16, TINTA, 6) +
            tachar(TINTA, 52, 26, 190, 152))


@_reg("pie_revision")
def _pie_revision():
    return (g(pie(TINTA, DORADO), 46, 34, 1.0) + circulo(158, 74, 30, TINTA) +
            linea(180, 96, 204, 122, TINTA, 7))


# ------------------------------------------------------------ 06 · cosmetologia

@_reg("sol_sin_proteccion")
def _sol_sin_proteccion():
    return (g(sol(TINTA, 22, 8), 88, 78) + g(piel(TINTA, TINTA, puntos=False), 142, 46, 0.72) +
            tachar(TINTA, 48, 26, 196, 150))


@_reg("protector_solar")
def _protector_solar():
    return g(tubo("SPF", TINTA, DORADO), 52, 40, 0.9) + g(sol(DORADO, 16, 8), 164, 68)


@_reg("piel_aprieta")
def _piel_aprieta():
    return g(piel(TINTA, TINTA), 72, 42, 1.0) + tachar(TINTA, 48, 26, 196, 150)


@_reg("piel_extraccion")
def _piel_extraccion():
    return (g(piel(TINTA, DORADO, puntos=False), 40, 42, 1.0) + circulo(164, 76, 28, TINTA) +
            linea(184, 96, 206, 120, TINTA, 7))


@_reg("desmaquilla")
def _desmaquilla():
    return g(frasco("", TINTA), 44, 40, 0.9) + g(rostro(TINTA), 126, 42, 0.92)


@_reg("rutina_piel")
def _rutina_piel():
    return (g(frasco("", TINTA), 28, 48, 0.7) + g(tubo("", TINTA), 104, 48, 0.7) +
            g(frasco("", DORADO), 166, 48, 0.7))


@_reg("calendario_mes")
def _calendario_mes():
    return g(calendario("30", TINTA, DORADO), 76, 48, 1.15)


@_reg("piel_limpia")
def _piel_limpia():
    return g(piel(TINTA, DORADO, puntos=False), 56, 42, 1.0) + g(estrella_destello(DORADO, 0.32), 166, 46)


# ------------------------------------------------------------ 09 · cejas y pestanas

@_reg("pinza_casa")
def _pinza_casa():
    return (g(ceja(TINTA), 60, 62, 1.0) +
            linea(190, 22, 174, 92, TINTA, 6) + linea(210, 24, 186, 92, TINTA, 6) +
            tachar(TINTA, 48, 26, 196, 150))


@_reg("ceja_perfilado")
def _ceja_perfilado():
    return g(ceja(TINTA, acento=DORADO), 66, 62, 1.05)


@_reg("pestana_frota")
def _pestana_frota():
    return (g(pestana(TINTA, TINTA), 64, 62, 1.0) + flecha(72, 132, 172, 132, TINTA, 5) +
            tachar(TINTA, 48, 26, 196, 150))


@_reg("pestana_relleno")
def _pestana_relleno():
    return g(pestana(TINTA, DORADO), 64, 60, 1.05) + g(check_circulo(DORADO, 22), 186, 128)


@_reg("maquina_vello")
def _maquina_vello():
    return g(maquina(TINTA), 76, 48, 1.0) + tachar(TINTA, 48, 26, 196, 150)


@_reg("cera_profesional")
def _cera_profesional():
    return (g(frasco("", TINTA), 44, 40, 0.9) + g(lima(), 116, 84, 0.95) +
            g(check_circulo(DORADO, 22), 190, 122))


@_reg("sol_despues")
def _sol_despues():
    return (g(sol(TINTA, 22, 8), 92, 72) + g(reloj(TINTA), 144, 84, 0.9) +
            tachar(TINTA, 48, 26, 196, 150))


@_reg("calmante")
def _calmante():
    return (g(tubo("", TINTA), 52, 40, 0.9) + g(gota(DORADO, 0.6), 130, 54) +
            g(gota(DORADO, 0.42), 174, 100))


# ------------------------------------------------------------ 10 · masajes

@_reg("dos_vasos")
def _dos_vasos():
    return g(vaso_agua(TINTA, DORADO), 58, 46, 1.0) + g(vaso_agua(TINTA, DORADO), 136, 46, 1.0)


@_reg("masaje_cierre")
def _masaje_cierre():
    return g(espalda(TINTA, DORADO), 64, 38, 1.05)


@_reg("calor_guatero")
def _calor_guatero():
    return g(toalla(TINTA, vapor=DORADO), 62, 78, 1.0) + g(reloj(TINTA), 170, 96, 0.7)


@_reg("calor_indicado")
def _calor_indicado():
    return g(espalda(TINTA, DORADO), 42, 38, 1.0) + g(toalla(TINTA, vapor=DORADO), 144, 84, 0.76)


@_reg("sentado_hora")
def _sentado_hora():
    return g(silla(TINTA), 44, 40, 1.0) + g(reloj(TINTA), 150, 60, 0.95)


@_reg("masaje_localizado")
def _masaje_localizado():
    return g(espalda(TINTA, DORADO), 46, 38, 1.0) + g(check_circulo(DORADO, 24), 174, 108)


@_reg("dolor_espera")
def _dolor_espera():
    return (g(espalda(TINTA, TINTA, manos=False), 42, 38, 1.0) +
            g(bocadillo("!", 60, 52, TINTA, 34, TINTA, "izq"), 154, 34))


@_reg("calendario_mantencion")
def _calendario_mantencion():
    return g(calendario("", TINTA), 40, 48, 1.05) + g(espalda(TINTA, DORADO), 134, 44, 0.86)


# ------------------------------------------------------------ cierres

@_reg("cierre_calendario")
def _cierre_calendario():
    return g(calendario("", TINTA, DORADO), 76, 48, 1.15) + g(estrella_destello(DORADO, 0.3), 176, 36)


@_reg("cierre_sello")
def _cierre_sello():
    return g(estrella_destello(DORADO, 0.9), 66, 40)


# --------------------------------------------------------------------------

def svg(nombre):
    """Devuelve el SVG completo de un icono."""
    if nombre not in ICONOS:
        raise KeyError("icono desconocido: %s" % nombre)
    return (
        '<svg class="ilu" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
        % (W, H, ICONOS[nombre]())
    )


def disponibles():
    return sorted(ICONOS)


if __name__ == "__main__":
    print("%d iconos: %s" % (len(ICONOS), ", ".join(disponibles())))
