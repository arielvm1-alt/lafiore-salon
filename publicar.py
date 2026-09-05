# -*- coding: utf-8 -*-
"""
Publicador de carruseles de La Fiore en Instagram (Content Publishing API de Meta).

Sube UN set por ejecucion: el siguiente pendiente segun estado.json.

Uso:
    python publicar.py                 # publica el siguiente set pendiente
    python publicar.py --set 3         # publica el set 03 aunque no toque
    python publicar.py --dry-run       # muestra que haria, sin llamar a la API
    python publicar.py --verificar     # comprueba token, cuenta y cuota
    python publicar.py --estado        # muestra el calendario de publicacion

Variables de entorno necesarias:
    IG_USER_ID       id de la cuenta profesional de Instagram
    IG_ACCESS_TOKEN  token de larga duracion
    IG_BASE_URL      URL publica donde viven las imagenes, sin barra final.
                     Ej: https://raw.githubusercontent.com/USUARIO/lafiore-salon/main/salida
    IG_API_VERSION   opcional, por defecto v26.0

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
ESTADO = os.path.join(RAIZ, "estado.json")

# La consola de Windows usa cp1252 y rompe con emojis y tildes: forzamos UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


LAMINAS = ["01_portada", "02_pagina", "03_pagina", "04_pagina", "05_pagina", "06_cierre"]
HISTORIA = "historia"      # 1080x1920, se publica como historia tras el carrusel

REINTENTOS = 4
ESPERA_BASE = 5           # segundos; se duplica en cada reintento
ESPERA_CONTENEDOR = 5     # segundos entre consultas de estado del contenedor
MAX_ESPERA_CONTENEDOR = 180


class ErrorPublicacion(Exception):
    pass


# --------------------------------------------------------------------------
# configuracion
# --------------------------------------------------------------------------

def config():
    faltan = [k for k in ("IG_USER_ID", "IG_ACCESS_TOKEN", "IG_BASE_URL") if not os.environ.get(k)]
    if faltan:
        raise ErrorPublicacion(
            "Faltan variables de entorno: %s\n"
            "Revisa el README, seccion 'Accesos'." % ", ".join(faltan))
    return {
        "user_id": os.environ["IG_USER_ID"].strip(),
        "token": os.environ["IG_ACCESS_TOKEN"].strip(),
        "base_url": os.environ["IG_BASE_URL"].strip().rstrip("/"),
        "version": os.environ.get("IG_API_VERSION", "v26.0").strip(),
    }


def _api(cfg, ruta):
    return "https://graph.facebook.com/%s/%s" % (cfg["version"], ruta.lstrip("/"))


# --------------------------------------------------------------------------
# llamadas HTTP
# --------------------------------------------------------------------------

def _peticion(url, datos=None, metodo=None):
    ctx = ssl.create_default_context()
    cuerpo = urllib.parse.urlencode(datos).encode("utf-8") if datos else None
    req = urllib.request.Request(url, data=cuerpo, method=metodo or ("POST" if datos else "GET"))
    req.add_header("User-Agent", "lafiore-salon-publisher/1.0")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(detalle).get("error", {})
            detalle = "%s (code %s, subcode %s)" % (
                err.get("message", detalle), err.get("code"), err.get("error_subcode"))
        except ValueError:
            pass
        raise ErrorPublicacion("HTTP %s en %s -> %s" % (e.code, url.split("?")[0], detalle))
    except urllib.error.URLError as e:
        raise ErrorPublicacion("Sin conexion con la API: %s" % e.reason)


def _con_reintento(descripcion, fn):
    espera = ESPERA_BASE
    ultimo = None
    for intento in range(1, REINTENTOS + 1):
        try:
            return fn()
        except ErrorPublicacion as e:
            ultimo = e
            if intento == REINTENTOS:
                break
            print("   ! %s fallo (intento %d/%d): %s" % (descripcion, intento, REINTENTOS, e))
            print("     reintento en %ds" % espera)
            time.sleep(espera)
            espera *= 2
    raise ErrorPublicacion("%s: agotados los reintentos. Ultimo error: %s" % (descripcion, ultimo))


# --------------------------------------------------------------------------
# estado
# --------------------------------------------------------------------------

def cargar_estado():
    if not os.path.exists(ESTADO):
        raise ErrorPublicacion("No existe estado.json. Ejecuta: python publicar.py --iniciar")
    with open(ESTADO, encoding="utf-8") as f:
        return json.load(f)


def guardar_estado(estado):
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
        f.write("\n")


def crear_estado():
    estado = {
        "zona_horaria": "America/Santiago",
        "orden": "un set por lunes y miercoles, 12:00 hora de Chile",
        "sets": [
            {"set": "set_%02d" % i, "estado": "pendiente",
             "publicado_en": None, "media_id": None, "intentos": 0}
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
# publicacion
# --------------------------------------------------------------------------

def caption_de(nombre_set):
    ruta = os.path.join(SALIDA, "captions.json")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)[nombre_set]


def urls_de(cfg, nombre_set):
    urls = []
    for lam in LAMINAS:
        local = os.path.join(SALIDA, nombre_set, lam + ".jpg")
        if not os.path.exists(local):
            raise ErrorPublicacion("Falta la imagen %s. Ejecuta primero el render." % local)
        urls.append("%s/%s/%s.jpg" % (cfg["base_url"], nombre_set, lam))
    return urls


def cuota(cfg):
    """Publicaciones consumidas en las ultimas 24 h (limite de Meta: 25)."""
    url = _api(cfg, "%s/content_publishing_limit?fields=quota_usage&access_token=%s"
               % (cfg["user_id"], urllib.parse.quote(cfg["token"])))
    datos = _peticion(url)
    try:
        return int(datos["data"][0]["quota_usage"])
    except (KeyError, IndexError, ValueError):
        return None


def crear_item(cfg, image_url):
    def hacer():
        return _peticion(_api(cfg, "%s/media" % cfg["user_id"]), {
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": cfg["token"],
        })
    return _con_reintento("subir %s" % image_url.rsplit("/", 1)[-1], hacer)["id"]


def crear_contenedor(cfg, hijos, caption):
    def hacer():
        return _peticion(_api(cfg, "%s/media" % cfg["user_id"]), {
            "media_type": "CAROUSEL",
            "children": ",".join(hijos),
            "caption": caption,
            "access_token": cfg["token"],
        })
    return _con_reintento("crear contenedor del carrusel", hacer)["id"]


def esperar_listo(cfg, creation_id):
    """Consulta el contenedor hasta que quede FINISHED."""
    limite = time.time() + MAX_ESPERA_CONTENEDOR
    while True:
        url = _api(cfg, "%s?fields=status_code,status&access_token=%s"
                   % (creation_id, urllib.parse.quote(cfg["token"])))
        datos = _peticion(url)
        codigo = datos.get("status_code")
        if codigo == "FINISHED":
            return
        if codigo in ("ERROR", "EXPIRED"):
            raise ErrorPublicacion("El contenedor quedo en %s: %s"
                                   % (codigo, datos.get("status", "sin detalle")))
        if time.time() > limite:
            raise ErrorPublicacion("El contenedor sigue en %s tras %ds"
                                   % (codigo, MAX_ESPERA_CONTENEDOR))
        print("   . contenedor %s, esperando..." % codigo)
        time.sleep(ESPERA_CONTENEDOR)


def publicar_contenedor(cfg, creation_id):
    def hacer():
        return _peticion(_api(cfg, "%s/media_publish" % cfg["user_id"]), {
            "creation_id": creation_id,
            "access_token": cfg["token"],
        })
    return _con_reintento("publicar el carrusel", hacer)["id"]


def publicar_historia(cfg, nombre_set):
    """Sube la portada 9:16 como historia. Devuelve el media_id o None."""
    local = os.path.join(SALIDA, nombre_set, HISTORIA + ".jpg")
    if not os.path.exists(local):
        print("   (sin historia.jpg, me la salto)")
        return None
    url = "%s/%s/%s.jpg" % (cfg["base_url"], nombre_set, HISTORIA)

    def crear():
        return _peticion(_api(cfg, "%s/media" % cfg["user_id"]), {
            "image_url": url,
            "media_type": "STORIES",
            "access_token": cfg["token"],
        })

    creation_id = _con_reintento("crear la historia", crear)["id"]
    esperar_listo(cfg, creation_id)
    media_id = publicar_contenedor(cfg, creation_id)
    print("   HISTORIA PUBLICADA. media_id = %s" % media_id)
    return media_id


def publicar_set(cfg, nombre_set, dry_run=False, sin_historia=False):
    caption = caption_de(nombre_set)
    urls = urls_de(cfg, nombre_set)

    print("Publicando %s (%d laminas)" % (nombre_set, len(urls)))
    for u in urls:
        print("   -", u)
    print("Caption:\n%s\n" % "\n".join("   | " + l for l in caption.split("\n")))

    if not sin_historia:
        print("Historia: %s/%s/%s.jpg" % (cfg["base_url"], nombre_set, HISTORIA))

    if dry_run:
        print("[dry-run] no se llamo a la API.")
        return None, None

    usadas = cuota(cfg)
    if usadas is not None:
        print("Cuota usada en 24 h: %d/25" % usadas)
        if usadas >= 25:
            raise ErrorPublicacion("Cuota de publicacion agotada. Reintenta mas tarde.")

    hijos = []
    for i, u in enumerate(urls, start=1):
        hijos.append(crear_item(cfg, u))
        print("   %d/%d subida (creation_id %s)" % (i, len(urls), hijos[-1]))

    contenedor = crear_contenedor(cfg, hijos, caption)
    print("   contenedor %s creado" % contenedor)

    esperar_listo(cfg, contenedor)
    print("   contenedor FINISHED")

    media_id = publicar_contenedor(cfg, contenedor)
    print("   PUBLICADO. media_id = %s" % media_id)

    historia_id = None
    if not sin_historia:
        print("\nPublicando la historia...")
        try:
            historia_id = publicar_historia(cfg, nombre_set)
        except ErrorPublicacion as e:
            # el carrusel ya esta publicado: la historia no debe tumbar la ejecucion
            print("   ! la historia fallo: %s" % e)
    return media_id, historia_id


# --------------------------------------------------------------------------
# comandos
# --------------------------------------------------------------------------

DIAS_DE_AVISO = 14        # por debajo de esto, --token-info avisa


def info_token(cfg):
    """Que clase de token hay cargado y cuanto le queda. Nunca lo imprime."""
    url = _api(cfg, "debug_token?input_token=%s&access_token=%s"
               % (urllib.parse.quote(cfg["token"]), urllib.parse.quote(cfg["token"])))
    datos = _peticion(url).get("data", {})
    caduca = int(datos.get("expires_at", 0) or 0)
    return {
        "tipo": datos.get("type", "?"),
        "valido": bool(datos.get("is_valid")),
        "caduca_en": caduca,                  # 0 = no caduca nunca
        "permisos": datos.get("scopes", []),
    }


def dias_restantes(caduca_en):
    """Dias hasta que caduque. None si no caduca nunca."""
    if not caduca_en:
        return None
    return int((caduca_en - time.time()) // 86400)


def token_de_pagina(cfg):
    """Token de la pagina dueña de la cuenta de Instagram, o None.

    Los tokens de pagina derivados de un token de usuario de larga duracion no
    caducan. Si el que esta cargado es de usuario, publicamos con el derivado.
    """
    try:
        url = _api(cfg, "me/accounts?fields=instagram_business_account,access_token"
                        "&access_token=%s" % urllib.parse.quote(cfg["token"]))
        for pagina in _peticion(url).get("data", []):
            ig = pagina.get("instagram_business_account") or {}
            if str(ig.get("id")) == str(cfg["user_id"]):
                return pagina.get("access_token")
    except ErrorPublicacion:
        return None
    return None


def cmd_token_info(cfg):
    """Informa del estado del token. Devuelve 3 si esta por caducar."""
    info = info_token(cfg)
    dias = dias_restantes(info["caduca_en"])

    print("Tipo de token:  %s" % info["tipo"])
    print("Valido:         %s" % ("si" if info["valido"] else "NO"))
    if dias is None:
        print("Caduca:         nunca")
    else:
        from datetime import datetime
        fecha = datetime.utcfromtimestamp(info["caduca_en"]).strftime("%d-%m-%Y")
        print("Caduca:         %s  (quedan %d dias)" % (fecha, dias))
    print("Permisos:       %s" % ", ".join(info["permisos"]) or "(ninguno)")

    if not info["valido"]:
        print("\nEl token ya no sirve. Hay que renovarlo: ver README, seccion 5.1c.")
        return 1

    if dias is None:
        print("\nEste token no caduca. No hay nada que renovar.")
        return 0

    print("\nEste token caduca. Para no depender de renovarlo a mano, cambialo por")
    print("un token de PAGINA, que no caduca nunca. Ver README, seccion 7.")

    if dias <= DIAS_DE_AVISO:
        print("\nAVISO: quedan %d dias. Renuevalo ya." % dias)
        return 3
    return 0


def cmd_verificar(cfg):
    url = _api(cfg, "%s?fields=id,username,media_count&access_token=%s"
               % (cfg["user_id"], urllib.parse.quote(cfg["token"])))
    datos = _peticion(url)
    print("Cuenta:      @%s (id %s)" % (datos.get("username", "?"), datos.get("id")))
    print("Media count: %s" % datos.get("media_count"))
    usadas = cuota(cfg)
    print("Cuota 24 h:  %s/25" % (usadas if usadas is not None else "?"))
    print("Version API: %s" % cfg["version"])
    print("Base URL:    %s" % cfg["base_url"])

    info = info_token(cfg)
    dias = dias_restantes(info["caduca_en"])
    print("Token:       %s, %s" % (
        info["tipo"], "no caduca" if dias is None else "caduca en %d dias" % dias))

    print("\nAccesos correctos.")
    if dias is not None and dias <= DIAS_DE_AVISO:
        print("AVISO: al token le quedan %d dias." % dias)
    return 0


def cmd_estado():
    estado = cargar_estado()
    print("Zona horaria: %s" % estado["zona_horaria"])
    for s in estado["sets"]:
        marca = {"publicado": "OK ", "pendiente": " . ", "error": "ERR"}.get(s["estado"], "  ?")
        extra = ""
        if s["publicado_en"]:
            extra = "  %s  media_id %s" % (s["publicado_en"], s["media_id"])
        elif s["intentos"]:
            extra = "  intentos: %d" % s["intentos"]
        print("  %s %s%s" % (marca, s["set"], extra))
    pendiente = siguiente_pendiente(estado)
    print("\nSiguiente: %s" % (pendiente["set"] if pendiente else "ninguno, todo publicado"))
    return 0


DIAS_DE_PUBLICACION = (0, 2)       # lunes y miercoles, en dias de Chile
HORA_DESDE, HORA_HASTA = 12, 20    # ventana local en la que se acepta publicar


def avisar_a_actions(clave, valor):
    """Deja un dato para los pasos siguientes del workflow. Fuera de GitHub, nada."""
    destino = os.environ.get("GITHUB_OUTPUT")
    if not destino:
        return
    try:
        with open(destino, "a", encoding="utf-8") as f:
            f.write("%s=%s\n" % (clave, valor))
    except OSError:
        pass


def dentro_de_la_ventana(desde=HORA_DESDE, hasta=HORA_HASTA):
    """True si en Santiago es dia de publicacion y la hora cae en la ventana.

    Esto antes exigia la hora exacta (ahora.hour == 12) y ahi se rompio la
    automatizacion. GitHub Actions no lanza el cron cuando se le pide: lo
    atrasa segun su carga, y se atrasa mucho. El lunes 31 de agosto la
    ejecucion llego a las 16:34 de Chile y el miercoles 2 de septiembre a
    las 14:19. Ninguna caia en la hora exacta, asi que ninguna publico, y
    nadie se entero: saltarse la publicacion no es un error y no abre
    incidencia. Instagram quedo detenido dos semanas.

    El candado contra publicar dos veces el mismo dia es la fecha
    -ya_se_publico_hoy-, no la hora. Con ese candado puesto la ventana puede
    ser ancha sin riesgo: vale mas salir a las tres de la tarde que no salir.
    """
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime
        ahora = datetime.now(ZoneInfo("America/Santiago"))
    except Exception as e:                                   # sin tzdata
        print("No se pudo leer la hora de Chile (%s)." % e)
        print("Esta ejecucion no publica: sin zona horaria no se sabe si toca.")
        print("Instala tzdata, o publica a mano con: python publicar.py")
        return False
    print("Hora en Santiago: %s" % ahora.strftime("%Y-%m-%d %H:%M %Z (%a)"))
    if ahora.weekday() not in DIAS_DE_PUBLICACION:
        print("Hoy no es lunes ni miercoles en Chile. Esta ejecucion no publica.")
        return False
    if not desde <= ahora.hour <= hasta:
        print("Son las %d h en Chile, fuera de la ventana de %d a %d h. No publica."
              % (ahora.hour, desde, hasta))
        return False
    return True


def fecha_chilena():
    """El dia de hoy en Santiago, o None si no se puede saber."""
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime
        return datetime.now(ZoneInfo("America/Santiago")).date()
    except Exception:
        return None


def ya_se_publico_hoy(estado):
    """True si algun set ya se publico hoy, en fecha de Chile.

    Este es el candado de verdad. El cron corre dos veces al dia a proposito
    (por el cambio de hora) y GitHub Actions no respeta el horario exacto: se
    atrasa segun su carga. Un 26 de agosto la ejecucion de las 15:00 UTC llego
    tarde y cayo dentro de la hora objetivo, asi que publicaron las dos y se
    gastaron dos sets. Comprobar la fecha lo hace imposible.
    """
    hoy = fecha_chilena()
    if hoy is None:
        return False
    from datetime import datetime
    for s in estado["sets"]:
        marca = s.get("publicado_en")
        if not marca:
            continue
        try:
            cuando = datetime.strptime(marca, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            continue
        try:
            from zoneinfo import ZoneInfo
            local = cuando.astimezone(ZoneInfo("America/Santiago")).date()
        except Exception:
            continue
        if local == hoy:
            print("Hoy (%s en Chile) ya se publico %s. Esta ejecucion no publica."
                  % (hoy.isoformat(), s["set"]))
            return True
    return False


def cmd_publicar(args):
    estado = cargar_estado()

    # Solo el cron pasa --respetar-hora. Una ejecucion a mano publica siempre,
    # que para eso se lanza a mano.
    if args.respetar_hora:
        if ya_se_publico_hoy(estado):
            avisar_a_actions("publico", "false")
            return 0
        if not dentro_de_la_ventana(args.desde, args.hasta):
            avisar_a_actions("publico", "false")
            return 0

    if args.set:
        nombre = "set_%02d" % args.set
        entrada = next((s for s in estado["sets"] if s["set"] == nombre), None)
        if entrada is None:
            raise ErrorPublicacion("No existe %s en estado.json" % nombre)
    else:
        entrada = siguiente_pendiente(estado)
        if entrada is None:
            print("No queda ningun set pendiente. Nada que hacer.")
            avisar_a_actions("publico", "false")
            return 0

    cfg = config()

    # Si el token cargado es de usuario, caduca. Publicamos con el token de la
    # pagina, que no caduca, y avisamos de cuanto le queda al de usuario.
    try:
        info = info_token(cfg)
        dias = dias_restantes(info["caduca_en"])
        if dias is not None:
            print("Aviso: el token cargado caduca en %d dias." % dias)
            if dias <= DIAS_DE_AVISO:
                print("       Renuevalo pronto: ver README, seccion 7.")
            de_pagina = token_de_pagina(cfg)
            if de_pagina:
                cfg["token"] = de_pagina
                print("       Publicando con el token de la pagina, que no caduca.")
    except ErrorPublicacion as e:
        print("Aviso: no se pudo revisar el token (%s). Se sigue igual." % e)

    try:
        media_id, historia_id = publicar_set(
            cfg, entrada["set"], dry_run=args.dry_run, sin_historia=args.sin_historia)
    except ErrorPublicacion:
        if not args.dry_run:
            entrada["estado"] = "error"
            entrada["intentos"] = entrada.get("intentos", 0) + 1
            guardar_estado(estado)
        raise

    if not args.dry_run:
        entrada["estado"] = "publicado"
        entrada["media_id"] = media_id
        entrada["historia_media_id"] = historia_id
        entrada["publicado_en"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        guardar_estado(estado)
    # TikTok solo sale detras de Instagram: si aqui no se publico, alla tampoco.
    avisar_a_actions("publico", "false" if args.dry_run else "true")
    return 0


def main():
    p = argparse.ArgumentParser(description="Publica un carrusel de La Fiore en Instagram.")
    p.add_argument("--set", type=int, help="numero de set a publicar (1-10)")
    p.add_argument("--dry-run", action="store_true", help="no llama a la API")
    p.add_argument("--sin-historia", action="store_true",
                   help="publica solo el carrusel, sin la historia")
    p.add_argument("--verificar", action="store_true", help="comprueba token, cuenta y cuota")
    p.add_argument("--estado", action="store_true", help="muestra el calendario de publicacion")
    p.add_argument("--token-info", action="store_true",
                   help="que clase de token hay y cuando caduca (nunca lo imprime)")
    p.add_argument("--iniciar", action="store_true", help="crea estado.json desde cero")
    p.add_argument("--respetar-hora", action="store_true",
                   help="solo publica si en Chile es lunes o miercoles dentro de la ventana (para el cron)")
    p.add_argument("--desde", type=int, default=HORA_DESDE,
                   help="hora de Chile desde la que se acepta publicar (defecto %d)" % HORA_DESDE)
    p.add_argument("--hasta", type=int, default=HORA_HASTA,
                   help="hora de Chile hasta la que se acepta publicar (defecto %d)" % HORA_HASTA)
    args = p.parse_args()

    try:
        if args.iniciar:
            crear_estado()
            print("estado.json creado con los 10 sets pendientes.")
            return 0
        if args.estado:
            return cmd_estado()
        if args.token_info:
            return cmd_token_info(config())
        if args.verificar:
            return cmd_verificar(config())
        return cmd_publicar(args)
    except ErrorPublicacion as e:
        print("\nERROR: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
