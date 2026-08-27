# -*- coding: utf-8 -*-
"""
Envia el carrusel vertical de un set al buzon de TikTok de @la_fiore.cl.

Usa el modo MEDIA_UPLOAD de la Content Posting API: TikTok recibe las seis
laminas, arma el borrador y manda una notificacion a la app. Desde el telefono
se abre, se elige la musica y se publica de un toque.

Por que este modo y no la publicacion directa:
  El modo DIRECT_POST necesita que TikTok audite la app. Mientras no lo haga,
  todo lo que publique queda en privado y no lo ve nadie. La auditoria evalua
  la interfaz de la aplicacion, y un publicador automatico sin pantallas no la
  pasa. MEDIA_UPLOAD no necesita auditoria y llega igual al telefono.

Uso:
    python publicar_tiktok.py                # el siguiente set pendiente
    python publicar_tiktok.py --set 3        # un set concreto
    python publicar_tiktok.py --dry-run      # muestra que enviaria
    python publicar_tiktok.py --verificar    # comprueba las credenciales
    python publicar_tiktok.py --estado       # que se envio y que falta

Variables de entorno:
    TIKTOK_CLIENT_KEY      la clave de la app (portal de desarrolladores)
    TIKTOK_CLIENT_SECRET   el secreto de la app
    TIKTOK_REFRESH_TOKEN   el token de refresco, dura un ano
    TIKTOK_BASE_URL        la URL publica de salida/, sin barra final.
                           Tiene que estar bajo el prefijo verificado en TikTok.
                           Ej: https://USUARIO.github.io/lafiore-salon/salida

Sin dependencias externas: solo biblioteca estandar.
"""

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "salida")
ESTADO = os.path.join(RAIZ, "estado_tiktok.json")

API = "https://open.tiktokapis.com/v2"
LAMINAS = ["01", "02", "03", "04", "05", "06"]

REINTENTOS = 4
ESPERA_BASE = 5

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class ErrorTikTok(Exception):
    pass


# --------------------------------------------------------------------------
# configuracion
# --------------------------------------------------------------------------

CREDENCIALES = os.path.join(RAIZ, "credenciales_tiktok.txt")


def _del_archivo_local():
    """Carga credenciales_tiktok.txt si existe, para poder ensayar en local.

    En GitHub Actions las credenciales llegan por variables de entorno y este
    archivo no existe: esta en .gitignore y nunca se sube. Sirve solo para
    probar desde el computador sin exportar nada a mano.
    """
    if not os.path.exists(CREDENCIALES):
        return
    with open(CREDENCIALES, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip())


def config():
    _del_archivo_local()
    faltan = [k for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET",
                          "TIKTOK_REFRESH_TOKEN", "TIKTOK_BASE_URL")
              if not os.environ.get(k)]
    if faltan:
        raise ErrorTikTok(
            "Faltan variables de entorno: %s\n"
            "Revisa el README, seccion 6." % ", ".join(faltan))
    return {
        "client_key": os.environ["TIKTOK_CLIENT_KEY"].strip(),
        "client_secret": os.environ["TIKTOK_CLIENT_SECRET"].strip(),
        "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN"].strip(),
        "base_url": os.environ["TIKTOK_BASE_URL"].strip().rstrip("/"),
        # "borrador" manda al buzon (default). "directo" publica sin pasar por
        # el telefono; mientras TikTok no audite la app, sale en privado.
        "modo": os.environ.get("TIKTOK_MODO", "borrador").strip().lower(),
    }


# --------------------------------------------------------------------------
# llamadas HTTP
# --------------------------------------------------------------------------

def _peticion(url, datos=None, cabeceras=None, json_body=False):
    ctx = ssl.create_default_context()
    cuerpo = None
    cab = {"User-Agent": "lafiore-salon-tiktok/1.0"}
    if datos is not None:
        if json_body:
            cuerpo = json.dumps(datos).encode("utf-8")
            cab["Content-Type"] = "application/json; charset=UTF-8"
        else:
            cuerpo = urllib.parse.urlencode(datos).encode("utf-8")
            cab["Content-Type"] = "application/x-www-form-urlencoded"
    cab.update(cabeceras or {})

    req = urllib.request.Request(url, data=cuerpo, headers=cab)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")
        raise ErrorTikTok("HTTP %s en %s -> %s"
                          % (e.code, url.replace(API, ""), _pista(detalle)))
    except urllib.error.URLError as e:
        raise ErrorTikTok("Sin conexion con TikTok: %s" % e.reason)


