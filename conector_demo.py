# -*- coding: utf-8 -*-
"""
Conector local del publicador (web/publicador.html).

    python conector_demo.py

Sirve la interfaz en  http://localhost:8724/publicador.html  y le presta ocho
rutas que hablan con la API de TikTok usando las credenciales del archivo
credenciales_tiktok.txt. La pagina nunca ve tokens: solo datos de pantalla.

Existe para la auditoria de TikTok: los revisores piden un video demo del
flujo completo con interfaz visible (consulta del creador, selector de
privacidad sin valor por defecto, confirmacion de derechos). Este es ese
flujo, ejecutado de verdad contra el Sandbox.

Sin dependencias externas: solo biblioteca estandar.
"""

import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "contenido"))
sys.path.insert(0, RAIZ)

import captions            # textos por set                       # noqa: E402
import sets as contenido   # titulos por set                      # noqa: E402

PUERTO = 8724
API = "https://open.tiktokapis.com/v2"
REDIRECT = "https://arielvm1-alt.github.io/lafiore-salon/autorizado.html"
AMBITOS = "user.info.basic,video.upload,video.publish"
BASE_IMAGENES = "https://arielvm1-alt.github.io/lafiore-salon/salida"

# La pagina puede servirse desde el propio conector o desde GitHub Pages.
ORIGENES = ("https://arielvm1-alt.github.io", "http://localhost:%d" % PUERTO)

