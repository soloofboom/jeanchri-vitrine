// Interactions de page : en-tête condensé, révélation au scroll, visionneuse.
// Le menu plein écran vit dans menu.js ; tout le reste est ici.
(function () {
  // --- En-tête condensé (accueil) ---------------------------------------
  // L'en-tête de l'accueil est en position: fixed, donc changer sa hauteur ne
  // provoque aucun reflow du contenu. On bascule juste une classe.
  var entete = document.querySelector('.site-header');
  if (entete && document.body.classList.contains('accueil')) {
    var condense = null;
    var enAttente = false;

    var majEntete = function () {
      enAttente = false;
      var etat = window.scrollY > 30;
      if (etat === condense) return;
      condense = etat;
      entete.classList.toggle('condense', etat);
    };

    window.addEventListener('scroll', function () {
      if (enAttente) return;
      enAttente = true;
      requestAnimationFrame(majEntete);
    }, { passive: true });

    majEntete();
  }

  // --- Révélation au scroll ---------------------------------------------
  // L'état caché vient de `.js .galerie figure` : sans JS, rien n'est masqué.
  var figures = Array.prototype.slice.call(document.querySelectorAll('.galerie figure'));

  if (figures.length) {
    if (!('IntersectionObserver' in window)) {
      figures.forEach(function (f) { f.classList.add('visible'); });
    } else {
      var observateur = new IntersectionObserver(function (entrees) {
        entrees.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('visible');
          observateur.unobserve(e.target); // une seule fois, pas de rejeu
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

      figures.forEach(function (f) { observateur.observe(f); });
    }
  }

  // --- Visionneuse ------------------------------------------------------
  var liens = Array.prototype.slice.call(document.querySelectorAll('.galerie a[data-zoom]'));
  if (!liens.length) return;

  var voile = document.createElement('div');
  voile.className = 'visionneuse';
  voile.setAttribute('role', 'dialog');
  voile.setAttribute('aria-modal', 'true');
  voile.setAttribute('aria-label', 'Image agrandie');

  var image = document.createElement('img');
  image.alt = '';

  var legende = document.createElement('p');
  legende.className = 'visionneuse-legende';

  function bouton(classe, libelle, texte) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = classe;
    b.setAttribute('aria-label', libelle);
    b.textContent = texte;
    return b;
  }

  var btnFermer = bouton('visionneuse-fermer', 'Fermer', '\u00d7');
  var btnPrec = bouton('visionneuse-prec', 'Image pr\u00e9c\u00e9dente', '\u2039');
  var btnSuiv = bouton('visionneuse-suiv', 'Image suivante', '\u203a');
  var boutons = [btnFermer, btnPrec, btnSuiv];

  voile.appendChild(image);
  voile.appendChild(legende);
  boutons.forEach(function (b) { voile.appendChild(b); });
  document.body.appendChild(voile);

  var index = 0;
  var retourFocus = null;

  function afficher(i) {
    index = (i + liens.length) % liens.length;
    var lien = liens[index];
    var vignette = lien.querySelector('img');
    image.src = lien.getAttribute('href');
    image.alt = vignette ? vignette.alt : '';
    legende.textContent = vignette ? vignette.alt : '';
  }

  function ouvrir(i, declencheur) {
    retourFocus = declencheur || document.activeElement;
    afficher(i);
    voile.classList.add('ouverte');
    document.body.classList.add('visionneuse-ouverte');
    btnFermer.focus({ preventScroll: true });
  }

  function fermer() {
    voile.classList.remove('ouverte');
    document.body.classList.remove('visionneuse-ouverte');
    if (retourFocus && typeof retourFocus.focus === 'function') {
      retourFocus.focus({ preventScroll: true });
    }
  }

  liens.forEach(function (lien, i) {
    lien.addEventListener('click', function (e) {
      // Clic avec modificateur : on laisse le navigateur ouvrir le .jpg.
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      e.preventDefault();
      ouvrir(i, lien);
    });
  });

  voile.addEventListener('click', function (e) {
    if (e.target === voile) { fermer(); return; }
    if (e.target === btnFermer) { fermer(); return; }
    if (e.target === btnPrec) { afficher(index - 1); return; }
    if (e.target === btnSuiv) { afficher(index + 1); }
  });

  document.addEventListener('keydown', function (e) {
    if (!voile.classList.contains('ouverte')) return;

    if (e.key === 'Escape') {
      e.preventDefault();
      fermer();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      afficher(index - 1);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      afficher(index + 1);
    } else if (e.key === 'Tab') {
      // Trois boutons seulement : on boucle sans laisser filer le focus.
      e.preventDefault();
      var actif = boutons.indexOf(document.activeElement);
      var suivant;
      if (e.shiftKey) {
        suivant = actif <= 0 ? boutons.length - 1 : actif - 1;
      } else if (actif === -1 || actif === boutons.length - 1) {
        suivant = 0;
      } else {
        suivant = actif + 1;
      }
      boutons[suivant].focus({ preventScroll: true });
    }
  });
})();
