#!/bin/bash
cd "$(dirname "$0")" || exit 1
M=$(ls -t ~/Downloads/Kalifai_musica_nueva*.mp3 2>/dev/null | head -1)
if [ -n "$M" ]; then cp "$M" hero/ambiente.mp3 && echo "OK musica nueva"; else echo "AVISO: no encuentro Kalifai_musica_nueva.mp3 en Descargas; publico solo el arreglo del sonido"; fi
git config http.postBuffer 524288000; git add -A && git commit -q -m "Kalifai: sin sonido constante, musica nueva"; (git push || (sleep 5 && git push)) && echo && echo "LISTO. Recarga https://ai-agency-orbit.com con Cmd+Shift+R"
