(()=>{
  const MONTHS={jan:0,feb:1,mar:2,apr:3,may:4,jun:5,jul:6,aug:7,sep:8,oct:9,nov:10,dec:11};
  const norm=s=>String(s||'').replace(/\s+/g,' ').trim();
  const money=s=>{const m=norm(s).replace(/,/g,'').match(/\$?(-?\d+(?:\.\d+)?)/);return m?Number(m[1]):null};
  const firstNumber=s=>{const m=norm(s).match(/-?\d+(?:\.\d+)?/);return m?Number(m[0]):null};
  function datesFrom(text){
    const s=norm(text),out=[];
    const re=/\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2})(?:,?\s+(20\d{2}))?/gi;
    let m;while((m=re.exec(s))){const mon=MONTHS[m[1].slice(0,3).toLowerCase()],day=Number(m[2]),yr=Number(m[3]||new Date().getFullYear());const d=new Date(yr,mon,day);if(!Number.isNaN(d.getTime()))out.push(d)}
    return out;
  }
  function upcomingKey(text){
    const ds=datesFrom(text);if(!ds.length)return Number.POSITIVE_INFINITY;
    const today=new Date();today.setHours(0,0,0,0);
    const future=ds.filter(d=>d>=today).sort((a,b)=>a-b);
    if(future.length)return future[0].getTime();
    return Number.MAX_SAFE_INTEGER-Math.max(...ds.map(d=>d.getTime()));
  }
  function aiKey(text){
    const s=norm(text).toLowerCase();
    const n=s.match(/\b(100|[1-9]?\d)\b/);if(n)return -Number(n[1]);
    if(s.includes('high'))return -3;if(s.includes('medium'))return -2;if(s.includes('low'))return -1;return 0;
  }
  function headerIndex(table,patterns){const hs=[...table.querySelectorAll('thead th')].map(x=>norm(x.textContent).toLowerCase());return hs.findIndex(h=>patterns.some(p=>p.test(h)))}
  function activeTable(){
    const active=document.querySelector('.panel.active table');if(active)return active;
    return document.querySelector('table');
  }
  function buildOptions(table){
    const opts=[];
    const date=headerIndex(table,[/sale date/,/auction date/,/2026 schedule/,/^schedule$/,/date/]);if(date>=0)opts.push(['upcoming','Upcoming date first',date]);
    const ai=headerIndex(table,[/research priority/,/ai suggested/,/ai score/]);if(ai>=0)opts.push(['ai','AI Suggested',ai]);
    const opening=headerIndex(table,[/opening bid/,/minimum bid/,/min\. bid/]);if(opening>=0){opts.push(['opening_low','Lowest opening / minimum bid',opening]);opts.push(['opening_high','Highest opening / minimum bid',opening])}
    const assessed=headerIndex(table,[/appraisal value/,/assessed value/,/market value/]);if(assessed>=0)opts.push(['assessed_high','Highest assessed / appraisal value',assessed]);
    const neighborhood=headerIndex(table,[/neighborhood value/]);if(neighborhood>=0)opts.push(['neighborhood_high','Highest Neighborhood Value',neighborhood]);
    const ret=headerIndex(table,[/max return/,/interest.*return/]);if(ret>=0)opts.push(['return_high','Highest stated return',ret]);
    const state=headerIndex(table,[/^state/,/state \/ market/]);if(state>=0)opts.push(['state','State A–Z',state]);
    const county=headerIndex(table,[/^county/,/county \/ market/]);if(county>=0)opts.push(['county','County A–Z',county]);
    return opts;
  }
  let select,observer,busy=false;
  function ensureControl(){
    const table=activeTable();if(!table)return;
    const toolbar=document.querySelector('.toolbar');if(!toolbar)return;
    const options=buildOptions(table);if(!options.length)return;
    if(!select){select=document.createElement('select');select.id='siteSort';select.className='control';select.setAttribute('aria-label','Sort results');toolbar.appendChild(select);select.addEventListener('change',applySort)}
    const old=select.value;
    select.innerHTML='<option value="">Sort by…</option>'+options.map(([v,l])=>`<option value="${v}">${l}</option>`).join('');
    if(options.some(o=>o[0]===old))select.value=old;else if(options.some(o=>o[0]==='upcoming'))select.value='upcoming';else if(options.some(o=>o[0]==='ai'))select.value='ai';
    select._sortOptions=options;
    applySort();
  }
  function applySort(){
    if(busy||!select||!select.value)return;
    const table=activeTable(),tbody=table?.querySelector('tbody');if(!tbody)return;
    const spec=(select._sortOptions||[]).find(o=>o[0]===select.value);if(!spec)return;
    const [mode,,idx]=spec,rows=[...tbody.querySelectorAll(':scope > tr')];if(rows.length<2)return;
    const val=r=>norm(r.children[idx]?.textContent);
    let cmp;
    if(mode==='upcoming')cmp=(a,b)=>upcomingKey(val(a))-upcomingKey(val(b));
    else if(mode==='ai')cmp=(a,b)=>aiKey(val(a))-aiKey(val(b));
    else if(mode==='opening_low')cmp=(a,b)=>(money(val(a))??Infinity)-(money(val(b))??Infinity);
    else if(mode==='opening_high'||mode==='assessed_high'||mode==='neighborhood_high'||mode==='return_high')cmp=(a,b)=>(firstNumber(val(b))??-Infinity)-(firstNumber(val(a))??-Infinity);
    else cmp=(a,b)=>val(a).localeCompare(val(b),undefined,{numeric:true,sensitivity:'base'});
    busy=true;rows.sort(cmp).forEach(r=>tbody.appendChild(r));busy=false;
  }
  function watch(){
    if(observer)observer.disconnect();observer=new MutationObserver(()=>{if(!busy)requestAnimationFrame(()=>{ensureControl();applySort()})});observer.observe(document.body,{subtree:true,childList:true});
  }
  document.addEventListener('DOMContentLoaded',()=>{ensureControl();watch();setTimeout(ensureControl,500)});
})();
