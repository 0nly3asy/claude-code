const fs = require('fs');
const path = require('path');
const src = fs.readFileSync('dist/cli.mjs', 'utf8');
const re = /(?:from\s*|import\s*\(\s*)["']([^"']+)["']/g;
const pkgs = new Map();
let m;
while ((m = re.exec(src))) {
  const s = m[1];
  if (s.startsWith('.') || s.startsWith('node:') || s.startsWith('bun:')) continue;
  if (!/^[a-z@]/.test(s)) continue;
  // skip node builtins (bare names with no scope and no slash that are builtin)
  const parts = s.split('/');
  const pkg = s.startsWith('@') ? parts.slice(0,2).join('/') : parts[0];
  const sub = s.startsWith('@') ? parts.slice(2).join('/') : parts.slice(1).join('/');
  // skip non-package junk matched inside strings
  if (/[\s{}()]/.test(pkg)) continue;
  if (!pkgs.has(pkg)) pkgs.set(pkg, new Set());
  if (sub) pkgs.get(pkg).add(sub);
}
const BUILTINS = new Set(require('module').builtinModules);
const lines = [];
const missing = [];
for (const [pkg, subs] of [...pkgs.entries()].sort()) {
  if (BUILTINS.has(pkg)) continue;          // node resolves these
  const dir = path.join('node_modules', pkg);
  const installed = fs.existsSync(dir);
  const subList = [...subs].map(x => '/' + x).join(', ');
  if (!installed) missing.push(pkg + (subList ? '  subs:' + subList : ''));
  lines.push(`${installed ? 'OK     ' : 'MISSING'} ${pkg}${subList ? '  subs:' + subList : ''}`);
}
console.log('=== REAL npm packages imported at runtime ===');
console.log('total:', lines.length, '| missing:', missing.length);
console.log(lines.join('\n'));
console.log('\n=== ONLY THE MISSING ONES ===');
console.log(missing.length ? missing.join('\n') : '(none)');
