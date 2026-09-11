const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');const vm=require('node:vm');
const scope={};vm.createContext(scope);vm.runInContext(fs.readFileSync('app/replacement.js','utf8'),scope);
test('literal correction keeps surrounding edits and handles genitive',()=>{
 const result=scope.replaceLiteral('Annas Idee. Anna hilft. Eigene Bearbeitung.','Anna','[Person]');
 assert.equal(result.text,'[Person]s Idee. [Person] hilft. Eigene Bearbeitung.');
});
test('existing markers and partial words are preserved',()=>{
 assert.equal(scope.replaceLiteral('[Person] und Person und Personal','Person','[Angabe]').text,'[Person] und [Angabe] und Personal');
});
