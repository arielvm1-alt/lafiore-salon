# -*- coding: utf-8 -*-
"""
Arma la pagina de revision de los 10 carruseles.

    python plantilla/hoja_revision.py

Deja un HTML autocontenido en insumos/revision/cuidado-en-casa.html con las
60 laminas del feed, las 10 historias y los captions, en la identidad de
La Fiore. Las imagenes van reducidas y embebidas, asi que el archivo se abre
o se publica tal cual, sin depender de rutas.
"""

import base64
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "contenido"))

from PIL import Image

import plantilla
import sets as contenido
import captions as textos_caption

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "salida")
DESTINO = os.path.join(RAIZ, "insumos", "revision", "cuidado-en-casa.html")

LAMINAS = [
    ("01_portada", "Portada"),
    ("02_pagina", "Clave 1"),
    ("03_pagina", "Clave 2"),
    ("04_pagina", "Clave 3"),
    ("05_pagina", "Clave 4"),
    ("06_cierre", "Cierre"),
]

ANCHO_LAMINA = 560
ANCHO_HISTORIA = 300
CALIDAD = 80

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _jpg(ruta, ancho):
    im = Image.open(ruta).convert("RGB")
    alto = round(im.height * ancho / im.width)
    im = im.resize((ancho, alto), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=CALIDAD, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _b64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _limpio(t):
    return _esc(plantilla.sin_marcas(t))


def construir():
    lady = "data:font/ttf;base64," + _b64(
        os.path.join(RAIZ, "assets", "fonts", "LadyIce-Bold.ttf"))
    sello = "data:image/png;base64," + _b64(
        os.path.join(RAIZ, "assets", "logo_dorado.png"))

    indice, pliegos = [], []

    for s in contenido.SETS:
        carpeta = os.path.join(SALIDA, "set_%02d" % s["id"])
        tiras = []
        for archivo, rotulo in LAMINAS:
            uri = _jpg(os.path.join(carpeta, archivo + ".jpg"), ANCHO_LAMINA)
            tiras.append(
                "<figure class='lam'><img src='%s' alt='%s · %s' loading='lazy'>"
                "<figcaption>%s</figcaption></figure>"
                % (uri, _limpio(s["seccion"]), rotulo, rotulo))
        historia = _jpg(os.path.join(carpeta, "historia.jpg"), ANCHO_HISTORIA)

        indice.append(
            "<li><span class='ix-num'>%s</span>"
            "<span class='ix-tema'>%s</span>"
            "<span class='ix-sec'>%s</span>"
            "<span class='ix-plazo'>%s</span></li>"
            % (s["num"], _limpio(s["portada"]["titulo"]),
               _limpio(s["seccion"]), _limpio(s["cierre"]["plazo"])))

        pliegos.append(PLIEGO % {
            "num": s["num"],
            "seccion": _limpio(s["seccion"]),
            "titulo": _limpio(s["portada"]["titulo"]),
            "sub": _limpio(s["portada"]["sub"]),
            "plazo": _limpio(s["cierre"]["plazo"]),
            "tiras": "".join(tiras),
            "caption": _esc(textos_caption.caption(s["id"])),
            "historia": historia,
        })

    html = PAGINA % {"lady": lady, "sello": sello,
                     "indice": "".join(indice), "pliegos": "".join(pliegos)}

    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(html)
    print("Hoja de revisión: %s" % DESTINO)
    print("  %d carruseles · %d láminas de feed · %d historias · %.1f MB"
          % (len(contenido.SETS), len(contenido.SETS) * 6, len(contenido.SETS),
             os.path.getsize(DESTINO) / 1024 / 1024))
    return DESTINO


PLIEGO = """
<article class="pliego" id="post-%(num)s">
  <header class="pl-cab">
    <div class="pl-folio">%(num)s</div>
    <div class="pl-tit">
      <p class="pl-sec">%(seccion)s</p>
      <h2>%(titulo)s</h2>
      <p class="pl-sub">%(sub)s</p>
    </div>
    <div class="pl-plazo"><span>Vuelve</span><strong>%(plazo)s</strong></div>
  </header>
  <div class="tira" tabindex="0" aria-label="Las seis láminas del carrusel %(num)s">%(tiras)s</div>
  <div class="pl-pie">
    <section class="pl-caption">
      <h3>El texto de la publicación</h3>
      <pre>%(caption)s</pre>
    </section>
    <section class="pl-historia">
      <h3>La historia</h3>
      <img src="%(historia)s" alt="Historia del carrusel %(num)s" loading="lazy">
      <p>Se publica sola después del carrusel, en 1080×1920.</p>
    </section>
  </div>
</article>"""


PAGINA = """<title>Cuidado en Casa</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Karla:wght@400;600&display=swap">
<style>
/* Lady Ice es el logotipo: aqui solo aparece en el nombre de la cabecera. */
@font-face { font-family:'Lady Ice'; src:url('%(lady)s') format('truetype');
             font-weight:700; font-display:swap; }

/* Paleta del manual de La Fiore: metal negro y dorado, cuero, hueso. */
:root {
  --negro:#15181A; --hueso:#EDE9D1; --dorado:#90651F; --dorado-luz:#E1C58F;
  --cuero:#6E432A;

  --fondo:#EDE9D1; --panel:#F6F3E5; --hundido:#E0DAC1;
  --tinta:#15181A; --tenue:#6B6656; --regla:rgba(21,24,26,.20);
  --acento:#90651F; --sobre-acento:#FFFFFF; --realce:#6E432A;
  --sombra:0 1px 2px rgba(21,24,26,.07), 0 10px 30px rgba(21,24,26,.10);

  --serif:'Playfair Display', Georgia, 'Times New Roman', serif;
  --sans:'Karla', 'Helvetica Neue', Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --fondo:#15181A; --panel:#1F2326; --hundido:#0F1213;
    --tinta:#EDE9D1; --tenue:#9A9583; --regla:rgba(237,233,209,.18);
    --acento:#E1C58F; --sobre-acento:#15181A; --realce:#E1C58F;
    --sombra:0 1px 2px rgba(0,0,0,.55), 0 10px 30px rgba(0,0,0,.5);
  }
}
:root[data-theme="dark"] {
  --fondo:#15181A; --panel:#1F2326; --hundido:#0F1213;
  --tinta:#EDE9D1; --tenue:#9A9583; --regla:rgba(237,233,209,.18);
  --acento:#E1C58F; --sobre-acento:#15181A; --realce:#E1C58F;
  --sombra:0 1px 2px rgba(0,0,0,.55), 0 10px 30px rgba(0,0,0,.5);
}

*, *::before, *::after { box-sizing:border-box; }
body {
  margin:0; background:var(--fondo); color:var(--tinta);
  font-family:var(--sans); font-size:17px; line-height:1.65;
  -webkit-font-smoothing:antialiased;
}
.envoltura { max-width:1180px; margin:0 auto; padding:0 26px 96px; }
h1, h2, h3 { font-family:var(--serif); font-weight:700; margin:0;
             text-wrap:balance; font-variant-numeric:lining-nums; }
:focus-visible { outline:3px solid var(--acento); outline-offset:3px; }

/* ---------------------------------------------------------- cabecera */
.masthead { padding:54px 0 0; }
.barra { display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap;
         font-size:13px; letter-spacing:.22em; text-transform:uppercase; color:var(--tenue); }
.marca { text-align:center; margin-top:26px; }
.marca img { width:104px; height:104px; display:block; margin:0 auto 16px; }
.marca .nombre { font-family:'Lady Ice', var(--serif); font-weight:700;
                 font-size:clamp(42px,7vw,66px); letter-spacing:.14em; line-height:1.06; }
.marca p { margin:12px 0 0; font-size:13px; letter-spacing:.34em;
           text-transform:uppercase; color:var(--realce); }
.reglas { margin-top:24px; }
.reglas i { display:block; background:var(--tinta); }
.reglas i:first-child { height:3px; }
.reglas i:last-child { height:2px; margin-top:6px; }

.entrada { display:grid; grid-template-columns:1.4fr 1fr; gap:46px; margin-top:46px; }
@media (max-width:820px) { .entrada { grid-template-columns:1fr; gap:30px; } }
.entrada p { margin:0 0 16px; max-width:62ch; }
.entrada p:last-child { margin-bottom:0; }
.destacado { font-family:var(--serif); font-size:26px; line-height:1.34; }
.ficha { background:var(--panel); border:2px solid var(--regla); padding:26px 28px;
         box-shadow:var(--sombra); }
.ficha h3 { font-size:23px; margin-bottom:16px; }
.ficha dl { margin:0; display:grid; grid-template-columns:auto 1fr; gap:9px 20px; font-size:16px; }
.ficha dt { color:var(--tenue); text-transform:uppercase; letter-spacing:.14em;
            font-size:12px; align-self:center; }
.ficha dd { margin:0; }

/* --------------------------------------- indice: el orden es el calendario */
.indice { margin-top:58px; }
.indice h2 { font-size:27px; margin-bottom:18px; }
.indice ol { list-style:none; margin:0; padding:0; border-top:2px solid var(--regla); }
.indice li { display:grid; grid-template-columns:52px 1fr 160px 150px;
             align-items:baseline; gap:16px; padding:15px 0;
             border-bottom:1px solid var(--regla); }
@media (max-width:780px) {
  .indice li { grid-template-columns:42px 1fr; gap:6px 14px; }
  .indice .ix-sec, .indice .ix-plazo { grid-column:2; }
}
.ix-num { font-family:var(--serif); font-size:25px; color:var(--acento);
          font-variant-numeric:lining-nums; }
.ix-tema { font-size:17px; }
.ix-sec, .ix-plazo { font-size:12px; letter-spacing:.16em; text-transform:uppercase;
                     color:var(--tenue); }
.ix-plazo { color:var(--acento); }

/* ----------------------------------------------------------- pliegos */
.pliego { margin-top:80px; padding-top:34px; border-top:3px solid var(--tinta); }
.pl-cab { display:grid; grid-template-columns:auto 1fr auto; gap:26px; align-items:start; }
@media (max-width:780px) {
  .pl-cab { grid-template-columns:auto 1fr; }
  .pl-plazo { grid-column:2; text-align:left; }
}
.pl-folio { font-family:var(--serif); font-size:32px; line-height:1;
            width:62px; height:62px; display:flex; align-items:center; justify-content:center;
            background:var(--acento); color:var(--sobre-acento);
            font-variant-numeric:lining-nums; }
.pl-sec { margin:0 0 8px; font-size:12px; letter-spacing:.24em;
          text-transform:uppercase; color:var(--realce); }
.pl-tit h2 { font-size:clamp(27px,3.5vw,40px); line-height:1.14; }
.pl-sub { margin:12px 0 0; color:var(--tenue); max-width:56ch; }
.pl-plazo { text-align:right; }
.pl-plazo span { display:block; font-size:11px; letter-spacing:.24em;
                 text-transform:uppercase; color:var(--tenue); }
.pl-plazo strong { display:block; margin-top:6px; font-family:var(--serif);
                   font-weight:700; font-size:23px; color:var(--acento);
                   white-space:nowrap; font-variant-numeric:lining-nums; }

/* la tira se desliza igual que el carrusel en el feed */
.tira { margin-top:28px; display:flex; gap:14px; overflow-x:auto; padding-bottom:14px;
        scroll-snap-type:x mandatory; scrollbar-width:thin;
        scrollbar-color:var(--acento) transparent; }
.tira::-webkit-scrollbar { height:9px; }
.tira::-webkit-scrollbar-track { background:var(--hundido); }
.tira::-webkit-scrollbar-thumb { background:var(--acento); }
.lam { margin:0; flex:0 0 auto; scroll-snap-align:start; }
.lam img { display:block; width:min(304px,72vw); height:auto; box-shadow:var(--sombra); }
.lam figcaption { margin-top:10px; font-size:11px; letter-spacing:.20em;
                  text-transform:uppercase; color:var(--tenue); }

.pl-pie { display:grid; grid-template-columns:1fr 300px; gap:36px; margin-top:28px; }
@media (max-width:820px) { .pl-pie { grid-template-columns:1fr; } }
.pl-pie h3 { font-family:var(--sans); font-weight:600; font-size:12px;
             letter-spacing:.20em; text-transform:uppercase;
             color:var(--tenue); margin-bottom:12px; }
.pl-caption pre { margin:0; background:var(--panel); border-left:4px solid var(--acento);
                  padding:24px 26px; font:inherit; font-size:16px; line-height:1.62;
                  white-space:pre-wrap; overflow-wrap:anywhere; box-shadow:var(--sombra); }
.pl-historia img { display:block; width:100%%; max-width:214px; height:auto;
                   box-shadow:var(--sombra); }
.pl-historia p { margin:12px 0 0; font-size:14px; color:var(--tenue); max-width:30ch; }

.cierre-pagina { margin-top:84px; padding-top:26px; border-top:3px solid var(--tinta);
                 display:flex; justify-content:space-between; gap:20px; flex-wrap:wrap;
                 font-size:12px; letter-spacing:.18em; text-transform:uppercase;
                 color:var(--tenue); }
</style>

<div class="envoltura">
  <header class="masthead">
    <div class="barra"><span>Revisión previa</span><span>Cuidado en casa</span><span>@la_fiore.cl · 2026</span></div>
    <div class="marca">
      <img src="%(sello)s" alt="Sello de La Fiore">
      <h1 class="nombre">LA FIORE</h1>
      <p>Studio and Barber Shop</p>
    </div>
    <div class="reglas"><i></i><i></i></div>
  </header>

  <div class="entrada">
    <div>
      <p class="destacado">Diez carruseles que enseñan a cuidar el resultado en casa
      y dicen cuándo toca volver.</p>
      <p>Cada lámina interior separa lo que hace la clienta de lo que hacemos nosotros:
      <strong>EN CASA</strong> es la indicación, <strong>EN EL SALÓN</strong> es el servicio y
      <strong>EL DATO</strong> explica el porqué en dos líneas. La lámina de cierre lleva el
      plazo en grande, los servicios que lo cubren y la invitación a agendar.</p>
      <p>Nada corrige ni reta a quien lee. El carrusel enseña; no señala lo que se hizo mal.</p>
    </div>
    <aside class="ficha">
      <h3>Cómo se publica</h3>
      <dl>
        <dt>Días</dt><dd>Lunes y miércoles</dd>
        <dt>Hora</dt><dd>12:00 de Chile</dd>
        <dt>Feed</dt><dd>Carrusel de 6 · 1080×1350 (4:5)</dd>
        <dt>Historia</dt><dd>1080×1920 (9:16)</dd>
        <dt>Cobertura</dt><dd>Cinco semanas</dd>
        <dt>Tipografía</dt><dd>Playfair Display y Karla. Lady Ice queda para el sello</dd>
      </dl>
    </aside>
  </div>

  <nav class="indice">
    <h2>Los diez, en orden de publicación</h2>
    <ol>%(indice)s</ol>
  </nav>

  %(pliegos)s

  <footer class="cierre-pagina">
    <span>La Fiore · Talagante, Chile</span>
    <span>@la_fiore.cl</span>
  </footer>
</div>
"""


if __name__ == "__main__":
    construir()
