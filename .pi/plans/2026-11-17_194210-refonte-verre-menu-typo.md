# Refonte design jeanchri.com — verre dépoli raffiné, menu enrichi, typographie display

**Goal**: Porter le site d'une reproduction fidèle du thème WordPress Photobook à une interface cohérente et finie, en conservant l'ADN sombre/translucide.
**Status**: draft
**Created**: 2026-11-17 19:42
**Slug**: refonte-verre-menu-typo

## Context

`jeanchri.com` est un site **statique pur** déployé sur GitHub Pages :

- `index.html` (accueil + galerie), `portfolio/index.html`, `jeanchri-musique/index.html`, `aux-temps-possibles/index.html`
- `assets/style.css` — 534 lignes, un seul fichier, variables CSS dans `:root`
- `assets/menu.js` — 41 lignes, menu plein écran (IIFE, pas de module)
- `build-galerie.py` — génère le bloc `<!-- GALERIE:DEBUT -->…<!-- GALERIE:FIN -->` de `index.html` depuis `galerie.json`, et les vignettes `images/mini/*.webp` via `cwebp`
- Aucun `package.json`, aucun build step, aucune dépendance. Google Fonts (Roboto 300→900) chargé par `<link>`.

Le fichier CSS se déclare comme « reproduction fidèle du thème Photobook » avec une palette extraite du WordPress d'origine. Le thème sombre a été ajouté après coup (commentaire daté 2026-09-05), et le vocabulaire de contrôles (`--filet`, `--teinte-accent`, `--duree`, `--courbe`) a été introduit plus tard encore. **Il y a donc trois strates empilées, pas un système.**

Gaps constatés à la lecture :

1. **Contraste cassé** — `a { color: var(--violet-lien) }` = `#4a0063` à 60 % sur `#0a0a0a` → ~1.3:1. `a:hover` = `#5500e8` → ~2.4:1. Les liens génériques sont illisibles ; seuls `.carte-contenu a` et `.site-title a` les rattrapent.
2. **`menu.js` sans focus trap** — le `<nav>` passe `aria-hidden="true"` mais le reste de la page reste focusable : au Tab, le focus sort du menu invisible. Rien n'est `inert`.
3. **CSS dupliqué** — `body.accueil .galerie { margin-top: 0 }` ×3, `.carte-contenu p:last-child` ×2, `body.accueil .site-header` redéclare `height`/`padding` déjà posés.
4. **`#dt_breadcrumbs { padding-left: 160px }`** — valeur magique non responsive.
5. **Aucun `prefers-reduced-motion`** alors que le site multiplie les transitions.
6. **Aucune meta sociale** (`og:`/`twitter:`) ni `theme-color` — un site d'artiste partagé sans vignette.
7. **Le burger est un carré blanc plein** au milieu d'une interface entièrement en verre : rupture de vocabulaire.
8. **`background-attachment: fixed`** sur `body` (desktop) = repaint coûteux au scroll.
9. **Typographie générique** — Roboto 300→900 avec `letter-spacing: .06em` global, sans hiérarchie d'échelle.
10. **Header `position: absolute` sur l'accueil** — le titre et la description disparaissent dès le premier scroll.
11. Cache-busting manuel (`?v=20261116-5`, `?v=20260905-6`) : deux valeurs à mettre à jour à la main dans 4 fichiers.

Décisions validées par l'utilisateur :

- **Direction** : verre dépoli raffiné — garder le sombre et la transparence, les rendre crédibles (bordure lumineuse, grain, ombre interne). Pas de changement de registre.
- **Menu** : plein écran enrichi — ouverture en cercle depuis le burger, liens en cascade, focus trap, numérotation monospace.
- **Typographie** : ajouter une display — `Instrument Serif` 400 pour les titres + `Inter` pour le corps.
- **Périmètre** : non répondu → les 4 chantiers sont retenus, mais en phases séparées pour permettre un arrêt propre après la phase 2.

## Approach

