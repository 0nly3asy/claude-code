const fs = require('fs');
const src = fs.readFileSync('dist/cli.mjs', 'utf8');
const re = /import\s*\{([^}]*)\}\s*from\s*["']([^"']+)["']/g;
const byPkg = new Map();
let m;
while ((m = re.exec(src))) {
  const names = m[1].split(',').map(s => s.trim().split(/\s+as\s+/)[0].trim()).filter(Boolean);
  const spec = m[2];
  if (spec.startsWith('.') || spec.startsWith('node:') || spec.startsWith('bun:')) continue;
  const parts = spec.split('/');
  const pkg = spec.startsWith('@') ? parts.slice(0,2).join('/') : parts[0];
  if (!byPkg.has(pkg)) byPkg.set(pkg, new Set());
  names.forEach(n => byPkg.get(pkg).add(n));
}
const stubRoot = 'node_modules/.convergence-stubs';
const out = {};
for (const [pkg, names] of byPkg) {
  const dir = require('path').join(stubRoot, pkg);
  if (!fs.existsSync(dir)) continue; // only stubs
  out[pkg] = [...names].sort();
}
fs.writeFileSync('stub_named_imports.json', JSON.stringify(out, null, 1));
console.log('stub packages with named imports:', Object.keys(out).length);
for (const [p, n] of Object.entries(out)) console.log('  ' + p + ' -> ' + n.join(', '));
