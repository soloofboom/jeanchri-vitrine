#!/usr/bin/env python3
"""Régénère la galerie de index.html à partir de galerie.json.

Usage :
    python3 build-galerie.py            # génère les miniatures manquantes, puis index.html
    python3 build-galerie.py --images   # ne génère que les miniatures
    python3 build-galerie.py --check    # vérifie que tout est à jour (exit 1 sinon)

Les originaux (images/*.jpg) ne sont jamais modifiés : les miniatures sont
écrites dans images/mini/ et servies par srcset. Le clic continue de pointer
vers l'original pleine taille.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).parent
DOSSIER_MINI = RACINE / "images" / "mini"
LARGEURS = (400, 800, 1200)
# Grille : 1 colonne ≤640 px, 2 colonnes ≤1024 px, 3 colonnes au-delà, bord à bord.
SIZES = "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"


def chemin_mini(source: str, largeur: int) -> Path:
    return DOSSIER_MINI / f"{Path(source).stem}-{largeur}.webp"


def miniatures_a_generer(donnees: dict) -> list[tuple[Path, Path, int]]:
    a_faire = []
    for img in donnees["images"]:
        source = RACINE / img["src"]
        if not source.exists():
            continue
        for largeur in LARGEURS:
            cible = chemin_mini(img["src"], largeur)
            if not cible.exists() or cible.stat().st_mtime < source.stat().st_mtime:
                a_faire.append((source, cible, largeur))
    return a_faire


def generer_miniatures(donnees: dict) -> None:
    """Crée les miniatures manquantes ou périmées. N'écrase jamais un original."""
    a_faire = miniatures_a_generer(donnees)
    if not a_faire:
        return
    cwebp = shutil.which("cwebp")
    if cwebp is None:
        sys.exit(
            "cwebp introuvable : installe-le (brew install webp) "
            "ou committe les miniatures dans images/mini/."
        )
    DOSSIER_MINI.mkdir(parents=True, exist_ok=True)
    print(f"{len(a_faire)} miniature(s) à générer…")
    for source, cible, largeur in a_faire:
        subprocess.run(
            [cwebp, "-quiet", "-q", "80", "-resize", str(largeur), "0",
             str(source), "-o", str(cible)],
            check=True,
        )


def generer_item(img: dict, premiere: bool = False) -> str:
    cible = img["lien"]
    if img["externe"]:
        # Photo seule : la visionneuse prend le relais au clic (assets/ui.js).
        # Le href reste l'original pleine taille, donc sans JS le lien marche
        # encore — dégradation acceptable, on perd juste les flèches.
        attrs = f' data-zoom="1" aria-label="Agrandir : {img["legende"]}"'
    else:
        attrs = ""
    if premiere:
        chargement = 'fetchpriority="high"'
    else:
        chargement = 'loading="lazy"'
    srcset = ", ".join(
        f"{chemin_mini(img['src'], largeur).relative_to(RACINE).as_posix()} {largeur}w"
        for largeur in LARGEURS
    )
    return f"""	<figure>
		<a href="{cible}"{attrs}><img src="{img['src']}" srcset="{srcset}" sizes="{SIZES}" alt="{img['legende']}" width="{img['largeur']}" height="{img['hauteur']}" {chargement} decoding="async"></a>
		<figcaption>{img['legende']}</figcaption>
	</figure>"""


def construire(html: str, donnees: dict) -> str:
    figures = "\n".join(generer_item(i, n == 0) for n, i in enumerate(donnees["images"]))
    bloc = f'<div class="galerie">\n{figures}\n</div>'

    debut = html.index("<!-- GALERIE:DEBUT")
    try:
        fin = html.index("<!-- GALERIE:FIN -->") + len("<!-- GALERIE:FIN -->")
    except ValueError:
        # première génération : le marqueur de fin suit la fin du bloc <div class="galerie">
        fin = html.index("</div>", html.index('<div class="galerie">')) + len("</div>")
    return (
        html[:debut]
        + "<!-- GALERIE:DEBUT — généré depuis galerie.json par build-galerie.py -->\n"
        + bloc
        + "\n<!-- GALERIE:FIN -->"
        + html[fin:]
    )


def problemes(donnees: dict, html: str, nouveau: str) -> list[str]:
    constats = []
    for img in donnees["images"]:
        source = RACINE / img["src"]
        if not source.exists():
            constats.append(f"original manquant : {img['src']}")
            continue
        for largeur in LARGEURS:
            cible = chemin_mini(img["src"], largeur)
            nom = cible.relative_to(RACINE).as_posix()
            if not cible.exists():
                constats.append(f"miniature manquante : {nom}")
            elif cible.stat().st_mtime < source.stat().st_mtime:
                constats.append(f"miniature périmée : {nom}")
    if nouveau != html:
        constats.append("index.html ne correspond plus à galerie.json")
    return constats


def main() -> None:
    donnees = json.loads((RACINE / "galerie.json").read_text(encoding="utf-8"))
    index = RACINE / "index.html"
    html = index.read_text(encoding="utf-8")
    nouveau = construire(html, donnees)
    args = sys.argv[1:]

    if "--check" in args:
        constats = problemes(donnees, html, nouveau)
        if constats:
            for constat in constats:
                print(f"✗ {constat}")
            print("→ lancer : python3 build-galerie.py")
            sys.exit(1)
        print(f"OK : galerie à jour ({len(donnees['images'])} images, miniatures présentes)")
        return

    generer_miniatures(donnees)
    if "--images" in args:
        print("OK : miniatures à jour")
        return

    index.write_text(nouveau, encoding="utf-8")
    print(f"OK : {len(donnees['images'])} images écrites dans index.html")


if __name__ == "__main__":
    main()
