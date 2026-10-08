#!/bin/bash
# Kalifai: descarga los vídeos (licencia Pexels, uso comercial gratis), los comprime y publica la web.
cd "$(dirname "$0")" || exit 1
command -v ffmpeg >/dev/null || { echo "Instalando ffmpeg..."; brew install ffmpeg || { echo "ERROR: no pude instalar ffmpeg"; exit 1; }; }
mkdir -p media /tmp/kalifai_v
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
bajar(){ # nombre url segundos
  if [ -s "media/$1.mp4" ]; then echo "OK $1 (ya estaba)"; return 0; fi
  echo "Descargando $1..."
  curl -fL --retry 3 -A "$UA" -e "https://www.pexels.com/" -o "/tmp/kalifai_v/$1.src" "$2" || { echo "FALLO al descargar $1"; return 1; }
  ffmpeg -loglevel error -y -i "/tmp/kalifai_v/$1.src" -t "$3" -vf "scale=-2:1280,fps=30" -an -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 26 -preset slow -movflags +faststart "media/$1.mp4" || { echo "FALLO al comprimir $1"; rm -f "media/$1.mp4"; return 1; }
  echo "OK $1 ($(du -h "media/$1.mp4" | cut -f1))"
}
F=0
bajar burj-hero   https://videos.pexels.com/video-files/29464628/12683301_1440_2560_60fps.mp4 10 || F=1
bajar burj-a      https://videos.pexels.com/video-files/34922677/14793314_1080_1920_60fps.mp4 6  || F=1
bajar burj-b      https://videos.pexels.com/video-files/36201517/15351886_1080_1920_30fps.mp4 10 || F=1
bajar burj-c      https://videos.pexels.com/video-files/37337933/15814428_1080_1920_30fps.mp4 11 || F=1
bajar luces       https://videos.pexels.com/video-files/5058333/5058333-uhd_1440_2560_25fps.mp4 14 || F=1
bajar dubai-noche https://videos.pexels.com/video-files/36174826/15340836_1440_2560_30fps.mp4 15 || F=1
if [ $F = 1 ]; then echo; echo "FALTA ALGÚN VÍDEO: no he publicado nada. Vuelve a pegar el mismo comando en unos minutos."; exit 1; fi
# Quitar los vídeos antiguos de Mixkit (licencia restringida)
git rm -q --ignore-unmatch hero/h1.mp4 hero/h2.mp4 hero/h3.mp4 hero/h4.mp4 hero/h5.mp4 2>/dev/null; rm -f hero/h1.mp4 hero/h2.mp4 hero/h3.mp4 hero/h4.mp4 hero/h5.mp4
rm -f subir_kalifai.sh.bak
git add -A && git commit -q -m "Kalifai: nuevo diseño negro con el Burj Khalifa en movimiento" && git push && echo && echo "LISTO: web publicada. Abre https://ai-agency-orbit.com en 1-2 minutos (Cmd+Shift+R para recargar)."
