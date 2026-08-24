# -*- coding: utf-8 -*-
"""
Generador del HTML/CSS de las laminas de La Fiore.

Cada lamina es un documento HTML autocontenido de 1080 x 1350 px:
fuentes y sello van embebidos en base64 para que el render sea
reproducible y no dependa de rutas relativas.

Identidad tomada de los originales de la marca (carpeta insumos/):

  Tipografias corporativas (tipografias_La_Fiore.pdf)
    - Lady Ice Bold                          -> display, la del logotipo
    - Berthold Akzidenz Grotesk Medium Cond. -> todo lo demas

  Paleta y materiales (LA FIORE_Interiorismo V2.pdf, pagina 10)
    metal negro y dorado / ladrillos / cuero / madera
    negro #15181A · hueso #EDE9D1 · dorado metalico · cuero #6E432A · blanco

El dorado del interiorismo es metalico con gradiente: sobre negro se usa su
tono claro (#E1C58F) y sobre hueso el dorado impreso del vinilo de acceso
(#90651F), que es el mismo color con contraste suficiente sobre claro.
"""

import base64
import os
import re

import iconos

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
FUENTES = os.path.join(ASSETS, "fonts")

ANCHO, ALTO = 1080, 1350
ALTO_HISTORIA = 1920          # las historias son 9:16

# ---- identidad -----------------------------------------------------------
NEGRO = "#15181A"             # negro corporativo
DORADO = "#90651F"            # dorado sobre fondo claro
DORADO_LUZ = "#E1C58F"        # dorado metalico sobre fondo negro
CUERO = "#6E432A"             # cafe cuero
HUESO = "#EDE9D1"             # crema corporativo, fondo de interiores
TINTA = "#15181A"
GRIS = "#726E62"              # datos secundarios sobre hueso
HUMO = "#C6C2B6"              # texto secundario sobre negro

ANO = "2026"
HANDLE = "@la_fiore.cl"
MARCA = "LA FIORE"
BAJADA = "Studio and Barber Shop"
CIUDAD = "Talagante · Chile"


# --------------------------------------------------------------------------
# assets embebidos
# --------------------------------------------------------------------------

def _b64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


_MIME = {".otf": "font/otf", ".ttf": "font/ttf", ".woff2": "font/woff2"}


def _fuente(archivo):
    tipo = _MIME[os.path.splitext(archivo)[1].lower()]
    return "data:%s;base64,%s" % (tipo, _b64(os.path.join(FUENTES, archivo)))


def _imagen(archivo):
    return "data:image/png;base64," + _b64(os.path.join(ASSETS, archivo))


_CACHE = {}


# Pares tipograficos. El sello lleva Lady Ice y ese papel no se toca; lo que
# cambia es la voz editorial de las laminas. Se elige con LAFIORE_PAR.
#
#   display  -> titulares, el plazo del cierre y EL DATO
#   texto    -> todo lo que se lee de corrido
#   caja     -> "uppercase" o "none" para los titulares
#   escala   -> ajuste fino del cuerpo del display, segun la altura de x
PAR = os.environ.get("LAFIORE_PAR", "playfair").strip().lower()

PARES = {
    # el kit de la marca, tal cual el manual
    "ladyice": {"display": "LadyIce-Bold.ttf",
                "texto": "AkzidenzGrotesk-MedCond.otf",
                "caja": "uppercase", "escala": 1.00},
    # serif editorial + sans limpia: el registro de revista de belleza
    "playfair": {"display": "PlayfairDisplay-Bold.woff2",
                 "texto": "Karla-Regular.woff2",
                 "caja": "none", "escala": 0.86},
    "instrument": {"display": "InstrumentSerif-Regular.woff2",
                   "texto": "InstrumentSans-Regular.woff2",
                   "caja": "none", "escala": 1.04},
    "fraunces": {"display": "Fraunces-Bold.woff2",
                 "texto": "Figtree-Regular.woff2",
                 "caja": "none", "escala": 0.90},
    "bodoni": {"display": "BodoniModa-Bold.woff2",
               "texto": "Jost-Regular.woff2",
               "caja": "none", "escala": 0.94},
}


