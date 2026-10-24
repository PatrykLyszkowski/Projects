let dividendSettings={configured:false,symbols:{},checked:{},errors:[]}, dividendBusy=false;
const localDate=()=>new Date().toLocaleDateString('en-CA');
function setDividendBusy(busy){
 dividendBusy=busy;
 document.querySelectorAll('button').forEach(button=>{if(busy){button.dataset.preDisabled=String(button.disabled);button.disabled=true}else if(button.dataset.preDisabled!==undefined){button.disabled=button.dataset.preDisabled==='true';delete button.dataset.preDisabled}});
}
async function dividendAPI(path,method='GET',body){
 const response=await fetch('/api/dividends/'+path,{method,cache:'no-store',...(body?{headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{})});
 const data=await response.json();if(!response.ok)throw Error(data.error||'Operacja nie powiodła się.');return data;
}
function renderDividendPanel(){
 $('#expected-dividends')?.remove();
 const expected=rows.filter(r=>r.kind==='expected_dividend').sort((a,b)=>(a.payment_date||'9999').localeCompare(b.payment_date||'9999'));
 const panel=document.createElement('div');panel.id='expected-dividends';panel.className='card dividend-panel';
 panel.innerHTML=`<div class="card-top"><div><span class="eyebrow">KALENDARZ DOCHODÓW</span><h2 style="margin-top:10px">Oczekiwane dywidendy</h2><p>Kwoty brutto w walucie wypłaty. Do wyniku portfela trafiają dopiero po potwierdzeniu w PLN.</p></div><div class="actions"><button id="dividend-settings">⚙ Ustawienia</button><button id="dividend-sync" class="primary">↻ Pobierz dywidendy</button></div></div>
 <p id="dividend-status" class="sync-status" role="status">${!csvReady?'Uruchom aplikację przez Uruchom.cmd, aby pobierać i zapisywać dywidendy.':!dividendSettings.configured?'Połącz EODHD w ustawieniach. Po konfiguracji dane sprawdzamy przy otwarciu aplikacji, najwyżej raz dziennie na instrument.':'Źródło: EODHD · tylko ogłoszone wypłaty dostępne u dostawcy. Przycisk pobierania wymusza odświeżenie.'}</p>
 ${dividendSettings.errors?.length?`<div class="sync-warning">${dividendSettings.errors.map(esc).join('<br>')}</div>`:''}
 ${expected.length?`<div class="table-wrap"><table><thead><tr><th>INSTRUMENT</th><th>BEZ PRAWA OD</th><th>WYPŁATA</th><th>SZTUKI UPRAWNIONE*</th><th>OCZEKIWANE BRUTTO</th><th></th></tr></thead><tbody>${expected.map(r=>`<tr><td><b>${esc(r.name)}</b><br><small>${esc(r.symbol)} · <a href="https://eodhd.com/financial-apis/api-splits-dividends" target="_blank" rel="noopener">EODHD</a></small></td><td>${esc(r.ex_date)}</td><td>${r.payment_date?esc(r.payment_date):'Termin nieznany'}${r.payment_date&&r.payment_date<=localDate()?'<br><span class="pill">Sprawdź wpływ</span>':''}</td><td>${num(r.quantity)}</td><td><b>${num(Number(r.expected_amount))} ${esc(r.currency)}</b><br><small>${num(Number(r.per_share))} / szt.</small></td><td><button data-confirm-dividend="${esc(r.id)}">Potwierdź wpływ →</button></td></tr>`).join('')}</tbody></table></div>`:'<div class="empty">Brak oczekiwanych wypłat.<br>Dodaj zakupy akcji lub ETF-ów, wskaż ich symbole i pobierz dane.</div>'}
 <small>* Według zapisanych zakupów sprzed dnia bez prawa do dywidendy (ex-date). Ta wersja nie uwzględnia sprzedaży, splitów ani transferów. Brak wpisu nie oznacza, że spółka nie wypłaci dywidendy.</small>`;
 $('#income').prepend(panel);
 $('#dividend-settings').onclick=openDividendSettings;
 $('#dividend-sync').onclick=()=>syncDividends(true);
 document.querySelectorAll('[data-confirm-dividend]').forEach(button=>button.onclick=()=>confirmDividend(button.dataset.confirmDividend));
}
function modalDialog(id,content){
 $('#'+id)?.remove();const dialog=document.createElement('dialog');dialog.id=id;dialog.innerHTML=content;document.body.append(dialog);dialog.querySelector('[data-close]').onclick=()=>dialog.close();dialog.showModal();return dialog;
}
async function openDividendSettings(){
 if(!csvReady)return toast('Uruchom aplikację przez Uruchom.cmd.');
 try{dividendSettings=await dividendAPI('settings')}catch(error){return toast(error.message)}
 const symbols=[...new Set(rows.filter(r=>r.kind==='buy'&&r.asset!=='Obligacje').map(r=>r.symbol))];
 const dialog=modalDialog('dividend-config',`<form><div class="modal-head"><h2>Pobieranie dywidend</h2><button type="button" data-close>✕</button></div><p>Połącz EODHD i przypisz instrumenty do ich notowań.</p><label style="margin-top:22px">Klucz API EODHD ${dividendSettings.configured?'· zapisany lokalnie':''}<input id="dividend-token" type="password" autocomplete="new-password" placeholder="${dividendSettings.configured?'Pozostaw puste, aby zachować klucz':'Wpisz swój klucz API'}" ${dividendSettings.configured?'':'required'}></label><p style="font-size:12px;margin-bottom:20px">Klucz pozostaje w lokalnym pliku ustawień; wysyłamy go wyłącznie do EODHD. <a href="https://eodhd.com/" target="_blank" rel="noopener">Załóż konto u dostawcy ↗</a> · zakres danych zależy od abonamentu.</p>${symbols.map((symbol,i)=>`<label>${esc(symbol)} — symbol EODHD z giełdą<input data-mapping="${i}" value="${esc(dividendSettings.symbols[symbol]||(symbol.includes('.')?symbol:''))}" placeholder="np. AAPL.US, KTY.WAR, VUAA.LSE"></label>`).join('')||'<p>Dodaj najpierw zakup akcji lub ETF-u.</p>'}<small>Weryfikuj symbol i giełdę u dostawcy. Puste przypisanie pomija instrument. Pobieramy dostępne ogłoszenia od daty pierwszego zakupu.</small><p id="config-error" class="negative" role="status"></p><button class="primary submit">Zapisz i sprawdź wypłaty →</button></form>`);
 dialog.querySelector('form').onsubmit=async event=>{
  event.preventDefault();const submit=dialog.querySelector('.submit');submit.disabled=true;
  try{
   const mappings={...dividendSettings.symbols};symbols.forEach((symbol,i)=>{const value=dialog.querySelector(`[data-mapping="${i}"]`).value.trim();if(value)mappings[symbol]=value;else delete mappings[symbol]});
   dividendSettings=await dividendAPI('settings','PUT',{token:$('#dividend-token').value,symbols:mappings});dialog.close();renderDividendPanel();await syncDividends(false);
  }catch(error){$('#config-error').textContent=error.message}finally{submit.disabled=false}
 };
}
async function syncDividends(force=false){
 if(dividendBusy)return;
 if(!csvReady)return toast('Uruchom aplikację przez Uruchom.cmd.');
 if(!dividendSettings.configured)return openDividendSettings();
 await writeQueue;setDividendBusy(true);
 if($('#dividend-status'))$('#dividend-status').textContent='Pobieranie ogłoszonych dywidend…';
 try{
  const result=await dividendAPI('sync','POST',{force});
  await loadPortfolio();dividendSettings=await dividendAPI('settings');renderDividendPanel();
  toast(result.errors.length?'Pobieranie zakończone z uwagami — sprawdź listę przy dywidendach.':`Dywidendy sprawdzone. Nowe: ${result.added}.`);
 }catch(error){toast(error.message);if($('#dividend-status'))$('#dividend-status').textContent=error.message}
 finally{setDividendBusy(false)}
}
function confirmDividend(id){
 if(!csvReady)return toast('Uruchom aplikację przez Uruchom.cmd.');
 const row=rows.find(r=>r.id===id);if(!row)return;
 const dialog=modalDialog('dividend-confirm',`<form><div class="modal-head"><h2>Potwierdź otrzymaną dywidendę</h2><button type="button" data-close>✕</button></div><p>${esc(row.name)} · oczekiwane ${num(Number(row.expected_amount))} ${esc(row.currency)} brutto.</p><label style="margin-top:22px">Faktycznie otrzymana kwota netto w PLN<input id="actual-dividend" type="number" min="0" step="0.01" required placeholder="Kwota zaksięgowana u brokera"></label><label>Data wpływu<input id="actual-date" type="date" max="${localDate()}" value="${row.payment_date&&row.payment_date<=localDate()?esc(row.payment_date):localDate()}" required></label><small>Jeśli wypłata była w obcej walucie, podaj jej wartość po przeliczeniu na PLN. Nie przeliczamy walut ani podatku automatycznie.</small><p id="confirm-error" class="negative" role="status"></p><button class="primary submit">Zapisz otrzymany wpływ →</button></form>`);
 dialog.querySelector('form').onsubmit=async event=>{
  event.preventDefault();const submit=dialog.querySelector('.submit');submit.disabled=true;
  try{await writeQueue;await dividendAPI('confirm','POST',{id,amount:Number($('#actual-dividend').value),date:$('#actual-date').value});dialog.close();await loadPortfolio();toast('Dywidenda potwierdzona i zapisana w CSV.')}catch(error){$('#confirm-error').textContent=error.message}finally{submit.disabled=false}
 };
}
async function initDividends(){
 if(!csvReady){renderDividendPanel();return}
 try{dividendSettings=await dividendAPI('settings');renderDividendPanel();if(dividendSettings.configured)await syncDividends(false)}catch(error){toast(error.message)}
 setInterval(()=>{if(!document.hidden&&!document.querySelector('dialog[open]')&&dividendSettings.configured)syncDividends(false)},3600000);
}
