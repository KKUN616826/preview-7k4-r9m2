/* Preserve navigation state across static pages; native links keep browser history reliable. */
(() => {
  const sidebar = document.querySelector('.workspace-sidebar');
  if (!sidebar) return;
  const key = 'mind2act-benchmark-navigation';
  const read = () => {
    try { return JSON.parse(sessionStorage.getItem(key)) || {}; }
    catch { return {}; }
  };
  const save = value => {
    try { sessionStorage.setItem(key, JSON.stringify(value)); }
    catch { /* Navigation still works when storage is unavailable. */ }
  };
  const state = read();
  sidebar.querySelectorAll('[data-group]').forEach(group => {
    const button = group.querySelector('button');
    const list = group.querySelector('ul');
    const open = group.dataset.containsCurrent === 'true' || state.groups?.[group.dataset.group] !== false;
    button.setAttribute('aria-expanded', String(open));
    list.hidden = !open;
  });
  sidebar.scrollTop = Number(state.scroll) || 0;

  const dialog = document.getElementById('task-drawer');
  const trigger = document.getElementById('browse-tasks');
  const drawerNavigation = document.getElementById('drawer-navigation');
  const mobileNav = sidebar.querySelector('nav').cloneNode(true);
  // Distinct IDs keep aria-controls unambiguous when both navigations are in the DOM.
  mobileNav.querySelectorAll('[id]').forEach(el => { el.id = 'drawer-' + el.id; });
  mobileNav.querySelectorAll('[aria-controls]').forEach(el => {
    el.setAttribute('aria-controls', 'drawer-' + el.getAttribute('aria-controls'));
  });
  drawerNavigation.append(mobileNav);

  function persist() {
    const groups = {};
    sidebar.querySelectorAll('[data-group]').forEach(group => {
      groups[group.dataset.group] = group.querySelector('button').getAttribute('aria-expanded') === 'true';
    });
    save({groups, scroll: sidebar.scrollTop});
  }

  for (const container of [sidebar, mobileNav]) {
    container.addEventListener('click', event => {
      const button = event.target.closest('.workspace-group-row button');
      if (!button) return;
      const groupName = button.closest('[data-group]').dataset.group;
      const open = button.getAttribute('aria-expanded') !== 'true';
      for (const nav of [sidebar, mobileNav]) {
        const group = nav.querySelector(`[data-group="${groupName}"]`);
        group.querySelector('button').setAttribute('aria-expanded', String(open));
        group.querySelector('ul').hidden = !open;
      }
      persist();
    });
  }
  window.addEventListener('pagehide', () => {
    persist();
    document.querySelectorAll('video').forEach(video => video.pause());
  });
  // Keep native history restoration on Back, but make direct navigation reveal the selected case.
  if (performance.getEntriesByType('navigation')[0]?.type !== 'back_forward') {
    const active = sidebar.querySelector('a[aria-current="page"]');
    if (active) {
      const bounds = sidebar.getBoundingClientRect(), item = active.getBoundingClientRect();
      if (item.bottom > bounds.bottom || item.top < bounds.top) {
        sidebar.scrollTop += item.top - bounds.top - bounds.height / 2;
      }
    }
  }

  trigger.addEventListener('click', () => {
    dialog.showModal();
    document.documentElement.style.overflow = 'hidden';
    // Focus the current location rather than making users rediscover it.
    const current = mobileNav.querySelector('a[aria-current="page"]');
    if (current) { current.focus(); current.scrollIntoView({block: 'nearest'}); }
  });
  const close = () => dialog.close();
  document.getElementById('close-task-drawer').addEventListener('click', close);
  dialog.addEventListener('click', event => {
    if (event.target === dialog) {
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) close();
    }
  });
  dialog.addEventListener('close', () => {
    document.documentElement.style.overflow = '';
    trigger.focus();
  });
  window.addEventListener('pageshow', () => {
    if (dialog.open) close();
    document.documentElement.style.overflow = '';
  });
  const desktop = matchMedia('(min-width:851px)');
  desktop.addEventListener('change', event => { if (event.matches && dialog.open) close(); });
})();
