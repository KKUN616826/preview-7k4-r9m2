/* Standalone leaderboard: one result snapshot drives sorting and model details. */
(() => {
  const payload = document.getElementById('leaderboardExplorerData');
  if (!payload) return;
  const data = JSON.parse(payload.textContent);
  const views = new Map(data.views.map(view => [view.key, view]));
  const models = new Map(data.models.map(model => [model.id, model]));
  const tbody = document.querySelector('.lb-table tbody');
  const rows = new Map([...tbody.querySelectorAll('.lb-result')].map(row => [row.dataset.model, row]));
  const details = new Map([...tbody.querySelectorAll('.lb-detail-row')].map(row => [row.dataset.detailModel, row]));
  const defaults = () => ({view: 'mind', metric: 'score', direction: 'desc', model: null, pending: false});
  function readURL() {
    const query = new URLSearchParams(location.search), state = defaults();
    if (views.has(query.get('view'))) state.view = query.get('view');
    if (query.get('metric') === 'success') state.metric = 'success';
    if (query.get('direction') === 'asc') state.direction = 'asc';
    if (models.has(query.get('model'))) state.model = query.get('model');
    state.pending = query.get('pending') === 'true';
    if (state.model && data.models.find(m => m.id === state.model).results[state.view][state.metric] == null) state.pending = true;
    return state;
  }
  let state = readURL();
  const value = model => model.results[state.view][state.metric];
  function writeURL(mode = 'push', hash) {
    const url = new URL(location.href), initial = defaults();
    for (const key of Object.keys(initial)) url.searchParams.delete(key);
    for (const key of ['columns', 'q', 'paradigm', 'status']) url.searchParams.delete(key);
    for (const key of ['view', 'metric', 'direction', 'model', 'pending']) {
      if (state[key] !== initial[key] && state[key] != null) url.searchParams.set(key, state[key]);
    }
    if (hash) url.hash = hash;
    if (url.href !== location.href) history[mode === 'replace' ? 'replaceState' : 'pushState'](null, '', url);
  }
  function render() {
    const focusedResultControl = tbody.contains(document.activeElement) ? document.activeElement : null;
    const selectedView = views.get(state.view);
    const ranked = data.models.filter(model => value(model) != null).sort((a, b) => value(b) - value(a));
    const ranks = new Map(ranked.map(model => [model.id, ranked.findIndex(other => value(other) === value(model)) + 1]));
    const ordered = [...data.models].sort((a, b) => {
      if (value(a) == null && value(b) == null) return 0;
      if (value(a) == null) return 1;
      if (value(b) == null) return -1;
      return state.direction === 'desc' ? value(b) - value(a) : value(a) - value(b);
    });
    let count = 0;
    const visible = new Set();
    const fragment = document.createDocumentFragment();
    for (const model of ordered) {
      const row = rows.get(model.id), detail = details.get(model.id);
      const hasValue = value(model) != null;
      const matches = hasValue || state.pending;
      row.hidden = !matches;
      row.dataset.stripe = String(matches && count % 2 === 1);
      row.querySelector('.lb-rank').textContent = ranks.get(model.id) || '—';
      row.classList.toggle('lb-unreported', !hasValue);
      row.dataset.top = String(ranks.get(model.id) === 1);
      row.querySelectorAll('[data-value]').forEach(cell => cell.dataset.sorted = String(cell.dataset.group === state.view && cell.dataset.value === state.metric));
      if (matches) { count++; visible.add(model.id); }
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
    const pendingCount = data.models.length - ranked.length;
    const pendingButton = document.getElementById('lb-pending');
    pendingButton.hidden = pendingCount === 0;
    pendingButton.setAttribute('aria-expanded', String(state.pending));
    pendingButton.textContent = `${state.pending ? 'Hide' : 'Show'} ${pendingCount} models without ${selectedView.label} ${state.metric === 'score' ? 'Score' : 'Success'} results ${state.pending ? '−' : '+'}`;
    document.getElementById('lb-status-line').textContent = `${ranked.length} models with reported results`;
    document.querySelectorAll('.lb-detail-row > td').forEach(cell => cell.colSpan = matchMedia('(max-width:760px)').matches ? 4 : 5);
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
  document.querySelectorAll('[data-rank-view]').forEach(button => button.addEventListener('click', () => update({view: button.dataset.rankView, metric: 'score', direction: 'desc', model: null})));
  document.querySelectorAll('[data-sort-view]').forEach(button => button.addEventListener('click', () => {
    const same = state.view === button.dataset.sortView && state.metric === button.dataset.sortMetric;
    update({view: button.dataset.sortView, metric: button.dataset.sortMetric, direction: same && state.direction === 'desc' ? 'asc' : 'desc'});
  }));
  document.querySelectorAll('[data-details]').forEach(button => button.addEventListener('click', () => {
    update({model: state.model === button.dataset.details ? null : button.dataset.details});
  }));
  document.getElementById('lb-pending').addEventListener('click', () => update({pending: !state.pending}));
  document.querySelectorAll('[data-jump-view]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    update({view: link.dataset.jumpView, metric: 'score', direction: 'desc'}, 'push', 'results');
    document.getElementById('results').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  }));
  window.addEventListener('lb:select', event => {
    const {view,model,reveal}=event.detail||{};
    if (!views.has(view)) return;
    update({view,metric:'score',direction:'desc', ...(model&&models.has(model)?{model,pending:models.get(model).results[view].score==null}:{})});
    if (reveal) {
      const target=model?rows.get(model):document.getElementById('results');
      target?.scrollIntoView({block:model?'center':'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
    }
  });
  matchMedia('(max-width:760px)').addEventListener('change', render);
  window.addEventListener('popstate', () => { state = readURL(); render(); });
  render();
})();