def _pista(detalle):
    """Traduce los errores mas comunes de TikTok a algo accionable."""
    try:
        error = json.loads(detalle).get("error", {})
        codigo = error.get("code", "")
        mensaje = error.get("message", detalle)
    except ValueError:
        return detalle

    ayudas = {
        "url_ownership_unverified":
            "La URL de las imagenes no esta verificada en TikTok. Ve al portal, "
            "'Manage URL properties', y verifica el prefijo con el archivo de firma.",
        "invalid_param":
            "Algun campo del envio no le gusto. Revisa que las seis URLs abran "
            "en el navegador y que sean https sin redirecciones.",
        "access_token_invalid":
            "El token de acceso no sirve. Suele arreglarse solo en el proximo "
            "intento; si insiste, vuelve a autorizar con obtener_credenciales_tiktok.py.",
        "scope_not_authorized":
            "A la app le falta el permiso video.upload. Anadelo en el portal y "
            "vuelve a autorizar.",
        "rate_limit_exceeded":
            "Demasiados envios seguidos. Espera y reintenta.",
        "unaudited_client_can_only_post_to_private_accounts":
            "El post directo publico requiere que TikTok audite la app. Mientras "
            "tanto, usa el modo borrador (TIKTOK_MODO=borrador o sin definir). "
            "Este error NO se arregla reintentando.",
    }
    extra = ayudas.get(codigo, "")
    return "%s (%s)%s" % (mensaje, codigo, "\n  -> " + extra if extra else "")


def _con_reintento(descripcion, fn):
    espera = ESPERA_BASE
    ultimo = None
    for intento in range(1, REINTENTOS + 1):
        try:
            return fn()
        except ErrorTikTok as e:
            ultimo = e
            if "NO se arregla reintentando" in str(e) or intento == REINTENTOS:
                break
            print("   ! %s fallo (intento %d/%d): %s" % (descripcion, intento, REINTENTOS, e))
            print("     reintento en %ds" % espera)
            time.sleep(espera)
            espera *= 2
    raise ErrorTikTok("%s: agotados los reintentos. Ultimo error: %s" % (descripcion, ultimo))


# --------------------------------------------------------------------------
# credenciales
# --------------------------------------------------------------------------

