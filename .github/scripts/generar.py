"""Dibuja los SVG del README del perfil: el encabezado animado y las stats (lenguajes y contribuciones del año).

Sin servicios externos: lee la API GraphQL de GitHub con GITHUB_TOKEN y escribe assets/*.svg en claro y oscuro.
    GITHUB_TOKEN=... python .github/scripts/generar.py Chava33165
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

USUARIO = sys.argv[1] if len(sys.argv) > 1 else "Chava33165"
SALIDA = Path(__file__).resolve().parents[2] / "assets"
# Mi avatar de rizos (los mismos trazos que el portafolio, sacados de rizos.js).
AVATAR = (Path(__file__).resolve().parent / "avatar.svgfrag").read_text(encoding="utf-8")

TEMAS = {
    "claro": {"papel": "#F5F4EE", "borde": "#E4E1D7", "tinta": "#1F1E1D", "tinta2": "#5E5D58", "tinta3": "#8E8C84",
              "acento": "#D97757", "riel": "#E9E5DA"},
    "oscuro": {"papel": "#1C1B1A", "borde": "#34322F", "tinta": "#F2F0E8", "tinta2": "#B9B6AC", "tinta3": "#85827A",
               "acento": "#E2896A", "riel": "#2C2A28"},
}
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def consulta() -> dict:
    q = """query($u:String!){ user(login:$u){
      repositories(ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC, first:100){ totalCount nodes{
        languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } } }
      contributionsCollection{ contributionCalendar{ totalContributions } } } }"""
    req = urllib.request.Request("https://api.github.com/graphql", method="POST",
                                 data=json.dumps({"query": q, "variables": {"u": USUARIO}}).encode(),
                                 headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
                                          "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]


def encabezado(t: dict) -> str:
    frases = ["reparo servidores de IA", "programo cosas útiles", "automatizo mi vida", "administro mi propio servidor"]
    n = len(frases)
    ciclo = n * 3
    rota = "".join(
        f'<text class="r r{i}" x="40" y="186">{f}</text>' for i, f in enumerate(frases))
    claves = "".join(
        f".r{i}{{animation-delay:{i * 3}s}}" for i in range(n))
    pct = 100 / n
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="840" height="230" viewBox="0 0 840 230" role="img" aria-label="Salvador Pantoja">
<style>
  .letra{{opacity:0;animation:entra 900ms cubic-bezier(.23,1,.32,1) forwards}}
  .sub{{stroke-dasharray:420;stroke-dashoffset:420;animation:traza 1s cubic-bezier(.77,0,.175,1) 1.4s forwards}}
  .r{{font:italic 400 24px {SERIF};fill:{t['tinta']};opacity:0;animation:rota {ciclo}s infinite}}
  {claves}
  @keyframes entra{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
  @keyframes traza{{to{{stroke-dashoffset:0}}}}
  @keyframes rota{{0%{{opacity:0;transform:translateY(8px)}}3%,{pct - 3:.0f}%{{opacity:1;transform:none}}{pct:.0f}%,100%{{opacity:0;transform:translateY(-8px)}}}}
  @media (prefers-reduced-motion:reduce){{.letra,.r0{{animation:none;opacity:1}}.sub{{animation:none;stroke-dashoffset:0}}.r1,.r2,.r3{{display:none}}}}
</style>
<rect x="1" y="1" width="838" height="228" rx="22" fill="{t['papel']}" stroke="{t['borde']}"/>
<g fill="{t['riel']}">{''.join(f'<circle cx="{x}" cy="{y}" r="1.4"/>' for x in range(560, 830, 18) for y in range(20, 220, 18))}</g>
<g transform="translate(620 22) scale(0.8)">{AVATAR.replace('{TINTA}', t['tinta']).replace('{ACENTO}', t['acento'])}</g>
<text x="40" y="52" font-family="{SANS}" font-size="13" letter-spacing="2.5" fill="{t['acento']}">HOLA, SOY</text>
<g class="letra" style="animation-delay:.15s"><text x="38" y="112" font-family="{SERIF}" font-size="60" fill="{t['tinta']}" letter-spacing="-1.5">Salvador</text></g>
<g class="letra" style="animation-delay:.45s"><text x="276" y="112" font-family="{SERIF}" font-size="60" font-style="italic" fill="{t['acento']}" letter-spacing="-1.5">Pantoja</text></g>
<path class="sub" d="M279 128 C 350 118, 430 118, 482 124" fill="none" stroke="{t['acento']}" stroke-width="4" stroke-linecap="round"/>
<text x="40" y="158" font-family="{SANS}" font-size="15" fill="{t['tinta3']}">Técnico en electrónica · Ingeniería en Software · Guadalajara, MX</text>
{rota}
</svg>"""


