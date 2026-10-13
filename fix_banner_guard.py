import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

old = "const require = createRequire(import.meta.url)"
new = "globalThis.require ??= createRequire(import.meta.url)"
if old not in src:
    print('ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(old, new, 1)

# also avoid re-declaring createRequire if a bundled module already did
old2 = "import { createRequire } from 'module'"
new2 = "import { createRequire as __createRequire } from 'module'"
if old2 in src:
    src = src.replace(old2, new2, 1)
    src = src.replace("globalThis.require ??= createRequire(import.meta.url)",
                      "globalThis.require ??= __createRequire(import.meta.url)", 1)
open(p, 'w', encoding='utf-8').write(src)
print('guarded require banner against redeclaration')
