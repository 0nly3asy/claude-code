import sys
p = 'src/utils/json.ts'
src = open(p, encoding='utf-8').read()

old = "} from 'jsonc-parser/lib/esm/main.js'"
new = "} from 'jsonc-parser'"
if old not in src:
    print('ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(src)
print('jsonc-parser import -> package root (fixes ESM extensionless resolution)')
