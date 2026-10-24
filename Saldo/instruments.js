let selectedInstrument=null, searchSequence=0;
function resetInstrumentForm(){
 selectedInstrument=null;searchSequence++;document.querySelector('#instrument-query').value='';document.querySelector('#instrument-results').innerHTML='';document.querySelector('#search-status').textContent='Wyszukaj instrument lub wpisz jego nazwę i symbol poniżej.';document.querySelector('#bond-description').textContent='';document.querySelector('#form').elements.date.setCustomValidity('');updateInstrumentForm();
}
function updateInstrumentForm(){
 const form=document.querySelector('#form'),buy=form.elements.kind.value==='buy',bond=buy&&form.elements.asset.value==='Obligacje';
 document.querySelector('#quantity-label').hidden=!buy;form.elements.quantity.required=buy;if(!buy)form.elements.quantity.value=1;
 document.querySelector('#price-label').textContent=buy?'Cena zakupu za sztukę (PLN)':'Faktycznie otrzymana kwota netto (PLN)';
 document.querySelector('#bond-fields').hidden=!bond;form.elements.bond_rate.required=bond;
 const terms=selectedInstrument;
 document.querySelector('#bond-description').innerHTML=bond?(terms?.asset==='Obligacje'?`${esc(terms.rule)} · Wypłata: ${esc(terms.payout)}.<br>Oferta serii: ${esc(terms.sale_from)} – ${esc(terms.sale_to)}. Weryfikacja: ${esc(terms.verified)}. <a href="https://www.obligacjeskarbowe.pl/oferta/" target="_blank" rel="noopener">Źródło ↗</a><br>To stawka pierwszego okresu, nie automatyczne naliczanie odsetek ani stawka na całe 10 lat.`:'Wpisz stopę z dokumentów swojej serii. Starszych serii, których nie ma w katalogu, nie zastępuj aktualną ofertą.'):'';
 const date=form.elements.date;date.setCustomValidity('');
 if(bond&&terms?.sale_from&&date.value&&(date.value<terms.sale_from||date.value>terms.sale_to))date.setCustomValidity('Data zakupu jest poza okresem sprzedaży wybranej serii. Wybierz właściwą serię lub wpisz instrument ręcznie.');
}
function transactionBondTerms(row){
 if(row.asset!=='Obligacje'||row.kind!=='buy')return '';
 const rate=Number(row.bond_rate),known=selectedInstrument?.symbol===row.symbol&&selectedInstrument?.asset==='Obligacje';
 return JSON.stringify({...(known?selectedInstrument:{}),rate,mode:known&&rate===selectedInstrument.rate?selectedInstrument.mode:'manual',rate_scope:'first_period'});
}
function bondBadge(row){
 if(!row.bond_terms)return '';
 try{const terms=JSON.parse(row.bond_terms);return ` · ${esc(num(Number(terms.rate)))}% (pierwszy okres)`}catch{return ''}
}
async function searchInstrument(){
 const query=document.querySelector('#instrument-query').value.trim(),asset=document.querySelector('#search-asset').value,sequence=++searchSequence;
 const status=document.querySelector('#search-status'),results=document.querySelector('#instrument-results');
 if(query.length<2){status.textContent='Wpisz co najmniej dwa znaki.';return}
 if(!csvReady){status.textContent='Uruchom aplikację przez Uruchom.cmd, aby wyszukiwać instrumenty.';return}
 status.textContent='Wyszukiwanie instrumentów…';results.innerHTML='';
 try{
  const response=await fetch('/api/instruments/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,asset})});
  const data=await response.json();if(!response.ok)throw Error(data.error||'Nie udało się wyszukać instrumentu.');if(sequence!==searchSequence)return;
  status.textContent=data.warning||(!data.items.length?'Brak wyników. Możesz dodać instrument ręcznie.':'Wybierz właściwą serię lub giełdę.');
  for(const item of data.items){
   const button=document.createElement('button');button.type='button';button.className='instrument-result';
   button.innerHTML=`<strong>${esc(item.name)}</strong><span>${esc(item.symbol)} · ${esc(item.asset)} · ${esc(item.currency)}${item.rate!==undefined?' · '+num(item.rate)+'% — pierwszy okres':''}</span>`;
   button.onclick=()=>{
    selectedInstrument=item;const form=document.querySelector('#form');form.elements.name.value=item.name;form.elements.symbol.value=item.symbol;form.elements.asset.value=item.asset;
    form.elements.bond_rate.value=item.rate??'';if(item.price!==undefined)form.elements.price.value=item.price;
    results.innerHTML='';status.textContent=item.asset==='Obligacje'?`Wybrano ${item.symbol}. Warunki przypisano do tej serii.`:`Wybrano ${item.symbol}. Waluta notowań: ${item.currency}. Cenę zakupu podaj w PLN; nie przeliczamy jej automatycznie.`;
    updateInstrumentForm();
   };results.append(button);
  }
 }catch(error){if(sequence===searchSequence)status.textContent=error.message}
}
document.addEventListener('DOMContentLoaded',()=>{
 const form=document.querySelector('#form');
 document.querySelector('#instrument-search').onclick=searchInstrument;
 document.querySelector('#instrument-query').onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();searchInstrument()}};
 form.elements.kind.onchange=updateInstrumentForm;form.elements.asset.onchange=()=>{selectedInstrument=null;form.elements.bond_rate.value='';updateInstrumentForm()};form.elements.date.oninput=updateInstrumentForm;
 form.elements.symbol.oninput=()=>{selectedInstrument=null;form.elements.bond_rate.value='';updateInstrumentForm()};
});
