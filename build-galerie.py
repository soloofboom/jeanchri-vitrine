#!/usr/bin/env python3
"""Régénère la galerie de index.html à partir de galerie.json.

Usage :
    python3 build-galerie.py            # miniatures + galerie + versions de cache
    python3 build-galerie.py --images   # ne génère que les miniatures
    python3 build-galerie.py --check    # vérifie que tout est à jour (exit 1 sinon)

Les originaux (images/*.jpg) ne sont jamais modifiés : les miniatures sont
écrites dans images/mini/ et servies par srcset. Le clic ouvre la visionneuse
(assets/ui.js), ou l'original pleine taille si le JS est absent.

La fraîcheur des miniatures est vérifiée par empreinte du CONTENU de l'original
et non par mtime : un clone frais a des mtime arbitraires, donc l'ancienne
comparaison signalait toutes les miniatures comme périmées après un checkout.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).parent
DOSSIER_MINI = RACINE / "images" / "mini"
MANIFESTE = DOSSIER_MINI / ".manifeste.json"
LARGEURS = (400, 800, 1200)
# Grille : 1 colonne ≤640 px, 2 colonnes ≤1024 px, 3 colonnes au-delà, bord à bord.
SIZES = "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"

# Fichiers dont le ?v= doit suivre le contenu, et pages à réécrire.
ASSETS = ("assets/style.css", "assets/menu.js", "assets/ui.js")
PAGES = (
    "index.html",
    "portfolio/index.html",
    "jeanchri-musique/index.html",
    "jeanchri-musique/liste-de-lecture/index.html",
    "aux-temps-possibles/index.html",
)


def empreinte(chemin: Path) -> str:
    """8 premiers caractères de l'empreinte du contenu du fichier."""
    return hashlib.sha256(chemin.read_bytes()).hexdigest()[:8]


def chemin_mini(source: str, largeur: int) -> Path:
    return DOSSIER_MINI / f"{Path(source).stem}-{largeur}.webp"


def lire_manifeste() -> dict:
    if not MANIFESTE.exists():
        return {}
    try:
        return json.loads(MANIFESTE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def ecrire_manifeste(donnees: dict) -> None:
    entrees = {}
    for img in donnees["images"]:
        source = RACINE / img["src"]
        if source.exists():
            entrees[img["src"]] = empreinte(source)
    DOSSIER_MINI.mkdir(parents=True, exist_ok=True)
    MANIFESTE.write_text(
        json.dumps(entrees, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def miniatures_a_generer(donnees: dict) -> list[tuple[Path, Path, int]]:
    manifeste = lire_manifeste()
    a_faire = []
    for img in donnees["images"]:
        source = RACINE / img["src"]
        if not source.exists():
            continue
        perimee = manifeste.get(img["src"]) != empreinte(source)
        for largeur in LARGEURS:
            cible = chemin_mini(img["src"], largeur)
            if perimee or not cible.exists():
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


def versionner(html: str) -> str:
    """Réécrit les ?v= des feuilles de style et scripts avec l'empreinte réelle."""
    for rel in ASSETS:
        jeton = re.escape(Path(rel).name)
        remplacement = empreinte(RACINE / rel)
        html = re.sub(
            rf"({jeton}\?v=)[^\"']+",
            lambda m, v=remplacement: m.group(1) + v,
            html,
        )
    return html


def versionner_fichier(chemin: Path) -> bool:
    """Réécrit les ?v= d'une page. True si le fichier a changé."""
    avant = chemin.read_text(encoding="utf-8")
    apres = versionner(avant)
    if apres == avant:
        return False
    chemin.write_text(apres, encoding="utf-8")
    return True


def problemes(donnees: dict, html: str, nouveau: str) -> list[str]:
    constats = []
    manifeste = lire_manifeste()
    for img in donnees["images"]:
        source = RACINE / img["src"]
        if not source.exists():
            constats.append(f"original manquant : {img['src']}")
            continue
        if manifeste.get(img["src"]) != empreinte(source):
            constats.append(
                f"miniatures périmées (original modifié) : {img['src']}"
            )
            continue
        for largeur in LARGEURS:
            cible = chemin_mini(img["src"], largeur)
            if not cible.exists():
                nom = cible.relative_to(RACINE).as_posix()
                constats.append(f"miniature manquante : {nom}")
    if nouveau != html:
        constats.append("index.html ne correspond plus à galerie.json ou aux ?v=")
    return constats


def problemes_versions() -> list[str]:
    """index.html est déjà couvert par la comparaison ci-dessus."""
    constats = []
    for nom in PAGES:
        if nom == "index.html":
            continue
        chemin = RACINE / nom
        avant = chemin.read_text(encoding="utf-8")
        if versionner(avant) != avant:
            constats.append(f"{nom} : ?v= périmé")
    return constats


def main() -> None:
    donnees = json.loads((RACINE / "galerie.json").read_text(encoding="utf-8"))
    index = RACINE / "index.html"
    html = index.read_text(encoding="utf-8")
    nouveau = versionner(construire(html, donnees))
    args = sys.argv[1:]

    if "--check" in args:
        constats = problemes(donnees, html, nouveau) + problemes_versions()
        if constats:
            for constat in constats:
                print(f"✗ {constat}")
            print("→ lancer : python3 build-galerie.py")
            sys.exit(1)
        print(
            f"OK : galerie à jour ({len(donnees['images'])} images, "
            "miniatures présentes, ?v= à jour)"
        )
        return

    generer_miniatures(donnees)
    ecrire_manifeste(donnees)
    if "--images" in args:
        print("OK : miniatures à jour")
        return

    index.write_text(nouveau, encoding="utf-8")
    pages = [nom for nom in PAGES if versionner_fichier(RACINE / nom)]
    print(f"OK : {len(donnees['images'])} images écrites dans index.html")
    if pages:
        print(f"OK : ?v= mis à jour dans {len(pages)} page(s)")


if __name__ == "__main__":
    main()
