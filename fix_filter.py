import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

old = "    build.onResolve({ filter: /^[^.@/]/ }, (args) => {"
new = "    // Match bare specifiers: unscoped ('foo', 'foo/bar') and scoped ('@ant/x', '@ant/x/y').\n    build.onResolve({ filter: /^(?:@[a-z0-9-]+\\/)?[a-z0-9-]+/i }, (args) => {"
if old not in src:
    print('ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(src)
print('FIXED onResolve filter to include scoped @ packages')
