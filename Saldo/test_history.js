const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const context={};vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/history.js','utf8'),context);
const rows=[{id:'a',kind:'buy',date:'2026-01-01',quantity:2,price:100,current:999},
 {id:'b',kind:'buy',date:'2026-01-03',quantity:1,price:100,current:999},
 {kind:'dividend',date:'2026-01-02',price:10},
 {kind:'interest',date:'2026-01-03',price:5},
 {kind:'expected_dividend',date:'2026-01-03',price:1000}];
const points=context.historySeries(rows,[{id:'a',date:'2026-01-03',unit_price:90},{id:'b',date:'2026-01-03',unit_price:100}], '2026-01-03');
assert.equal(points[0].capital,200);assert.equal(points[0].value,200);
assert.equal(points[1].value,null); // Never backfill past values with today's price.
assert.equal(points[2].capital,300);assert.equal(points[2].value,295);assert.equal(points[2].result,-5);
assert.equal(points[2].income,15); // Pending distributions must not increase the result.
const empty=context.historySeries([],[],'2026-01-03');assert.equal(empty.length,1);assert.equal(empty[0].value,0);
console.log('OK: capital, paid income, negative returns, missing valuations and pending exclusions');
