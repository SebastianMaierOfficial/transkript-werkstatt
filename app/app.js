'use strict';
const $ = id => document.getElementById(id);
const fragment = location.hash.slice(1);
if (fragment) { sessionStorage.setItem('werkstatt-token', fragment); history.replaceState(null, '', '/'); }
const token = fragment || sessionStorage.getItem('werkstatt-token') || '';
let configSnapshot = null;
let files = [], results = [], selected = 0, busy = false, dirty = false, controller = null;

function status(message, error = false) { $('status').textContent = message; $('status').classList.toggle('bad', error); }
function confirmation(title, message) {
  return new Promise(resolve => {
    $('confirm-title').textContent = title; $('confirm-text').textContent = message;
    const dialog = $('confirm');
    const finish = value => { dialog.close(); resolve(value); };
    $('confirm-yes').onclick = () => finish(true); $('confirm-no').onclick = () => finish(false);
    dialog.oncancel = event => { event.preventDefault(); finish(false); }; dialog.showModal();
  });
}
async function api(route, data) {
  const response = await fetch(route, {method:'POST', headers:{'Content-Type':'application/json','X-Session':token}, body:JSON.stringify(data), signal:controller?.signal});
  if (!response.ok) { const error = await response.json(); throw new Error(error.error || 'Verarbeitung fehlgeschlagen.'); }
  return response;
}
function controls() {
  $('process').disabled = busy || files.length === 0 || !token;
  $('process').textContent = busy ? 'Wird verarbeitet …' : 'Dateien verarbeiten →';
  for(const id of ['result-text','reviewed','replace-selection','delete-selection','selection-kind'])$(id).disabled=busy; $('files').disabled = busy; $('terms').disabled = busy; $('numbers').disabled = busy; $('speakers').disabled = busy; for(const id of ['auto-names','places','companies','other','mode','demo']) $(id).disabled=busy; document.querySelectorAll('#name-candidates input, #override-rows input, #override-rows select, #override-rows button, #add-override').forEach(el=>el.disabled=busy);
  const good = results.filter(r => !r.error), checked = good.filter(r => r.reviewed);
  $('export').disabled = busy || dirty || !checked.length;
  $('export').textContent = checked.length === 1 ? '1 geprüften Text speichern ↓' : checked.length ? `${checked.length} geprüfte Texte speichern ↓` : 'Geprüfte Texte speichern ↓';
  $('review-progress').textContent = `${checked.length} von ${good.length} geprüft`;
  $('export-hint').textContent = dirty ? 'Die Auswahl oder Regeln wurden geändert. Bitte erneut verarbeiten.' : `${checked.length === 1 ? 'Eine TXT-Datei, ohne ZIP.' : `ZIP mit ${checked.length} geprüften TXT-Dateien.`} Speicherung im Download-Ordner oder am vom Browser abgefragten Ort. Ungeprüfte Dateien werden nicht exportiert.`;
}
function changed() { if(results.length) {dirty = true; status('Auswahl oder Regeln geändert. Bitte erneut verarbeiten.');} controls(); }
function showFiles() {
  $('file-list').replaceChildren();
  files.forEach((file, index) => {
    const li = document.createElement('li'), name = document.createElement('span'), button = document.createElement('button');
    name.textContent = file.name; button.textContent = '×'; button.ariaLabel = `${file.name} entfernen`; button.disabled = busy;
    button.onclick = () => {files.splice(index,1); changed(); showFiles();}; li.append(name,button); $('file-list').append(li);
  });
  $('file-summary').textContent = files.length ? `${files.length} ${files.length===1?'Datei':'Dateien'} · ${(files.reduce((n,f)=>n+f.size,0)/1024/1024).toFixed(1)} MB` : 'Noch keine Dateien ausgewählt.';
  controls();
}
function addFiles(incoming) {
  if(busy) return;
  let rejected = 0;
  for (const file of incoming) {
    if (!/\.(txt|docx)$/i.test(file.name) || file.size > 10*1024*1024 || files.length >= 50 || files.reduce((n,f)=>n+f.size,0)+file.size > 40*1024*1024) {rejected++; continue;}
    if (!files.some(f=>f.name===file.name && f.size===file.size && f.lastModified===file.lastModified)) files.push(file);
  }
  changed(); showFiles(); if(rejected) status(`${rejected} Dateien nicht hinzugefügt. Erlaubt: TXT/DOCX, je 10 MB, insgesamt 40 MB und höchstens 50 Dateien.`, true);
}
$('files').onchange = event => {addFiles(event.target.files); event.target.value='';};
for(const name of ['dragenter','dragover']) $('dropzone').addEventListener(name,event=>{event.preventDefault();$('dropzone').classList.add('drag');});
for(const name of ['dragleave','drop']) $('dropzone').addEventListener(name,event=>{event.preventDefault();$('dropzone').classList.remove('drag');});
$('dropzone').addEventListener('drop',event=>addFiles(event.dataTransfer.files));
window.addEventListener('dragover',event=>event.preventDefault()); window.addEventListener('drop',event=>event.preventDefault());
for(const id of ['terms','numbers','speakers','auto-names','places','companies','other','mode']) $(id).addEventListener('input', changed);
function readBase64(file) { return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=()=>reject(new Error('Datei konnte nicht gelesen werden.'));reader.readAsDataURL(file);}); }
$('process').onclick = async () => {
  if (results.length && !await confirmation('Erneut verarbeiten?', 'Manuelle Änderungen und Prüfbestätigungen der bisherigen Ergebnisse werden ersetzt. Bereits gespeicherte Dateien bleiben erhalten.')) return;
  busy = true; controller = new AbortController(); controls(); showFiles(); status('Dateien werden lokal gelesen und verarbeitet …');
  try {
    const payload=[];
    for(const file of files) payload.push({name:file.name,data:await readBase64(file)});
    if(controller.signal.aborted) throw new DOMException('Abgebrochen','AbortError');
    configSnapshot={overrides:readOverrides(),mode:$('mode').value,terms:{person:lines('terms'),place:lines('places'),company:lines('companies'),other:lines('other')},numbers:$('numbers').checked,speakers:$('speakers').checked,auto_names:$('auto-names').checked};
    const response=await api('/process',{files:payload,...configSnapshot});
    const body=await response.json();
    results=body.results.map((result,i)=>({...result,name:files[i].name,reviewed:false,edited:false,excluded:[]}));
    dirty=false; selected=0; $('review').hidden=false; showResult();
    const errors=results.filter(r=>r.error).length;
    status(`${results.length-errors} Dateien verarbeitet${errors ? `, ${errors} nicht lesbar` : ''}. Bitte jeden Ergebnistext vollständig prüfen.`, !!errors);
    $('review').scrollIntoView({behavior:'smooth',block:'start'});
  } catch(error) { if(error.name!=='AbortError') status(error.message || 'Verbindung unterbrochen. Programm erneut öffnen.',true); }
  finally {busy=false;controller=null;controls();showFiles();}
};
function showNavigation() {
  $('result-list').replaceChildren();
  results.forEach((result,i)=>{const button=document.createElement('button');button.classList.toggle('active',i===selected);button.setAttribute('aria-current',i===selected?'true':'false');button.textContent=`Transkript ${String(i+1).padStart(3,'0')}`;const sub=document.createElement('small');sub.textContent=result.error?'Nicht verarbeitet':result.reviewed?'✓ Geprüft':'Durchsicht ausstehend';button.append(sub);button.onclick=()=>{selected=i;showResult();};$('result-list').append(button);});
  controls();
}
function showResult() {
  const result=results[selected]; if(!result) return;
  showNavigation(); $('result-title').textContent=`Transkript ${String(selected+1).padStart(3,'0')}`;
  $('source-name').textContent=`Quelle nur zur Orientierung: ${result.name}`;
  $('match-count').textContent=result.error?'Importfehler':`${result.count} Stellen ersetzt`;
  $('error-panel').hidden=!result.error; $('edit-area').hidden=!!result.error;
  $('error-panel').textContent=result.error||''; $('original-details').open=false;
  $('original').value=result.original||''; $('result-text').value=result.text||''; $('reviewed').checked=!!result.reviewed; showCandidates();
}
$('result-text').oninput=()=>{const result=results[selected];if(!result)return;result.text=$('result-text').value;result.edited=true;result.reviewed=false;$('reviewed').checked=false;showNavigation();};
$('reviewed').onchange=()=>{results[selected].reviewed=$('reviewed').checked;showNavigation();};
$('delete-selection').onclick=()=>{const text=$('result-text');if(text.selectionStart===text.selectionEnd){status('Zuerst eine Textstelle im Ergebnis markieren.');return;}text.setRangeText('',text.selectionStart,text.selectionEnd,'start');text.dispatchEvent(new Event('input'));text.focus();};
$('export').onclick=async()=>{
  const documents=results.filter(r=>!r.error&&r.reviewed).map(r=>({text:r.text,reviewed:true}));
  busy=true;controls();
  try {const response=await api('/export',{documents});const blob=await response.blob();const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=documents.length===1?'transkript-001.txt':'gepruefte-transkripte.zip';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),15000);status(documents.length===1?'TXT-Download gestartet. Den Speicherort bestimmt dein Browser.':'ZIP-Download gestartet. Enthalten sind nur die ausgewählten geprüften Texte.');}
  catch(error){status(error.message,true);}finally{busy=false;controls();}
};
function reset() {controller?.abort();$('override-rows').replaceChildren();files=[];results=[];selected=0;dirty=false;configSnapshot=null;for(const id of ['terms','places','companies','other'])$(id).value='';$('name-candidates').replaceChildren();$('original').value='';$('result-text').value='';$('reviewed').checked=false;$('source-name').textContent='';$('error-panel').textContent='';$('files').value='';$('file-list').replaceChildren();$('result-list').replaceChildren();$('review').hidden=true;showFiles();status('Sitzung geleert. Bereits gespeicherte Downloads bleiben erhalten.');}
$('clear').onclick=async()=>{if((files.length||results.length||$('override-rows').children.length||['terms','places','companies','other'].some(id=>$(id).value))&&!await confirmation('Sitzung leeren?', 'Auswahl, Begriffe und ungespeicherte Ergebnisse werden aus dieser Oberfläche entfernt.'))return;reset();};
$('quit').onclick=async()=>{if(!await confirmation('Programm beenden?', 'Ungespeicherte Ergebnisse gehen verloren. Der lokale Dienst wird beendet.'))return;controller?.abort();controller=null;try{await api('/shutdown',{});}catch{}reset();sessionStorage.removeItem('werkstatt-token');$('setup').hidden=true;$('process').disabled=true;$('quit').disabled=true;status('Programm beendet. Du kannst diesen Tab schließen und die App später erneut öffnen.');};
window.addEventListener('beforeunload',event=>{if(results.length||files.length||$('override-rows').children.length){event.preventDefault();event.returnValue='';}});
function lines(id){return $(id).value.split('\n').map(x=>x.trim()).filter(Boolean);}
function showCandidates(){
  const result=results[selected]; $('name-candidates').replaceChildren();
  const names=result?.candidates||[];
  $('name-summary').textContent=`Automatisch gefundene Angaben prüfen (${names.length})`;
  if(!names.length){const p=document.createElement('p');p.className='small';p.textContent='Keine automatischen Angaben gefunden. Das bedeutet nicht, dass der Text frei von personenbezogenen Angaben ist.';$('name-candidates').append(p);return;}
  for(const item of names){
    const label=document.createElement('label'), input=document.createElement('input'), name=document.createElement('span'), detail=document.createElement('small');
    input.type='checkbox'; input.checked=!result.excluded.includes(item.name);input.disabled=busy;
    name.textContent=item.name;detail.textContent=`${({person:'[Person]',place:'[Ort]',company:'[Unternehmen]'})[item.kind]||'[Person]'} · ${item.source} · ${item.count}×`;
    input.onchange=async()=>{
      const index=selected, target=results[index];
      if(target.edited&&!await confirmation('Automatische Funde neu anwenden?', 'Die Änderung berechnet diesen Text aus dem Original neu. Manuelle Änderungen an diesem Text gehen dabei verloren.')){showCandidates();return;}
      const excluded=input.checked?target.excluded.filter(n=>n!==item.name):[...target.excluded,item.name];
      busy=true;controls();
      try{const response=await api('/refine',{text:target.original,...configSnapshot,excluded});const update=await response.json();Object.assign(target,update,{excluded,reviewed:false,edited:false});if(selected===index)showResult();else showNavigation();status('Automatische Funde angepasst. Bitte Ergebnis erneut prüfen.');}
      catch(error){status(error.message,true);showCandidates();}finally{busy=false;controls();}
    };
    label.append(input,name,detail);$('name-candidates').append(label);
  }
}
$('replace-selection').onclick=async()=>{
  const editor=$('result-text'); const chosen=editor.value.slice(editor.selectionStart,editor.selectionEnd).trim();
  if(!chosen||chosen.includes('[')||chosen.includes(']')){status('Bitte einen noch nicht ersetzten Namen oder Ausdruck im Ergebnis markieren.');return;}
  const label=$('selection-kind').value;
  let count=0;
  for(const result of results){
    if(result.error)continue;
    const replacement=replaceLiteral(result.text,chosen,label);const text=replacement.text;count+=replacement.count;
    if(text!==result.text){result.text=text;result.reviewed=false;result.edited=true;}
  }
  showResult();status(`${count} Vorkommen durch ${label} ersetzt. Betroffene Texte bitte erneut prüfen.`);
};
if(!token)status('Bitte über Start-Mac.command oder Start-Windows.cmd öffnen.',true);
controls();

