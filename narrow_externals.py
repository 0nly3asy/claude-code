import os, re, sys

p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()
bundle = open('dist/cli.mjs', encoding='utf-8', errors='replace').read()

# Node builtins (the ones that matter when required from CJS).
BUILTINS = {
 'assert','buffer','child_process','cluster','console','constants','crypto','dgram',
 'dns','domain','events','fs','http','http2','https','module','net','os','path',
 'perf_hooks','process','punycode','querystring','readline','repl','stream',
 'string_decoder','sys','timers','tls','tty','url','util','v8','vm','zlib',
}

lines = bundle.splitlines()
bad_pkgs = set()
cur_pkg = None
for ln in lines:
    mm = re.search(r'// node_modules/(@[^/\s]+/[^/\s]+|[^/\s]+)/', ln)
    if mm:
        cur_pkg = mm.group(1)
    for req in re.findall(r'__require2\("([^"]+)"\)', ln):
        base = req[5:] if req.startswith('node:') else req
        if base in BUILTINS and cur_pkg:
            bad_pkgs.add(cur_pkg)

for must in ('node-fetch', 'agentkeepalive', 'commander', '@commander-js/extra-typings'):
    bad_pkgs.add(must)

KEEP_BUNDLED = {'jsonc-parser','react','react-reconciler','scheduler',
                '@anthropic-ai/sdk','undici','ws','qrcode','turndown','xss',
                'zod-to-json-schema','highlight.js','diff','asciichart','yaml'}
bad_pkgs = {b for b in bad_pkgs if b not in KEEP_BUNDLED}

# strip the previously added CJS block: from the marker (or node-fetch line) to
# the "// Handle the .js" anchor
start = src.find('    // CJS packages')
if start == -1:
    start = src.find("    'node-fetch',")
anchor = '    // Handle the .js'
end = src.find(anchor)
if start != -1 and end != -1 and end > start:
    src = src[:start] + src[end:]

add = ''.join(f"    '{c}',\n" for c in sorted(bad_pkgs))
if "    'node-fetch'," in src:
    src = src.replace("    'node-fetch',", "    'node-fetch',\n" + add, 1)
else:
    src = src.replace("    'console', 'process', 'v8', 'inspector',",
                      "    'console', 'process', 'v8', 'inspector',\n" + add, 1)

open(p, 'w', encoding='utf-8').write(src)
print(f'narrowed CJS externals to {len(bad_pkgs)}:')
print(', '.join(sorted(bad_pkgs)))
