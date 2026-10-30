/* Lunar explorer. Task data and all destinations come from the shared catalog.
 * Orthographic projection keeps HTML labels legible; Three.js renders the mesh.
 * Category lighting is attached to local coordinates, so rotating cannot reclassify tasks. */
(async () => {
  const root=document.querySelector('.capability-map');if(!root)return;
  const suites=JSON.parse(root.querySelector('#cm-data').textContent);
  const orbit=root.querySelector('.cm-orbit'),canvas=root.querySelector('canvas');
  const cards=[...root.querySelectorAll('[data-task]')],choices=[...root.querySelectorAll('[data-suite]')];
  const preview=root.querySelector('.cm-task-preview'),close=root.querySelector('.cm-preview-close');
  const motion=root.querySelector('.cm-motion'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let THREE,renderer,scene,camera,moon,geometry,material;
  // The 632px map column and this radius add ~25% sphere area within the 920px page grid.
  const sphereRadius=.4875;
  orbit.style.setProperty('--cm-sphere-inset',`${(0.5-sphereRadius)*100}%`);
  let size=400,visible=false,frame=0,last=0,target=null,selected=null,origin=null,drag=null,suppress=false,playing=false,hover=false;
  let quaternion,base;
  // Keep the populated hemisphere in view; rebuild from two angles to avoid accumulated roll.
  const limits={yaw:Math.PI/3,pitch:Math.PI/9},view={yaw:0,pitch:0};
  let motionCenter={...view},motionPhase=0;
  const clamp=(value,limit)=>Math.max(-limit,Math.min(limit,value));
  function bounded(next){return {yaw:clamp(next.yaw,limits.yaw),pitch:clamp(next.pitch,limits.pitch)}}
  function resisted(value,limit){const magnitude=Math.abs(value);return magnitude<=limit?value:Math.sign(value)*(limit+.055*(1-Math.exp(-(magnitude-limit)/.16)))}
  function applyView(){if(quaternion)quaternion.copy(base).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(view.pitch,view.yaw,0,'XYZ')))}
  function aim(next){target=bounded(next);wake()}
  const connector=root.querySelector('.cm-connector'),visual=root.querySelector('.cm-visual');
  let activePoint=null,pinned=false,enterTimer,leaveTimer,ignoreFocus=false;
  function cancelTimers(){clearTimeout(enterTimer);clearTimeout(leaveTimer)}
  function hidePreview(){cancelTimers();selected=null;activePoint=null;pinned=false;preview.hidden=true;connector.setAttribute('hidden','');cards.forEach(c=>{c.setAttribute('aria-pressed','false');c.classList.remove('is-previewed')})}
  function scheduleHide(){clearTimeout(enterTimer);clearTimeout(leaveTimer);if(!pinned)leaveTimer=setTimeout(()=>{hidePreview();wake()},300)}
  function connectPreview(){
    if(!activePoint||preview.hidden||activePoint.card.dataset.front==='false'){connector.setAttribute('hidden','');return}
    const v=visual.getBoundingClientRect();
    // Shift desktop previews into the outer margin without crossing the viewport edge.
    if(matchMedia('(min-width:851px)').matches){
      preview.style.right=`${-Math.min(36,Math.max(0,innerWidth-v.right-16))}px`;
    }else preview.style.removeProperty('right');
    const n=activePoint.card.getBoundingClientRect(),r=preview.getBoundingClientRect();
    let x=n.x+n.width/2-v.x,y=n.y+n.height/2-v.y;
    const left=r.left-v.left,right=r.right-v.left,top=r.top-v.top,bottom=r.bottom-v.top;
    const candidates=[[left,Math.max(top+12,Math.min(bottom-12,y))],[right,Math.max(top+12,Math.min(bottom-12,y))],[Math.max(left+12,Math.min(right-12,x)),top],[Math.max(left+12,Math.min(right-12,x)),bottom]];
    const [ex,ey]=y<top?[left+(right-left)*.65,top]:y>bottom?[left+(right-left)*.35,bottom]:candidates.sort((a,b)=>Math.hypot(x-a[0],y-a[1])-Math.hypot(x-b[0],y-b[1]))[0];
    const dx=ex-x,dy=ey-y,edge=1/Math.max(Math.abs(dx)/(n.width/2+3),Math.abs(dy)/(n.height/2+3),1);
    x+=dx*edge;y+=dy*edge;
    connector.removeAttribute('hidden');connector.setAttribute('viewBox',`0 0 ${v.width} ${v.height}`);connector.style.color=colors[activePoint.suite.slug];
    connector.querySelector('path').setAttribute('d',`M ${x} ${y} L ${ex+(ex>x?-14:14)} ${ey} L ${ex} ${ey}`);
    connector.querySelector('circle').setAttribute('cx',x);connector.querySelector('circle').setAttribute('cy',y);
  }
  const colors={mind:'#4a786a',act:'#527d9b',mind2act:'#a07b30'};
  const positions=cards.map(card=>{
    const suite=suites.find(s=>s.slug===card.dataset.parent),index=suite.cases.findIndex(t=>t.id===card.dataset.task);
    const row=index%5,column=Math.floor(index/5),lat=(-42+row*21+(column?5:-5))*Math.PI/180;
    const lon=suite.slug==='mind2act'?(column?.14:-.14): (suite.slug==='mind'?-1:1)*(.60+column*.45);
    return {card,suite,task:suite.cases[index],lat,lon,v:[Math.cos(lat)*Math.sin(lon),Math.sin(lat),Math.cos(lat)*Math.cos(lon)]};
  });
  const regionSvg=root.querySelector('.cm-regions');
  const regionLabels=[...root.querySelectorAll('[data-region-label]')];
  function projectRegion(lon,lat){
    let x=Math.cos(lat)*Math.sin(lon),y=Math.sin(lat),z=Math.cos(lat)*Math.cos(lon);
    if(THREE&&quaternion){const v=new THREE.Vector3(x,y,z).applyQuaternion(quaternion);[x,y,z]=v.toArray()}
    else {const a=x;x=a*.866+y*.5;y=-a*.5+y*.866}
    return {x:size*(.5+x*sphereRadius),y:size*(.5-y*sphereRadius),z};
  }
  function renderRegions(){
    regionSvg.setAttribute('viewBox',`0 0 ${size} ${size}`);
    regionSvg.querySelectorAll('[data-band-edge]').forEach(path=>{
      let d='',connected=false;
      for(let i=0;i<=96;i++){
        const point=projectRegion(Number(path.dataset.bandEdge),-Math.PI/2+i*Math.PI/96);
        if(point.z<.012){connected=false;continue}
        d+=`${connected?'L':'M'}${point.x.toFixed(2)} ${point.y.toFixed(2)} `;connected=true;
      }
      path.setAttribute('d',d);
    });
    const bounds=orbit.getBoundingClientRect();
    const anchors={mind:[-.8,.4],act:[.8,-.4],mind2act:[0,1.02]};
    regionLabels.forEach(label=>{
      const slug=label.dataset.regionLabel;
      let point=projectRegion(...anchors[slug]);
      if(point.z<.08){
        const front=positions.filter(p=>p.suite.slug===slug).map(p=>projectRegion(p.lon,p.lat)).filter(p=>p.z>.08);
        if(front.length)point={x:front.reduce((s,p)=>s+p.x,0)/front.length,y:front.reduce((s,p)=>s+p.y,0)/front.length,z:1};
      }
      const path=regionSvg.querySelector(`[data-region-line="${slug}"]`),dot=regionSvg.querySelector(`[data-region-dot="${slug}"]`);
      const r=label.getBoundingClientRect(),centerX=r.x+r.width/2-bounds.x,centerY=r.y+r.height/2-bounds.y;
      const dx=point.x-centerX,dy=point.y-centerY;
      const fraction=Math.min(1,1/Math.max(Math.abs(dx)/(r.width/2+6),Math.abs(dy)/(r.height/2+5),1));
      path.setAttribute('d',point.z>.08?`M${centerX+dx*fraction} ${centerY+dy*fraction} L${point.x} ${point.y}`:'');
      path.style.stroke=colors[slug];dot.style.fill=colors[slug];
      dot.setAttribute('cx',point.x);dot.setAttribute('cy',point.y);dot.style.display=point.z>.08?'':'none';
      label.setAttribute('aria-pressed',String(slug===activeSuite));
    });
  }
  let activeSuite='mind2act';
  function updateInfo(suite){
    activeSuite=suite.slug;root.dataset.suite=activeSuite;
    choices.forEach(choice=>{
      const active=choice.dataset.suite===suite.slug;
      choice.setAttribute('aria-pressed',String(active));
      choice.setAttribute('aria-expanded',String(active));
      root.querySelector(`#${choice.getAttribute('aria-controls')}`).hidden=!active;
    });
  }
  function selectSuite(slug){
    hidePreview();playing=false;
    updateInfo(suites.find(s=>s.slug===slug));cards.forEach(c=>c.setAttribute('aria-pressed','false'));
    if(THREE)aim({yaw:slug==='mind'?.82:slug==='act'?-.82:0,pitch:0});
    motionState();wake();render();
  }
  function showPreview(point,pin=false){
    if(suppress||drag?.moved)return;
    if(pinned&&!pin&&activePoint!==point)return;
    cancelTimers();origin=point.card;activePoint=point;pinned=pin||pinned;selected=point.task.id;playing=false;
    cards.forEach(c=>{c.setAttribute('aria-pressed',String(pinned&&c===point.card));c.classList.toggle('is-previewed',c===point.card)});
    preview.className=`cm-task-preview cm-${point.suite.slug}`;preview.hidden=false;
    const image=preview.querySelector('img');image.src=point.task.row_cover;image.alt=point.task.title+' demonstration';
    preview.querySelector('.cm-preview-meta').textContent=`${point.suite.name} · ${point.task.id}`;
    preview.querySelector('h3').textContent=point.task.title;
    preview.querySelector('.cm-preview-summary').textContent=point.task.summary;
    preview.querySelector('a').href=`tasks/${point.task.id}.html`;
    motionState();render();
  }
  function dismiss(){const source=origin;hidePreview();if(source){ignoreFocus=true;source.focus({preventScroll:true});ignoreFocus=false}wake();render()}
  function motionState(){motion.disabled=reduced.matches||!renderer;motion.textContent=reduced.matches?'Motion reduced':playing?'Pause motion':'Play motion';motion.setAttribute('aria-pressed',String(playing))}
  function render(){
    applyView();
    if(renderer) {moon.quaternion.copy(quaternion);renderer.render(scene,camera)}
    positions.forEach((point,index)=>{
      let x,y,z;
      if(THREE){const v=new THREE.Vector3(...point.v).applyQuaternion(quaternion);[x,y,z]=v.toArray()}
      else {const [a,b,c]=point.v;x=a*.866+b*.5;y=-a*.5+b*.866;z=c}
      const front=z>.075;
      point.card.style.transform=`translate(${x*size*sphereRadius}px,${-y*size*sphereRadius}px) scale(${.65+.35*Math.max(0,z)})`;
      point.card.style.visibility=front?'visible':'hidden';point.card.style.pointerEvents=front?'auto':'none';
      point.card.tabIndex=front?0:-1;point.card.style.zIndex=String(10+Math.round(z*10));
      point.card.style.setProperty('--node-color',colors[point.suite.slug]);
      point.card.classList.toggle('is-region',point.suite.slug===activeSuite);
      point.card.style.opacity=String((.48+.52*Math.max(0,z))*(point.suite.slug===activeSuite?1:.58));point.card.dataset.front=String(front);point.card.dataset.edge=x>.76?'right':'normal';
    });
    renderRegions();connectPreview();
  }
  function tick(now){frame=0;const dt=Math.min((now-(last||now))/1000,.045);last=now;
    if(target&&quaternion){
      const blend=reduced.matches?1:1-Math.exp(-dt*8);
      view.yaw+=(target.yaw-view.yaw)*blend;view.pitch+=(target.pitch-view.pitch)*blend;
      if(Math.hypot(target.yaw-view.yaw,target.pitch-view.pitch)<.002){Object.assign(view,target);target=null}
    }else if(playing&&!hover&&!drag&&!selected&&!reduced.matches&&quaternion){
      motionPhase+=dt*.35;
      const amplitude=Math.min(.10,Math.max(0,limits.yaw-Math.abs(motionCenter.yaw)));
      view.yaw=motionCenter.yaw+Math.sin(motionPhase)*amplitude;
    }
    render();if(visible&&!document.hidden&&(target||(playing&&!hover&&!selected&&!reduced.matches)))frame=requestAnimationFrame(tick);
  }
  function wake(){if(!frame&&visible&&!document.hidden){last=0;frame=requestAnimationFrame(tick)}}
  choices.forEach(c=>c.addEventListener('click',()=>selectSuite(c.dataset.suite)));
  regionLabels.forEach(label=>label.addEventListener('click',()=>selectSuite(label.dataset.regionLabel)));
  positions.forEach(p=>{
    p.card.addEventListener('click',()=>showPreview(p,true));
    p.card.addEventListener('pointerenter',e=>{if(e.pointerType==='touch')return;cancelTimers();enterTimer=setTimeout(()=>showPreview(p),100)});
    p.card.addEventListener('pointerleave',scheduleHide);
    p.card.addEventListener('focus',()=>{if(!ignoreFocus)showPreview(p)});
    p.card.addEventListener('blur',()=>{if(!preview.contains(document.activeElement))scheduleHide()});
  });
  preview.addEventListener('pointerenter',cancelTimers);preview.addEventListener('pointerleave',scheduleHide);
  preview.addEventListener('focusin',cancelTimers);preview.addEventListener('focusout',e=>{if(!preview.contains(e.relatedTarget))scheduleHide()});
  new ResizeObserver(connectPreview).observe(preview);
  window.addEventListener('resize',connectPreview);
  close.addEventListener('click',dismiss);root.addEventListener('keydown',e=>{if(e.key==='Escape'&&!preview.hidden){e.preventDefault();dismiss()}});
  root.querySelector('.cm-reset').addEventListener('click',()=>selectSuite('mind2act'));
  motion.addEventListener('click',()=>{playing=!playing;target=null;Object.assign(view,bounded(view));motionCenter={...view};motionPhase=0;motionState();wake()});
  orbit.addEventListener('focusin',()=>{playing=false;motionState()});
  orbit.addEventListener('pointerenter',()=>{hover=true});orbit.addEventListener('pointerleave',()=>{hover=false;wake()});
  orbit.addEventListener('pointerdown',e=>{if(e.button!==0||!quaternion)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,start:{...view},moved:false};target=null;playing=false;motionState()});
  orbit.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(!drag.moved&&Math.hypot(dx,dy)<7)return;if(e.pointerType==='touch'&&!drag.moved&&Math.abs(dy)>Math.abs(dx)){drag=null;return}if(!drag.moved)hidePreview();drag.moved=true;orbit.setPointerCapture(e.pointerId);orbit.classList.add('is-dragging');view.yaw=resisted(drag.start.yaw+dx*.004,limits.yaw);view.pitch=resisted(drag.start.pitch+dy*.004,limits.pitch);render()});
  function end(e){if(!drag||drag.id!==e.pointerId)return;if(drag.moved){aim(view);suppress=true;setTimeout(()=>suppress=false,50)}drag=null;orbit.classList.remove('is-dragging');if(orbit.hasPointerCapture(e.pointerId))orbit.releasePointerCapture(e.pointerId)}
  orbit.addEventListener('pointerup',end);orbit.addEventListener('pointercancel',end);window.addEventListener('pointerup',end);
  orbit.addEventListener('keydown',e=>{if(e.target!==orbit||!THREE)return;const axes={ArrowLeft:[0,-.22],ArrowRight:[0,.22],ArrowUp:[-.14,0],ArrowDown:[.14,0]};if(!axes[e.key])return;e.preventDefault();hidePreview();playing=false;const start=target||view;aim({pitch:start.pitch+axes[e.key][0],yaw:start.yaw+axes[e.key][1]});motionState()});
  function syncCopyAlignment(){
    const globeBox=orbit.getBoundingClientRect(),visualBox=visual.getBoundingClientRect();
    const sphereBottom=globeBox.top+globeBox.height*(.5+sphereRadius);
    root.style.setProperty('--cm-copy-bottom-gap',`${Math.max(0,visualBox.bottom-sphereBottom)}px`);
  }
  function resize(){size=orbit.clientWidth;visual.style.setProperty('--cm-orbit-size',`${size}px`);if(renderer){renderer.setSize(size,size,false)}syncCopyAlignment();render()}
  new ResizeObserver(resize).observe(orbit);
  new ResizeObserver(syncCopyAlignment).observe(visual);
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)wake();else if(frame){cancelAnimationFrame(frame);frame=0}},{threshold:.02}).observe(orbit);
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0}else wake()});
  reduced.addEventListener('change',()=>{if(reduced.matches)playing=false;motionState();wake()});
  // A no-script task list remains in the HTML; a CSS moon is the WebGL fallback.
  updateInfo(suites.find(s=>s.slug==='mind2act'));root.classList.add('cm-lunar-ready');resize();
  try {
    THREE=await import('./vendor/three/three.module.min.js');
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'low-power'});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.75));renderer.setClearColor(0x000000,0);
    scene=new THREE.Scene();const halfView=1/(2*sphereRadius);camera=new THREE.OrthographicCamera(-halfView,halfView,halfView,-halfView,.1,10);camera.position.z=4;
    base=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1),-Math.PI/6);quaternion=base.clone();
    geometry=new THREE.SphereGeometry(1,96,64);
    material=new THREE.ShaderMaterial({uniforms:{moonMap:{value:null},hasTexture:{value:0}},vertexShader:`varying vec3 localP; varying vec3 viewN; varying vec2 moonUv; void main(){moonUv=uv;localP=position;viewN=normalize(normalMatrix*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
      fragmentShader:`varying vec3 localP; varying vec3 viewN; varying vec2 moonUv; uniform sampler2D moonMap; uniform float hasTexture;
      float line(float v){float d=abs(fract(v-.5)-.5);return 1.0-smoothstep(0.0,fwidth(v)*.8,d);}
      void main(){vec3 p=normalize(localP);float light=1.0-smoothstep(-.24,.27,p.x);
      vec3 dark=vec3(.018,.023,.029);vec3 bright=vec3(.84,.835,.80);
      float albedo=dot(texture2D(moonMap,vec2(fract(moonUv.x+.24),moonUv.y)).rgb,vec3(.299,.587,.114));
      float terrain=mix(1.0,clamp(.24+albedo*1.15,.30,1.05),hasTexture);
      vec3 col=mix(dark*terrain,bright*terrain,light);float edge=pow(max(viewN.z,0.0),.24);col*=.69+.31*edge;
      float band=1.0-smoothstep(.27,.31,abs(atan(p.x,p.z)));col=mix(col,vec3(.48,.37,.17),band*.12);
      float lon=atan(p.z,p.x)/6.2831853;float lat=asin(p.y)/3.14159265;
      float grid=max(line(lon*16.0),line(lat*9.0));
      vec3 ink=mix(vec3(.25,.29,.32),vec3(.46,.48,.46),light);col=mix(col,ink,grid*.12);
      float texture=(sin(p.x*21.0+p.z*13.0)*sin(p.y*17.0-p.z*8.0))*.002;col+=texture*light;
      gl_FragColor=vec4(col,1.0);
      #include <colorspace_fragment>
      }`});
    moon=new THREE.Mesh(geometry,material);scene.add(moon);root.classList.add('cm-webgl');root.dataset.renderer='webgl';resize();motionState();wake();
    new THREE.TextureLoader().load('media/moon/lroc-color-2k.jpg',texture=>{
      texture.wrapS=THREE.RepeatWrapping;material.uniforms.moonMap.value=texture;material.uniforms.hasTexture.value=1;
      root.dataset.texture='loaded';render();
    },undefined,()=>{root.dataset.texture='fallback'});
    canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();cancelAnimationFrame(frame);frame=0;renderer=null;root.classList.remove('cm-webgl');root.dataset.renderer='fallback';motionState();render()});
  }catch(error){renderer=null;THREE=null;root.dataset.renderer='fallback';motionState();render()}
})();