def token_de_acceso(cfg):
    """Cambia el token de refresco por uno de acceso. El de acceso dura 24 h."""
    def hacer():
        return _peticion(API + "/oauth/token/", {
            "client_key": cfg["client_key"],
            "client_secret": cfg["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": cfg["refresh_token"],
        })
    datos = _con_reintento("pedir el token de acceso", hacer)
    if "access_token" not in datos:
        raise ErrorTikTok("TikTok no devolvio token: %s" % json.dumps(datos)[:300])
    return datos["access_token"]


def cmd_verificar(cfg):
    token = token_de_acceso(cfg)
    datos = _peticion(API + "/user/info/?fields=open_id,display_name",
                      cabeceras={"Authorization": "Bearer " + token})
    usuario = (datos.get("data") or {}).get("user") or {}
    print("Cuenta:     %s" % usuario.get("display_name", "?"))
    print("Base URL:   %s" % cfg["base_url"])
    if cfg.get("modo") == "directo":
        creador = info_creador(token)
        opciones = creador.get("privacy_level_options") or []
        print("Modo:       DIRECT_POST (publica sin intervencion)")
        print("Privacidades disponibles: %s" % (opciones or "?"))
    else:
        print("Modo:       MEDIA_UPLOAD (llega al buzon, se publica desde el telefono)")

    faltan = [u for u in urls_de(cfg, "set_01") if not _url_viva(u)]
    if faltan:
        print("\nOJO: estas URLs no responden y TikTok no podra descargarlas:")
        for u in faltan:
            print("   -", u)
        return 1
    print("Imagenes:   las seis del set_01 responden correctamente")
    print("\nAccesos correctos.")
    return 0


def _url_viva(url):
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "lafiore-salon-tiktok/1.0")
        with urllib.request.urlopen(req, context=ssl.create_default_context(),
                                    timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


# --------------------------------------------------------------------------
# estado
# --------------------------------------------------------------------------

def cargar_estado():
    if not os.path.exists(ESTADO):
        return crear_estado()
    with open(ESTADO, encoding="utf-8") as f:
        return json.load(f)


def guardar_estado(estado):
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
        f.write("\n")


def crear_estado():
    estado = {
        "destino": "TikTok · @la_fiore.cl",
        "modo": "MEDIA_UPLOAD: llega al buzon y se publica desde el telefono",
        "sets": [
            {"set": "set_%02d" % i, "estado": "pendiente",
             "enviado_en": None, "publish_id": None, "intentos": 0}
            for i in range(1, 11)
        ],
    }
    guardar_estado(estado)
    return estado


def siguiente_pendiente(estado):
    for s in estado["sets"]:
        if s["estado"] == "pendiente":
            return s
    return None


# --------------------------------------------------------------------------
# envio
# --------------------------------------------------------------------------

def info_creador(token):
    """Consulta obligatoria antes de un post directo.

    Devuelve las opciones reales del creador: privacidades disponibles y si
    puede recibir posts ahora. TikTok exige hacer esta consulta antes de cada
    publicacion directa; saltarsela es ademas causal de rechazo en auditoria.
    """
    datos = _peticion(API + "/post/publish/creator_info/query/", {},
                      cabeceras={"Authorization": "Bearer " + token},
                      json_body=True)
    return datos.get("data") or {}


def elegir_privacidad(opciones):
    """La mas publica que el creador tenga disponible."""
    for nivel in ("PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR",
                  "SELF_ONLY"):
        if nivel in opciones:
            return nivel
    return "SELF_ONLY"


def urls_de(cfg, nombre_set):
    urls = []
    for lam in LAMINAS:
        local = os.path.join(SALIDA, nombre_set, "tiktok", lam + ".jpg")
        if not os.path.exists(local):
            raise ErrorTikTok(
                "Falta %s. Ejecuta primero: python plantilla/render.py" % local)
        urls.append("%s/%s/tiktok/%s.jpg" % (cfg["base_url"], nombre_set, lam))
    return urls


def texto_de(nombre_set):
    ruta = os.path.join(SALIDA, "captions_tiktok.json")
    if not os.path.exists(ruta):
        ruta = os.path.join(SALIDA, "captions.json")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)[nombre_set]


def enviar_set(cfg, nombre_set, dry_run=False):
    urls = urls_de(cfg, nombre_set)
    texto = texto_de(nombre_set)

    print("Enviando %s al buzon de TikTok (%d laminas)" % (nombre_set, len(urls)))
    for u in urls:
        print("   -", u)
    print("Texto:\n%s\n" % "\n".join("   | " + l for l in texto.split("\n")))

    if dry_run:
        print("[dry-run] no se llamo a la API.")
        return None

    token = token_de_acceso(cfg)

    directo = cfg.get("modo") == "directo"
    post_info = {"title": texto[:90], "description": texto}
    if directo:
        creador = info_creador(token)
        opciones = creador.get("privacy_level_options") or []
        privacidad = elegir_privacidad(opciones)
        post_info["privacy_level"] = privacidad
        post_info["disable_comment"] = False
        print("   Modo directo. Privacidades disponibles: %s" % (opciones or "?"))
        print("   Se publica con: %s" % privacidad)
        if privacidad == "SELF_ONLY":
            print("   OJO: saldra en privado. Es el limite de una app sin auditar.")

    def hacer():
        return _peticion(API + "/post/publish/content/init/", {
            "post_info": post_info,
            "source_info": {
                "source": "PULL_FROM_URL",
                "photo_cover_index": 0,
                "photo_images": urls,
            },
            "post_mode": "DIRECT_POST" if directo else "MEDIA_UPLOAD",
            "media_type": "PHOTO",
        }, cabeceras={"Authorization": "Bearer " + token}, json_body=True)

    datos = _con_reintento("enviar el carrusel", hacer)
    publish_id = (datos.get("data") or {}).get("publish_id")
    if not publish_id:
        raise ErrorTikTok("TikTok no devolvio publish_id: %s" % json.dumps(datos)[:300])

    if directo:
        print("   PUBLICADO DIRECTO. publish_id = %s" % publish_id)
    else:
        print("   ENVIADO. publish_id = %s" % publish_id)
        print("   Revisa la notificacion en la app de TikTok para publicarlo.")
    return publish_id


