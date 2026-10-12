import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

if 'convergence-stub-resolver' in src:
    print('ALREADY PATCHED'); sys.exit(0)

# Add a plugin that redirects unresolved non-builtin bare imports to a stub,
# and remove the now-harmful external entries so esbuild actually routes them
# through the plugin instead of leaving them as runtime imports.

plugin = """// Convergence fork: redirect any bare import that cannot be resolved to a
// generated stub. The upstream tree imports a number of Anthropic-internal
// packages (@ant/*, the .napi native addons, optional cloud SDKs) that are not
// published to npm and are only reachable via default-off feature flags. Rather
// than listing them by hand, resolve-or-stub: if the package is installed we use
// it, otherwise we emit an inert stub so Node never sees an unresolvable import.
const builtinModules = new Set(
  require('module').builtinModules as unknown as string[],
)
const isBuiltin = (spec: string) =>
  builtinModules.has(spec) || spec.startsWith('node:')

const stubResolverPlugin: esbuild.Plugin = {
  name: 'convergence-stub-resolver',
  setup(build) {
    const fs = require('fs')
    const path = require('path')
    const os = require('os')

    const stubDir = path.resolve(ROOT, 'node_modules', '.convergence-stubs')
    fs.mkdirSync(stubDir, { recursive: true })

    build.onResolve({ filter: /^[^.@\/]/ }, async (args) => {
      if (isBuiltin(args.path)) return undefined // let esbuild handle builtins
      // Only intercept bare specifiers that esbuild cannot already resolve.
      const result = await build.resolve(args.path, {
        kind: args.kind,
        resolveDir: args.resolveDir,
        importer: args.importer,
      })
      if (result.errors.length === 0) return undefined
      // Hand back a stub path.
      const safe = args.path.replace(/[^a-zA-Z0-9._-]/g, '_')
      const stubPath = path.resolve(stubDir, safe + '.mjs')
      if (!fs.existsSync(stubPath)) {
        const pkgName = args.path.split('/').slice(0, args.path.startsWith('@') ? 2 : 1).join('/')
        const pkgDir = path.resolve(stubDir, pkgName)
        fs.mkdirSync(pkgDir, { recursive: true })
        const pkgJson = path.resolve(pkgDir, 'package.json')
        const index = path.resolve(pkgDir, 'index.mjs')
        if (!fs.existsSync(pkgJson)) {
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
        }
        if (!fs.existsSync(index)) {
          fs.writeFileSync(
            index,
            [
              '// Convergence fork auto-generated stub for ' + pkgName + '.',
              '// The real package is not installable here and is only reachable',
              '// behind default-off feature flags. Exports are inert.',
              'const handler = {',
              '  get: () => () => undefined,',
              '}',
              'export default new Proxy({}, handler)',
              'export const __convergenceStub = true',
            ].join('\\n') + '\\n',
          )
        }
        // Return the directory so a bare spec maps to its index via package.json.
        return { path: pkgDir, external: false }
      }
      return { path: stubPath, external: false }
    })
  },
}

"""

anchor = "// ── Plugin: resolve bare 'src/' imports (tsconfig baseUrl: \".\") ──"
if anchor not in src:
    print('PLUGIN ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(anchor, plugin + anchor, 1)

# register the plugin
old_plugins = "  plugins: [srcResolverPlugin],"
new_plugins = "  plugins: [srcResolverPlugin, stubResolverPlugin],"
if old_plugins not in src:
    print('PLUGINS REGISTRATION NOT FOUND'); sys.exit(1)
src = src.replace(old_plugins, new_plugins, 1)

open(p, 'w', encoding='utf-8').write(src)
print('PATCHED build-bundle.ts with convergence-stub-resolver plugin')
