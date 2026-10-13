const fs = require('fs');
const path = require('path');
// Scan the bundle for modules that call require() at module scope, and report
// the npm package each belongs to, so we can mark them external.
const src = fs.readFileSync('dist/cli.mjs', 'utf8');
// esbuild's cjs shim: __require2(...) with the literal arg
const re = /__require2\("([^"]+)"\)/g;
const needs = new Set();
let m;
while ((m = re.exec(src))) needs.add(m[1]);
// Map to the packages we saw in stack traces / obvious CJS ones
const suspects = ['node-fetch','agentkeepalive','commander','@commander-js/extra-typings'];
console.log('dynamic require targets:', [...needs].sort().join(', '));
console.log('---');
console.log('CJS packages to mark external:');
suspects.forEach(s => console.log('  ' + s));
