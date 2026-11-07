/* Homepage behaviour not covered by scripts/site-shell.js (shared menu handling). */
document.addEventListener('DOMContentLoaded', () => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const syncScroll = () => { document.documentElement.style.scrollBehavior = reduced.matches ? 'auto' : ''; };
  syncScroll();
  reduced.addEventListener('change', syncScroll);
  document.getElementById('backTop')?.addEventListener('click', () => scrollTo({ top: 0, behavior: reduced.matches ? 'auto' : 'smooth' }));
});