- **Réparer avant d'embellir.** Les phases 1 et 2 ne changent volontairement presque rien à l'apparence : elles posent le contraste, l'accessibilité et le système de verre. Sans ça, chaque effet ajouté ensuite s'empile sur une base fausse.
- **Un système de verre nommé, pas des valeurs éparpillées.** Aujourd'hui `backdrop-filter` apparaît avec 6 valeurs de flou et 5 fonds différents. On introduit un jeu de tokens (`--verre-*`) et une recette unique appliquée aux 5 surfaces concernées.
- **Le markup de la galerie appartient à `build-galerie.py`.** Toute modification de `<figure>`/`<figcaption>` doit passer par le générateur, sinon elle est écrasée au prochain `python3 build-galerie.py`. C'est la principale source d'erreur de ce chantier.
- **Une phase = un commit.** Chaque phase est visuellement réversible et validable seule.
- **Zéro dépendance ajoutée.** Pas de bundler, pas de framework, pas de librairie d'animation. On reste sur du CSS natif + ~80 lignes de JS.

## Steps

### Phase 0 — Filet de sécurité

1. [ ] **Créer la branche et capturer l'état de référence.**
   `git checkout -b design/verre-2026-11`
   Lancer `python3 build-galerie.py --check` (doit sortir 0) et capturer `index.html`, `jeanchri-musique/`, `aux-temps-possibles/` en 390 px / 768 px / 1440 px.
   *Succès* : `--check` sort 0, 9 captures archivées dans `.pi/captures/avant/`.

2. [ ] **Extraire un inventaire du verre existant.**
   `grep -n 'backdrop-filter\|rgba(30, 38, 46' assets/style.css`
   Consigner les 5 surfaces (`.site-header`, `body.accueil .site-header`, `.dt-main-menu`, `#dt_breadcrumbs`, `.carte-contenu`) et leurs valeurs actuelles.
   *Succès* : liste écrite en tête de la section « Système de verre » du CSS.

### Phase 1 — Corrections de fond (aucun changement visuel voulu)

3. [ ] **Réparer les couleurs de lien** dans `assets/style.css`.
   Ajouter `--lien: rgba(255,255,255,.72)` et `--lien-survol: #c9a8ff`, remplacer `a { color: var(--violet-lien) }` / `a:hover { color: var(--accent) }`. Conserver `--violet*` pour ne pas casser les usages existants, mais ne plus les employer sur fond sombre.
   *Succès* : tout `a` sans règle spécifique atteint ≥ 4.5:1 (vérifié avec un inspecteur de contraste).

4. [ ] **Ajouter le bloc `prefers-reduced-motion`** en fin de `assets/style.css` : neutraliser `transition`, `animation`, `scroll-behavior` et les `transform` de survol.
   *Succès* : avec « Réduire les animations » activé dans macOS Réglages → Accessibilité, le menu s'ouvre sans transition et la galerie ne zoome plus.

5. [ ] **Dédoublonner le CSS.** Supprimer les 2 déclarations `body.accueil .galerie { margin-top: 0 }` redondantes, le `.carte-contenu p:last-child` dupliqué, et fusionner `body.accueil .site-header` avec `.site-header` en ne gardant que les 4 propriétés réellement différentes (`position`, `background`, `backdrop-filter`, `font-weight` du titre).
   *Succès* : `git diff --stat` négatif sur `style.css`, rendu identique (captures avant/après superposables).

6. [ ] **Corriger `#dt_breadcrumbs`** : remplacer `padding: 20px 0 20px 160px` par un `padding: 20px 24px` sur un conteneur centré `max-width: 1100px; margin: 0 auto`.
   *Succès* : fil d'Ariane aligné à gauche du contenu à 390 px comme à 1440 px.

7. [ ] **Ajouter un fallback `@supports`** : `@supports not ((backdrop-filter: blur(0)) or (-webkit-backdrop-filter: blur(0)))` → opacifier les fonds (`rgba(30,38,46,.97)`).
   *Succès* : testé en commentant la propriété dans l'inspecteur, les cartes restent lisibles.

