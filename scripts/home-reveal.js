(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches || !('IntersectionObserver' in window)) return;
  const targets = [...document.querySelectorAll('.lb-stage, .lb-results, .lb-protocol, .lb-scope, .lb-comparison, .lb-evidence, .bo-hero, .bo-explorer-heading, .bo-chapter, .documentation article > section, .project-identity, .academic-project-meta > *, .intro-film, #introduction > *, .intro-overview, #capability-explorer, #news, #top-ten, #tasks, #contributors, #resources-overview')].filter(el => !el.closest('[hidden]')).filter((el, _, all) => !all.some(parent => parent !== el && parent.contains(el)));
  const animations = new Set();
  const observer = new IntersectionObserver(entries => {
    entries.forEach(({target, isIntersecting}) => {
      if (!isIntersecting) return;
      observer.unobserve(target);
      target.classList.remove('home-reveal-pending');
      if (reduced.matches) return;
      const animation = target.animate([
        {opacity:0, transform:'translateY(40px) scale(.985)', offset:0},
        {opacity:1, transform:'translateY(-2px) scale(1)', offset:.8},
        {opacity:1, transform:'translateY(0) scale(1)', offset:1}
      ], {duration:900, easing:'cubic-bezier(.2,.7,.25,1)'});
      animations.add(animation);
      animation.onfinish = () => animations.delete(animation);
    });
  }, {threshold:0, rootMargin:`0px 0px -${Math.round(innerHeight * .25)}px 0px`});
  targets.forEach(el => {
    // Keep initial viewport and direct anchor navigation immediately readable.
    if (el.getBoundingClientRect().bottom <= 0) return;
    el.classList.add('home-reveal-pending');
    observer.observe(el);
  });
  const revealAll = () => {
    observer.disconnect();
    targets.forEach(el => el.classList.remove('home-reveal-pending'));
    animations.forEach(a => a.cancel());
    animations.clear();
  };
  reduced.addEventListener('change', e => { if(e.matches) revealAll(); });
  window.addEventListener('beforeprint', revealAll);

  document.addEventListener('focusin', e => {
    const target = e.target.closest('.home-reveal-pending');
    if(target){observer.unobserve(target);target.classList.remove('home-reveal-pending');}
  });
})();
