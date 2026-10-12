// Extract every bare-specifier import the bundle could hit at runtime.
const fs = require('fs');
const src = fs.readFileSync('dist/cli.mjs', 'utf8');
const re = /(?:^|[^.\w/])import\s*(?:[\s\S]{0,40}?\sfrom\s*)?["']([^"']+)["']/g;
const specs = new Set();
let m;
while ((m = re.exec(src))) {
  const s = m[1];
  if (s.startsWith('.') || s.startsWith('node:') || s.startsWith('bun:')) continue;
  if (/^[a-z]/.test(s) && s.includes('/')) {
    // scoped or org/pkg - keep only the package root
    const parts = s.split('/');
    const pkg = s.startsWith('@') ? parts.slice(0,2).join('/') : parts[0];
    specs.add(pkg + '  ::subpath:: ' + s);
  } else if (/^[a-z]/.test(s)) {
    specs.add(s);
  }
}
const out = [...specs].sort();
console.log('total runtime bare imports:', out.length);
out.forEach(s => console.log('  ' + s));
