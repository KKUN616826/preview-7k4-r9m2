/* Keep the contents rail aligned with the section currently being read. */
(() => {
  const rail = document.querySelector('.documentation aside');
  if (!rail || !('IntersectionObserver' in window)) return;
  const links = [...rail.querySelectorAll('a[href^="#"]')];
  const sections = links.map(link => document.getElementById(link.hash.slice(1))).filter(Boolean);
  const visible = new Set();
  const select = id => links.forEach(link => {
    if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) visible.add(entry.target);
      else visible.delete(entry.target);
    });
    const atBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4;
    const readingEdge = parseFloat(getComputedStyle(document.body).getPropertyValue('--doc-header-height')) + 36;
    const passed = sections.filter(section => section.getBoundingClientRect().top <= readingEdge);
    const current = atBottom ? sections[sections.length - 1] : passed[passed.length - 1] || sections.find(section => visible.has(section));
    if (current) select(current.id);
  }, { rootMargin: '-110px 0px -35% 0px', threshold: 0 });
  sections.forEach(section => observer.observe(section));
  links.forEach(link => link.addEventListener('click', () => select(link.hash.slice(1))));
})();