def par():
    if PAR not in PARES:
        raise SystemExit("LAFIORE_PAR debe ser: %s" % ", ".join(sorted(PARES)))
    return PARES[PAR]


def assets():
    if not _CACHE:
        p = par()
        _CACHE.update({
            "marca": _fuente("LadyIce-Bold.ttf"),
            "display": _fuente(p["display"]),
            "texto": _fuente(p["texto"]),
            "logo_dorado": _imagen("logo_dorado.png"),
            "logo_blanco": _imagen("logo_blanco.png"),
        })
    return _CACHE


# --------------------------------------------------------------------------
# marcado del copy
# --------------------------------------------------------------------------

def _escapar(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def marcar(texto, simple="em", doble="b"):
    """Convierte **negrita** y *resalte* en etiquetas HTML."""
    t = _escapar(texto)
    t = re.sub(r"\*\*(.+?)\*\*", r"<%s>\1</%s>" % (doble, doble), t)
    t = re.sub(r"\*(.+?)\*", r"<%s>\1</%s>" % (simple, simple), t)
    return t


def sin_marcas(texto):
    return texto.replace("*", "")


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------

GRANO = (
    "data:image/svg+xml;utf8,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E"
    "%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' "
    "numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E"
    "%3Crect width='300' height='300' filter='url(%23g)'/%3E%3C/svg%3E"
)


def css():
    a = assets()
    p = par()
    e = p["escala"]
    return """
@font-face { font-family:'Marca'; src:url('%(marca)s') format('truetype'); font-weight:700; }
@font-face { font-family:'Display'; src:url('%(display)s'); font-weight:700; }
@font-face { font-family:'Texto'; src:url('%(texto)s'); font-weight:500; }

/* Playfair y Bodoni traen cifras antiguas por defecto: en un titular
   como 'Cada 3 semanas' el numero debe apoyarse en la linea base. */
.portada-titulo, .titulo, .cierre-plazo, .dato-lineas, .banda-cta .txt, .folio {
  font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1, 'onum' 0;
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
html, body { width:%(ancho)dpx; height:%(alto)dpx; }
body { -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision;
       font-family:Texto; font-weight:500; }

.lamina {
  position:relative; width:%(ancho)dpx; height:%(alto)dpx; overflow:hidden;
  display:flex; flex-direction:column;
}
.grano {
  position:absolute; inset:0; z-index:5; pointer-events:none;
  background-image:url("%(grano)s"); background-size:300px 300px;
  opacity:.15; mix-blend-mode:multiply;
}
.capa { position:relative; z-index:1; display:flex; flex-direction:column; height:100%%; }

/* ------------------------------------------------------------ PORTADA */
.portada { background:%(negro)s; padding:72px 66px; }
.kicker {
  font-family:Texto; font-size:30px; letter-spacing:.30em;
  color:%(dorado_luz)s; text-transform:uppercase;
}
.regla-dorada { width:110px; height:4px; background:%(dorado_luz)s; margin-top:26px; }
.portada-centro { flex:1; display:flex; flex-direction:column; justify-content:flex-end;
                  padding-bottom:96px; }
.portada-titulo {
  font-family:Display; font-weight:700; font-size:%(t_portada)dpx; line-height:1.06;
  letter-spacing:.01em; color:#FFFFFF; text-transform:%(caja)s;
}
.portada-titulo em { font-style:normal; color:%(dorado_luz)s; }
.portada-sub {
  font-family:Texto; font-size:42px; line-height:1.36;
  color:%(humo)s; margin-top:40px; max-width:900px;
}
.portada-sub b { color:%(dorado_luz)s; font-weight:500; }
.portada-pie { display:flex; align-items:flex-end; justify-content:space-between; }
.desliza { display:flex; align-items:center; gap:22px; }
.desliza .circulo {
  width:62px; height:62px; border-radius:50%%; background:%(dorado_luz)s;
  display:flex; align-items:center; justify-content:center;
  color:%(negro)s; font-family:Texto; font-size:34px; line-height:1;
}
.desliza .txt {
  font-family:Texto; font-size:30px; letter-spacing:.26em;
  color:%(dorado_luz)s; text-transform:uppercase;
}
.logo-portada { height:190px; width:auto; display:block; }
/* en historias, Instagram superpone su interfaz arriba y abajo */
.lamina.historia .portada { padding:250px 66px 280px; }
.lamina.historia .portada-centro { justify-content:center; padding-bottom:0; }

/* ----------------------------------------------------------- INTERIOR */
.interior { background:%(hueso)s; padding:50px 54px; color:%(tinta)s; }

.barra-sup {
  display:flex; justify-content:space-between; align-items:baseline;
  font-family:Texto; font-size:24px; letter-spacing:.20em;
  color:%(gris)s; text-transform:uppercase;
}
.masthead { position:relative; margin-top:18px; text-align:center; }
.masthead .marca {
  font-family:'Marca'; font-weight:700; font-size:62px; letter-spacing:.14em;
  line-height:1.06; color:%(tinta)s;
}
.masthead .bajada {
  font-family:Texto; font-size:23px; letter-spacing:.32em;
  color:%(cuero)s; margin-top:10px; text-transform:uppercase;
}
.folio {
  position:absolute; left:0; top:50%%; transform:translateY(-50%%);
  width:58px; height:58px; background:%(dorado)s; color:#FFFFFF;
  display:flex; align-items:center; justify-content:center;
  font-family:'Marca'; font-weight:700; font-size:32px; line-height:1;
}
.doble-regla { margin-top:18px; }
.doble-regla i { display:block; background:%(tinta)s; }
.doble-regla i:first-child { height:3px; }
.doble-regla i:last-child { height:2px; margin-top:6px; }

.antetitulo {
  font-family:Texto; font-size:36px; letter-spacing:.20em;
  color:%(cuero)s; margin-top:24px; line-height:1; text-transform:uppercase;
}
.titulo {
  font-family:Display; font-weight:700; font-size:%(t_titulo)dpx; line-height:1.02;
  letter-spacing:.01em; color:%(tinta)s; margin-top:12px; text-transform:%(caja)s;
}
.titulo em { font-style:normal; color:%(dorado)s; }

.filas { flex:1; display:flex; flex-direction:column; justify-content:space-between; margin-top:26px; }
.fila { display:flex; align-items:center; gap:22px; padding:26px 0; }
.fila + .fila { border-top:2px solid rgba(21,24,26,.18); }
.disco {
  flex:0 0 58px; width:58px; height:58px; border-radius:50%%; align-self:flex-start;
  margin-top:2px; display:flex; align-items:center; justify-content:center;
}
.disco-marca { width:32px; height:32px; display:block; }
.disco.casa { background:%(tinta)s; }
.disco.salon { background:%(dorado)s; }
.disco.dato { border:5px solid %(dorado)s; }
/* la etiqueta va encima del texto: asi el texto se lleva todo el ancho */
.bloque { flex:1 1 auto; min-width:0; }
.etiqueta {
  font-family:Texto; font-size:28px; line-height:1;
  letter-spacing:.22em; text-transform:uppercase;
}
.etiqueta.casa { color:%(gris)s; }
.etiqueta.salon { color:%(dorado)s; }
.etiqueta.dato { font-size:28px; color:%(dorado)s; letter-spacing:.22em; }
.fila.dato-fila { display:flex; }
.cuerpo {
  font-family:Texto; font-size:51px; line-height:1.18; color:#2B2E30; margin-top:12px;
}
.dato-lineas {
  margin-top:14px; font-family:Display; font-weight:700; font-size:%(t_dato)dpx;
  line-height:1.16; text-transform:%(caja)s; letter-spacing:.01em;
}
.dato-lineas .a { color:%(tinta)s; }
.dato-lineas .b { color:%(dorado)s; }
.ilu-col { flex:0 0 178px; height:150px; display:flex; align-items:center; justify-content:center; }
.ilu { width:100%%; height:100%%; display:block; }

/* ------------------------------------------------------------- CIERRE */
.cierre { background:%(negro)s; padding:72px 66px; color:#FFFFFF; }
.cierre-centro { flex:1; display:flex; flex-direction:column; justify-content:flex-end;
                 padding-bottom:52px; }
.cierre-plazo {
  font-family:Display; font-weight:700; font-size:%(t_plazo)dpx; line-height:1.06;
  letter-spacing:.01em; color:%(dorado_luz)s; text-transform:%(caja)s;
}
.cierre-detalle {
  font-family:Texto; font-size:42px; line-height:1.36;
  color:%(humo)s; margin-top:34px; max-width:900px;
}
.cierre-detalle b { color:#FFFFFF; font-weight:500; }
.banda-cta {
  border-top:3px solid %(dorado_luz)s; margin-top:38px; padding-top:30px;
  display:flex; align-items:flex-end; justify-content:space-between; gap:40px;
}
.banda-cta .txt {
  font-family:Display; font-weight:700; font-size:%(t_cta)dpx; line-height:1.10;
  letter-spacing:.02em; color:#FFFFFF; text-transform:%(caja)s;
}
.banda-cta .sub {
  font-family:Texto; font-size:32px; line-height:1.32;
  color:%(dorado_luz)s; margin-top:14px; text-transform:none; letter-spacing:.01em;
}
.banda-cta .logo-cierre { height:150px; width:auto; display:block; flex:0 0 auto; }

/* ---------------------------------------------------------------- PIE */
.pie { margin-top:24px; border-top:3px solid %(tinta)s; padding-top:20px;
       display:flex; align-items:center; justify-content:space-between; }
.pie-izq { display:flex; align-items:center; gap:20px; }
.logo-pie { height:104px; width:auto; display:block; }
.pie-txt { font-family:Texto; font-size:26px; letter-spacing:.16em;
           line-height:1.5; color:%(tinta)s; text-transform:uppercase; }
.pie-txt .handle { text-transform:none; letter-spacing:.07em; color:%(cuero)s; }
.pie-der { font-family:Texto; font-size:26px; letter-spacing:.16em;
           color:%(tinta)s; text-transform:uppercase; text-align:right; }
""" % {
        "marca": a["marca"], "display": a["display"], "texto": a["texto"],
        "caja": p["caja"], "t_portada": round(96 * e), "t_titulo": round(88 * e),
        "t_dato": round(58 * e), "t_plazo": round(124 * e), "t_cta": round(50 * e),
        "grano": GRANO, "ancho": ANCHO, "alto": ALTO,
        "negro": NEGRO, "dorado": DORADO, "dorado_luz": DORADO_LUZ,
        "cuero": CUERO, "hueso": HUESO, "tinta": TINTA, "gris": GRIS, "humo": HUMO,
    }


# --------------------------------------------------------------------------
# bloques
# --------------------------------------------------------------------------

def _documento(clase, contenido, alto=ALTO):
    extra = ""
    if alto != ALTO:
        extra = "<style>html,body,.lamina{height:%dpx;}</style>" % alto
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        "<style>%s</style>%s</head><body>"
        "<div class='lamina %s'><div class='capa'>%s</div><div class='grano'></div></div>"
        "</body></html>" % (css(), extra, clase, contenido)
    )


