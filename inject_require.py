import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

if 'inject:' in src and 'createRequire' in src:
    print('ALREADY PATCHED'); sys.exit(1)

# Provide a real `require` in ESM scope via esbuild's inject option. esbuild
# hoists the injected module above all bundled code, so CJS deps that call
# require('fs') at load time get a working require instead of the throwing shim.
inject_path = 'scripts/require-shim.js'
import os
with open(inject_path, 'w', encoding='utf-8') as f:
    f.write(
        "// Convergence fork: injected at the top of the bundle so CommonJS\n"
        "// dependencies inlined into this ESM output get a working require().\n"
        "import { createRequire as __cr } from 'module'\n"
        "if (typeof require === 'undefined' || (require as any).__isShim) {\n"
        "  const __r = __cr(import.meta.url)\n"
        "  ;(globalThis as any).require = __r\n"
        "}\n"
    )

anchor = "  jsx: 'automatic',"
if anchor not in src:
    print('JSX ANCHOR NOT FOUND'); sys.exit(1)
inject_block = "  // Convergence fork: give the ESM bundle a working require() for inlined CJS deps\n  inject: [resolve(ROOT, 'scripts/require-shim.js')],\n\n"
src = src.replace(anchor, inject_block + anchor, 1)
open(p, 'w', encoding='utf-8').write(src)
print('added inject: require-shim.js')