CREDENCIALES = os.path.join(RAIZ, "credenciales_tiktok.txt")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def credenciales():
    valores = {}
    if os.path.exists(CREDENCIALES):
        with open(CREDENCIALES, encoding="utf-8") as f:
            for linea in f:
                if "=" in linea:
                    k, v = linea.strip().split("=", 1)
                    valores[k] = v
    faltan = [k for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET") if k not in valores]
    if faltan:
        raise SystemExit("Faltan %s en credenciales_tiktok.txt" % ", ".join(faltan))
    return valores


CRED = credenciales()
_token = {"acceso": None}      # el token de acceso vive solo en memoria


def _tiktok(ruta, datos=None, con_token=True, formulario=False):
    cab = {"User-Agent": "lafiore-salon-demo/1.0"}
    cuerpo = None
    if datos is not None:
        if formulario:
            cuerpo = urllib.parse.urlencode(datos).encode("utf-8")
            cab["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            cuerpo = json.dumps(datos).encode("utf-8")
            cab["Content-Type"] = "application/json; charset=UTF-8"
    if con_token:
        if not _token["acceso"]:
            _refrescar()
        cab["Authorization"] = "Bearer " + _token["acceso"]
    req = urllib.request.Request(API + ruta, data=cuerpo, headers=cab)
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(),
                                    timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(detalle).get("error", {})
            detalle = "%s (%s)" % (err.get("message", detalle), err.get("code"))
        except ValueError:
            pass
        raise RuntimeError(detalle)


def _refrescar():
    if "TIKTOK_REFRESH_TOKEN" not in CRED:
        raise RuntimeError("Sin autorizar: usa 'Conectar con TikTok' primero.")
    d = _tiktok("/oauth/token/", {
        "client_key": CRED["TIKTOK_CLIENT_KEY"],
        "client_secret": CRED["TIKTOK_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": CRED["TIKTOK_REFRESH_TOKEN"],
    }, con_token=False, formulario=True)
    if "access_token" not in d:
        raise RuntimeError("TikTok no devolvio token: %s" % json.dumps(d)[:200])
    _token["acceso"] = d["access_token"]


# --------------------------------------------------------------------------
# las rutas
# --------------------------------------------------------------------------

def r_auth_url(_):
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
        "client_key": CRED["TIKTOK_CLIENT_KEY"],
        "scope": AMBITOS,
        "response_type": "code",
        "redirect_uri": REDIRECT,
        "state": "demo",
    })
    return {"url": url}


def r_canjear(cuerpo):
    code = (cuerpo or {}).get("code", "").strip()
    if not code:
        raise RuntimeError("Falta el codigo.")
    d = _tiktok("/oauth/token/", {
        "client_key": CRED["TIKTOK_CLIENT_KEY"],
        "client_secret": CRED["TIKTOK_CLIENT_SECRET"],
        "code": urllib.parse.unquote(code),
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT,
    }, con_token=False, formulario=True)
    if "access_token" not in d:
        raise RuntimeError("Canje fallido: %s" % json.dumps(d)[:200])
    _token["acceso"] = d["access_token"]
    if d.get("refresh_token"):
        CRED["TIKTOK_REFRESH_TOKEN"] = d["refresh_token"]
    return {"ok": True}


def r_perfil(_):
    d = _tiktok("/user/info/?fields=open_id,display_name,avatar_url")
    return (d.get("data") or {}).get("user") or {}


def r_creator_info(_):
    d = _tiktok("/post/publish/creator_info/query/", {})
    return d.get("data") or {}


def r_sets(_):
    filas = []
    for s in contenido.SETS:
        filas.append({"numero": s["id"],
                      "titulo": contenido.__dict__["SETS"] and
                                s["seccion"] + " — " +
                                s["portada"]["titulo"].replace("*", "")})
    return {"sets": filas}


def r_texto(consulta):
    n = int((consulta.get("set") or ["1"])[0])
    return {"texto": captions.caption_tiktok(n)}


def r_enviar(cuerpo):
    c = cuerpo or {}
    n = int(c.get("set") or 0)
    modo = c.get("modo") or "borrador"
    texto = (c.get("texto") or captions.caption_tiktok(n)).strip()
    urls = ["%s/set_%02d/tiktok/%02d.jpg" % (BASE_IMAGENES, n, i)
            for i in range(1, 7)]

    post_info = {"title": texto[:90], "description": texto}
    if modo == "directo":
        privacidad = c.get("privacidad")
        if not privacidad:
            raise RuntimeError("Elige la visibilidad antes de publicar.")
        post_info["privacy_level"] = privacidad
        post_info["disable_comment"] = not c.get("comentarios", True)

    d = _tiktok("/post/publish/content/init/", {
        "post_info": post_info,
        "source_info": {"source": "PULL_FROM_URL",
                        "photo_cover_index": 0,
                        "photo_images": urls},
        "post_mode": "DIRECT_POST" if modo == "directo" else "MEDIA_UPLOAD",
        "media_type": "PHOTO",
    })
    publish_id = (d.get("data") or {}).get("publish_id")
    if not publish_id:
        raise RuntimeError("Sin publish_id: %s" % json.dumps(d)[:200])
    return {"publish_id": publish_id}


def r_estado_envio(consulta):
    pid = (consulta.get("id") or [""])[0]
    d = _tiktok("/post/publish/status/fetch/", {"publish_id": pid})
    datos = d.get("data") or {}
    return {"status": datos.get("status", "?"),
            "fail_reason": datos.get("fail_reason")}


RUTAS_GET = {"/auth-url": r_auth_url, "/perfil": r_perfil,
             "/creator-info": r_creator_info, "/sets": r_sets,
             "/texto": r_texto, "/estado-envio": r_estado_envio,
             "/salud": lambda _: {"ok": True}}
RUTAS_POST = {"/canjear": r_canjear, "/enviar": r_enviar}


class Manejador(BaseHTTPRequestHandler):

    def _cors(self):
        origen = self.headers.get("Origin", "")
        if origen in ORIGENES:
            self.send_header("Access-Control-Allow-Origin", origen)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # Chrome exige esta cabecera cuando una pagina https llama a localhost.
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _json(self, codigo, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        partes = urllib.parse.urlparse(self.path)
        if partes.path in ("/", "/publicador.html"):
            try:
                with open(os.path.join(RAIZ, "web", "publicador.html"), "rb") as f:
                    cuerpo = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(cuerpo)
            except OSError:
                self._json(404, {"error": "no encuentro web/publicador.html"})
            return
        if partes.path == "/icono-app.png":
            try:
                with open(os.path.join(RAIZ, "web", "icono-app.png"), "rb") as f:
                    cuerpo = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(cuerpo)
            except OSError:
                self._json(404, {"error": "sin icono"})
            return
        fn = RUTAS_GET.get(partes.path)
        if not fn:
            self._json(404, {"error": "ruta desconocida"})
            return
        try:
            self._json(200, fn(urllib.parse.parse_qs(partes.query)))
        except Exception as e:
            self._json(500, {"error": str(e)})

    def do_POST(self):
        partes = urllib.parse.urlparse(self.path)
        fn = RUTAS_POST.get(partes.path)
        if not fn:
            self._json(404, {"error": "ruta desconocida"})
            return
        try:
            largo = int(self.headers.get("Content-Length") or 0)
            cuerpo = json.loads(self.rfile.read(largo) or b"{}")
            self._json(200, fn(cuerpo))
        except Exception as e:
            self._json(500, {"error": str(e)})

    def log_message(self, formato, *args):
        # sin ruido, y jamas tokens en el log
        sys.stdout.write("  %s %s\n" % (self.command, self.path.split("?")[0]))


if __name__ == "__main__":
    print("Publicador de La Fiore  ·  http://localhost:%d/publicador.html" % PUERTO)
    print("(las credenciales quedan en este proceso; la pagina nunca las ve)")
    ThreadingHTTPServer(("localhost", PUERTO), Manejador).serve_forever()