8. [ ] **Réparer `assets/menu.js`** : focus trap (Tab/Shift+Tab cycliques sur les liens du menu + le bouton fermer), `inert` sur `header` / `main` / `footer` à l'ouverture (retiré à la fermeture), restauration du focus sur le déclencheur, et `document.body.style` remplacé par la classe `menu-ouvert` déjà en place.
   *Succès* : menu ouvert, 8 pressions sur Tab ne font jamais sortir du menu ni ne donnent le focus à un élément derrière.

9. [ ] **Sémantique du fil d'Ariane** — dans les 3 pages internes, remplacer `<ul id="dt_breadcrumbs">` par `<nav aria-label="Fil d'Ariane"><ol id="dt_breadcrumbs">…</ol></nav>` et ajuster le CSS (`ol`/`li`).
   *Succès* : `grep -c 'aria-label="Fil d'Ariane"' */index.html` = 1 pour chaque page interne ; validateur HTML sans erreur.

10. [ ] **`aria-hidden="true"` sur les 3 `<span>` du burger**, dans les 4 fichiers HTML.
    *Succès* : `grep -c 'span aria-hidden' */index.html index.html` = 3 par page.

> **Commit de fin de phase 1** : `fix(a11y): contraste des liens, focus trap du menu, fil d'Ariane sémantique`

### Phase 2 — Système de verre

11. [ ] **Introduire les tokens** dans `:root` : `--verre-fond`, `--verre-bord`, `--verre-flou`, `--verre-ombre`, `--grain`.
    Une seule recette appliquée aux 5 surfaces inventoriées à l'étape 2 :
    ```css
    background: var(--verre-fond);
    border: 1px solid var(--verre-bord);
    backdrop-filter: blur(var(--verre-flou));
    box-shadow: var(--verre-ombre);
    ```
    *Succès* : `grep -c 'backdrop-filter' assets/style.css` chute de 6 à 5 occurrences, toutes via `var(--verre-flou)`.

12. [ ] **Ajouter le grain** — un `body::after` en `position: fixed; inset: 0; pointer-events: none; opacity: .04` avec un motif `feTurbulence` en data-URI SVG, `z-index` sous le menu (200) mais au-dessus du contenu.
    *Succès* : grain visible sur un aplat sombre, invisible sur une photo claire, `pointer-events` non bloquant (les liens restent cliquables).

13. [ ] **Bordures lumineuses + ombre interne** sur `.carte-contenu` et `.dt-main-menu` : `1px solid rgba(255,255,255,.10)` + `inset 0 1px 0 rgba(255,255,255,.06)`.
    *Succès* : les cartes ne flottent plus « à plat » sur le wallpaper ; comparaison avant/après convaincante en capture.

> **Commit de fin de phase 2** : `feat(design): système de verre unifié (tokens, grain, bordures)`

### Phase 3 — Typographie

14. [ ] **Changer la requête Google Fonts** dans les 4 fichiers HTML :
    `family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&display=swap`
    Ajouter `<link rel="preload" as="font" type="font/woff2" crossorigin>` pour les 2 woff2 critiques si les URL sont stables, sinon laisser `preconnect` + `display=swap`.
    *Succès* : aucune erreur en console, pas de FOIT, titre rendu en serif.

15. [ ] **Poser l'échelle typographique** : `--titre-1` (44 px → 30 px mobile), `--titre-2`, `--corps` (16 px, `line-height: 1.8`), `--micro` (12 px monospace pour les badges).
    `.site-title`, `.entry-title` → `Instrument Serif 400` avec `letter-spacing: -.01em`. `.dt-main-menu li a` → `Instrument Serif 400` à 34 px. Corps → `Inter 400`.
    Réduire le `letter-spacing: .06em` global du `body` à `.01em` (le `.06em` sur du texte courant est une signature de thème, pas un choix).
    *Succès* : hiérarchie lisible sans graisse (Instrument Serif n'a qu'un poids) — validée sur `jeanchri-musique/` qui contient titres, citation et paragraphes longs.