def _cabecera(s, pagina):
    return (
        "<div class='barra-sup'><span>%s</span>"
        "<span>Cuidado en casa</span><span>N.&deg; %s · %s</span></div>"
        "<div class='masthead'><div class='folio'>%d</div>"
        "<div class='marca'>%s</div>"
        "<div class='bajada'>%s</div></div>"
        "<div class='doble-regla'><i></i><i></i></div>"
        % (_escapar(s["seccion"]), s["num"], ANO, pagina, MARCA, BAJADA)
    )


def _pie(pagina, derecha=None):
    a = assets()
    der = derecha if derecha is not None else "Lámina %d de 6" % pagina
    return (
        "<div class='pie'><div class='pie-izq'>"
        "<img class='logo-pie' src='%s' alt=''>"
        "<div class='pie-txt'>La Fiore /<br><span class='handle'>%s</span></div>"
        "</div><div class='pie-der'>%s</div></div>"
        % (a["logo_dorado"], HANDLE, der)
    )


def _fila(tipo, etiqueta, simbolo, texto, icono):
    return (
        "<div class='fila'><div class='disco %s'>%s</div>"
        "<div class='bloque'><div class='etiqueta %s'>%s</div>"
        "<div class='cuerpo'>%s</div></div>"
        "<div class='ilu-col'>%s</div></div>"
        % (tipo, simbolo, tipo, etiqueta, _escapar(texto), iconos.svg(icono))
    )


