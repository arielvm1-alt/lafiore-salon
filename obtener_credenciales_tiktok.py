# -*- coding: utf-8 -*-
"""
Autoriza la app de TikTok una sola vez y consigue el token de refresco.

    python obtener_credenciales_tiktok.py

Te pide la clave y el secreto de la app (se escriben ocultos), abre el
navegador para que autorices con la cuenta del SALON, y guarda el token de
refresco en credenciales_tiktok.txt, que esta en .gitignore.

El token de refresco dura un ano. El de acceso dura 24 horas y el publicador
lo renueva solo en cada ejecucion, asi que no hay que tocarlo.

ANTES de correr esto, en el portal de desarrolladores de TikTok:
  - la app tiene que tener el permiso  video.upload
  - y esta URL registrada como Redirect URI:
    https://arielvm1-alt.github.io/lafiore-salon/autorizado.html

OJO: hay que autorizar con la cuenta de TikTok del SALON
(lafiorebarberia@gmail.com), no con la de Academy.

Sin dependencias externas: solo biblioteca estandar.
"""

import json
import os
import secrets
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

# TikTok exige que la URL de retorno sea https, asi que localhost no sirve.
# Se usa una pagina estatica del propio sitio: recibe el codigo, lo muestra
# y lo copia al portapapeles para pegarlo aqui.
REDIRECT = "https://arielvm1-alt.github.io/lafiore-salon/autorizado.html"
AMBITOS = "user.info.basic,video.upload"
AUTORIZAR = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN = "https://open.tiktokapis.com/v2/oauth/token/"

RAIZ = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(RAIZ, "credenciales_tiktok.txt")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
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
        detalle = e.read().decode("utf-8", "replace")
        pista = ""
        if "redirect_uri" in detalle:
            pista = ("\n\nLa URL de retorno no coincide con la registrada en el portal.\n"
                     "Tiene que ser exactamente:\n  %s" % REDIRECT)
        elif "authorization_code" in detalle or "invalid_grant" in detalle:
            pista = ("\n\nEse codigo ya se uso o se vencio: duran pocos minutos.\n"
                     "Vuelve a ejecutar el script y autoriza de nuevo.")
        raise SystemExit("\nERROR de TikTok: %s%s" % (detalle, pista))
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


def _del_portapapeles():
    """Lo que haya en el portapapeles, en una linea. Cadena vacia si no se puede."""
    try:
        if sys.platform == "win32":
            orden = ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"]
        elif sys.platform == "darwin":
            orden = ["pbpaste"]
        else:
            orden = ["xclip", "-selection", "clipboard", "-o"]
        salida = subprocess.run(orden, capture_output=True, timeout=15)
        texto = salida.stdout.decode("utf-8", "replace")
    except Exception:
        return ""
    # Un token no tiene saltos de linea ni espacios alrededor.
    return texto.replace("\r", "").replace("\n", "").strip()


def pedir_oculto(etiqueta):
    """Lee una clave mostrando un asterisco por caracter.

    getpass no dibuja nada. Es lo mas discreto, pero pegar a ciegas hace
    imposible notar que la pega se corto o que no entro nada. Aqui se ve un
    asterisco por letra y el total al final, sin revelar el valor.
    """
    sys.stdout.write(etiqueta)
    sys.stdout.flush()

    try:
        import msvcrt
    except ImportError:
        texto = _oculto_posix()
    else:
        letras = []
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                break
            if ch == "\x03":                     # Ctrl+C
                raise KeyboardInterrupt
            if ch == "\x16":                     # Ctrl+V
                # Leyendo tecla a tecla, Ctrl+V no pega: llega como un solo
                # caracter de control. Asi que vamos a buscar el portapapeles.
                pegado = _del_portapapeles()
                if pegado:
                    letras.extend(pegado)
                    sys.stdout.write("*" * len(pegado))
                    sys.stdout.flush()
                continue
            if ch in ("\x00", "\xe0"):           # flechas y teclas especiales
                msvcrt.getwch()
                continue
            if ch == "\b":                       # borrar
                if letras:
                    letras.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if ch < " ":                         # cualquier otro control
                continue
            letras.append(ch)
            sys.stdout.write("*")
            sys.stdout.flush()
        texto = "".join(letras)

    print("   (%d caracteres)" % len(texto))
    return texto.strip()


def _oculto_posix():
    """Lo mismo, en macOS y Linux."""
    import termios
    import tty
    fd = sys.stdin.fileno()
    previo = termios.tcgetattr(fd)
    letras = []
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\r", "\n"):
                break
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch in ("\x7f", "\b"):
                if letras:
                    letras.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            letras.append(ch)
            sys.stdout.write("*")
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previo)
    return "".join(letras)


def main():
    print("Autorizacion de TikTok  ·  La Fiore SALON")
    print("Veras un asterisco por caracter y el total al pulsar Enter.\n")

    client_key = pedir_oculto("1. Client key de la app:    ")
    client_secret = pedir_oculto("2. Client secret de la app: ")
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

    print("\nAbriendo el navegador para que autorices.")
    print("IMPORTANTE: entra con la cuenta del SALON (lafiorebarberia@gmail.com),")
    print("NO con la de Academy.")
    print("\nSi no se abre solo, entra a esta direccion:\n\n%s\n" % url)
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print("Al aceptar, TikTok te lleva a una pagina de La Fiore que muestra un")
    print("codigo con un boton para copiarlo. Pegalo aqui abajo.\n")
    pegado = input("Codigo de autorizacion: ").strip()
    if not pegado:
        raise SystemExit("Sin codigo. No se hizo nada.")

    # Por si pegan la URL entera en vez de solo el codigo.
    codigo = pegado
    if pegado.startswith("http"):
        consulta = urllib.parse.parse_qs(urllib.parse.urlparse(pegado).query)
        codigo = (consulta.get("code") or [None])[0]
        vuelto = (consulta.get("state") or [None])[0]
        if vuelto and vuelto != estado:
            raise SystemExit("El 'state' no coincide. Vuelve a empezar.")
    if not codigo:
        raise SystemExit("No se pudo leer el codigo. Vuelve a empezar.")

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
    print("  y ademas:")
    print("    TIKTOK_BASE_URL = https://arielvm1-alt.github.io/lafiore-salon/salida")
    print()
    print("Cuando termines, borra el archivo:  del credenciales_tiktok.txt")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
