"""Kalifai Música: listas de éxitos actualizadas (Apple Music, herramientas de marketing oficiales)
con previsualización de 30 s. Escribe app/musica.json. Se ejecuta en GitHub Actions o en el Mac.
Solo librería estándar (usa curl si está disponible)."""
import json, subprocess, time, datetime, urllib.request

COUNTRIES = [("es", "España"), ("us", "EE. UU."), ("gb", "Reino Unido"), ("mx", "México"), ("co", "Colombia"),
             ("ar", "Argentina"), ("fr", "Francia"), ("it", "Italia"), ("pt", "Portugal"), ("br", "Brasil"),
             ("de", "Alemania"), ("jp", "Japón")]
UA = "KalifaiMusica/1.0 (+https://ai-agency-orbit.com)"

def get(url):
    try:
        r = subprocess.run(["curl", "-s", "-f", "-L", "--max-time", "40", "-A", UA, url], capture_output=True)
        if r.returncode == 0: return json.loads(r.stdout)
    except FileNotFoundError:
        pass
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
        return json.loads(r.read())

def chart(cc):
    for host in ("https://rss.marketingtools.apple.com", "https://rss.applemarketingtools.com"):
        try:
            d = get(f"{host}/api/v2/{cc}/music/most-played/50/songs.json")
            return d["feed"]["results"]
        except Exception as e:
            last = e
    raise last

def previews(ids, cc):
    out = {}
    for i in range(0, len(ids), 25):
        try:
            d = get("https://itunes.apple.com/lookup?country=" + cc + "&id=" + ",".join(ids[i:i + 25]))
            for r in d.get("results", []):
                if r.get("previewUrl"): out[str(r.get("trackId"))] = r["previewUrl"]
        except Exception as e:
            print("   sin previews", e)
        time.sleep(1.5)
    return out

def main():
    data = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "charts": {}}
    try:
        old = json.load(open("app/musica.json"))
    except Exception:
        old = {"charts": {}}
    for cc, name in COUNTRIES:
        try:
            res = chart(cc); pv = previews([r["id"] for r in res], cc)
            data["charts"][cc] = {"name": name, "songs": [{
                "t": r.get("name", ""), "a": r.get("artistName", ""), "img": (r.get("artworkUrl100") or "").replace("100x100", "200x200"),
                "url": r.get("url", ""), "p": pv.get(str(r["id"]), ""), "g": (r.get("genres") or [{}])[0].get("name", "")}
                for r in res]}
            print("OK", name, len(res), "canciones,", len(pv), "con preview")
        except Exception as e:
            print("FALLA", name, e)
            if cc in old.get("charts", {}): data["charts"][cc] = old["charts"][cc]
        time.sleep(2)
    json.dump(data, open("app/musica.json", "w"), ensure_ascii=False, separators=(",", ":"))

if __name__ == "__main__":
    main()