$('mode').addEventListener('change',()=>{ $('mode-hint').textContent=$('mode').value==='model'?'Sucht Personen mit Vor- und Nachnamen, Orte und Organisationen im Zusammenhang. Das installierte deutsche Modell läuft auf deinem Mac. Beim ersten Lauf dauert das Laden etwas länger.':'Nur Namenslisten und Suchregeln. Unbekannte Nachnamen und Orte werden damit häufig übersehen. Optionale Korrekturen oder manuelle Nachbearbeitung sind besonders wichtig.'; });
$('demo').onclick=async()=>{
  if((files.length||results.length)&&!await confirmation('Beispiel laden?', 'Die aktuelle Auswahl und ungespeicherte Ergebnisse werden durch ein erfundenes Beispiel ersetzt.'))return;
  reset();
  const example="Sebastian: Was beschäftigt dich gerade?\nPetra: Ich habe mit Thomas Zappelwitz gesprochen. Zappelwitz kennt Anna von Winterfels. Winterfels arbeitet in München. Morgen fahren wir nach Hamburg. Meine Kollegin Claudia arbeitet bei Siemens. Sie erreicht mich unter anna@example.org.\nSebastian: Wie fühlst du dich damit?\nPetra: Ich möchte meine Grenzen besser ausdrücken.";
  addFiles([new File([example],'Erfundenes-Beispiel.txt',{type:'text/plain'})]);
  status('Erfundenes Beispiel geladen. Klicke auf Dateien verarbeiten.');
};

