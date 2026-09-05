// Menu plein écran (burger)
(function () {
  var trigger = document.querySelector('.dt-menu-trigger');
  if (!trigger) return;

  trigger.addEventListener('click', function () {
    document.body.classList.toggle('menu-ouvert');
  });

  // Fermer au clavier et en cliquant un lien
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') document.body.classList.remove('menu-ouvert');
  });

  document.querySelectorAll('.dt-main-menu a').forEach(function (a) {
    a.addEventListener('click', function () {
      document.body.classList.remove('menu-ouvert');
    });
  });
})();