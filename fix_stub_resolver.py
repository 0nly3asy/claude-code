import re, sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

# Replace the entire stubResolverPlugin block with a safe, non-recursive version.
start = src.find('const stubResolverPlugin: esbuild.Plugin = {')
end = src.find('const srcResolverPlugin: esbuild.Plugin = {')
if start == -1 or end == -1 or end < start:
    print('BLOCK BOUNDARIES NOT FOUND'); sys.exit(1)

new_plugin = '''const stubResolverPlugin: esbuild.Plugin = {
  name: 'convergence-stub-resolver',
  setup(build) {
    const fs = require('fs')
    const path = require('path')

    // Precompute the stub directory once.
    const stubRoot = path.resolve(ROOT, 'node_modules', '.convergence-stubs')
    fs.mkdirSync(stubRoot, { recursive: true })

    const ensureStub = (spec: string): string => {
      const pkgName = spec.startsWith('@')
        ? spec.split('/').slice(0, 2).join('/')
        : spec.split('/')[0]
      const pkgDir = path.resolve(stubRoot, pkgName)
      const index = path.resolve(pkgDir, 'index.mjs')
      const pkgJson = path.resolve(pkgDir, 'package.json')
      if (!fs.existsSync(pkgJson)) {
        fs.mkdirSync(pkgDir, { recursive: true })
        fs.writeFileSync(
          pkgJson,
          JSON.stringify(
            {
              name: pkgName + '.convergence-stub',
              version: '0.0.0',
              description:
                'Convergence fork auto-stub for an unresolvable Anthropic-internal/optional package.',
              type: 'module',
              main: './index.mjs',
              exports: { '.': './index.mjs' },
            },
            null,
            2,
          ),
        )
        fs.writeFileSync(
          index,
          [
            '// Convergence fork auto-generated stub for ' + pkgName + '.',
            '// The real package is not installable here and is only reachable',
            '// behind default-off feature flags. Exports are inert.',
            'const handler = { get: () => () => undefined }',
            'export default new Proxy({}, handler)',
            'export const __convergenceStub = true',
          ].join('\\n') + '\\n',
        )
      }
      return pkgDir
    }

    // Only intercept bare specifiers whose package is NOT installed under
    // node_modules. Installed packages resolve normally through esbuild.
    build.onResolve({ filter: /^[^.@/]/ }, (args) => {
      const spec = args.path
      if (isBuiltin(spec)) return undefined
      if (spec.startsWith('bun:')) return undefined
      const pkgName = spec.startsWith('@')
        ? spec.split('/').slice(0, 2).join('/')
        : spec.split('/')[0]
      const installedDir = path.resolve(ROOT, 'node_modules', pkgName)
      if (fs.existsSync(installedDir)) return undefined // let esbuild resolve it
      return { path: ensureStub(spec), external: false }
    })
  },
}

'''
src = src[:start] + new_plugin + src[end:]
open(p, 'w', encoding='utf-8').write(src)
print('REPLACED stubResolverPlugin with non-recursive version')
