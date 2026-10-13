import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

if 'patchRequireShim' in src:
    print('ALREADY PATCHED'); sys.exit(1)

# Call the patcher right after the bundle is written.
anchor = "    const outPath = resolve(ROOT, 'dist/cli.mjs')"
if anchor not in src:
    print('OUTPATH ANCHOR NOT FOUND'); sys.exit(1)
src = src.replace(anchor, "  // Convergence fork: give inlined CJS deps a working require().\n  patchRequireShim(outPath)\n\n" + anchor, 1)

# Define the patcher inside build-bundle.ts, above main().
anchor2 = "async function main() {"
if anchor2 not in src:
    print('MAIN ANCHOR NOT FOUND'); sys.exit(1)
fn = '''// Convergence fork: esbuild's CJS shim throws "Dynamic require of X is not
// supported" when a CommonJS dependency inlined into the ESM bundle calls
// require('fs') at load time. Rewrite the throwing branch to fall back to
// createRequire(import.meta.url) instead.
function patchRequireShim(outPath: string): void {
  const code = readFileSync(outPath, 'utf8')
  const marker = `throw Error('Dynamic require of "' + x3 + '" is not supported');`
  if (!code.includes(marker)) {
    return
  }
  const old = `if (typeof require !== "undefined") return require.apply(this, arguments);
  ` + marker
  const replacement =
    `if (typeof require !== "undefined") return require.apply(this, arguments);
  {
    const __cr = (await import('node:module')).createRequire(import.meta.url)
    return __cr(x3)
  }`
  if (!code.includes(old)) {
    console.warn('[convergence] require-shim marker found but exact match failed')
    return
  }
  writeFileSync(outPath, code.replace(old, replacement))
  console.log('[convergence] patched require shim for inlined CJS dependencies')
}

'''
src = src.replace(anchor2, fn + anchor2, 1)

# ensure readFileSync/writeFileSync are imported
old_imp = "import { chmodSync, readFileSync, existsSync } from 'fs'"
if old_imp in src:
    src = src.replace(old_imp, "import { chmodSync, readFileSync, writeFileSync, existsSync } from 'fs'", 1)
else:
    print('FS IMPORT NOT FOUND (non-fatal)')

open(p, 'w', encoding='utf-8').write(src)
print('added patchRequireShim')
