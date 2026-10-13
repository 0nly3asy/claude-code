import os, re, json, subprocess, sys

# Build the bundle, run it, parse every "Dynamic require of X" and the package
# it came from, then add those packages to the external list. Repeat-safe.
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

# Run current build + CLI to collect failing packages
subprocess.run(['C:\\Users\\Admin\\.bun\\bin\\bun.exe','run','build'],
               cwd='.', capture_output=True)
out = subprocess.run(['node','dist/cli.mjs','--version'],
                     cwd='.', capture_output=True, text=True, timeout=60)
text = out.stdout + out.stderr
pkgs = set()
# stack frames look like: at node_modules/<pkg>/... (...)
for m in re.finditer(r'at node_modules/(@[^/\s]+/[^/\s]+|[^/\s]+)/', text):
    pkgs.add(m.group(1))
# Also scan the bundle for every __require2 usage and its owning module comment
bundle = open('dist/cli.mjs', encoding='utf-8', errors='replace').read()
BUILTINS = {'assert','buffer','child_process','cluster','console','constants','crypto',
 'dgram','dns','domain','events','fs','http','http2','https','module','net','os','path',
 'perf_hooks','process','punycode','querystring','readline','repl','stream',
 'string_decoder','sys','timers','tls','tty','url','util','v8','vm','zlib'}
cur = None
for ln in bundle.splitlines():
    mm = re.search(r'// node_modules/(@[^/\s]+/[^/\s]+|[^/\s]+)/', ln)
    if mm: cur = mm.group(1)
    for req in re.findall(r'__require2\("([^"]+)"\)', ln):
        base = req[5:] if req.startswith('node:') else req
        if base in BUILTINS and cur:
            pkgs.add(cur)

KEEP = {'jsonc-parser','react','react-reconciler','scheduler','@anthropic-ai/sdk',
        'undici','ws','qrcode','turndown','xss','zod-to-json-schema','highlight.js',
        'diff','asciichart','yaml','execa','google-auth-library'}
pkgs = {x for x in pkgs if x not in KEEP}

# Replace the CJS external block content
start = src.find("    // CJS packages that call require()")
if start == -1:
    print('CJS MARKER NOT FOUND'); sys.exit(1)
# find end: next line that is '  ],' after start
end = src.find('  ],', start)
# remove from marker through the closing '  ],'
block_end = src.find('\n', end) + 1
newblock = "    // CJS packages that call require() at load time; must stay external\n"
newblock += "    // so Node loads them natively instead of being inlined into the ESM bundle.\n"
newblock += ''.join(f"    '{c}',\n" for c in sorted(pkgs))
src = src[:start] + newblock + src[block_end:]

open(p, 'w', encoding='utf-8').write(src)
print(f'auto-externalized {len(pkgs)} CJS packages:')
print(', '.join(sorted(pkgs)))
