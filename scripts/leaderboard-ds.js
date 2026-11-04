// Leaderboard: suite tabs, type filter, rank-by toggle and matrix sorting.
// State is mirrored in the URL (?view=act&type=vla&rank=success).
(() => {
  const views = JSON.parse(document.getElementById('lb-views').textContent);
  const params = new URLSearchParams(location.search);
  const state = {
    view: views[params.get('view')] ? params.get('view') : Object.keys(views)[0],
    type: params.get('type') || 'all',
    rank: params.get('rank') === 'success' ? 'success' : 'score',
  };
  const table = document.getElementById('ranking');
  const body = table.tBodies[0];
  const desc = document.getElementById('lb-view-desc');
  const suiteOf = { mind: 'mind', act: 'act', coupling: 'm2a' };

  const render = () => {
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-selected', b.dataset.view === state.view));
    document.querySelectorAll('.chip[data-type]').forEach(b => b.setAttribute('aria-pressed', b.dataset.type === state.type));
    document.querySelectorAll('[data-rank]').forEach(b => b.setAttribute('aria-selected', b.dataset.rank === state.rank));
    desc.textContent = views[state.view];
    table.dataset.suite = suiteOf[state.view];
    const rows = [...body.rows];
    const value = (row, metric) => parseFloat(row.dataset[`${state.view}${metric[0].toUpperCase()}${metric.slice(1)}`]);
    rows.sort((a, b) => value(b, state.rank) - value(a, state.rank));
    let rank = 0;
    rows.forEach(row => {
      body.appendChild(row);
      const score = value(row, 'score');
      const success = value(row, 'success');
      const visible = (state.type === 'all' || row.dataset.type === state.type) && score >= 0;
      row.hidden = !visible;
      if (!visible) return;
      rank += 1;
      const disc = row.querySelector('.rank');
      disc.textContent = rank;
      disc.className = 'rank' + (rank <= 3 ? ` rank--${rank}` : '');
      row.querySelector('.score').textContent = score.toFixed(2);
      row.querySelector('.bar i').style.width = `${score}%`;
      row.querySelector('.success').textContent = success >= 0 ? `${success.toFixed(1)}%` : '—';
    });
    const next = new URLSearchParams();
    if (state.view !== Object.keys(views)[0]) next.set('view', state.view);
    if (state.type !== 'all') next.set('type', state.type);
    if (state.rank !== 'score') next.set('rank', state.rank);
    history.replaceState(null, '', `${location.pathname}${next.toString() ? '?' + next : ''}${location.hash}`);
  };

  document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => { state.view = b.dataset.view; render(); }));
  document.querySelectorAll('.chip[data-type]').forEach(b => b.addEventListener('click', () => { state.type = b.dataset.type; render(); }));
  document.querySelectorAll('[data-rank]').forEach(b => b.addEventListener('click', () => { state.rank = b.dataset.rank; render(); }));
  render();

  // Matrix: click a column header to sort descending.
  const matrix = document.getElementById('matrix');
  if (matrix) {
    const heads = [...matrix.tHead.rows[0].cells];
    heads.forEach((th, col) => {
      const button = th.querySelector('[data-sort]');
      if (!button) return;
      button.addEventListener('click', () => {
        const rows = [...matrix.tBodies[0].rows];
        rows.sort((a, b) => parseFloat(b.cells[col].dataset.v) - parseFloat(a.cells[col].dataset.v));
        rows.forEach(r => matrix.tBodies[0].appendChild(r));
        heads.forEach(h => h.removeAttribute('aria-sort'));
        th.setAttribute('aria-sort', 'descending');
      });
    });
  }
})();
