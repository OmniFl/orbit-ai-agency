"""Actualiza zona.json con titulares (título + enlace + medio) de fuentes RSS públicas.
Se ejecuta gratis en GitHub Actions cada 2 horas. Solo usa la librería estándar de Python.
No copia artículos ni imágenes: muestra el titular y enlaza al medio original."""
import json, re, html, datetime, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEEDS = [
    ("Trendencias", "https://www.trendencias.com/feedburner.xml", "estilo"),
    ("Vitónica", "https://www.vitonica.com/feedburner.xml", "sana"),
    ("Marca", "https://e00-xlk-ue-marca.uecdn.es/rss/googlenews/portada.xml", "deportes"),
    ("AS", "https://feeds.as.com/mrss-s/pages/as/site/as.com/portada", "deportes"),
    ("Mundo Deportivo", "https://www.mundodeportivo.com/rss/home.xml", "deportes"),
]
KW = {
    "piel": r"\bpiel\b|s[eé]rum|crema|protector solar|acn[eé]|arrugas|hidrata|retinol|vitamina c|manchas|ojeras|skincare|limpiador|exfolia|contorno",
    "belleza": r"maquillaje|labial|pintalabios|perfume|u[ñn]as|manicura|\bpelo\b|cabello|peinado|mechas|r[ií]mel|m[aá]scara de pesta|colorete|belleza|beauty|melena|corte de pelo|base de maquillaje",
    "moda": r"zapatilla|vestido|\blook|abrigo|chaqueta|falda|pantal[oó]n|bolso|botas|zara|mango|h&m|primark|tendencia|moda|outfit|jersey|camisa|blazer|vaqueros|prenda|colecci[oó]n|rebajas|sandalias|gabardina|cazadora",
}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 KalifaiZona/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()

def items(raw):
    root = ET.fromstring(raw)
    for it in root.iter("item"):
        t = clean(it.findtext("title")); l = (it.findtext("link") or "").strip()
        d = it.findtext("pubDate") or ""
        try: d = parsedate_to_datetime(d).astimezone(datetime.timezone.utc).isoformat()
        except Exception: d = ""
        if t and l.startswith("http"): yield t, l, d

def main():
    out, seen = [], set()
    for src, url, cat in FEEDS:
        try:
            n = 0
            for t, l, d in items(get(url)):
                if l in seen: continue
                c = cat
                if cat == "estilo":
                    low = t.lower(); c = next((k for k in ("piel", "belleza", "moda") if re.search(KW[k], low)), None)
                    if not c: continue
                seen.add(l); out.append({"c": c, "t": t, "l": l, "s": src, "d": d}); n += 1
                if n >= 25: break
            print("OK", src, n)
        except Exception as e:
            print("FALLA", src, e)
    out.sort(key=lambda x: x["d"], reverse=True)
    json.dump({"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "items": out},
              open("zona.json", "w"), ensure_ascii=False)

if __name__ == "__main__":
    main()
