import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

old = """      if (fs.existsSync(installedDir)) return undefined // let esbuild resolve it
      ensureStub(spec)
      const pkgName = spec.startsWith('@')
        ? spec.split('/').slice(0, 2).join('/')
        : spec.split('/')[0]
      return {"""
new = """      if (fs.existsSync(installedDir)) return undefined // let esbuild resolve it
      ensureStub(spec)
      return {"""
if old not in src:
    print('ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(src)
print('removed duplicate pkgName declaration')
