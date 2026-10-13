import sys
p = 'scripts/build-bundle.ts'
lines = open(p, encoding='utf-8').read().splitlines(keepends=True)

# Insert CJS externals at the blank lines 179-180, before the closing '],'
anchor = None
for i, ln in enumerate(lines):
    if ln.strip() == "// so Node loads them natively instead of being inlined into the ESM bundle.":
        anchor = i
        break
if anchor is None:
    print('COMMENT ANCHOR NOT FOUND'); sys.exit(1)

add = [
    "    'node-fetch',\n",
    "    'agentkeepalive',\n",
    "    'commander',\n",
    "    '@commander-js/extra-typings',\n",
    "    'jsonc-parser',\n",
]
# skip existing blank lines after the comment
j = anchor + 1
while j < len(lines) and lines[j].strip() == '':
    j += 1
lines[anchor+1:j] = add
open(p, 'w', encoding='utf-8').write(''.join(lines))
print('added CJS externals: node-fetch, agentkeepalive, commander, @commander-js/extra-typings, jsonc-parser')
