'use strict';
// Shared by the browser and focused unit tests; no storage or network access.
function replaceLiteral(text, chosen, label) {
  if (!chosen || chosen.length > 2000 || /[\[\]]/.test(chosen)) return {text, count:0};
  const escaped=chosen.split(/\s+/).map(part=>part.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('\\s+');
  const suffix=label==='[Person]'?'(?:s|[’\x27]s?)?':'';
  const pattern=new RegExp('(?<![\\p{L}\\p{N}_])'+escaped+suffix+'(?![\\p{L}\\p{N}_])','giu');
  let count=0;
  const output=text.split(/(\[[^\]\n]*\])/g).map(part=>part.startsWith('[')?part:part.replace(pattern,match=>{
    count++;
    const hasGenitive=label==='[Person]'&&match.toLocaleLowerCase().replace(/\s+/g,' ')!==chosen.toLocaleLowerCase().replace(/\s+/g,' ');
    return hasGenitive ? '[Person]s' : label;
  })).join('');
  return {text:output,count};
}
if(typeof module!=='undefined') module.exports={replaceLiteral};
