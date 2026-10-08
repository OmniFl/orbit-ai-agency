#!/bin/bash
cd "$(dirname "$0")" || exit 1
git rm -q --ignore-unmatch hero/ambiente.mp3; rm -f hero/ambiente.mp3
M=$(mdfind -name "Kalifai_afro_Desierto_PURO" 2>/dev/null | grep -i "\.mp3$" | head -1)
if [ -n "$M" ]; then cp "$M" hero/musica.mp3 && echo "OK musica Desierto puro"; else echo "Sin musica por ahora: la web queda en silencio salvo el sonido corto de Kalifai al entrar"; fi
rm -f musica.sh completar.sh
git config http.postBuffer 524288000; git add -A && git commit -q -m "Kalifai: sin piano ni sonido continuo"; (git push || (sleep 5 && git push)) && echo && echo "LISTO. Cierra la pestaña de la web y vuelve a abrir https://ai-agency-orbit.com"
