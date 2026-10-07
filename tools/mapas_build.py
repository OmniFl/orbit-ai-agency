"""Kalifai Mapas: genera los paquetes de lugares por ciudad (app/mapas/<ciudad>.json).
Datos abiertos de OpenStreetMap (ODbL) vía Overpass. Una consulta por ciudad: uso mínimo y respetuoso.
Uso:  python3 tools/mapas_build.py            (todas las ciudades)
      python3 tools/mapas_build.py cordoba    (solo una)
Solo librería estándar de Python. Ejecutar desde la carpeta raíz del repositorio."""
import json, math, os, sys, time, urllib.request, urllib.parse, datetime

CITIES = [  # slug, nombre, país, lat, lon
    ("cordoba", "Córdoba", "España", 37.8847, -4.7792), ("sevilla", "Sevilla", "España", 37.3891, -5.9845),
    ("granada", "Granada", "España", 37.1773, -3.5986), ("malaga", "Málaga", "España", 36.7213, -4.4214),
    ("madrid", "Madrid", "España", 40.4168, -3.7038), ("barcelona", "Barcelona", "España", 41.3874, 2.1686),
    ("valencia", "Valencia", "España", 39.4699, -0.3763), ("lisboa", "Lisboa", "Portugal", 38.7223, -9.1393),
    ("oporto", "Oporto", "Portugal", 41.1579, -8.6291), ("paris", "París", "Francia", 48.8566, 2.3522),
    ("niza", "Niza", "Francia", 43.7102, 7.2620), ("londres", "Londres", "Reino Unido", 51.5072, -0.1276),
    ("edimburgo", "Edimburgo", "Reino Unido", 55.9533, -3.1883), ("dublin", "Dublín", "Irlanda", 53.3498, -6.2603),
    ("roma", "Roma", "Italia", 41.9028, 12.4964), ("milan", "Milán", "Italia", 45.4642, 9.1900),
    ("florencia", "Florencia", "Italia", 43.7696, 11.2558), ("venecia", "Venecia", "Italia", 45.4408, 12.3155),
    ("berlin", "Berlín", "Alemania", 52.5200, 13.4050), ("munich", "Múnich", "Alemania", 48.1351, 11.5820),
    ("amsterdam", "Ámsterdam", "Países Bajos", 52.3676, 4.9041), ("bruselas", "Bruselas", "Bélgica", 50.8503, 4.3517),
    ("viena", "Viena", "Austria", 48.2082, 16.3738), ("praga", "Praga", "Chequia", 50.0755, 14.4378),
    ("budapest", "Budapest", "Hungría", 47.4979, 19.0402), ("atenas", "Atenas", "Grecia", 37.9838, 23.7275),
    ("copenhague", "Copenhague", "Dinamarca", 55.6761, 12.5683), ("estocolmo", "Estocolmo", "Suecia", 59.3293, 18.0686),
    ("zurich", "Zúrich", "Suiza", 47.3769, 8.5417), ("tirana", "Tirana", "Albania", 41.3275, 19.8187),
]
ENDPOINTS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"]
CAP = {"ver": 160, "comer": 260, "ocio": 140, "parking": 220}
KEEP = ["cuisine", "opening_hours", "fee", "capacity", "website", "wheelchair", "parking", "charge", "maxstay",
        "tourism", "historic", "amenity", "leisure", "name:en", "diet:vegetarian", "diet:vegan", "outdoor_seating", "stars"]

def bbox(lat, lon, r=0.05):
    dl = r / max(0.3, math.cos(math.radians(lat)))
    return round(lat - r, 4), round(lon - dl, 4), round(lat + r, 4), round(lon + dl, 4)

def query(b):
    s, w, n, e = b; bb = f"({s},{w},{n},{e})"
    return f"""[out:json][timeout:180];(
 nwr["tourism"~"^(attraction|museum|viewpoint|gallery|zoo|aquarium|theme_park)$"]["name"]{bb};
 nwr["historic"~"^(monument|castle|palace|archaeological_site|city_gate|fort|church|cathedral)$"]["name"]{bb};
 nwr["amenity"="place_of_worship"]["wikidata"]["name"]{bb};
 nwr["amenity"~"^(restaurant|cafe|bar|pub|ice_cream)$"]["name"]{bb};
 nwr["amenity"="parking"]{bb};
 nwr["leisure"~"^(park|garden|water_park|marina|beach_resort)$"]["name"]{bb};
 nwr["amenity"~"^(theatre|cinema|nightclub|arts_centre)$"]["name"]{bb};
);out center tags;"""

