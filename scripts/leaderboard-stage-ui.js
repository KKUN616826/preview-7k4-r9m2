/* Hero rankings and the detailed table consume exactly the same immutable score snapshot. */
(() => {
 const root=document.querySelector('.lb-stage');if(!root)return;
 const data=JSON.parse(document.getElementById('leaderboardExplorerData').textContent);
 const views=new Map(data.views.map(v=>[v.key,v]));
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 function render(view){
  if(!views.has(view))view='mind';
  const v=views.get(view);root.dataset.currentView=view;
  root.querySelector('.lb-stage-caption strong').textContent=v.label;
  root.querySelectorAll('[data-stage-select]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.stageSelect===view)));
  root.querySelectorAll('[data-board-view]').forEach(b=>b.classList.toggle('is-active',b.dataset.boardView===view));
  const leaders=data.models.filter(m=>m.results[view].score!=null).sort((a,b)=>b.results[view].score-a.results[view].score).slice(0,3);
  root.querySelectorAll('[data-podium-rank]').forEach(button=>{
   const model=leaders[Number(button.dataset.podiumRank)-1];button.hidden=!model;if(!model)return;
   button.dataset.stageModel=model.id;button.dataset.stageSuite=view;
   const icon=button.querySelector('img'),fallback=button.querySelector('.lb-podium-monogram');
   icon.hidden=!model.icon;fallback.hidden=!!model.icon;
   if(model.icon)icon.src=model.icon;else icon.removeAttribute('src');
   fallback.textContent=model.name.slice(0,2);
   button.querySelector('.lb-podium-name').textContent=model.name;
   button.querySelector('strong').textContent=model.results[view].score.toFixed(2);
   button.setAttribute('aria-label',`${v.label} rank ${button.dataset.podiumRank}: ${model.name}, Score ${model.results[view].score.toFixed(2)}. View model details.`);
   button.title=`${model.name} · Score ${model.results[view].score.toFixed(2)} · Success ${model.results[view].success==null?'unreported':model.results[view].success.toFixed(1)+'%'}`;
  });
  root.querySelector('.lb-podium-labels').getAnimations().forEach(a=>a.cancel());
  if(!reduced.matches)root.querySelector('.lb-podium-labels').animate([{opacity:.45},{opacity:1}],{duration:200});
 }
 root.addEventListener('click',event=>{
  const tab=event.target.closest('[data-stage-select]');
  const model=event.target.closest('[data-stage-model]');
  if(tab)window.dispatchEvent(new CustomEvent('lb:select',{detail:{view:tab.dataset.stageSelect}}));
  if(model)window.dispatchEvent(new CustomEvent('lb:select',{detail:{view:model.dataset.stageSuite,model:model.dataset.stageModel,reveal:true}}));
 });
 root.querySelector('.lb-stage-full').addEventListener('click',event=>{event.preventDefault();document.getElementById('results').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});});
 window.addEventListener('lb:state',event=>{if(event.detail.view!==root.dataset.currentView)render(event.detail.view);});
 render(new URLSearchParams(location.search).get('view')||'mind');
})();
