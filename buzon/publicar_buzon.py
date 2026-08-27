# -*- coding: utf-8 -*-
"""
Buzon de replica automatica a TikTok.

Todo lo que caiga en buzon/entrada/ (normalmente lo baja rclone desde la
carpeta "Buzon TikTok" de Google Drive) se envia como borrador al buzon de
TikTok de @la_fiore.cl, en modo MEDIA_UPLOAD: llega la notificacion al
telefono y se publica de un toque.

Reglas de la carpeta de entrada:
  - Una subcarpeta = un envio. El nombre de la carpeta se usa como texto si
    no hay texto.txt dentro.
  - 2 o mas imagenes  -> carrusel de fotos (orden alfabetico de archivo).
  - 1 imagen          -> foto suelta (sirve para historia: se elige el
                         formato al publicar desde el telefono).
  - un .mp4           -> video. Si ademas hay imagenes, se ignoran con aviso.
  - texto.txt         -> el copy del post (solo aplica a fotos y carruseles;
                         los borradores de video no aceptan texto por API).
  - Una carpeta se envia una sola vez. Para otro post, otra carpeta.

Antes de enviar, el script renombra carpeta y archivos a nombres seguros
para URL (minusculas, sin acentos ni espacios), y espera a que GitHub Pages
sirva las URLs, porque TikTok las descarga desde ahi.

Uso:
    python buzon/publicar_buzon.py              # procesa todo lo pendiente
    python buzon/publicar_buzon.py --preparar   # solo renombra a nombres de
                                                # URL y dice cuantos hay listos
                                                # (el workflow lo usa antes de
                                                # desplegar Pages)
    python buzon/publicar_buzon.py --dry-run    # muestra que enviaria
    python buzon/publicar_buzon.py --estado     # que se envio y que falta

Variables de entorno:
    TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET / TIKTOK_REFRESH_TOKEN
        las mismas de publicar_tiktok.py (o credenciales_tiktok.txt en local)
    BUZON_BASE_URL
        URL publica de buzon/entrada, bajo el prefijo verificado en TikTok.
        Por defecto: https://arielvm1-alt.github.io/lafiore-salon/buzon
    BUZON_RCLONE_REMOTE (opcional)
        remoto rclone de la carpeta de Drive, ej: gdrive:Buzon TikTok.
        Si esta definido y rclone existe, se deja un archivo
        "ENVIADO A TIKTOK.txt" en la carpeta de Drive como confirmacion.
    BUZON_MINUTOS_REPOSO (opcional, defecto 10)
        minutos sin cambios que debe tener una carpeta antes de enviarse,
        para no pillar una subida a medias desde el telefono.

Sin dependencias externas: solo biblioteca estandar (y rclone si se quiere
la marca de confirmacion en Drive).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ENTRADA = os.path.join(AQUI, "entrada")
ESTADO = os.path.join(AQUI, "estado_buzon.json")

# Reusa las funciones de red y de credenciales del publicador de sets.
sys.path.insert(0, RAIZ)
from publicar_tiktok import (  # noqa: E402
    API, ErrorTikTok, _con_reintento, _del_archivo_local, _peticion,
    _url_viva, token_de_acceso,
)

IMAGENES = (".jpg", ".jpeg", ".png", ".webp")
VIDEOS = (".mp4",)
MAX_INTENTOS = 5
ESPERA_PAGES_SEG = 360  # cuanto esperar a que Pages sirva las URLs nuevas

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# --------------------------------------------------------------------------
# configuracion
# --------------------------------------------------------------------------

def config():
    _del_archivo_local()
    faltan = [k for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET",
                          "TIKTOK_REFRESH_TOKEN") if not os.environ.get(k)]
    if faltan:
        raise ErrorTikTok("Faltan variables de entorno: %s" % ", ".join(faltan))
    base = os.environ.get(
        "BUZON_BASE_URL",
        "https://arielvm1-alt.github.io/lafiore-salon/buzon").strip().rstrip("/")
    return {
        "client_key": os.environ["TIKTOK_CLIENT_KEY"].strip(),
        "client_secret": os.environ["TIKTOK_CLIENT_SECRET"].strip(),
        "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN"].strip(),
        "base_url": base,
        "rclone_remote": os.environ.get("BUZON_RCLONE_REMOTE", "").strip(),
        "minutos_reposo": int(os.environ.get("BUZON_MINUTOS_REPOSO", "10")),
    }


# --------------------------------------------------------------------------
# estado
# --------------------------------------------------------------------------

def cargar_estado():
    if not os.path.exists(ESTADO):
        return {"posts": {}}
    with open(ESTADO, encoding="utf-8") as f:
        return json.load(f)


def guardar_estado(estado):
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
        f.write("\n")


# --------------------------------------------------------------------------
# nombres seguros para URL
# --------------------------------------------------------------------------

def slug(texto, conservar_ext=False):
    base, ext = (os.path.splitext(texto) if conservar_ext else (texto, ""))
    limpio = unicodedata.normalize("NFKD", base)
    limpio = limpio.encode("ascii", "ignore").decode("ascii").lower()
    limpio = re.sub(r"[^a-z0-9]+", "-", limpio).strip("-") or "post"
    return limpio + ext.lower()


def renombrar_seguro(ruta_actual, nombre_nuevo):
    destino = os.path.join(os.path.dirname(ruta_actual), nombre_nuevo)
    if ruta_actual == destino:
        return destino
    n = 2
    base, ext = os.path.splitext(nombre_nuevo)
    while os.path.exists(destino):
        destino = os.path.join(os.path.dirname(ruta_actual), "%s-%d%s" % (base, n, ext))
        n += 1
    os.rename(ruta_actual, destino)
    return destino


# --------------------------------------------------------------------------
# lectura de la entrada
# --------------------------------------------------------------------------

def clasificar(carpeta):
    """Devuelve (tipo, archivos_de_medios, texto) de una carpeta de entrada."""
    archivos = sorted(os.listdir(carpeta))
    imagenes = [a for a in archivos if a.lower().endswith(IMAGENES)]
    videos = [a for a in archivos if a.lower().endswith(VIDEOS)]

    texto = None
    ruta_texto = os.path.join(carpeta, "texto.txt")
    if os.path.exists(ruta_texto):
        with open(ruta_texto, encoding="utf-8-sig") as f:
            texto = f.read().strip()

    if videos:
        if imagenes:
            print("   ! %s tiene video e imagenes: se envia solo el video %s"
                  % (os.path.basename(carpeta), videos[0]))
        return "video", [videos[0]], texto
    if len(imagenes) >= 2:
        return "carrusel", imagenes, texto
    if len(imagenes) == 1:
        return "foto", imagenes, texto
    return None, [], texto


def en_reposo(carpeta, minutos):
    """True si nada dentro de la carpeta cambio en los ultimos N minutos."""
    reciente = 0
    for raiz, _, archivos in os.walk(carpeta):
        for a in archivos:
            try:
                reciente = max(reciente, os.path.getmtime(os.path.join(raiz, a)))
            except OSError:
                pass
    return reciente > 0 and (time.time() - reciente) >= minutos * 60


def pendientes(estado, minutos_reposo):
    """Carpetas de entrada listas para enviar, ya con nombres seguros."""
    if not os.path.isdir(ENTRADA):
        return []
    listos = []
    for nombre in sorted(os.listdir(ENTRADA)):
        ruta = os.path.join(ENTRADA, nombre)
        if not os.path.isdir(ruta):
            continue
        nombre_seguro = slug(nombre)
        registro = estado["posts"].get(nombre_seguro)
        if registro and registro["estado"] == "enviado":
            continue
        if registro and registro.get("intentos", 0) >= MAX_INTENTOS:
            print("   ! %s supero los %d intentos: se salta. Borra su entrada"
                  " de estado_buzon.json para reintentar." % (nombre_seguro, MAX_INTENTOS))
            continue
        if not en_reposo(ruta, minutos_reposo):
            print("   . %s tiene cambios de hace menos de %d min:"
                  " se deja para la proxima pasada." % (nombre, minutos_reposo))
            continue
        ruta = renombrar_seguro(ruta, nombre_seguro)
        for archivo in os.listdir(ruta):
            completa = os.path.join(ruta, archivo)
            if os.path.isfile(completa):
                renombrar_seguro(completa, slug(archivo, conservar_ext=True))
        # se guarda el nombre original: en Drive la carpeta sigue llamandose asi
        listos.append((ruta, nombre))
    return listos


# --------------------------------------------------------------------------
# envio
# --------------------------------------------------------------------------

def esperar_urls(urls, dry_run):
    if dry_run:
        return
    limite = time.time() + ESPERA_PAGES_SEG
    faltan = list(urls)
    while faltan and time.time() < limite:
        faltan = [u for u in faltan if not _url_viva(u)]
        if faltan:
            print("   ... esperando a que Pages sirva %d archivo(s)" % len(faltan))
            time.sleep(15)
    if faltan:
        raise ErrorTikTok(
            "GitHub Pages no sirve estas URLs (y TikTok no podra bajarlas):\n"
            + "\n".join("   - " + u for u in faltan))


def enviar_post(cfg, carpeta, dry_run=False):
    nombre = os.path.basename(carpeta)
    tipo, archivos, texto = clasificar(carpeta)
    if tipo is None:
        print("   ! %s no tiene imagenes ni video: se ignora." % nombre)
        return None, None, None

    if texto is None:
        texto = nombre.replace("-", " ").strip().capitalize()
    urls = ["%s/%s/%s" % (cfg["base_url"], urllib.parse.quote(nombre),
                          urllib.parse.quote(a)) for a in archivos]

    print("Enviando %s (%s) al buzon de TikTok" % (nombre, tipo))
    for u in urls:
        print("   -", u)

    if dry_run:
        print("   [dry-run] no se llamo a la API.")
        return tipo, archivos, None

    esperar_urls(urls, dry_run)
    token = token_de_acceso(cfg)

    if tipo == "video":
        # Los borradores de video van por el endpoint del buzon y no aceptan
        # texto: el copy se escribe al publicar desde el telefono.
        def hacer():
            return _peticion(API + "/post/publish/inbox/video/init/", {
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": urls[0],
                },
            }, cabeceras={"Authorization": "Bearer " + token}, json_body=True)
    else:
        def hacer():
            return _peticion(API + "/post/publish/content/init/", {
                "post_info": {
                    "title": texto[:90],
                    "description": texto,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "photo_cover_index": 0,
                    "photo_images": urls,
                },
                "post_mode": "MEDIA_UPLOAD",
                "media_type": "PHOTO",
            }, cabeceras={"Authorization": "Bearer " + token}, json_body=True)

    datos = _con_reintento("enviar " + nombre, hacer)
    publish_id = (datos.get("data") or {}).get("publish_id")
    if not publish_id:
        raise ErrorTikTok("TikTok no devolvio publish_id: %s" % json.dumps(datos)[:300])
    print("   ENVIADO. publish_id = %s" % publish_id)
    print("   Revisa la notificacion en la app de TikTok para publicarlo.")
    return tipo, archivos, publish_id


def marcar_en_drive(cfg, nombre_original):
    """Deja ENVIADO A TIKTOK.txt en la carpeta de Drive, si hay rclone."""
    if not cfg["rclone_remote"] or not shutil.which("rclone"):
        return
    marca = os.path.join(AQUI, "_marca_enviado.txt")
    with open(marca, "w", encoding="utf-8") as f:
        f.write("Este post ya se envio al buzon de TikTok el %s.\n"
                "Publicalo desde la notificacion de la app.\n"
                % time.strftime("%Y-%m-%d %H:%M"))
    destino = "%s/%s/ENVIADO A TIKTOK.txt" % (cfg["rclone_remote"], nombre_original)
    try:
        subprocess.run(["rclone", "copyto", marca, destino],
                       check=True, capture_output=True, timeout=120)
        print("   Marca de enviado dejada en Drive.")
    except Exception as e:
        print("   ! No se pudo dejar la marca en Drive: %s" % e)
    finally:
        os.remove(marca)


# --------------------------------------------------------------------------
# comandos
# --------------------------------------------------------------------------

def cmd_estado():
    estado = cargar_estado()
    if not estado["posts"]:
        print("Todavia no se ha enviado nada desde el buzon.")
        return 0
    for nombre, p in sorted(estado["posts"].items()):
        marca = {"enviado": "OK ", "error": "ERR"}.get(p["estado"], "  ?")
        print("  %s %-30s %-8s %s" % (marca, nombre, p.get("tipo", ""),
                                      p.get("enviado_en") or
                                      "intentos: %d" % p.get("intentos", 0)))
    return 0


def cmd_preparar():
    """Renombra lo pendiente a nombres de URL, sin credenciales ni API.

    Deja cada carpeta registrada en el estado con su nombre original de
    Drive: con eso el workflow construye los filtros de rclone y la carpeta
    ya renombrada no se vuelve a bajar (ni a enviar) dos veces.
    """
    estado = cargar_estado()
    minutos = int(os.environ.get("BUZON_MINUTOS_REPOSO", "10"))
    listos = pendientes(estado, minutos)
    for ruta, origen in listos:
        estado["posts"].setdefault(
            os.path.basename(ruta),
            {"origen": origen, "estado": "pendiente", "intentos": 0})
    guardar_estado(estado)
    print("Listos para enviar: %d" % len(listos))
    for ruta, origen in listos:
        print("   -", os.path.basename(ruta))
    return 0


def cmd_filtros_rclone():
    """Imprime un filtro de rclone que excluye las carpetas ya registradas."""
    estado = cargar_estado()
    print("- /ENVIADO A TIKTOK.txt")
    for p in estado["posts"].values():
        print("- /%s/**" % p.get("origen"))
    print("- **/ENVIADO A TIKTOK.txt")
    return 0


def cmd_enviar(args):
    cfg = config()
    estado = cargar_estado()
    listos = pendientes(estado, cfg["minutos_reposo"])
    if not listos:
        print("No hay nada pendiente en el buzon.")
        return 0

    fallos = 0
    for carpeta, nombre_original in listos:
        nombre = os.path.basename(carpeta)
        registro = estado["posts"].setdefault(
            nombre, {"origen": nombre_original, "estado": "pendiente", "intentos": 0})
        try:
            tipo, archivos, publish_id = enviar_post(cfg, carpeta, args.dry_run)
        except ErrorTikTok as e:
            print("   ERROR con %s: %s" % (nombre, e), file=sys.stderr)
            registro["estado"] = "error"
            registro["intentos"] = registro.get("intentos", 0) + 1
            fallos += 1
            continue
        if tipo is None or args.dry_run:
            if tipo is None:
                estado["posts"].pop(nombre, None)
            continue
        registro.update({
            "estado": "enviado",
            "tipo": tipo,
            "archivos": archivos,
            "publish_id": publish_id,
            "enviado_en": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        })
        marcar_en_drive(cfg, registro["origen"])
        time.sleep(3)

    if not args.dry_run:
        guardar_estado(estado)
    return 1 if fallos else 0


def main():
    p = argparse.ArgumentParser(
        description="Replica en TikTok lo que caiga en buzon/entrada/.")
    p.add_argument("--dry-run", action="store_true", help="no llama a la API")
    p.add_argument("--preparar", action="store_true",
                   help="solo renombra y cuenta lo pendiente")
    p.add_argument("--filtros-rclone", action="store_true",
                   help="imprime los filtros para no rebajar lo ya enviado")
    p.add_argument("--estado", action="store_true", help="que se envio")
    args = p.parse_args()
    try:
        if args.estado:
            return cmd_estado()
        if args.preparar:
            return cmd_preparar()
        if args.filtros_rclone:
            return cmd_filtros_rclone()
        return cmd_enviar(args)
    except ErrorTikTok as e:
        print("\nERROR: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