def fetch(q):
    """Usa curl (viene en todos los Mac) y, si no, urllib."""
    import subprocess
    last = None
    for attempt in range(4):
        url = ENDPOINTS[attempt % len(ENDPOINTS)]
        try:
            r = subprocess.run(["curl", "-s", "-f", "--max-time", "240", "-A", "KalifaiMapas/1.0 (+https://ai-agency-orbit.com)",
                                "--data-urlencode", "data@-", url], input=q.encode(), capture_output=True)
            if r.returncode == 0 and r.stdout.strip().startswith(b"{"):
                return json.loads(r.stdout)
            raise RuntimeError("curl codigo %s" % r.returncode)
        except FileNotFoundError:
            data = urllib.parse.urlencode({"data": q}).encode()
            try:
                req = urllib.request.Request(url, data=data, headers={"User-Agent": "KalifaiMapas/1.0"})
                with urllib.request.urlopen(req, timeout=240) as resp:
                    return json.loads(resp.read())
            except Exception as ex:
                last = ex
        except Exception as ex:
            last = ex
        print("   reintento", attempt + 1, last or ""); time.sleep(15 * (attempt + 1))
    raise last or RuntimeError("sin respuesta")

def cat(t):
    a = t.get("amenity", "")
    if a == "parking": return "parking"
    if a in ("restaurant", "cafe", "bar", "pub", "ice_cream"): return "comer"
    if a in ("theatre", "cinema", "nightclub", "arts_centre") or t.get("leisure") or t.get("tourism") in ("zoo", "aquarium", "theme_park"): return "ocio"
    return "ver"

def score(c, t):
    s = 0.0
    if t.get("wikidata") or t.get("wikipedia"): s += 6
    if t.get("name:en"): s += 1
    if t.get("website") or t.get("contact:website"): s += 1
    if t.get("opening_hours"): s += 1
    if c == "ver" and t.get("tourism") in ("museum", "attraction", "viewpoint"): s += 2
    if c == "ver" and t.get("historic") in ("castle", "palace", "cathedral", "archaeological_site"): s += 2
    if c == "comer" and t.get("cuisine"): s += 0.5
    if c == "parking":
        try: s += min(float(t.get("capacity", "0")) / 100, 8)
        except ValueError: pass
        if t.get("parking") in ("underground", "multi-storey"): s += 1
    return round(s, 1)

def build(slug, name, country, lat, lon):
    b = bbox(lat, lon); res = fetch(query(b)); out = []; seen = set()
    for el in res.get("elements", []):
        t = el.get("tags", {}); c = cat(t)
        y = el.get("lat") or el.get("center", {}).get("lat"); x = el.get("lon") or el.get("center", {}).get("lon")
        if y is None or x is None: continue
        if c == "parking" and t.get("access") in ("private", "customers", "no", "permit", "residents"): continue
        nm = t.get("name") or ("Aparcamiento" if c == "parking" else None)
        if not nm: continue
        key = (c, nm, round(y, 3), round(x, 3))
        if key in seen: continue
        seen.add(key)
        info = {k: t[k] for k in KEEP if k in t}
        if t.get("contact:website") and "website" not in info: info["website"] = t["contact:website"]
        if t.get("wikidata") or t.get("wikipedia"): info["wiki"] = 1
        out.append([c, nm[:80], round(y, 5), round(x, 5), score(c, t), info])
    pois = []
    for c in CAP:
        part = sorted([p for p in out if p[0] == c], key=lambda p: -p[4])
        if c == "parking":  # mitad gratis, mitad de pago si hay
            free = [p for p in part if p[5].get("fee") == "no"]; paid = [p for p in part if p[5].get("fee") != "no"]
            part = free[:CAP[c] // 2] + paid[:CAP[c] - min(len(free), CAP[c] // 2)]
        pois += part[:CAP[c]]
    os.makedirs("app/mapas", exist_ok=True)
    doc = {"slug": slug, "name": name, "country": country, "center": [lat, lon], "bbox": b,
           "updated": datetime.date.today().isoformat(), "pois": pois}
    json.dump(doc, open(f"app/mapas/{slug}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return len(pois)

def main():
    only = set(sys.argv[1:]); idx = []
    for i, (slug, name, country, lat, lon) in enumerate(CITIES):
        if only and slug not in only: continue
        print(f"[{i+1}/{len(CITIES)}] {name}…", flush=True)
        try:
            n = build(slug, name, country, lat, lon); print("   OK", n, "lugares")
        except Exception as ex:
            print("   FALLA", name, ex)
        time.sleep(6)
    for slug, name, country, lat, lon in CITIES:
        if os.path.exists(f"app/mapas/{slug}.json"):
            idx.append({"slug": slug, "name": name, "country": country, "center": [lat, lon], "bbox": bbox(lat, lon)})
    json.dump({"updated": datetime.date.today().isoformat(), "cities": idx}, open("app/mapas/index.json", "w"), ensure_ascii=False)
    print("Ciudades listas:", len(idx))

if __name__ == "__main__":
    main()
