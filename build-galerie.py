#!/usr/bin/env python3
"""Régénère la galerie de index.html à partir de galerie.json.

Usage : éditez galerie.json (ajoutez/retirez/modifiez des photos), puis :
    python3 build-galerie.py
"""
import json
from pathlib import Path

RACINE = Path(__file__).parent

def generer_item(img: dict, premiere: bool = False) -> str:
    cible = img["lien"]
    externe = ' target="_blank" rel="noopener"' if img["externe"] else ""
    if premiere:
        chargement = 'fetchpriority="high"'
    else:
        chargement = 'loading="lazy"'
    return f"""	<figure>
		<a href="{cible}"{externe}><img src="{img['src']}" alt="{img['legende']}" width="{img['largeur']}" height="{img['hauteur']}" {chargement}></a>
		<figcaption>{img['legende']}</figcaption>
	</figure>"""

def main() -> None:
    donnees = json.loads((RACINE / "galerie.json").read_text(encoding="utf-8"))
    figures = "\n".join(generer_item(i, n == 0) for n, i in enumerate(donnees["images"]))
    bloc = f'<div class="galerie">\n{figures}\n</div>'

    index = RACINE / "index.html"
    html = index.read_text(encoding="utf-8")
    debut = html.index("<!-- GALERIE:DEBUT")
    try:
        fin = html.index("<!-- GALERIE:FIN -->") + len("<!-- GALERIE:FIN -->")
    except ValueError:
        # première génération : le marqueur de fin suit la fin du bloc <div class="galerie">
        fin = html.index("</div>", html.index('<div class="galerie">')) + len("</div>")
    nouveau = html[:debut] + "<!-- GALERIE:DEBUT — généré depuis galerie.json par build-galerie.py -->\n" + bloc + "\n<!-- GALERIE:FIN -->" + html[fin:]
    index.write_text(nouveau, encoding="utf-8")
    print(f"OK : {len(donnees['images'])} images écrites dans index.html")

if __name__ == "__main__":
    main()