# --------------------------------------------------------------------------
# comandos
# --------------------------------------------------------------------------

def cmd_estado():
    estado = cargar_estado()
    print("Destino: %s" % estado["destino"])
    print("Modo:    %s" % estado["modo"])
    for s in estado["sets"]:
        marca = {"enviado": "OK ", "pendiente": " . ", "error": "ERR"}.get(s["estado"], "  ?")
        extra = ""
        if s["enviado_en"]:
            extra = "  %s  publish_id %s" % (s["enviado_en"], s["publish_id"])
        elif s["intentos"]:
            extra = "  intentos: %d" % s["intentos"]
        print("  %s %s%s" % (marca, s["set"], extra))
    pendiente = siguiente_pendiente(estado)
    print("\nSiguiente: %s" % (pendiente["set"] if pendiente else "ninguno"))
    return 0


def ya_se_envio_hoy(estado):
    """True si hoy, en fecha de Chile, ya se mando un set al buzon."""
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime
        hoy = datetime.now(ZoneInfo("America/Santiago")).date()
    except Exception:
        return False
    from datetime import datetime
    for s in estado["sets"]:
        marca = s.get("enviado_en")
        if not marca:
            continue
        try:
            cuando = datetime.strptime(marca, "%Y-%m-%dT%H:%M:%S%z")
            from zoneinfo import ZoneInfo as Z
            if cuando.astimezone(Z("America/Santiago")).date() == hoy:
                print("Hoy ya se envio %s a TikTok. No se envia otro." % s["set"])
                return True
        except Exception:
            continue
    return False


def cmd_enviar(args):
    estado = cargar_estado()

    # Mismo candado que en Instagram: un envio por dia como maximo, salvo que
    # se pida un set concreto a mano.
    if not args.set and not args.dry_run and ya_se_envio_hoy(estado):
        return 0

    if args.set:
        nombre = "set_%02d" % args.set
        entrada = next((s for s in estado["sets"] if s["set"] == nombre), None)
        if entrada is None:
            raise ErrorTikTok("No existe %s" % nombre)
    else:
        entrada = siguiente_pendiente(estado)
        if entrada is None:
            print("No queda ningun set pendiente para TikTok.")
            return 0

    cfg = config()
    try:
        publish_id = enviar_set(cfg, entrada["set"], dry_run=args.dry_run)
    except ErrorTikTok:
        if not args.dry_run:
            entrada["estado"] = "error"
            entrada["intentos"] = entrada.get("intentos", 0) + 1
            guardar_estado(estado)
        raise

    if not args.dry_run:
        entrada["estado"] = "enviado"
        entrada["publish_id"] = publish_id
        entrada["enviado_en"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        guardar_estado(estado)
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Envia el carrusel vertical de La Fiore al buzon de TikTok.")
    p.add_argument("--set", type=int, help="numero de set (1-10)")
    p.add_argument("--dry-run", action="store_true", help="no llama a la API")
    p.add_argument("--verificar", action="store_true", help="comprueba credenciales y URLs")
    p.add_argument("--estado", action="store_true", help="que se envio y que falta")
    p.add_argument("--iniciar", action="store_true", help="crea estado_tiktok.json desde cero")
    args = p.parse_args()

    try:
        if args.iniciar:
            crear_estado()
            print("estado_tiktok.json creado con los 10 sets pendientes.")
            return 0
        if args.estado:
            return cmd_estado()
        if args.verificar:
            return cmd_verificar(config())
        return cmd_enviar(args)
    except ErrorTikTok as e:
        print("\nERROR: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
