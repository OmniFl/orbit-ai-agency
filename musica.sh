#!/bin/bash
cd "$(dirname "$0")" || exit 1
M=$(ls -t ~/Downloads/Kalifai_tech_house*.mp3 2>/dev/null | head -1)
if [ -n "$M" ]; then cp "$M" hero/ambiente.mp3 && echo "OK musica tech house"; else echo "AVISO: no encuentro Kalifai_tech_house.mp3 en Descargas; publico solo el arreglo del sonido"; fi
git config http.postBuffer 524288000; git add -A && git commit -q -m "Kalifai: sin sonido constante, musica tech house"; (git push || (sleep 5 && git push)) && echo && echo "LISTO. Recarga https://ai-agency-orbit.com con Cmd+Shift+R"
