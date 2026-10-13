import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

# Replace the previous exact-match logic with a robust single-line replacement.
old_fn_start = src.find('function patchRequireShim(outPath: string): void {')
old_fn_end = src.find('\n}\n', old_fn_start)
if old_fn_start == -1 or old_fn_end == -1:
    print('OLD FN NOT FOUND'); sys.exit(1)

new_fn = '''function patchRequireShim(outPath: string): void {
  const code = readFileSync(outPath, 'utf8')
  const marker = `throw Error('Dynamic require of "' + x3 + '" is not supported');`
  if (!code.includes(marker)) {
    return
  }
  // Replace the throwing branch with a createRequire fallback. The marker line
  // is unique in the bundle, so a direct replace is safe.
  const replacement = `const __cr = (await import('node:module')).createRequire(import.meta.url)
    return __cr(x3)`
  writeFileSync(outPath, code.replace(marker, replacement))
  console.log('[convergence] patched require shim for inlined CJS dependencies')
}'''
src = src[:old_fn_start] + new_fn + src[old_fn_end+1:]
open(p, 'w', encoding='utf-8').write(src)
print('patchRequireShim now replaces the throw line directly')
