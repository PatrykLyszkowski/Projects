async function loadHistory(){
 if(!csvReady){historyPrices=[];historyError='';return}
 try{const response=await fetch('/api/history',{cache:'no-store'});if(!response.ok)throw Error();const data=await response.json();if(!Array.isArray(data.prices))throw Error();historyPrices=data.prices;historyError=''}
 catch{historyError='Nie udało się odczytać historii wycen. Jeśli aplikacja była uruchomiona podczas aktualizacji, uruchom ją ponownie.'}
}
function historySeries(transactions,prices,today){
 const buys=transactions.filter(r=>r.kind==='buy'&&r.date<=today);
 const received=transactions.filter(r=>['dividend','interest'].includes(r.kind)&&r.date<=today);
 const relevantIds=new Set(buys.map(r=>r.id));
 const relevant=prices.filter(p=>relevantIds.has(p.id)&&p.date<=today);
 const days=[...new Set([...buys.map(r=>r.date),...received.map(r=>r.date),...relevant.map(p=>p.date),today])].sort();
 const lookup=new Map(relevant.map(p=>[p.date+'|'+p.id,Number(p.unit_price)]));
 return days.map(date=>{
  const held=buys.filter(r=>r.date<=date);
  const capital=held.reduce((sum,r)=>sum+r.quantity*r.price,0);
  const income=received.filter(r=>r.date<=date).reduce((sum,r)=>sum+r.price,0);
  const quotes=held.map(r=>lookup.has(date+'|'+r.id)?lookup.get(date+'|'+r.id):r.date===date?r.price:null);
  const complete=quotes.every(v=>v!==null&&Number.isFinite(v));
  const value=complete?held.reduce((sum,r,i)=>sum+r.quantity*quotes[i],0)+income:null;
  return {date,capital,value,result:value===null?null:value-capital,income};
 });
}
function historySVG(points){
 const width=760,height=250,left=80,right=20,top=18,bottom=30;
 const values=points.flatMap(p=>[p.capital,p.value,p.result]).filter(v=>v!==null);
 let min=Math.min(0,...values),max=Math.max(1,...values);const padding=(max-min)*.08;min-=padding;max+=padding;
 const start=Date.parse(points[0].date),end=Date.parse(points.at(-1).date),span=end-start;
 const x=date=>span?left+(Date.parse(date)-start)/span*(width-left-right):width-right;
 const y=value=>top+(max-value)/(max-min)*(height-top-bottom);
 const series=[['capital','#9aa9b2','Zainwestowany kapitał'],['value','#237d66','Wartość + wypłaty'],['result','#c59a48','Sam wynik']];
 const grid=Array.from({length:5},(_,i)=>{const value=min+(max-min)*i/4;return `<line x1="${left}" x2="${width-right}" y1="${y(value)}" y2="${y(value)}" stroke="#e9edef"/><text x="${left-10}" y="${y(value)+4}" text-anchor="end" fill="#849095" font-size="10">${esc(money(value))}</text>`}).join('');
 const paths=series.map(([field,color,label])=>{
  let path='',open=false;for(const p of points){if(p[field]===null){open=false;continue}path+=`${open?'L':'M'}${x(p.date)},${y(p[field])} `;open=true}
  return `<path data-history-line="${field}" d="${path}" fill="none" stroke="${color}" stroke-width="${field==='value'?3:2}" ${field==='capital'?'stroke-dasharray="6 4"':''}/>${points.filter(p=>p[field]!==null).map(p=>`<circle cx="${x(p.date)}" cy="${y(p[field])}" r="3.5" fill="${color}"><title>${esc(p.date)} · ${label}: ${esc(money(p[field]))}</title></circle>`).join('')}`;
 }).join('');
 const labels=[points[0],...(points.length>2?[points[Math.floor(points.length/2)]]:[]),...(points.length>1?[points.at(-1)]:[])].map((p,i,arr)=>`<text x="${x(p.date)}" y="${height-5}" text-anchor="${i===0&&arr.length>1?'start':i===arr.length-1?'end':'middle'}" fill="#849095" font-size="10">${esc(p.date)}</text>`).join('');
 return `<div class="history-plot"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Historia zainwestowanego kapitału, wartości z wypłatami i wyniku w złotych">${grid}${paths}${labels}</svg></div>`;
}
function renderHistory(){
 const container=document.querySelector('#portfolio-history');if(!container)return;
 const today=new Date().toLocaleDateString('en-CA');
 const prices=csvReady?historyPrices:rows.filter(r=>r.kind==='buy').map(r=>({id:r.id,date:today,unit_price:r.current}));
 const points=historySeries(rows,prices,today);
 container.innerHTML=`<div class="card-top"><div><h2>Historia portfela</h2><p>Kapitał i rzeczywisty wynik · PLN</p></div><span class="tag">Od początku</span></div><div class="legend history-legend"><span><i class="dot" style="background:#9aa9b2"></i>Zainwestowany kapitał</span><span><i class="dot"></i>Wartość + wypłaty</span><span><i class="dot" style="background:#c59a48"></i>Sam wynik</span></div>
 ${historyError?`<p class="sync-warning">${esc(historyError)}</p>`:''}
 ${rows.some(r=>r.kind==='buy'&&r.date<=today)?historySVG(points):'<div class="empty">Dodaj pierwszy zakup, aby rozpocząć historię portfela.</div>'}
 <p class="history-note">Kapitał = koszt zakupów. Wartość + wypłaty = wycena instrumentów oraz otrzymane dywidendy i odsetki. Sam wynik = ta wartość minus kapitał. Oczekiwane wypłaty nie są uwzględniane.</p>
 <p class="history-note">Wycenę zapisujemy w dniach korzystania z aplikacji, według ręcznie wpisanych cen. Dla dni bez wyceny nie wyliczamy wyniku cenowego. Odsetki skapitalizowane w obligacji uwzględnij w jej wycenie; nie dodawaj ich ponownie jako wypłaty.</p>
 ${points.length>1?`<details class="history-details"><summary>Pokaż dane wykresu</summary><div class="table-wrap"><table><thead><tr><th>DATA</th><th>KAPITAŁ</th><th>WARTOŚĆ + WYPŁATY</th><th>WYNIK</th></tr></thead><tbody>${points.map(p=>`<tr><td>${esc(p.date)}</td><td>${money(p.capital)}</td><td>${p.value===null?'Brak wyceny':money(p.value)}</td><td>${p.result===null?'—':money(p.result)}</td></tr>`).join('')}</tbody></table></div></details>`:''}`;
}
