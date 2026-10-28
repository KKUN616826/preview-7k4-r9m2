(() => {
  const root = document.querySelector('.capability-map');
  if (!root) return;
  const suites = JSON.parse(root.querySelector('#cm-data').textContent);
  const orbit = root.querySelector('.cm-orbit');
  const cards = [...root.querySelectorAll('.cm-orbit-card')];
  const controls = [...root.querySelectorAll('[data-suite], [data-task]')];
  const canvas = root.querySelector('.cm-particles');
  const ctx = canvas.getContext('2d');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const coarse = matchMedia('(pointer: coarse)');
  const motion = root.querySelector('.cm-motion');
  const detail = root.querySelector('.cm-detail');
  const label = root.querySelector('.cm-detail-label');
  const title = root.querySelector('.cm-detail-title');
  const copy = root.querySelector('.cm-detail-copy');
  const link = root.querySelector('.cm-detail-link');
  const preview=root.querySelector('.cm-task-preview');
  const closePreview=root.querySelector('.cm-preview-close');
  let selectedCard=null;
  const colors = ['#4a786a','#456d85','#8b743d'];
  const tau = Math.PI*2;
  const total=suites.reduce((n,s)=>n+s.cases.length,0);
  let yaw=-.28, pitch=-.12, target=null, selected=null, suiteKey=null;
  let visible=false, hovering=false, focused=false, paused=coarse.matches, frame=0, lastTime=0;
  let size=420, radius=150, perspective=760, dragging=null, suppressClick=false;
  const points = cards.map((card,i) => {
    const group=suites.findIndex(s=>s.slug===card.dataset.parent);
    const index=suites[group].cases.findIndex(c=>c.id===card.dataset.task);
    // Two staggered meridians per suite keep all ten tasks on the same sphere.
    const rows=Math.ceil(suites[group].cases.length/2);
    const row=index%rows, column=Math.floor(index/rows);
    const lat=(-55+row*(110/Math.max(1,rows-1))+column*4)*Math.PI/180;
    const lon=group*tau/3+(column-.5)*.98+(row%2 ? .05 : -.05);
    return {card,lat,lon,v:[Math.cos(lat)*Math.sin(lon),Math.sin(lat),Math.cos(lat)*Math.cos(lon)]};
  });
  const dust = Array.from({length:780},(_,i)=>{
    const y=1-2*(i+.5)/780, phi=i*2.399963229728653;
    const v=[Math.sqrt(1-y*y)*Math.cos(phi),y,Math.sqrt(1-y*y)*Math.sin(phi)];
    const group=Math.floor(((Math.atan2(v[0],v[2])+Math.PI/3+tau)%tau)/(tau/3));
    return {v,group};
  });
  function rotate(v) {
    const x=v[0]*Math.cos(yaw)+v[2]*Math.sin(yaw);
    const z=-v[0]*Math.sin(yaw)+v[2]*Math.cos(yaw);
    return [x,v[1]*Math.cos(pitch)-z*Math.sin(pitch),v[1]*Math.sin(pitch)+z*Math.cos(pitch)];
  }
  function render() {
    if(ctx) {
      ctx.clearRect(0,0,size,size);
      // A continuous, perspective-correct silhouette gives the dots a readable sphere.
      const r=radius*1.02, silhouette=r/Math.sqrt(1-(r/perspective)**2), center=size/2;
      const surface=ctx.createRadialGradient(center-r*.32,center-r*.38,r*.06,center,center,silhouette);
      surface.addColorStop(0,'rgba(255,255,255,.12)');
      surface.addColorStop(.65,'rgba(173,194,186,.035)');
      surface.addColorStop(1,'rgba(93,129,136,.13)');
      ctx.fillStyle=surface;ctx.beginPath();ctx.arc(center,center,silhouette,0,tau);ctx.fill();
      ctx.strokeStyle='rgba(95,130,137,.28)';ctx.lineWidth=.8;ctx.stroke();
      const activeGroup=suites.findIndex(s=>s.slug===suiteKey);
      const particles=dust.map(p=>({position:rotate(p.v),group:p.group})).sort((a,b)=>a.position[2]-b.position[2]);
      for(const particle of particles) {
        const [x,y,z]=particle.position, scale=perspective/(perspective-z*r);
        const depth=(z+1)/2;
        ctx.globalAlpha=(.12+.72*depth**1.6)*(activeGroup>=0&&particle.group!==activeGroup?.42:1);
        ctx.fillStyle=colors[particle.group];ctx.beginPath();
        ctx.arc(center+x*r*scale,center+y*r*scale,(.8+depth*1.05)*Math.max(.7,size/500),0,tau);ctx.fill();
      }
      ctx.globalAlpha=1;
    }
    for(const point of points) {
      const [x,y,z]=rotate(point.v);
      const card=point.card, matching=!suiteKey || card.dataset.parent===suiteKey;
      card.style.transform=`translate3d(${x*radius}px,${y*radius}px,${z*radius}px) scale(${card.dataset.task===selected?1.12:.92})`;
      card.style.opacity=String((.16+.84*((z+1)/2)**1.25)*(matching?1:.32));
      card.style.filter=z<-.15?'saturate(.6)':'none';
    }
  }
  function auto() {return !paused&&!selected&&!hovering&&!focused&&!dragging&&!reduced.matches;}
  function updateMotion() {
    const disabled=reduced.matches;
    motion.disabled=disabled;
    motion.textContent=disabled?'Motion reduced':paused||selected?'Play rotation':'Pause rotation';
    motion.setAttribute('aria-pressed',String(paused||!!selected));
  }
  function tick(now) {
    frame=0;
    const dt=Math.min((now-(lastTime||now))/1000,.05);lastTime=now;
    if(target) {
      const delta=Math.atan2(Math.sin(target.yaw-yaw),Math.cos(target.yaw-yaw));
      const blend=reduced.matches?1:1-Math.exp(-dt*9);
      yaw+=delta*blend;pitch+=(target.pitch-pitch)*blend;
      if(Math.abs(delta)<.002&&Math.abs(target.pitch-pitch)<.002){yaw=target.yaw;pitch=target.pitch;target=null;}
    } else if(auto()) yaw+=dt*.10;
    render();
    if(visible&&!document.hidden&&(target||auto())) frame=requestAnimationFrame(tick);
  }
  function wake() { if(!frame&&visible&&!document.hidden){lastTime=0;frame=requestAnimationFrame(tick);} }
  function select(el) {
    selected=el ? el.dataset.task||el.dataset.suite : null;
    const suite=suites.find(s=>s.slug===(el?.dataset.parent||el?.dataset.suite));
    const task=suite?.cases.find(t=>t.id===el?.dataset.task);
    suiteKey=suite?.slug||null;
    root.classList.toggle('cm-has-selection',!!selected);
    detail.className='cm-detail'+(suite?` cm-${suite.slug} cm-detail-selected`:'');
    controls.forEach(c=>{
      c.setAttribute('aria-pressed',String(!!selected&&(c.dataset.task||c.dataset.suite)===selected));
      c.classList.toggle('is-context',!!suite&&(c.dataset.parent||c.dataset.suite)===suite.slug);
    });
    label.textContent=task?`${suite.name} · Easy / Medium / Hard`:suite?`${suite.name} · ${suite.cases.length} tasks`:'THE FULL BENCHMARK';
    title.textContent=task?`${task.id} · ${task.title}`:suite?suite.label:'Three views of robotic manipulation';
    copy.textContent=task?task.summary:suite?suite.description:'Explore tasks across three suites, with Easy, Medium, and Hard configurations.';
    link.href=task?`tasks/${task.id}.html`:suite?`benchmark/${suite.slug}.html`:'benchmark.html';
    link.textContent=task?'View task ↗':suite?`Explore ${suite.cases.length} ${suite.name} tasks ↗`:`Explore all ${total} tasks ↗`;
    const point=task?points.find(p=>p.card.dataset.task===task.id):null;
    preview.hidden=!task;
    if(task){
      selectedCard=point.card;
      preview.className=`cm-task-preview cm-${suite.slug}`;
      const image=preview.querySelector('.cm-preview-image');
      image.src=task.row_cover||task.cover;image.alt=task.title+' demonstration';
      preview.querySelector('.cm-preview-meta').textContent=`${suite.name} · ${task.id}`;
      preview.querySelector('#cm-preview-title').textContent=task.title;
      preview.querySelector('.cm-preview-link').href=`tasks/${task.id}.html`;
      if(!reduced.matches)preview.animate([{opacity:0,translate:'0 8px'},{opacity:1,translate:'0 0'}],{duration:220,easing:'ease-out'});
      // Give keyboard users a visible close control instead of leaving focus behind the card.
      if(document.activeElement===el)closePreview.focus({preventScroll:true});
    }
    target=point?{yaw:-point.lon,pitch:point.lat}:suite?{yaw:-suites.indexOf(suite)*tau/3,pitch:0}:{yaw:-.28,pitch:-.12};
    if(selected&&!reduced.matches) detail.animate([{opacity:.55},{opacity:1}],{duration:220});
    if(selected) {
      const readingTarget=task?preview:detail;
      const box=readingTarget.getBoundingClientRect();
      if(box.top<110||box.bottom>innerHeight-12) readingTarget.scrollIntoView({block:'nearest',behavior:'instant'});
    }
    updateMotion();wake();
  }
  controls.forEach(el=>{
    el.addEventListener('click',()=>{if(!suppressClick)select(el);});
    el.addEventListener('pointerenter',()=>{
      const slug=el.dataset.parent||el.dataset.suite;
      root.querySelectorAll('.cm-suite-choice').forEach(c=>c.classList.toggle('is-preview',c.dataset.suite===slug));
    });
    el.addEventListener('pointerleave',()=>root.querySelectorAll('.is-preview').forEach(c=>c.classList.remove('is-preview')));
  });
  orbit.addEventListener('pointerenter',()=>{hovering=true;});
  orbit.addEventListener('pointerleave',()=>{hovering=false;wake();});
  orbit.addEventListener('focusin',e=>{
    focused=true;
    const point=points.find(p=>p.card===e.target);
    if(point){target={yaw:-point.lon,pitch:point.lat};wake();}
  });
  orbit.addEventListener('focusout',()=>{requestAnimationFrame(()=>{focused=orbit.contains(document.activeElement);wake();});});
  orbit.addEventListener('pointerdown',e=>{
    if(e.button!==0)return;
    dragging={id:e.pointerId,x:e.clientX,y:e.clientY,yaw,pitch,moved:false};target=null;
  });
  orbit.addEventListener('pointermove',e=>{
    if(!dragging||e.pointerId!==dragging.id)return;
    const dx=e.clientX-dragging.x,dy=e.clientY-dragging.y;
    if(!dragging.moved&&Math.hypot(dx,dy)<7)return;
    if(!dragging.moved){dragging.moved=true;orbit.setPointerCapture(e.pointerId);orbit.classList.add('is-dragging');}
    yaw=dragging.yaw+dx*.008;pitch=Math.max(-1.2,Math.min(1.2,dragging.pitch-dy*.008));render();
  });
  function endDrag(e) {
    if(!dragging||e.pointerId!==dragging.id)return;
    const moved=dragging.moved;dragging=null;orbit.classList.remove('is-dragging');
    if(orbit.hasPointerCapture(e.pointerId))orbit.releasePointerCapture(e.pointerId);
    if(moved){paused=true;suppressClick=true;setTimeout(()=>{suppressClick=false;},0);updateMotion();}
    wake();
  }
  orbit.addEventListener('pointerup',endDrag);orbit.addEventListener('pointercancel',endDrag);
  window.addEventListener('pointerup',endDrag);
  function dismissPreview(){
    const origin=selectedCard;selectedCard=null;select(null);
    if(origin)origin.focus({preventScroll:true});
  }
  closePreview.addEventListener('click',dismissPreview);
  root.addEventListener('keydown',event=>{if(event.key==='Escape'&&!preview.hidden){event.preventDefault();dismissPreview();}});
  root.querySelector('.cm-reset').addEventListener('click',()=>select(null));
  motion.addEventListener('click',()=>{
    if(selected){select(null);paused=false;}else paused=!paused;
    updateMotion();wake();
  });
  const resize=new ResizeObserver(()=>{
    size=orbit.clientWidth;radius=size*(innerWidth>850?.42:.40);
    // Scale the viewing distance with the desktop sphere, so cards keep their screen size.
    perspective=innerWidth>850?radius*3.8:760;
    root.querySelector('.cm-orbit-cards').style.perspective=perspective+'px';
    const dpr=Math.min(devicePixelRatio||1,1.5);canvas.width=Math.round(size*dpr);canvas.height=Math.round(size*dpr);
    ctx?.setTransform(dpr,0,0,dpr,0,0);render();
  });resize.observe(orbit);
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)wake();else if(frame){cancelAnimationFrame(frame);frame=0;}},{threshold:.05}).observe(root);
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&frame){cancelAnimationFrame(frame);frame=0;}else wake();});
  reduced.addEventListener('change',()=>{updateMotion();wake();});
  updateMotion();render();
})();