> **Commit de fin de phase 3** : `feat(type): Instrument Serif + Inter, échelle typographique`

### Phase 4 — Menu plein écran enrichi

16. [ ] **Ouverture en cercle.** Dans `assets/menu.js`, calculer le centre du burger et exposer `--origine-menu: {x}px {y}px` sur `.dt-main-menu`. En CSS : `clip-path: circle(0% at var(--origine-menu))` → `circle(150% at …)` sur `body.menu-ouvert`.
    Fallback `@supports not (clip-path: circle(0% at 0 0))` → retour au fade actuel.
    *Succès* : le cercle part bien du burger en haut à droite, pas du centre ; aucune saccade en Safari.

17. [ ] **Cascade des liens.** Poser `style="--i:0"` … `--i:3` sur les `<li>` (dans les 4 fichiers HTML), puis `transition-delay: calc(var(--i) * 60ms)` sur `opacity` + `translateY(12px)`.
    *Succès* : ouverture perçue comme séquencée, fermeture en cascade inverse (`calc((3 - var(--i)) * 40ms)`).

18. [ ] **Numérotation monospace** : préfixe `01 —`, `02 —`, `03 —` en `ui-monospace` 11 px, `letter-spacing: .2em`, couleur `--texte-clair-2`, aligné en colonne fixe pour raccorder au badge `ai ↗`.
    *Succès* : le `ai ↗` n'est plus un objet isolé, il termine la même série.

19. [ ] **Burger en verre.** Remplacer `background: #fff` par la recette de verre, barres en `#fff`. Vérifier le contraste sur les photos claires (`images/nuages.jpg`).
    *Succès* : burger lisible sur l'accueil (photo `creation.jpg`) comme sur une carte sombre.

> **Commit de fin de phase 4** : `feat(menu): ouverture circulaire, cascade, numérotation, burger en verre`

### Phase 5 — Accueil et galerie

20. [ ] **Header sticky sur l'accueil** : passer `body.accueil .site-header` de `absolute` à `sticky; top: 0`, avec condensation au scroll (classe `.condense` posée par `IntersectionObserver` sur un sentinel, `padding` et `height` réduits, titre à 22 px).
    *Succès* : après 400 px de scroll, le titre reste visible ; le wallpaper n'est plus amputé de la hauteur du header.

21. [ ] **Wallpaper sans `background-attachment: fixed`** : sortir l'image de `body` vers `<div class="toile" aria-hidden="true">` en `position: fixed; inset: 0; z-index: -1; background: url(../images/creation.jpg) center/cover`. Supprimer `background-image` de `body` et le bloc `@media (max-width: 640px)` qui échange la vignette.
    *Succès* : rendu identique, repaint au scroll mesurablement réduit (onglet Performance, pas de « Paint » pleine page par frame).

22. [ ] **Survol de la galerie** : `img { transition: transform .6s var(--courbe) }`, `figure:hover img { transform: scale(1.04) }`, plus passage de `figcaption` d'un `opacity` à un `translateY(8px) → 0` avec un `linear-gradient` en bas au lieu du violet `rgba(85,0,175,.3)`.
    ⚠️ **Modifier le gabarit dans `build-galerie.py`**, pas `index.html` — puis relancer `python3 build-galerie.py`.
    *Succès* : `python3 build-galerie.py --check` sort 0, `git diff index.html` ne montre que le bloc galerie, zoom fluide à 60 fps.

23. [ ] **Révélation au scroll** : `IntersectionObserver` avec `threshold: .15` posant `.visible` sur les `figure` de la galerie, `opacity: 0 → 1` + `translateY(16px) → 0`. Désactivé si `prefers-reduced-motion` ou si `IntersectionObserver` absent.
    *Succès* : les tuiles apparaissent une fois, ne rejouent pas au scroll arrière, et restent visibles sans JS.

> **Commit de fin de phase 5** : `feat(accueil): header sticky, wallpaper fixe performant, survols de galerie`

