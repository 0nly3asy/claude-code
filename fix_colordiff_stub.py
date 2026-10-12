import os, json

root = 'node_modules/.convergence-stubs/color-diff-napi'
os.makedirs(root, exist_ok=True)

with open(os.path.join(root, 'package.json'), 'w') as f:
    json.dump({
        'name': 'color-diff-napi.convergence-stub',
        'version': '0.0.0',
        'description': 'Convergence fork stub: color-diff-napi is a native addon not installable here. Provides inert classes so the import resolves; syntax highlighting falls back to the TS port.',
        'type': 'module',
        'main': './index.mjs',
        'exports': {'.': './index.mjs'},
    }, f, indent=2)

index = """// Convergence fork stub for color-diff-napi.
// The real package is a native (NAPI) addon that is not published for this
// platform. src/components/StructuredDiff/colorDiff.ts imports it directly, so
// we provide inert stand-ins. Callers fall back to the pure-TS color path when
// these are unavailable.
export class ColorDiff {
  constructor(..._args) {}
  async compute(..._args) { return [] }
}
export class ColorFile {
  constructor(..._args) {}
}
export function getSyntaxTheme(..._args) {
  return undefined
}
export const __convergenceStub = true
"""
with open(os.path.join(root, 'index.mjs'), 'w') as f:
    f.write(index)
print('wrote color-diff-napi stub with ColorDiff, ColorFile, getSyntaxTheme')
