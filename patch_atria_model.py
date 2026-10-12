import sys
p = 'src/utils/model/model.ts'
src = open(p, encoding='utf-8').read()

if 'isAtriaProvider' in src:
    print('ALREADY PATCHED'); sys.exit(0)

# 1) import atria helpers
old = "import { getAPIProvider } from './providers.js'"
if old not in src:
    # find the actual import line for providers
    import re
    m = re.search(r"import \{[^}]*\} from '\./providers\.js'", src)
    if not m:
        print('PROVIDERS IMPORT NOT FOUND'); sys.exit(1)
    old = m.group(0)
new = old.replace('} from', ', getAtriaDefaultModel, isAtriaProvider } from', 1)
src = src.replace(old, new, 1)

# 2) getMainLoopModel: when no model is specified and Atria is active, use the
#    Atria default instead of a claude-* model.
old_main = """export function getMainLoopModel(): ModelName {
  const model = getUserSpecifiedModelSetting()
  if (model !== undefined && model !== null) {
    return parseUserSpecifiedModel(model)
  }
  return getDefaultMainLoopModel()
}"""
new_main = """export function getMainLoopModel(): ModelName {
  const model = getUserSpecifiedModelSetting()
  if (model !== undefined && model !== null) {
    return parseUserSpecifiedModel(model)
  }
  // Convergence fork: when the Atria provider is active and the user has not
  // chosen a model, default to the Atria model instead of a claude-* model.
  if (isAtriaProvider()) {
    return getAtriaDefaultModel() as ModelName
  }
  return getDefaultMainLoopModel()
}"""
assert old_main in src, 'getMainLoopModel anchor not found'
src = src.replace(old_main, new_main, 1)

open(p, 'w', encoding='utf-8').write(src)
print('PATCHED model.ts with Atria default model')
