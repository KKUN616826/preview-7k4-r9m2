/* Two independent boards (VLA / WAM and coding agents): setting, metric and column sorting.
   Rows without published results stay below the ranked rows, in release order, unranked. */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.lb-board').forEach(board => {
    const tbody = board.querySelector('tbody');
    const ranked = [...tbody.querySelectorAll('tr.lb-result:not(.lb-pending)')];
    const pending = [...tbody.querySelectorAll('tr.lb-pending')];
    const format = (value, metric) => metric === 'success' ? `${Number(value).toFixed(1)}%` : Number(value).toFixed(2);

    function render() {
      const { sort, setting, metric } = board.dataset;
      const value = row => Number(row.querySelector(`td[data-col="${sort}"]`).dataset[`${setting}${metric[0].toUpperCase()}${metric.slice(1)}`]);
      ranked.sort((a, b) => value(b) - value(a));
      ranked.forEach(row => {
        row.querySelector('.lb-rank').textContent = 1 + ranked.filter(other => value(other) > value(row)).length;
        row.querySelectorAll('td[data-col]').forEach(cell => {
          cell.textContent = format(cell.dataset[`${setting}${metric[0].toUpperCase()}${metric.slice(1)}`], metric);
        });
      });
      tbody.append(...ranked, ...pending);
      board.querySelectorAll('thead th[data-col]').forEach(th => {
        const active = th.dataset.col === sort;
        if (active) th.setAttribute('aria-sort', 'descending'); else th.removeAttribute('aria-sort');
        th.querySelector('.lb-sort-arrow').textContent = active ? '↓' : '↕';
      });
      board.querySelectorAll('[data-setting]').forEach(b => { if (b !== board) b.setAttribute('aria-pressed', String(b.dataset.setting === setting)); });
      board.querySelectorAll('button[data-metric]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.metric === metric)));
    }

    board.addEventListener('click', event => {
      const button = event.target.closest('button');
      if (!button || !board.contains(button)) return;
      if (button.dataset.sort) board.dataset.sort = button.dataset.sort;
      else if (button.dataset.setting) board.dataset.setting = button.dataset.setting;
      else if (button.dataset.metric) board.dataset.metric = button.dataset.metric;
      else return;
      render();
    });
    if (ranked.length) render();
  });
});