def stats(t: dict, datos: dict) -> str:
    total_bytes: dict[str, list] = {}
    for repo in datos["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            nombre = e["node"]["name"]
            total_bytes.setdefault(nombre, [0, e["node"]["color"] or t["tinta3"]])[0] += e["size"]
    # Lo generado por plataformas (CMake, C/C++ de Flutter, etc.) infla el conteo: se ignora.
    for ruido in ("CMake", "C", "Objective-C", "Swift", "Ruby", "Kotlin", "Procfile", "TeX"):
        total_bytes.pop(ruido, None)
    top = sorted(total_bytes.items(), key=lambda kv: -kv[1][0])[:6]
    suma = sum(v[0] for _, v in top) or 1
    x, barras, etiquetas = 40, "", ""
    ancho = 760
    for i, (nombre, (b, color)) in enumerate(top):
        w = ancho * b / suma
        barras += f'<rect x="{x:.1f}" y="92" width="{max(w - 3, 2):.1f}" height="12" rx="6" fill="{color}"/>'
        col, fila = i % 3, i // 3
        etiquetas += (f'<g transform="translate({40 + col * 260},{140 + fila * 30})"><circle cx="6" cy="-5" r="6" fill="{color}"/>'
                      f'<text x="20" y="0" font-family="{SANS}" font-size="15" fill="{t["tinta"]}">{nombre}'
                      f'<tspan fill="{t["tinta3"]}"> {100 * b / suma:.0f}%</tspan></text></g>')
        x += w
    contrib = datos["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    repos = datos["repositories"]["totalCount"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="840" height="220" viewBox="0 0 840 220" role="img" aria-label="Lenguajes y actividad">
<style>.b{{animation:crece 1.2s cubic-bezier(.23,1,.32,1) both;transform-origin:40px 98px}}@keyframes crece{{from{{transform:scaleX(0)}}}}@media (prefers-reduced-motion:reduce){{.b{{animation:none}}}}</style>
<rect x="1" y="1" width="838" height="218" rx="22" fill="{t['papel']}" stroke="{t['borde']}"/>
<text x="40" y="50" font-family="{SANS}" font-size="13" letter-spacing="2.5" fill="{t['acento']}">LO QUE MÁS ESCRIBO</text>
<text x="800" y="50" text-anchor="end" font-family="{SERIF}" font-size="22" fill="{t['tinta']}">{contrib} <tspan font-family="{SANS}" font-size="13" fill="{t['tinta3']}">contribuciones este año · {repos} repos públicos</tspan></text>
<rect x="40" y="92" width="{ancho}" height="12" rx="6" fill="{t['riel']}"/>
<g class="b">{barras}</g>
{etiquetas}
</svg>"""


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    datos = consulta()
    for nombre, t in TEMAS.items():
        (SALIDA / f"encabezado-{nombre}.svg").write_text(encabezado(t), encoding="utf-8")
        (SALIDA / f"stats-{nombre}.svg").write_text(stats(t, datos), encoding="utf-8")
    print("listo:", sorted(p.name for p in SALIDA.glob("*.svg")))


if __name__ == "__main__":
    main()