### Phase 6 — Meta sociales et cache-busting

24. [ ] **Image de partage 1200×630.** Générer `images/partage.jpg` depuis `images/creation.jpg` (recadrage centré) :
    `sips -Z 1200 images/creation.jpg --out /tmp/p.jpg && sips -c 630 1200 /tmp/p.jpg --out images/partage.jpg`
    Puis ajouter dans les 4 pages : `og:title`, `og:description`, `og:image` (absolue `https://jeanchri.com/images/partage.jpg`), `og:type`, `og:locale` `fr_FR`, `twitter:card` `summary_large_image`, `theme-color` `#1e262e`.
    *Succès* : carte de prévisualisation correcte via `https://cards-dev.twitter.com/validator` ou un débogueur OG équivalent.

25. [ ] **Cache-busting automatique.** Dans `build-galerie.py`, calculer un hash court (`hashlib.md5`) de `assets/style.css` et `assets/menu.js` et réécrire les `?v=` dans les 4 HTML lors de l'exécution. Ajouter `--check` pour détecter un `?v=` périmé.
    *Succès* : après une modification de `style.css`, `python3 build-galerie.py --check` sort 1 et l'exécution met les 4 fichiers à jour.

26. [ ] **JSON-LD `Person`** dans `index.html` (nom `jeanChri`, `jobTitle`, `url`, `sameAs` = Facebook / YouTube / LinkedIn déjà présents dans le footer).
    *Succès* : pas d'erreur au test des résultats enrichis Google.

> **Commit de fin de phase 6** : `feat(seo): meta sociales, image de partage, cache-busting automatique`

### Phase 7 — Validation

27. [ ] **Passe finale** — `python3 build-galerie.py --check` (0), validation HTML des 4 pages, `axe` en console sur les 4 pages (0 `violation` sérieuse), captures après aux 3 largeurs, superposition avant/après.
    *Succès* : aucune régression visuelle non intentionnelle, 0 violation critique d'accessibilité.

28. [ ] **Déployer** — merge sur `main`, push (GitHub Pages), vérifier `https://jeanchri.com` en cache neuf (navigation privée).
    *Rollback* : `git revert` du merge commit ; GitHub Pages republie l'état précédent sans manipulation manuelle.

## Files Likely to Change

- `assets/style.css` — réécriture de la couche tokens, système de verre, échelle typographique, menu, galerie, header sticky, bloc `prefers-reduced-motion`. **Le gros du travail.**
- `assets/menu.js` — focus trap, `inert`, calcul de l'origine du `clip-path`. Passage de ~41 à ~110 lignes.
- `index.html` — fonts, meta sociales, JSON-LD, burger `aria-hidden`, `--i` du menu, `div.toile`. Le bloc galerie est régénéré, pas édité à la main.
- `portfolio/index.html`, `jeanchri-musique/index.html`, `aux-temps-possibles/index.html` — mêmes changements de `<head>`, fil d'Ariane, `--i`, `div.toile`.
- `build-galerie.py` — gabarit `<figure>` (survol/légende), hash de cache-busting, `--check` étendu.
- `images/partage.jpg` — **nouveau fichier**, 1200×630.

## Tests / Validation

Aucun framework de test dans le repo — la validation est manuelle et scriptée, pas unitaire.

