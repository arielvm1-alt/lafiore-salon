# Archivos de verificación

Aquí van los archivos que las plataformas piden alojar para comprobar que la
URL es nuestra. El workflow `paginas.yml` los copia a la raíz del sitio.

- `tiktok*.txt` — verificación de propiedad de URL de TikTok. Es un token
  público, pensado para publicarse: no es una credencial. Si se borra, la
  verificación se cae y el publicador de TikTok deja de poder descargar
  las imágenes.
