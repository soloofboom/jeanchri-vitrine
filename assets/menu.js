// Menu plein écran (burger)
(function () {
  var trigger = document.querySelector('.dt-menu-trigger');
  var menu = document.querySelector('.dt-main-menu');
  if (!trigger || !menu) return;

  var ouvert = false;

  menu.setAttribute('aria-hidden', 'true');
  trigger.setAttribute('aria-expanded', 'false');
  trigger.setAttribute('aria-controls', 'menu-principal');

  function basculer(etat) {
    ouvert = etat;
    document.body.classList.toggle('menu-ouvert', ouvert);
    trigger.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
    trigger.setAttribute('aria-label', ouvert ? 'Fermer le menu' : 'Ouvrir le menu');
    menu.setAttribute('aria-hidden', ouvert ? 'false' : 'true');
    if (ouvert) {
      var premier = menu.querySelector('a');
      if (premier) premier.focus({ preventScroll: true });
    }
  }

  trigger.addEventListener('click', function () {
    basculer(!ouvert);
  });

  // Fermer au clavier
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && ouvert) {
      basculer(false);
      trigger.focus({ preventScroll: true });
    }
  });

  // Fermer en cliquant un lien
  menu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { basculer(false); });
  });
})();
