/* Mini-lecteur du menu — lecture/pause et piste suivante.
   YouTube Music n'a pas d'embed : c'est une vidéo YouTube ordinaire dont
   l'image est masquée, pilotée par l'IFrame Player API chargée au premier clic. */
(function () {
  "use strict";

  var PISTES = [
    { id: "O5jdQcj1Lrw", titre: "Altitude", artiste: "Nate Smith · Joel Ross · Michael Mayo" },
    { id: "SCryzwyYnFU", titre: "Your Eyes", artiste: "Robert Glasper" },
    { id: "2adGvQy4POY", titre: "Team Warp", artiste: "Misc" },
    { id: "nrVgXySO0zk", titre: "Into You", artiste: "Moses Yoofee Trio" },
    { id: "s1GRieP2d6s", titre: "Between Us", artiste: "Jacob Karlzon" },
    { id: "s3YpauPC4ZY", titre: "Loving Without Asking", artiste: "Brian Blade" }
  ];

  var racine = document.querySelector("[data-lecteur]");
  if (!racine) return;

  var zone = racine.querySelector("[data-lecteur-video]");
  var boutonLecture = racine.querySelector("[data-lecteur='lecture']");
  var boutonSuivant = racine.querySelector("[data-lecteur='suivant']");

  var index = 0;
  var lecteur = null;
  var pret = false;
  var enLecture = false;
  var lectureDemandee = false;
  var erreurs = 0;
  var chargement = false;

  function afficherPiste() {
    var piste = PISTES[index];
    racine.title = piste.titre + " — " + piste.artiste;
  }

  function refleterEtat() {
    boutonLecture.setAttribute("aria-pressed", enLecture ? "true" : "false");
    boutonLecture.setAttribute("aria-label", enLecture ? "Mettre en pause" : "Lecture");
    boutonLecture.classList.toggle("est-en-lecture", enLecture);
  }

  function pisteSuivante() {
    index = (index + 1) % PISTES.length;
    afficherPiste();
    lectureDemandee = true;
    if (pret) lecteur.loadVideoById(PISTES[index].id);
  }

  function chargerApi() {
    if (chargement) return;
    chargement = true;
    var script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(script);
  }

  window.onYouTubeIframeAPIReady = function () {
    lecteur = new YT.Player(zone, {
      width: "1",
      height: "1",
      host: "https://www.youtube-nocookie.com",
      videoId: PISTES[0].id,
      playerVars: { controls: 0, disablekb: 1, playsinline: 1, rel: 0, origin: location.origin },
      events: {
        onReady: function () {
          pret = true;
          if (index !== 0) lecteur.loadVideoById(PISTES[index].id);
          if (lectureDemandee) lecteur.playVideo();
        },
        onStateChange: function (e) {
          if (e.data === YT.PlayerState.PLAYING) { erreurs = 0; enLecture = true; refleterEtat(); }
          else if (e.data === YT.PlayerState.PAUSED) { enLecture = false; refleterEtat(); }
          else if (e.data === YT.PlayerState.ENDED) pisteSuivante();
        },
        // Une vidéo retirée ou bloquée ne doit pas faire tourner la liste en boucle.
        onError: function () { if (++erreurs < PISTES.length) pisteSuivante(); }
      }
    });
  };

  boutonLecture.addEventListener("click", function () {
    chargerApi();
    if (!pret) { lectureDemandee = true; return; }
    if (enLecture) lecteur.pauseVideo();
    else lecteur.playVideo();
  });

  boutonSuivant.addEventListener("click", function () {
    chargerApi();
    pisteSuivante();
  });

  afficherPiste();
  refleterEtat();
})();
