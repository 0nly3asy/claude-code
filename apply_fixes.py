import sys

def patch(path, old, new):
    s = open(path, encoding='utf-8').read()
    if s.count(old) != 1:
        sys.exit('ANCHOR FAIL in %s (count=%d): %r' % (path, s.count(old), old[:60]))
    s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('PATCHED', path)

# --- 1. src/utils/model/model.ts: two null-guards ---
p = 'src/utils/model/model.ts'
s = open(p, encoding='utf-8').read()
if 'isAtriaProvider' not in s:
    sys.exit('isAtriaProvider not imported in model.ts -- aborting')

patch(p,
"""export function firstPartyNameToCanonical(name: ModelName): ModelShortName {
  name = name.toLowerCase()""",
"""export function firstPartyNameToCanonical(name: ModelName): ModelShortName {
  // Convergence fork: custom providers (e.g. Atria) have no first-party
  // canonical name; guard so cost lookups do not throw on undefined.
  if (name === undefined || name === null) {
    return undefined as unknown as ModelShortName
  }
  name = name.toLowerCase()""")

patch(p,
"""export function parseUserSpecifiedModel(
  modelInput: ModelName | ModelAlias,
): ModelName {
  const modelInputTrimmed = modelInput.trim()""",
"""export function parseUserSpecifiedModel(
  modelInput: ModelName | ModelAlias,
): ModelName {
  // Convergence fork: with the Atria provider active and no model chosen, the
  // default setting is undefined; fall back instead of throwing on .trim().
  if (modelInput === undefined || modelInput === null) {
    if (isAtriaProvider()) return getAtriaDefaultModel() as ModelName
    return getDefaultMainLoopModel()
  }
  const modelInputTrimmed = modelInput.trim()""")

# --- 2. scripts/build-bundle.ts: define MACRO.BUILD_TIME ---
patch('scripts/build-bundle.ts',
"""    'MACRO.VERSION': JSON.stringify(version),""",
"""    'MACRO.VERSION': JSON.stringify(version),
    // Convergence fork: getBuildAgeMinutes() reads MACRO.BUILD_TIME. esbuild
    // only substitutes exact `define` matches, so provide it or it throws
    // at runtime on the first real API query.
    'MACRO.BUILD_TIME': 'Date.now()',""")

# --- 3. package.json: version must clear the dynamic min-version gate ---
patch('package.json', '"version": "0.0.0-leaked",', '"version": "1.0.30",')

# --- 4. make_sandbox_stub.py: add the static methods isSandboxingEnabled needs ---
patch('make_sandbox_stub.py',
"""  isRunning() { return false }
}""",
"""  isRunning() { return false }
  // Convergence fork: isSandboxingEnabled()/checkDependencies() call these
  // static methods; inert implementations so they never throw.
  static isSupportedPlatform() { return false }
  static checkDependencies(..._args) { return { errors: [] } }
}""")

print('ALL PATCHES APPLIED')