def _fila_dato(a_txt, b_txt):
    return (
        "<div class='fila dato-fila'><div class='disco dato'>%s</div>" % iconos.marca("dato", DORADO)
        + "<div class='bloque'><div class='etiqueta dato'>El dato</div>"
          "<div class='dato-lineas'><div class='a'>%s</div><div class='b'>%s</div></div></div></div>"
          % (_escapar(a_txt), _escapar(b_txt))
    )


# --------------------------------------------------------------------------
# laminas
# --------------------------------------------------------------------------

def _cuerpo_portada(s, cta="Desliza"):
    a = assets()
    return (
        "<div><div class='kicker'>La Fiore · %s</div>"
        "<div class='regla-dorada'></div></div>"
        "<div class='portada-centro'>"
        "<h1 class='portada-titulo'>%s</h1>"
        "<p class='portada-sub'>%s</p></div>"
        "<div class='portada-pie'>"
        "<div class='desliza'><div class='circulo'>&#8594;</div><div class='txt'>%s</div></div>"
        "<img class='logo-portada' src='%s' alt=''></div>"
        % (_escapar(s["seccion"]), marcar(s["portada"]["titulo"]),
           marcar(s["portada"]["sub"]), _escapar(cta), a["logo_blanco"])
    )


def portada(s):
    return _documento("portada", _cuerpo_portada(s))


