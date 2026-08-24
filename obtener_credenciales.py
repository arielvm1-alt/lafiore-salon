# -*- coding: utf-8 -*-
"""
Convierte el token corto del Explorador en el de 60 dias y averigua el
IG_USER_ID de @la_fiore.cl.

Uso:
    python obtener_credenciales.py

Te pide dos cosas, que se escriben ocultas (no se ven al teclear ni quedan en
el historial de la consola):
  - la clave secreta de la app
  - el token corto del Explorador de la API Graph

Y hace por ti:
  1. El intercambio por el token de larga duracion (60 dias).
  2. La busqueda de la pagina y su cuenta de Instagram vinculada.

El token NUNCA se imprime en pantalla. Se guarda en credenciales.txt (que esta
en .gitignore) y se copia al portapapeles para que lo pegues en GitHub Secrets.

Sin dependencias externas: solo biblioteca estandar.
"""

import getpass
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

APP_ID = os.environ.get("IG_APP_ID", "826170617184855")
VERSION = os.environ.get("IG_API_VERSION", "v26.0")

RAIZ = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(RAIZ, "credenciales.txt")


def _get(ruta, **params):
    url = "https://graph.facebook.com/%s/%s?%s" % (
        VERSION, ruta.lstrip("/"), urllib.parse.urlencode(params))
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "lafiore-salon-setup/1.0")
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")
        try:
            detalle = json.loads(detalle)["error"]["message"]
        except Exception:
            pass
        pista = ""
        bajo = detalle.lower()
        if "client secret" in bajo:
            pista = (
                "\n\nEsa clave no es la de esta app. Hay DOS claves distintas y se confunden:\n"
                "  - La que necesitas aqui: Configuracion de la app -> Basica ->\n"
                "    'Clave secreta de la app'  (pulsa Mostrar y copiala entera)\n"
                "    https://developers.facebook.com/apps/%s/settings/basic/\n"
                "  - La que NO sirve: la 'Clave secreta de la app de Instagram',\n"
                "    que sale en la pantalla del producto Instagram.\n"
                "Vuelve a ejecutar el script con la primera." % APP_ID)
        elif "expired" in bajo or "session" in bajo:
            pista = ("\n\nEl token corto del Explorador dura 1 hora. Genera uno nuevo\n"
                     "y vuelve a ejecutar el script.")
        raise SystemExit("\nERROR de la API: %s%s" % (detalle, pista))
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
    print("Credenciales de publicacion de La Fiore  ·  @la_fiore.cl")
    print("App: %s   API: %s\n" % (APP_ID, VERSION))
    print("Los dos valores se escriben ocultos. Pegalos y pulsa Enter.\n")

    app_secret = getpass.getpass("1. Clave secreta de la app: ").strip()
    token_corto = getpass.getpass("2. Token corto del Explorador: ").strip()

    if not app_secret or not token_corto:
        raise SystemExit("Faltan datos. No se hizo nada.")

    # --- diagnostico: los dos valores tienen formas muy distintas -----------
    def parece_token(v):
        return len(v) > 60 or v[:2].upper() == "EA"

    def parece_secreto(v):
        return len(v) == 32 and all(c in "0123456789abcdefABCDEF" for c in v)

    print("\nRevisando lo que pegaste (sin mostrarlo):")
    print("   clave: %d caracteres%s" % (
        len(app_secret), "" if parece_secreto(app_secret) else "   <- no parece una clave"))
    print("   token: %d caracteres%s" % (
        len(token_corto), "" if parece_token(token_corto) else "   <- no parece un token"))

    if parece_token(app_secret) and parece_secreto(token_corto):
        print("\n   Los pegaste al reves. Los intercambio y sigo.")
        app_secret, token_corto = token_corto, app_secret
    elif not parece_secreto(app_secret):
        raise SystemExit(
            "\nLa clave secreta de la app son exactamente 32 caracteres hexadecimales\n"
            "(solo 0-9 y a-f), y lo que pegaste tiene %d.\n\n"
            "Sacala de aqui, del campo 'Clave secreta de la app', pulsando Mostrar:\n"
            "  https://developers.facebook.com/apps/%s/settings/basic/\n\n"
            "Copiala con doble clic para no arrastrar espacios ni cortarla."
            % (len(app_secret), APP_ID))

    # --- comprobar la clave por separado, antes de tocar el token ----------
    print("\nComprobando solo la clave de la app...")
    _get("oauth/access_token",
         grant_type="client_credentials",
         client_id=APP_ID,
         client_secret=app_secret)
    print("   OK, la clave es correcta.")

    print("\nCambiando el token por el de 60 dias...")
    r = _get("oauth/access_token",
             grant_type="fb_exchange_token",
             client_id=APP_ID,
             client_secret=app_secret,
             fb_exchange_token=token_corto)
    token_largo = r["access_token"]
    dias = int(r.get("expires_in", 0)) // 86400
    print("   OK. Caduca en unos %d dias." % (dias or 60))

    print("\nBuscando tus paginas y sus cuentas de Instagram...")
    paginas = _get("me/accounts",
                   fields="id,name,instagram_business_account{id,username}",
                   access_token=token_largo).get("data", [])

    if not paginas:
        raise SystemExit("No apareció ninguna página. ¿Diste los cuatro permisos?")

    vinculadas = [p for p in paginas if p.get("instagram_business_account")]

    print("\n   Paginas encontradas:")
    for p in paginas:
        ig = p.get("instagram_business_account")
        marca = "@%s" % ig["username"] if ig else "(sin Instagram vinculado)"
        print("     - %-28s %s" % (p["name"], marca))

    if not vinculadas:
        raise SystemExit("\nNinguna pagina tiene Instagram vinculado.")

    def es_el_salon(p):
        usuario = p["instagram_business_account"]["username"].lower()
        if "academy" in usuario or "academy" in p["name"].lower():
            return False          # esa es la otra cuenta, la de formacion
        return usuario in ("la_fiore.cl", "lafiore.cl") or "fiore" in usuario

    elegida = next((p for p in vinculadas if es_el_salon(p)), None)
    if elegida is None and len(vinculadas) == 1:
        elegida = vinculadas[0]
    if elegida is None:
        print("\nHay varias paginas con Instagram.")
        print("Elige la del SALON (@la_fiore.cl), NO la de Academy:")
        for i, p in enumerate(vinculadas, 1):
            print("  %d) %s -> @%s" % (i, p["name"], p["instagram_business_account"]["username"]))
        elegida = vinculadas[int(input("Numero: ")) - 1]

    ig = elegida["instagram_business_account"]

    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write("IG_USER_ID=%s\n" % ig["id"])
        f.write("IG_ACCESS_TOKEN=%s\n" % token_largo)

    copiado = al_portapapeles(token_largo)

    print("\n" + "=" * 62)
    print("LISTO")
    print("=" * 62)
    print("Pagina:     %s" % elegida["name"])
    print("Instagram:  @%s" % ig["username"])
    print()
    print("IG_USER_ID = %s        <- este valor es publico, cargalo tal cual" % ig["id"])
    print()
    if copiado:
        print("IG_ACCESS_TOKEN ya esta en tu portapapeles: pegalo con Ctrl+V.")
    else:
        print("IG_ACCESS_TOKEN esta en credenciales.txt (no se sube al repositorio).")
    print()
    print("Cargalos en:")
    print("  https://github.com/arielvm1-alt/lafiore-salon/settings/secrets/actions/new")
    print()
    print("Cuando termines, borra credenciales.txt:  del credenciales.txt")
    print("=" * 62)


if __name__ == "__main__":
    main()