function addOverride() {
  if($('override-rows').children.length>=200){status('Maximal 200 Ausnahmeregeln möglich.',true);return;}
  const row=document.createElement('div');row.className='override-row';
  const source=document.createElement('input');source.type='text';source.maxLength=200;source.placeholder='z. B. Sebastian';source.setAttribute('aria-label','Suchausdruck');source.autocomplete='off';source.spellcheck=false;source.className='override-source';
  const action=document.createElement('select');action.setAttribute('aria-label','Aktion');action.className='override-action';
  for(const [value,text] of [['replace','Ersetzen durch'],['keep','Beibehalten']]){const option=document.createElement('option');option.value=value;option.textContent=text;action.append(option);}
  const target=document.createElement('input');target.type='text';target.maxLength=200;target.placeholder='z. B. Coach';target.setAttribute('aria-label','Ersatztext');target.autocomplete='off';target.spellcheck=false;target.className='override-target';
  const remove=document.createElement('button');remove.type='button';remove.className='quiet';remove.textContent='×';remove.setAttribute('aria-label','Ausnahmeregel entfernen');
  action.onchange=()=>{target.hidden=action.value==='keep';changed();};
  source.oninput=changed;target.oninput=changed;remove.onclick=()=>{row.remove();changed();};
  row.append(source,action,target,remove);$('override-rows').append(row);changed();source.focus();
}
function readOverrides() {
  const rules=[],seen=new Map();
  for(const row of $('override-rows').children){
    const source=row.querySelector('.override-source').value.trim().normalize('NFC'),action=row.querySelector('.override-action').value,target=action==='keep'?'':row.querySelector('.override-target').value.trim().normalize('NFC');
    if(!source&&!target)continue;
    if(!source||action==='replace'&&!target)throw new Error('Bitte bei jeder Ausnahmeregel einen Suchausdruck und bei „Ersetzen durch“ einen Ersatztext eintragen.');
    const key=source.toLocaleLowerCase('de').replace(/\s+/g,' '),value=JSON.stringify([action,target]);
    if(seen.has(key)&&seen.get(key)!==value)throw new Error('Derselbe Suchausdruck hat widersprüchliche Ausnahmeregeln. Bitte eine davon entfernen.');
    if(!seen.has(key))rules.push({source,action,target});seen.set(key,value);
  }
  return rules;
}
$('add-override').onclick=addOverride;
