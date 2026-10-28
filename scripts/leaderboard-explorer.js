/* Standalone leaderboard: one result snapshot drives sorting, filtering and model details. */
(() => {
  const payload = document.getElementById('leaderboardExplorerData');
  if (!payload) return;
  const data = JSON.parse(payload.textContent);
  const views = new Map(data.views.map(view => [view.key, view]));
  const models = new Map(data.models.map(model => [model.id, model]));
  const search = document.getElementById('lb-search');
  const paradigm = document.getElementById('lb-paradigm');
  const status = document.getElementById('lb-status');
  const metric = document.getElementById('lb-metric');
  const tbody = document.querySelector('.lb-table tbody');
  const rows = new Map([...tbody.querySelectorAll('.lb-result')].map(row => [row.dataset.model, row]));
  const details = new Map([...tbody.querySelectorAll('.lb-detail-row')].map(row => [row.dataset.detailModel, row]));
  const defaults = () => ({view: 'mind', metric: 'score', direction: 'desc', paradigm: 'all', status: 'all', q: '', model: null, allMetrics: false});
  function readURL() {
    const query = new URLSearchParams(location.search), state = defaults();
    if (views.has(query.get('view'))) state.view = query.get('view');
    if (query.get('metric') === 'success') state.metric = 'success';
    if (query.get('direction') === 'asc') state.direction = 'asc';
    if (Object.hasOwn(data.paradigms, query.get('paradigm'))) state.paradigm = query.get('paradigm');
    if (['reported', 'pending'].includes(query.get('status'))) state.status = query.get('status');
    state.q = (query.get('q') || '').slice(0, 200);
    if (models.has(query.get('model'))) state.model = query.get('model');
    state.allMetrics = query.get('columns') === 'all';
    return state;
  }
  let state = readURL();
  const value = model => model.results[state.view][state.metric];
  function writeURL(mode = 'push', hash) {
    const url = new URL(location.href), initial = defaults();
    for (const key of Object.keys(initial)) url.searchParams.delete(key);
    url.searchParams.delete('columns');
    for (const key of ['view', 'metric', 'direction', 'paradigm', 'status', 'q', 'model']) {
      if (state[key] !== initial[key] && state[key] != null) url.searchParams.set(key, state[key]);
    }
    if (state.allMetrics) url.searchParams.set('columns', 'all');
    if (hash) url.hash = hash;
    if (url.href !== location.href) history[mode === 'replace' ? 'replaceState' : 'pushState'](null, '', url);
  }
  function render() {
    const focusedResultControl = tbody.contains(document.activeElement) ? document.activeElement : null;
    search.value = state.q;
    paradigm.value = state.paradigm;
    status.value = state.status;
    metric.value = state.metric;
    const selectedView = views.get(state.view);
    const ranked = data.models.filter(model => value(model) != null).sort((a, b) => value(b) - value(a));
    const ranks = new Map(ranked.map(model => [model.id, ranked.findIndex(other => value(other) === value(model)) + 1]));
    const ordered = [...data.models].sort((a, b) => {
      if (value(a) == null && value(b) == null) return 0;
      if (value(a) == null) return 1;
      if (value(b) == null) return -1;
      return state.direction === 'desc' ? value(b) - value(a) : value(a) - value(b);
    });
    let count = 0, reported = 0;
    const visible = new Set();
    const fragment = document.createDocumentFragment();
    for (const model of ordered) {
      const row = rows.get(model.id), detail = details.get(model.id);
      const hasValue = value(model) != null;
      const matches = (state.paradigm === 'all' || state.paradigm === model.paradigm)
        && model.name.toLocaleLowerCase().includes(state.q.trim().toLocaleLowerCase())
        && (state.status === 'all' || (state.status === 'reported' ? hasValue : !hasValue));
      row.hidden = !matches;
      row.querySelector('.lb-rank').textContent = ranks.get(model.id) || '—';
      row.classList.toggle('lb-unreported', !hasValue);
      if (matches) { count++; if (hasValue) reported++; visible.add(model.id); }
      fragment.append(row, detail);
    }
    tbody.append(fragment);
    if (state.model && !visible.has(state.model)) state.model = null;
    for (const [id, detail] of details) {
      const open = state.model === id;
      detail.hidden = !open;
      rows.get(id).classList.toggle('lb-selected', open);
      rows.get(id).querySelectorAll('[data-details]').forEach(button => {
        button.setAttribute('aria-expanded', String(open));
        if (button.classList.contains('lb-details-button')) button.innerHTML = open ? 'Hide <span aria-hidden="true">−</span>' : 'Details <span aria-hidden="true">+</span>';
      });
    }
    document.querySelectorAll('[data-rank-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.rankView === state.view)));
    document.querySelectorAll('.lb-table [data-group]').forEach(cell => {
      cell.dataset.activeGroup = String(cell.dataset.group === state.view);
    });
    document.querySelectorAll('[data-sort-cell]').forEach(cell => {
      const active = cell.dataset.sortCell === `${state.view}-${state.metric}`;
      cell.setAttribute('aria-sort', active ? (state.direction === 'desc' ? 'descending' : 'ascending') : 'none');
      cell.querySelector('.lb-sort-arrow').textContent = active ? (state.direction === 'desc' ? '↓' : '↑') : '↕';
    });
    document.querySelector('.lb-table').dataset.allMetrics = String(state.allMetrics);
    const allButton = document.getElementById('lb-all-metrics');
    allButton.setAttribute('aria-pressed', String(state.allMetrics));
    allButton.textContent = state.allMetrics ? 'Selected suite only' : 'View all metrics';
    document.getElementById('lb-status-line').textContent = `Ranked by ${selectedView.label} ${state.metric === 'score' ? 'Score' : 'Success'} · ${state.direction === 'desc' ? 'Descending' : 'Ascending'} · ${count} entries · ${reported} reported`;
    document.getElementById('lb-empty').hidden = count !== 0;
    document.querySelector('.lb-table-scroll').hidden = count === 0;
    document.querySelectorAll('[data-jump-view]').forEach(link => {
      link.classList.toggle('lb-highlight-active', link.dataset.jumpView === state.view);
    });
    if (focusedResultControl && !focusedResultControl.closest('[hidden]')) focusedResultControl.focus({preventScroll: true});
    window.dispatchEvent(new CustomEvent('lb:state', {detail:{view:state.view,metric:state.metric}}));
  }
  function update(changes, mode = 'push', hash) {
    state = {...state, ...changes};
    render();
    writeURL(mode, hash);
  }
  search.addEventListener('input', () => update({q: search.value}, 'replace'));
  paradigm.addEventListener('change', () => update({paradigm: paradigm.value}));
  status.addEventListener('change', () => update({status: status.value}));
  metric.addEventListener('change', () => update({metric: metric.value, direction: 'desc'}));
  document.querySelector('.lb-filters').addEventListener('submit', event => event.preventDefault());
  document.querySelectorAll('[data-rank-view]').forEach(button => button.addEventListener('click', () => update({view: button.dataset.rankView, direction: 'desc'})));
  document.querySelectorAll('[data-sort-view]').forEach(button => button.addEventListener('click', () => {
    const same = state.view === button.dataset.sortView && state.metric === button.dataset.sortMetric;
    update({view: button.dataset.sortView, metric: button.dataset.sortMetric, direction: same && state.direction === 'desc' ? 'asc' : 'desc'});
  }));
  document.querySelectorAll('[data-details]').forEach(button => button.addEventListener('click', () => {
    update({model: state.model === button.dataset.details ? null : button.dataset.details});
  }));
  document.getElementById('lb-reset').addEventListener('click', () => update(defaults()));
  document.getElementById('lb-clear').addEventListener('click', () => update({q: '', paradigm: 'all', status: 'all'}));
  document.getElementById('lb-all-metrics').addEventListener('click', () => update({allMetrics: !state.allMetrics}));
  document.querySelectorAll('[data-jump-view]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    update({view: link.dataset.jumpView, metric: 'score', direction: 'desc'}, 'push', 'results');
    document.getElementById('results').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  }));
  window.addEventListener('lb:select', event => {
    const {view,model,reveal}=event.detail||{};
    if (!views.has(view)) return;
    update({view,metric:'score',direction:'desc', ...(model&&models.has(model)?{model,q:'',paradigm:'all',status:'all'}:{})});
    if (reveal) {
      const target=model?rows.get(model):document.getElementById('results');
      target?.scrollIntoView({block:model?'center':'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
    }
  });
  window.addEventListener('popstate', () => { state = readURL(); render(); });
  render();
})();
