# -*- coding: utf-8 -*-
"""
Graba el video demo para la auditoria de TikTok.

    python grabar_demo.py

Abre un Chromium visible que graba en video y recorre el flujo completo del
publicador: autorizacion con Login Kit (la contrasena la escribe la persona,
el script solo espera), perfil conectado, consulta del creador, seleccion de
carrusel, privacidad sin valor por defecto, confirmacion de derechos, envio
como borrador (video.upload) y publicacion directa (video.publish) hasta
PUBLISH_COMPLETE.

Para que la autorizacion salga en camara, el conector arranca con una copia
de las credenciales SIN token de refresco: la pagina parte desconectada.
El archivo real no se toca.

Salida:  demo-tiktok.mp4  (H.264, listo para subir al formulario de revision)
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
CREDENCIALES = os.path.join(RAIZ, "credenciales_tiktok.txt")
PUERTO = 8724
COMPOSER = "http://localhost:%d/publicador.html" % PUERTO
MP4 = os.path.join(RAIZ, "demo-tiktok.mp4")

SET_DEMO = 2                  # Color: contenido real, aun no publicado en TikTok
PRIVACIDAD_DEMO = "SELF_ONLY"  # la prueba no debe quedar visible a nadie

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def log(msg):
    print(msg, flush=True)


def conector_vivo():
    try:
        with urllib.request.urlopen("http://localhost:%d/salud" % PUERTO, timeout=2):
            return True
    except Exception:
        return False


def matar_conector():
    """Apaga cualquier conector previo escuchando en el puerto."""
    try:
        salida = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                                timeout=15).stdout
        pids = set()
        for linea in salida.splitlines():
            if (":%d" % PUERTO) in linea and "LISTENING" in linea:
                pids.add(linea.split()[-1])
        for pid in pids:
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        if pids:
            time.sleep(1)
    except Exception:
        pass


def main():
    if not os.path.exists(CREDENCIALES):
        raise SystemExit("Falta credenciales_tiktok.txt: corre antes "
                         "obtener_credenciales_tiktok.py")

    # -- credenciales sin refresh, para que la autorizacion salga en camara --
    tmp = tempfile.mkdtemp(prefix="demo_tiktok_")
    cred_demo = os.path.join(tmp, "credenciales_demo.txt")
    with open(CREDENCIALES, encoding="utf-8") as f, \
         open(cred_demo, "w", encoding="utf-8") as g:
        for linea in f:
            if not linea.startswith("TIKTOK_REFRESH_TOKEN"):
                g.write(linea)

    matar_conector()
    entorno = dict(os.environ, CONECTOR_CREDENCIALES=cred_demo,
                   PYTHONIOENCODING="utf-8")
    conector = subprocess.Popen([sys.executable, os.path.join(RAIZ, "conector_demo.py")],
                                env=entorno, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
    for _ in range(20):
        if conector_vivo():
            break
        time.sleep(0.5)
    else:
        conector.kill()
        raise SystemExit("El conector no arranco.")
    log("Conector de demo arriba (sin sesion previa).")

    from playwright.sync_api import sync_playwright

    videos = os.path.join(tmp, "video")
    exito = False
    # Perfil persistente con el Chrome real instalado en el equipo: misma
    # huella que un Chrome normal (Google no lo rechaza) y la sesion queda
    # guardada, asi que un reintento no vuelve a pedir el login.
    perfil = os.path.join(RAIZ, ".perfil_demo")
    try:
        with sync_playwright() as pw:
            contexto = pw.chromium.launch_persistent_context(
                perfil,
                channel="chrome",
                headless=False,
                viewport={"width": 1280, "height": 720},
                record_video_dir=videos,
                record_video_size={"width": 1280, "height": 720},
                locale="es-CL",
                args=["--window-size=1300,800",
                      "--disable-blink-features=AutomationControlled"],
            )
            pagina = contexto.pages[0] if contexto.pages else contexto.new_page()
            # Nada de trucos con window.open: el login de Google necesita su
            # propia ventana emergente y se rompe si se le fuerza a una sola
            # pestana. La autorizacion de TikTok va directo en esta pestana y
            # la emergente de Google vive y muere por su cuenta.

            log("Abriendo el publicador...")
            pagina.goto(COMPOSER)
            pagina.wait_for_timeout(3000)

            log("Voy a la autorizacion de TikTok.")
            import json as _json
            with urllib.request.urlopen("http://localhost:%d/auth-url" % PUERTO,
                                        timeout=10) as r:
                auth_url = _json.loads(r.read().decode("utf-8"))["url"]
            pagina.goto(auth_url)

            log("")
            log("=" * 62)
            log("TU TURNO, en la ventana de grabacion:")
            log("  1. Inicia sesion como prefieras: el QR es lo mas rapido, y")
            log("     'Continuar con Google' ahora si funciona (abre su propia")
            log("     ventanita; completala ahi y se cierra sola).")
            log("  2. Acepta los TRES permisos de la app.")
            log("Tienes 5 minutos. El video sigue grabando.")
            log("=" * 62)
            pagina.wait_for_url("**/autorizado.html*", timeout=300000)
            pagina.wait_for_timeout(2000)     # que se vea la pagina de retorno

            consulta = urllib.parse.parse_qs(
                urllib.parse.urlparse(pagina.url).query)
            codigo = (consulta.get("code") or [""])[0]
            if not codigo:
                raise SystemExit("TikTok no devolvio codigo: %s" % pagina.url)
            log("Codigo recibido. Vuelvo al publicador.")

            pagina.goto(COMPOSER)
            pagina.wait_for_timeout(1500)
            pagina.fill("#codigo", codigo)
            pagina.wait_for_timeout(800)
            pagina.click("#btn-canjear")
            pagina.wait_for_selector("#con-conexion:not(.oculto)", timeout=30000)
            log("Perfil conectado en pantalla.")
            pagina.wait_for_timeout(2500)

            log("Elijo el set %d y espero la vista previa." % SET_DEMO)
            pagina.select_option("#set", str(SET_DEMO))
            pagina.wait_for_timeout(4000)

            pagina.click("#privacidad")
            pagina.wait_for_timeout(1200)
            pagina.select_option("#privacidad", PRIVACIDAD_DEMO)
            pagina.wait_for_timeout(1000)
            pagina.check("#acepta-musica")
            pagina.wait_for_timeout(1200)

            log("Envio como borrador (video.upload)...")
            pagina.click("#btn-borrador")
            pagina.wait_for_function(
                "document.getElementById('estado-envio').textContent"
                ".includes('publish_id')", timeout=120000)
            pagina.wait_for_timeout(9000)     # que se vea el estado

            log("Publicacion directa (video.publish)...")
            pagina.click("#btn-directo")
            pagina.wait_for_function(
                "(/PUBLISH_COMPLETE|FAILED|Error/).test("
                "document.getElementById('estado-envio').textContent)",
                timeout=150000)
            estado = pagina.inner_text("#estado-envio")
            log("Estado final en pantalla: %s" % estado.replace("\n", " | "))
            pagina.wait_for_timeout(4000)

            exito = "PUBLISH_COMPLETE" in estado
            contexto.close()                  # cierra y escribe el video
    finally:
        conector.kill()

    # ------------------------------------------------------------- a mp4
    webms = [os.path.join(videos, f) for f in os.listdir(videos)
             if f.endswith(".webm")] if os.path.isdir(videos) else []
    if not webms:
        raise SystemExit("No quedo video grabado.")
    webm = max(webms, key=os.path.getsize)

    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    log("Convirtiendo a mp4...")
    subprocess.run([ffmpeg, "-y", "-i", webm, "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", MP4],
                   check=True, capture_output=True)
    mb = os.path.getsize(MP4) / 1024 / 1024
    log("Video listo: %s  (%.1f MB)" % (MP4, mb))
    if not exito:
        log("OJO: la publicacion directa NO llego a PUBLISH_COMPLETE. "
            "Revisa si la cuenta estaba en privado y repite la grabacion.")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if exito else 2


if __name__ == "__main__":
    sys.exit(main())
