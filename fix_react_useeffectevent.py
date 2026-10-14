"""Convergence fork: React 19.2.4 exports useEffectEvent, but the hook
dispatchers in BOTH published CJS builds lack the method, so the first call
kills the TUI renderer (resolveDispatcher().useEffectEvent is not a function
-> AppStateProvider dies on first render).

The fork builds DEV-mode by default (scripts/build-bundle.ts ties the
NODE_ENV define to --minify), so react.development.js is the file that
actually gets bundled; react.production.js is patched too so a --minify
build is equally covered.

Polyfills the export with the canonical stable-identity pattern using hooks
that DO exist in both builds (useRef + useEffect + useCallback([])).
Anchor-verified, CRLF-preserving, idempotent. Run BEFORE
`bun scripts/build-bundle.ts`.
"""
import io
import os
import re
import sys

FILES = [
    r'node_modules\react\cjs\react.development.js',
    r'node_modules\react\cjs\react.production.js',
]

# Pristine export in either CJS build (either dispatcher style, any indent).
PATTERN = re.compile(
    r'^([ \t]*)exports\.useEffectEvent = function \(callback\) \{\r?\n'
    r'[ \t]*return (?:resolveDispatcher\(\)|ReactSharedInternals\.H)\.useEffectEvent\(callback\);\r?\n'
    r'[ \t]*\};',
    re.M,
)
MARKER = 'ref.current.apply(undefined, arguments)'


def polyfill(nl, indent):
    lines = [
        'exports.useEffectEvent = function (callback) {',
        '  var ref = exports.useRef(callback);',
        '  exports.useEffect(function () {',
        '    ref.current = callback;',
        '  });',
        '  return exports.useCallback(function () {',
        '    return ref.current.apply(undefined, arguments);',
        '  }, []);',
        '};',
    ]
    return nl.join(indent + line for line in lines)


def patch(path):
    if not os.path.exists(path):
        print('SKIP (missing file):', path)
        return
    with io.open(path, encoding='utf-8', newline='') as f:
        source = f.read()
    if MARKER in source:
        print('ALREADY PATCHED:', path)
        return
    matches = list(PATTERN.finditer(source))
    if len(matches) != 1:
        print('ANCHOR FAIL %s count=%d (expected 1)' % (path, len(matches)))
        sys.exit(1)
    nl = '\r\n' if '\r\n' in source else '\n'
    match = matches[0]
    replacement = polyfill(nl, match.group(1))
    patched = source[:match.start()] + replacement + source[match.end():]
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(patched)
    print('PATCHED:', path)


for rel in FILES:
    patch(rel)
