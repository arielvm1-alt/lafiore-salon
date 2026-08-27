# -*- coding: utf-8 -*-
"""
Autoriza la app de TikTok una sola vez y consigue el token de refresco.

    python obtener_credenciales_tiktok.py

Te pide la clave y el secreto de la app (se escriben ocultos), abre el
navegador para que autorices con la cuenta de @la_fiore.cl, y guarda el token
de refresco en credenciales_tiktok.txt, que esta en .gitignore.

El token de refresco dura un ano. El de acceso dura 24 horas y el publicador
lo renueva solo en cada ejecucion, asi que no hay que tocarlo.

ANTES de correr esto, en el portal de desarrolladores de TikTok:
  - la app tiene que tener el permiso  video.upload
  - y esta URL registrada como Redirect URI:  http://localhost:8723/callback

Sin dependencias externas: solo biblioteca estandar.
"""

import getpass
import http.server
import json
import os
import secrets
import ssl
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

PUERTO = 8723
REDIRECT = "http://localhost:%d/callback" % PUERTO
AMBITOS = "user.info.basic,video.upload"
AUTORIZAR = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN = "https://open.tiktokapis.com/v2/oauth/token/"

RAIZ = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(RAIZ, "credenciales_tiktok.txt")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_recibido = {}


class _Manejador(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        partes = urllib.parse.urlparse(self.path)
        if partes.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
        _recibido.update(urllib.parse.parse_qs(partes.query))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            "<!doctype html><meta charset='utf-8'>"
            "<body style='font-family:system-ui;padding:60px;text-align:center'>"
            "<h2>Listo</h2><p>Ya puedes cerrar esta pestaña y volver a la consola.</p>"
            "</body>".encode("utf-8"))

    def log_message(self, *_):
        pass


def _post(url, datos):
    cuerpo = urllib.parse.urlencode(datos).encode("utf-8")
    req = urllib.request.Request(url, data=cuerpo)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "lafiore-salon-tiktok-setup/1.0")
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(),
                                    timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit("\nERROR de TikTok: %s" % e.read().decode("utf-8", "replace"))
    except urllib.error.URLError as e:
        raise SystemExit("\nERROR de conexion: %s" % e.reason)


def al_portapapeles(texto):
    try:
        if sys.platform == "win32":
            p = subprocess.Popen("clip", stdin=subprocess.PIPE, shell=True)
        elif sys.platform == "darwin":
            p = subprocess.Popen("pbcopy", stdin=subprocess.PIPE)
        else:
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        p.communicate(texto.encode("utf-8"))
        return p.returncode == 0
    except Exception:
        return False


def main():
    print("Autorizacion de TikTok para La Fiore  ·  @la_fiore.cl")
    print("Los dos valores se escriben ocultos. Pegalos y pulsa Enter.\n")

    client_key = getpass.getpass("1. Client key de la app:    ").strip()
    client_secret = getpass.getpass("2. Client secret de la app: ").strip()
    if not client_key or not client_secret:
        raise SystemExit("Faltan datos. No se hizo nada.")

    estado = secrets.token_urlsafe(16)
    url = AUTORIZAR + "?" + urllib.parse.urlencode({
        "client_key": client_key,
        "scope": AMBITOS,
        "response_type": "code",
        "redirect_uri": REDIRECT,
        "state": estado,
    })

    servidor = http.server.HTTPServer(("localhost", PUERTO), _Manejador)
    hilo = threading.Thread(target=servidor.handle_request, daemon=True)
    hilo.start()

    print("\nAbriendo el navegador para que autorices con @la_fiore.cl...")
    print("Si no se abre solo, entra a esta direccion:\n\n%s\n" % url)
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print("Esperando la autorizacion (2 minutos)...")
    hilo.join(timeout=120)

    codigo = (_recibido.get("code") or [None])[0]
    if not codigo:
        print("\nNo llego la respuesta al servidor local.")
        print("Si el navegador quedo en una pagina de localhost que no cargo,")
        print("copia la barra de direcciones completa y pegala aqui.\n")
        pegado = input("URL de redireccion: ").strip()
        if pegado:
            consulta = urllib.parse.parse_qs(urllib.parse.urlparse(pegado).query)
            codigo = (consulta.get("code") or [None])[0]
            estado_vuelto = (consulta.get("state") or [None])[0]
            if estado_vuelto and estado_vuelto != estado:
                raise SystemExit("El 'state' no coincide. Vuelve a empezar.")
    if not codigo:
        raise SystemExit("Sin codigo de autorizacion. No se hizo nada.")

    print("\nCambiando el codigo por los tokens...")
    datos = _post(TOKEN, {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": urllib.parse.unquote(codigo),
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT,
    })

    refresh = datos.get("refresh_token")
    if not refresh:
        raise SystemExit("TikTok no devolvio token de refresco: %s"
                         % json.dumps(datos)[:400])
    dias = int(datos.get("refresh_expires_in", 0)) // 86400

    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write("TIKTOK_CLIENT_KEY=%s\n" % client_key)
        f.write("TIKTOK_CLIENT_SECRET=%s\n" % client_secret)
        f.write("TIKTOK_REFRESH_TOKEN=%s\n" % refresh)

    copiado = al_portapapeles(refresh)

    print("\n" + "=" * 62)
    print("LISTO")
    print("=" * 62)
    print("Permisos:  %s" % datos.get("scope", AMBITOS))
    print("El token de refresco dura %d dias." % (dias or 365))
    print()
    if copiado:
        print("TIKTOK_REFRESH_TOKEN ya esta en tu portapapeles: pegalo con Ctrl+V.")
    print("Los tres valores estan en credenciales_tiktok.txt (no se sube al repo).")
    print()
    print("Cargalos como secretos en:")
    print("  https://github.com/arielvm1-alt/lafiore-salon/settings/secrets/actions")
    print("    TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN")
    print()
    print("Cuando termines, borra el archivo:  del credenciales_tiktok.txt")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
