import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

# Return the index.mjs file path, not the package directory.
old = "      return { path: ensureStub(spec), external: false }"
new = "      ensureStub(spec)\n      const pkgName = spec.startsWith('@')\n        ? spec.split('/').slice(0, 2).join('/')\n        : spec.split('/')[0]\n      return {\n        path: path.resolve(stubRoot, pkgName, 'index.mjs'),\n        external: false,\n      }"
if old not in src:
    print('ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(src)
print('FIXED stub path to point at index.mjs')
