import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

if "'node-fetch'" in src:
    print('ALREADY PATCHED'); sys.exit(0)

# node-fetch is CommonJS and calls require('stream'/'http'/...) at load time.
# Bundled into an ESM output that becomes "Dynamic require of X is not supported".
# Marking it external lets Node load it natively as CJS.
anchor = "    'console', 'process', 'v8', 'inspector',"
if anchor not in src:
    print('ANCHOR NOT FOUND'); sys.exit(1)
add = anchor + "\n    // CJS packages that call require() at load time; must stay external\n    // so Node loads them natively instead of being inlined into the ESM bundle.\n    'node-fetch',"
src = src.replace(anchor, add, 1)
open(p, 'w', encoding='utf-8').write(src)
print('marked node-fetch external')
