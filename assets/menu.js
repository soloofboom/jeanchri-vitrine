// Menu plein écran (burger)
// Le menu est un dialogue modal : focus piégé à l'intérieur, reste de la page
// rendu inerte, focus rendu au déclencheur à la fermeture.
(function () {
  var trigger = document.querySelector('.dt-menu-trigger');
  var menu = document.querySelector('.dt-main-menu');
  if (!trigger || !menu) return;

  var ouvert = false;
  var dernierFocus = null;

  // Tout ce qui n'est ni le menu ni le burger devient inerte à l'ouverture.
  var fond = Array.prototype.filter.call(
    document.body.children,
    function (el) { return el !== menu && el !== trigger; }
  );

  menu.setAttribute('aria-hidden', 'true');
  trigger.setAttribute('aria-expanded', 'false');
  trigger.setAttribute('aria-controls', 'menu-principal');

  // Le burger reste dans la boucle : il porte la fermeture et reste au-dessus du menu.
  function focusables() {
    return Array.prototype.slice
      .call(menu.querySelectorAll('a[href], button:not([disabled])'))
      .concat(trigger);
  }

  function basculer(etat) {
    if (etat === ouvert) return;
    ouvert = etat;

    document.body.classList.toggle('menu-ouvert', ouvert);
    trigger.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
    trigger.setAttribute('aria-label', ouvert ? 'Fermer le menu' : 'Ouvrir le menu');
    menu.setAttribute('aria-hidden', ouvert ? 'false' : 'true');

    fond.forEach(function (el) { el.inert = ouvert; });

    if (ouvert) {
      dernierFocus = document.activeElement;
      var premier = menu.querySelector('a');
      if (premier) premier.focus({ preventScroll: true });
    } else if (dernierFocus && typeof dernierFocus.focus === 'function') {
      dernierFocus.focus({ preventScroll: true });
    }
  }

  trigger.addEventListener('click', function () {
    basculer(!ouvert);
  });

  // Fermer au clavier, et maintenir le focus à l'intérieur
  document.addEventListener('keydown', function (e) {
    if (!ouvert) return;

    if (e.key === 'Escape') {
      e.preventDefault();
      basculer(false);
      return;
    }
    if (e.key !== 'Tab') return;

    var liste = focusables();
    if (!liste.length) return;

    var premier = liste[0];
    var dernier = liste[liste.length - 1];
    var actif = document.activeElement;

    // Le focus a fui hors du menu (ex. clic sur le fond) : on le ramène.
    if (!menu.contains(actif) && actif !== trigger) {
      e.preventDefault();
      premier.focus({ preventScroll: true });
      return;
    }

    if (e.shiftKey && actif === premier) {
      e.preventDefault();
      dernier.focus({ preventScroll: true });
    } else if (!e.shiftKey && actif === dernier) {
      e.preventDefault();
      premier.focus({ preventScroll: true });
    }
  });

  // Fermer en cliquant un lien
  menu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { basculer(false); });
  });
})();
