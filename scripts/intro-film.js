// Native controls, with a modest brightness lift only while showing the poster.
(() => {
  document.querySelectorAll('.intro-film-player video').forEach(video => {
    const showPoster = () => { video.style.filter = 'brightness(1.25)'; };
    showPoster();
    video.addEventListener('play', () => { video.style.removeProperty('filter'); });
    video.addEventListener('ended', () => {
      video.load();
      showPoster();
    });
  });
})();
