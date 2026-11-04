// Homepage interactions: leaderboard preview tabs and copy buttons.
(() => {
  document.querySelectorAll('.lbp').forEach(card => {
    const tabs = [...card.querySelectorAll('[role=tab]')];
    const select = tab => {
      tabs.forEach(t => {
        const on = t === tab;
        t.setAttribute('aria-selected', on);
        t.tabIndex = on ? 0 : -1;
        const panel = document.getElementById(t.getAttribute('aria-controls'));
        if (!panel) return;
        panel.hidden = !on;
        if (on) panel.querySelectorAll('.bar i').forEach(bar => {
          const width = bar.style.width;
          bar.style.width = '0';
          requestAnimationFrame(() => requestAnimationFrame(() => { bar.style.width = width; }));
        });
      });
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => select(tab));
      tab.addEventListener('keydown', ev => {
        if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
        const next = tabs[(i + (ev.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
        next.focus();
        select(next);
      });
    });
  });

  const flash = (button, text) => {
    const label = button.querySelector('span') || button;
    const original = label.textContent;
    label.textContent = text;
    setTimeout(() => { label.textContent = original; }, 1500);
  };
  document.querySelectorAll('[data-copy], [data-copy-target]').forEach(button => {
    button.addEventListener('click', async () => {
      const target = button.dataset.copyTarget && document.getElementById(button.dataset.copyTarget);
      const text = target ? target.textContent : button.dataset.copy;
      try { await navigator.clipboard.writeText(text); flash(button, button.dataset.copied || 'Copied'); }
      catch { flash(button, 'Press Ctrl+C'); }
    });
  });
})();
