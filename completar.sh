#!/bin/bash
# Kalifai: añade Shanghái, Singapur y Nueva York al carrete (vídeos Pexels, uso comercial gratis) y publica.
cd "$(dirname "$0")" || exit 1
command -v ffmpeg >/dev/null || brew install ffmpeg
mkdir -p media /tmp/kalifai_v
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
bajar(){
  if [ -s "media/$1.mp4" ]; then echo "OK $1 (ya estaba)"; return; fi
  echo "Descargando $1..."
  curl -fL --retry 3 -A "$UA" -e "https://www.pexels.com/" -o "/tmp/kalifai_v/$1.src" "$2" || { echo "FALLO $1 (se publica sin él)"; return; }
  ffmpeg -loglevel error -y -i "/tmp/kalifai_v/$1.src" -t 12 -vf "scale='if(gt(iw,ih),-2,720)':'if(gt(iw,ih),720,-2)',fps=30" -an -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 26 -preset slow -movflags +faststart "media/$1.mp4" && echo "OK $1 ($(du -h media/$1.mp4 | cut -f1))" || rm -f "media/$1.mp4"
}
bajar shanghai   https://videos.pexels.com/video-files/31776600/13536901_2560_1440_30fps.mp4
bajar singapur   https://videos.pexels.com/video-files/15999788/15999788-uhd_2560_1440_30fps.mp4
bajar nueva-york https://videos.pexels.com/video-files/36206025/15353618_1440_2560_24fps.mp4
rm -f flow_kalifai.sh
git add -A && git commit -q -m "Kalifai: carrete de 4 ciudades y sonido continuo"; git push && echo && echo "LISTO. Abre https://ai-agency-orbit.com y recarga con Cmd+Shift+R"
