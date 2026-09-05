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


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
FUENTES = os.path.join(ASSETS, "fonts")

ANCHO, ALTO = 1080, 1350
ALTO_HISTORIA = 1920          # las historias son 9:16
ALTO_TIKTOK = 1920            # el carrusel de TikTok tambien

# TikTok dibuja su interfaz sobre la foto: abajo el nombre de la cuenta y el
# texto, a la derecha la columna de botones. Estas son las franjas que hay
# que dejar libres para que no tape nada.
SEGURO_ABAJO = 300
SEGURO_DERECHA = 150

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
/* Dos vestidos para la misma lamina, clara y oscura, que se alternan al
   deslizar. Antes las cuatro interiores eran identicas y el carrusel se
   leia como un formulario: mismo encabezado, misma grilla, mismo beige.
   Lo que cambia es el fondo y los colores del texto; la estructura es una
   sola, asi que el copy no se toca. */
.interior { padding:64px 70px 54px; }
.interior.clara {
  background:radial-gradient(120%% 80%% at 12%% 0%%, #F6F2DC 0%%, %(hueso)s 55%%, #E2DCC0 100%%);
  color:%(tinta)s;
}
.interior.oscura {
  background:radial-gradient(130%% 90%% at 82%% 6%%, #23282B 0%%, %(negro)s 62%%);
  color:#FFFFFF;
}

/* El sello ya se vio en la portada: aqui basta un riel fino. Antes ocupaba
   la quinta parte de cada lamina, repetido cinco veces. */
.riel { display:flex; align-items:baseline; gap:20px;
        font-family:Texto; font-size:25px; letter-spacing:.24em; text-transform:uppercase; }
.riel i { flex:1; height:1px; display:block; transform:translateY(-8px); }
.clara .riel { color:%(gris)s; }
.clara .riel .sec { color:%(cuero)s; }
.clara .riel i { background:rgba(21,24,26,.22); }
.oscura .riel { color:%(humo)s; }
.oscura .riel .sec { color:%(dorado_luz)s; }
.oscura .riel i { background:rgba(225,197,143,.30); }

.cab { display:flex; align-items:flex-start; gap:34px; margin-top:52px; }
.cifra { font-family:Display; font-weight:700; font-size:176px; line-height:.78;
         color:transparent; flex:0 0 auto;
         font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1, 'onum' 0; }
.clara .cifra { -webkit-text-stroke:3px rgba(144,101,31,.55); }
.oscura .cifra { -webkit-text-stroke:3px rgba(225,197,143,.45); }
.tit-col { flex:1; min-width:0; padding-top:10px; }

.antetitulo { font-family:Texto; font-size:32px; letter-spacing:.22em;
              line-height:1; text-transform:uppercase; }
.clara .antetitulo { color:%(cuero)s; }
.oscura .antetitulo { color:%(dorado_luz)s; }
.titulo { font-family:Display; font-weight:700; font-size:%(t_titulo)dpx; line-height:1.02;
          letter-spacing:.01em; margin-top:14px; text-transform:%(caja)s; }
.clara .titulo { color:%(tinta)s; }
.clara .titulo em { font-style:normal; color:%(dorado)s; }
.oscura .titulo { color:#FFFFFF; }
.oscura .titulo em { font-style:normal; color:%(dorado_luz)s; }

/* Sin columna de ilustracion: el texto se lleva el ancho completo y sube de
   51 a 54 px. Los dibujos genericos restaban mas de lo que sumaban. */
/* space-evenly y no center: con center todo el aire sobrante se iba a los
   extremos y en la version oscura quedaba un hueco evidente sobre el dato. */
.filas { flex:1; display:flex; flex-direction:column; justify-content:space-evenly; }
.fila { padding:32px 0; }
.clara .fila + .fila { border-top:1px solid rgba(21,24,26,.20); }
.oscura .fila + .fila { border-top:1px solid rgba(225,197,143,.24); }
.etiqueta { font-family:Texto; font-size:26px; letter-spacing:.26em; line-height:1;
            text-transform:uppercase; display:flex; align-items:center; gap:16px; }
.etiqueta i { flex:0 0 auto; width:26px; height:3px; background:currentColor; display:block; }
.clara .etiqueta.casa { color:%(gris)s; }
.clara .etiqueta.salon { color:%(dorado)s; }
.oscura .etiqueta.casa { color:%(humo)s; }
.oscura .etiqueta.salon { color:%(dorado_luz)s; }
.cuerpo { font-family:Texto; font-size:54px; line-height:1.16; margin-top:16px; }
.clara .cuerpo { color:#24272A; }
.oscura .cuerpo { color:#F2EFE6; }

/* El dato en cuero cafe: el tercer color de la identidad no aparecia nunca. */
.dato-bloque { margin-top:4px; }
.clara .dato-bloque { background:%(cuero)s; padding:34px 36px; }
.oscura .dato-bloque { border-left:5px solid %(dorado_luz)s; padding:6px 0 6px 34px; }
.dato-bloque .etiqueta { font-size:24px; letter-spacing:.28em; }
.clara .dato-bloque .etiqueta { color:rgba(246,242,220,.75); }
.oscura .dato-bloque .etiqueta { color:%(humo)s; }
.dato-lineas { margin-top:14px; font-family:Display; font-weight:700; font-size:%(t_dato)dpx;
               line-height:1.14; text-transform:%(caja)s; letter-spacing:.01em; }
.clara .dato-lineas .a { color:#F6F2DC; }
.clara .dato-lineas .b { color:%(dorado_luz)s; }
.oscura .dato-lineas .a { color:#FFFFFF; }
.oscura .dato-lineas .b { color:%(dorado_luz)s; }

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

/* ------------------------------------------------------- TIKTOK 9:16 */
/* Misma retorica, otro lienzo. Lo que cambia es el aire: hay 570 px mas de
   alto, y hay que respetar las franjas donde TikTok pone su interfaz. */
.lamina.tiktok.interior { padding:84px %(seg_der)dpx %(seg_abajo)dpx 54px; }
.lamina.tiktok.portada,
.lamina.tiktok.cierre { padding:110px %(seg_der)dpx %(seg_abajo)dpx 66px; }

.lamina.tiktok .riel { font-size:26px; }
/* En vertical quedan 876 px de ancho util: la cifra se va arriba en vez de
   comerle la mitad del ancho al titular. */
.lamina.tiktok .cab { flex-direction:column; gap:16px; margin-top:56px; }
.lamina.tiktok .cifra { font-size:150px; }
.lamina.tiktok .tit-col { padding-top:0; }
.lamina.tiktok .antetitulo { font-size:34px; }
.lamina.tiktok .titulo { font-size:84px; }
.lamina.tiktok .fila { padding:38px 0; }
.lamina.tiktok .etiqueta { font-size:28px; }
.lamina.tiktok .cuerpo { font-size:52px; }
.lamina.tiktok .dato-lineas { font-size:46px; }
.lamina.tiktok .clara .dato-bloque,
.lamina.tiktok.clara .dato-bloque { padding:30px; }

.lamina.tiktok .kicker { font-size:32px; }
.lamina.tiktok .portada-titulo { font-size:102px; }
.lamina.tiktok .portada-sub { font-size:44px; max-width:100%%; }
.lamina.tiktok .portada-centro { padding-bottom:70px; }
.lamina.tiktok .logo-portada { height:170px; }
.lamina.tiktok .desliza .txt { font-size:32px; }

.lamina.tiktok .cierre-plazo { font-size:118px; }
.lamina.tiktok .cierre-detalle { font-size:44px; max-width:100%%; }
.lamina.tiktok .cierre-centro { padding-bottom:40px; }
.lamina.tiktok .banda-cta .txt { font-size:54px; }
.lamina.tiktok .banda-cta .sub { font-size:34px; }
.lamina.tiktok .banda-cta .logo-cierre { height:140px; }

.lamina.tiktok .pie { margin-top:30px; padding-top:24px; }
.lamina.tiktok .logo-pie { height:112px; }
.lamina.tiktok .pie-txt, .lamina.tiktok .pie-der { font-size:28px; }

/* ---------------------------------------------------------------- PIE */
.pie { margin-top:34px; padding-top:22px;
       display:flex; align-items:center; justify-content:space-between; }
.clara .pie { border-top:2px solid %(tinta)s; }
.oscura .pie { border-top:2px solid rgba(225,197,143,.45); }
.pie-izq { display:flex; align-items:center; gap:22px; }
.logo-pie { height:86px; width:auto; display:block; }
.pie-txt { font-family:Texto; font-size:26px; letter-spacing:.10em; line-height:1.4; }
.clara .pie-txt { color:%(cuero)s; }
.oscura .pie-txt { color:%(dorado_luz)s; }
.pie-der { font-family:Texto; font-size:25px; letter-spacing:.18em;
           text-transform:uppercase; text-align:right; }
.clara .pie-der { color:%(gris)s; }
.oscura .pie-der { color:%(humo)s; }
""" % {
        "marca": a["marca"], "display": a["display"], "texto": a["texto"],
        "caja": p["caja"], "t_portada": round(96 * e), "t_titulo": round(94 * e),
        "t_dato": round(60 * e), "t_plazo": round(124 * e), "t_cta": round(50 * e),
        "grano": GRANO, "ancho": ANCHO, "alto": ALTO,
        "seg_abajo": SEGURO_ABAJO, "seg_der": SEGURO_DERECHA,
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


def _riel(s):
    """La franja de arriba. Reemplaza al masthead, que se repetia en las cinco
    laminas ocupando la quinta parte de cada una."""
    return (
        "<div class='riel'><span>%s</span><i></i>"
        "<span class='sec'>%s</span><i></i>"
        "<span>N.&deg; %s · %s</span></div>"
        % (MARCA, _escapar(s["seccion"]), s["num"], ANO)
    )


def _pie(pagina, oscura=False, derecha=None):
    a = assets()
    der = derecha if derecha is not None else "Lámina %d de 6" % pagina
    return (
        "<div class='pie'><div class='pie-izq'>"
        "<img class='logo-pie' src='%s' alt=''>"
        "<div class='pie-txt'>%s</div>"
        "</div><div class='pie-der'>%s</div></div>"
        % (a["logo_blanco"] if oscura else a["logo_dorado"], HANDLE, der)
    )


def _fila(tipo, etiqueta, texto):
    return (
        "<div class='fila'><div class='etiqueta %s'><i></i>%s</div>"
        "<div class='cuerpo'>%s</div></div>"
        % (tipo, _escapar(etiqueta), _escapar(texto))
    )


def _bloque_dato(a_txt, b_txt):
    return (
        "<div class='dato-bloque'><div class='etiqueta dato'>El dato</div>"
        "<div class='dato-lineas'><div class='a'>%s</div><div class='b'>%s</div></div></div>"
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
    """Misma portada en 1080x1920 para publicar como historia.

    La historia va al perfil, no al carrusel: por eso el llamado no es
    "desliza" sino la invitacion a ver el carrusel completo en el feed.
    """
    return _documento("portada historia",
                      _cuerpo_portada(s, "Míralo en el perfil"), ALTO_HISTORIA)


def interior(s, indice):
    """indice 0..3 -> laminas 2..5.

    Las pares van claras y las impares oscuras, para que el carrusel lata al
    deslizar en vez de mostrar cuatro fichas iguales.
    """
    p = s["paginas"][indice]
    n = indice + 2
    oscura = indice % 2 == 1
    contenido = (
        _riel(s)
        + "<div class='cab'><div class='cifra'>%02d</div><div class='tit-col'>"
          "<div class='antetitulo'>%s</div>"
          "<h2 class='titulo'>%s</h2></div></div>" % (
              indice + 1, _escapar(p["ante"]), marcar(p["titulo"]))
        + "<div class='filas'>%s%s</div>" % (
            _fila("casa", "En casa", p["casa"]),
            _fila("salon", "En el salón", p["salon"]),
        )
        + _bloque_dato(p["dato_a"], p["dato_b"])
        + _pie(n, oscura=oscura)
    )
    return _documento("interior " + ("oscura" if oscura else "clara"), contenido)


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


# --------------------------------------------------------------------------
# variante vertical para el carrusel de fotos de TikTok
# --------------------------------------------------------------------------

def _vertical(html):
    """Pasa una lamina al lienzo 9:16 anadiendole la clase 'tiktok'."""
    return html.replace("<div class='lamina ", "<div class='lamina tiktok ", 1)


def portada_tiktok(s):
    return _documento("portada tiktok", _cuerpo_portada(s, "Desliza"), ALTO_TIKTOK)


def interior_tiktok(s, indice):
    return _vertical(_documento_alto(interior(s, indice), ALTO_TIKTOK))


def cierre_tiktok(s):
    return _vertical(_documento_alto(cierre(s), ALTO_TIKTOK))


def _documento_alto(html, alto):
    """Cambia el alto del lienzo de un documento ya generado."""
    return html.replace(
        "</head>",
        "<style>html,body,.lamina{height:%dpx;}</style></head>" % alto, 1)


def laminas_tiktok(s):
    """Las mismas 6 laminas en 1080x1920, para el carrusel de TikTok."""
    out = [("01", portada_tiktok(s))]
    for i in range(4):
        out.append(("%02d" % (i + 2), interior_tiktok(s, i)))
    out.append(("06", cierre_tiktok(s)))
    return out
