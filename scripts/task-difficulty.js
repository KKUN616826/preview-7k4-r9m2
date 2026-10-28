/* Each difficulty owns its video; pending levels never substitute another recording. */
(() => {
  const nav=document.querySelector('.difficulty[data-default]');
  if(!nav)return;
  function select() {
    const requested=location.hash.slice(1);
    const level=['easy','medium','hard'].includes(requested)?requested:nav.dataset.default;
    document.querySelectorAll('[data-level]').forEach(a=>a.setAttribute('aria-current',String(a.dataset.level===level)));
    document.querySelectorAll('[data-panel]').forEach(panel=>{
      panel.hidden=panel.dataset.panel!==level;
      if(panel.hidden)panel.querySelector('video')?.pause();
    });
  }
  addEventListener('hashchange',select);select();
})();
