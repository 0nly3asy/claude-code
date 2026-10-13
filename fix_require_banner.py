import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

if 'createRequire' in src:
    print('ALREADY PATCHED'); sys.exit(1)

# CJS deps pulled into the ESM bundle (node-fetch, agentkeepalive, ...) call
# require('http') etc. at load time. esbuild rewrites those to a throwing shim.
# Give the bundle a real require backed by createRequire so they work.
old = """  // Banner: shebang for direct CLI execution
  banner: {
    js: '#!/usr/bin/env node\\n',
  },"""
new = """  // Banner: shebang for direct CLI execution, plus a require shim so CJS
  // dependencies inlined into this ESM bundle (node-fetch, agentkeepalive, ...)
  // can call require('http') at load time instead of throwing.
  banner: {
    js: '#!/usr/bin/env node\\nimport { createRequire } from \\'module\\'\\nconst require = createRequire(import.meta.url)\\n',
  },"""
if old not in src:
    print('BANNER ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(src)
print('added createRequire banner')