def historia(s):
    """Misma portada en 1080x1920 para publicar como historia."""
    return _documento("portada historia", _cuerpo_portada(s, "En el perfil"), ALTO_HISTORIA)


def interior(s, indice):
    """indice 0..3 -> laminas 2..5."""
    p = s["paginas"][indice]
    n = indice + 2
    contenido = (
        _cabecera(s, n)
        + "<div class='antetitulo'>%s</div>" % _escapar(p["ante"])
        + "<h2 class='titulo'>%s</h2>" % marcar(p["titulo"])
        + "<div class='filas'>%s%s%s</div>" % (
            _fila("casa", "En casa", iconos.marca("casa", HUESO), p["casa"], p["casa_icono"]),
            _fila("salon", "En el salón", iconos.marca("salon", "#FFFFFF"),
                  p["salon"], p["salon_icono"]),
            _fila_dato(p["dato_a"], p["dato_b"]),
        )
        + _pie(n)
    )
    return _documento("interior", contenido)


def cierre(s):
    a = assets()
    c = s["cierre"]
    contenido = (
        "<div><div class='kicker'>%s</div><div class='regla-dorada'></div></div>"
        "<div class='cierre-centro'>"
        "<div class='cierre-plazo'>%s</div>"
        "<p class='cierre-detalle'>%s</p></div>"
        "<div class='banda-cta'>"
        "<div><div class='txt'>%s</div><div class='sub'>%s</div></div>"
        "<img class='logo-cierre' src='%s' alt=''></div>"
        % (_escapar(c["ante"]), _escapar(c["plazo"]), marcar(c["detalle"]),
           _escapar(c["cta"]), _escapar(c["sub"]), a["logo_blanco"])
    )
    return _documento("cierre", contenido)


def laminas(s):
    """Devuelve las 6 laminas del set como lista de (nombre, html)."""
    out = [("01_portada", portada(s))]
    for i in range(4):
        out.append(("%02d_pagina" % (i + 2), interior(s, i)))
    out.append(("06_cierre", cierre(s)))
    return out
