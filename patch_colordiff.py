"""Convergence fork: color-diff-napi is Anthropic-internal and not installable,
so the stubResolverPlugin redirects it to the auto-stub whose Proxy get-trap
returns a no-op FUNCTION for every named import. That value is truthy AND
constructable, so it slips past `if (!ColorDiff) return null` — `new ColorDiff()`
then yields an object with no `.render`, killing the TUI renderer.

Duck-type the real class at module scope: if ColorDiff lacks a prototype.render
method, treat the module as unavailable so every expect* helper returns null and
callers fall back to StructuredDiffFallback (the designed degradation path).

Idempotent, newline-style-preserving, anchor-verified. Source-of-truth patch
(no node_modules edits).
"""
import io
import sys

PATH = r'src\components\StructuredDiff\colorDiff.ts'

OLD = """export function expectColorDiff(): typeof ColorDiff | null {
  return getColorModuleUnavailableReason() === null ? ColorDiff : null
}

export function expectColorFile(): typeof ColorFile | null {
  return getColorModuleUnavailableReason() === null ? ColorFile : null
}

export function getSyntaxTheme(themeName: string): SyntaxTheme | null {
  return getColorModuleUnavailableReason() === null
    ? nativeGetSyntaxTheme(themeName)
    : null
}"""

NEW = """// Convergence fork: the module is not installable here and resolves to the
// auto-stub, whose Proxy get-trap returns a no-op function for EVERY named
// import. That value is truthy and constructable, so a plain truthiness guard
// passes and `new ColorDiff(...).render(...)` throws inside the TUI renderer.
// Duck-type the real class instead: no prototype.render => unavailable, and the
// callers render StructuredDiffFallback (the designed degradation path).
const colorModuleUsable =
  typeof ColorDiff === 'function' &&
  typeof ColorDiff?.prototype?.render === 'function'

export function expectColorDiff(): typeof ColorDiff | null {
  return getColorModuleUnavailableReason() === null && colorModuleUsable
    ? ColorDiff
    : null
}

export function expectColorFile(): typeof ColorFile | null {
  return getColorModuleUnavailableReason() === null && colorModuleUsable
    ? ColorFile
    : null
}

export function getSyntaxTheme(themeName: string): SyntaxTheme | null {
  return getColorModuleUnavailableReason() === null && colorModuleUsable
    ? nativeGetSyntaxTheme(themeName)
    : null
}"""

def renl(txt, nl):
    return txt.replace('\n', nl)

with io.open(PATH, encoding='utf-8', newline='') as f:
    s = f.read()
if 'colorModuleUsable' in s:
    print('ALREADY PATCHED')
    sys.exit(0)
nl = '\r\n' if '\r\n' in s else '\n'
old, new = renl(OLD, nl), renl(NEW, nl)
if s.count(old) != 1:
    print('ANCHOR FAIL count=%d (expected 1), nl=%r' % (s.count(old), nl))
    sys.exit(1)
with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
    f.write(s.replace(old, new))
print('PATCHED colorDiff.ts (nl=%r): duck-type gate on colorModuleUsable' % nl)