- [ ] `python3 build-galerie.py --check` sort 0 avant et après chaque phase (sauf après ajout de l'extension `--check` de l'étape 25).
- [ ] Contraste : les 6 tokens de texte atteignent 4.5:1 sur leur fond réel (inspecteur ou `npx pa11y`).
- [ ] Clavier : Tab/Shift+Tab dans le menu restent cycliques ; Esc ferme et rend le focus au burger ; le burger est atteignable au Tab depuis le haut de page.
- [ ] `prefers-reduced-motion: reduce` : ouverture du menu instantanée, galerie sans zoom ni révélation.
- [ ] `@supports` : en désactivant `backdrop-filter`, header, cartes, fil d'Ariane et menu restent lisibles.
- [ ] 390 / 768 / 1440 px : aucune superposition burger/header, fil d'Ariane aligné, galerie 1/2/3 colonnes.
- [ ] Perf : onglet Performance, scroll de l'accueil → pas de « Paint » plein écran par frame après l'étape 21.
- [ ] Sans JS : galerie et contenu entièrement visibles (la révélation au scroll doit être une amélioration, pas une condition d'affichage).
- [ ] Rollback : `git revert <merge>` puis vérifier que `https://jeanchri.com` revient à l'état précédent.

## Risks & Tradeoffs

- **Instrument Serif n'a qu'un poids (400)**: élevée × moyen — `.entry-title` et les entrées de menu perdent la graisse 500/700 qui les distinguait aujourd'hui. Mitigation : compenser par l'échelle et la casse (`text-transform`, `letter-spacing`), valider sur `jeanchri-musique/` qui a le plus de niveaux ; basculer sur **Fraunces** (variable, 100→900) si le rendu est trop plat.
- **Modifier `index.html` au lieu de `build-galerie.py`** : élevée × élevé — le prochain `python3 build-galerie.py` écrase silencieusement le travail. Mitigation : étape 22 impose le générateur, et `--check` est lancé après chaque retouche de galerie.
- **Grain + blur sur 5 surfaces** : moyenne × moyen — coût GPU réel sur machines anciennes et iOS. Mitigation : opacité `.04`, pas de `will-change` permanent, grain limité à la couche `body::after`, mesure en Performance avant merge.
- **`clip-path: circle()` animé** : moyenne × moyen — janky sur Safari ancien, et l'origine doit suivre le burger si la fenêtre est redimensionnée. Mitigation : fallback fade sous `@supports`, recalcul de `--origine-menu` sur `resize`.
- **Focus trap maison** : faible × élevé — une erreur enferme l'utilisateur clavier dans le menu. Mitigation : tester les 8 Tab + Escape + clic sur lien, avant commit.
- **Header sticky sur l'accueil** : moyenne × moyen — l'accueil repose aujourd'hui sur une photo pleine page ; un header permanent réduit l'effet hero. Mitigation : condensation agressive (titre 22 px) et fond quasi transparent au repos.
- **Cache-busting automatique** : faible × moyen — un hash dans 4 fichiers crée des conflits de merge avec le clone parallèle. Mitigation : le clone `~/jeanchri.com/site` a été supprimé le 2026-11-17, il ne reste qu'un checkout.
- **Retrait de `background-attachment: fixed`** : faible × moyen — si le `div.toile` est mal empilé, le wallpaper disparaît ou passe devant le contenu. Mitigation : `z-index: -1` + `isolation: isolate` sur `body`, vérification visuelle avant commit.

## Open Questions

- **Frapper ou pas le hero ?** Le header sticky (étape 20) transforme l'accueil « photo plein écran avec titre par-dessus » en « photo + header permanent ». C'est le seul changement de composition du plan. On le fait, ou on garde le header en overlay et on ne corrige qu'à partir des pages internes ?
- **Lightbox ?** Aujourd'hui les photos s'ouvrent en `target="_blank"` vers le `.jpg` brut. Une lightbox maison (~40 lignes) serait nettement plus soignée, mais c'est un chantier non listé ci-dessus. À arbitrer.
- **Quelle image pour `images/partage.jpg` ?** `creation.jpg` (l'accueil, cohérent avec la première tuile) ou une photo plus forte visuellement (`feu.jpg`, `vaisseau.jpg`) ?
- **Auto-héberger les polices ?** Google Fonts reste une requête tierce bloquante en `preconnect` seulement. Auto-héberger `Instrument Serif` + `Inter` en woff2 supprime le risque de latence et le transfert de données, au prix de 2 fichiers binaires dans le repo. Non tranché.
- **`portfolio/` est une page vide** (« No items were found matching your selection. ») et n'est pas listée dans le menu. Elle reste en ligne et dans le `sitemap.xml`. On la masque (`noindex`), ou on la remplit ?
