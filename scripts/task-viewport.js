/* Fit task media around the actual heading and navigation, without cropping video. */
(() => {
  const main = document.querySelector('body.task-detail main.workspace-content');
  if (!main) return;
  function fit() {
    if (!matchMedia('(min-width:851px)').matches) {
      main.style.removeProperty('--task-fit-video-height');
      return;
    }
    const toolbar = main.querySelector('.demo-toolbar');
    const footer = main.querySelector('.task-footer');
    if (!toolbar || !footer) return;
    const mediaTop = toolbar.getBoundingClientRect().bottom + window.scrollY;
    const footerSpace = footer.getBoundingClientRect().height + 12;
    const remaining = window.innerHeight - mediaTop - footerSpace - 34 - 20;
    main.style.setProperty('--task-fit-video-height', `${Math.max(180, remaining)}px`);
  }
  const observer = new ResizeObserver(fit);
  ['.task-head', '.demo-toolbar', '.task-footer'].forEach(selector => {
    const element = main.querySelector(selector);
    if (element) observer.observe(element);
  });
  window.addEventListener('resize', fit);
  window.addEventListener('hashchange', fit);
  document.fonts.ready.then(fit);
  fit();
})();
