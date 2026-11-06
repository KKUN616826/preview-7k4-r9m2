/* Homepage behaviour not covered by scripts/site-shell.js (shared menu handling). */
document.addEventListener('DOMContentLoaded', () => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const syncScroll = () => { document.documentElement.style.scrollBehavior = reduced.matches ? 'auto' : ''; };
  syncScroll();
  reduced.addEventListener('change', syncScroll);
  document.getElementById('backTop')?.addEventListener('click', () => scrollTo({ top: 0, behavior: reduced.matches ? 'auto' : 'smooth' }));
});

/* Leaderboard preview: re-rank the reported models by the chosen suite. */
document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('#top-ten.home-leaderboard');
  if (!root) return;
  const tbody = root.querySelector('tbody');
  const rows = [...tbody.rows];
  function rank(view) {
    const score = row => Number(row.dataset[view]);
    rows.sort((a, b) => score(b) - score(a));
    rows.forEach(row => {
      row.querySelector('.hl-rank').textContent = 1 + rows.filter(other => score(other) > score(row)).length;
      tbody.append(row);
    });
    root.querySelectorAll('[data-hl-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.hlView === view)));
    root.querySelectorAll('thead [data-col]').forEach(cell => {
      if (cell.dataset.col === view) cell.setAttribute('aria-sort', 'descending');
      else cell.removeAttribute('aria-sort');
    });
    root.dataset.view = view;
  }
  root.querySelectorAll('[data-hl-view]').forEach(button => button.addEventListener('click', () => rank(button.dataset.hlView)));
});
