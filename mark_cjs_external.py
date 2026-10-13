import json, os, sys

p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

if '// CJS packages' in src and "'commander'," in src:
    print('ALREADY PATCHED'); sys.exit(0)

# Scan installed deps: any whose package.json lacks "type": "module" is CJS.
# Bundling CJS into an ESM output makes esbuild rewrite require() to a throwing
# shim, which breaks at load. Keeping them external lets Node load them natively.
roots = ['node_modules']
cjs = []
for root in roots:
    if not os.path.isdir(root):
        continue
    for entry in sorted(os.listdir(root)):
        if entry.startswith('.'):
            continue
        if entry.startswith('@'):
            scope = os.path.join(root, entry)
            for sub in sorted(os.listdir(scope)):
                pkgdir = os.path.join(scope, sub)
                pj = os.path.join(pkgdir, 'package.json')
                if os.path.isfile(pj):
                    try:
                        d = json.load(open(pj, encoding='utf-8'))
                    except Exception:
                        continue
                    if d.get('type') != 'module':
                        cjs.append(f"{entry}/{sub}")
        else:
            pj = os.path.join(root, entry, 'package.json')
            if os.path.isfile(pj):
                try:
                    d = json.load(open(pj, encoding='utf-8'))
                except Exception:
                    continue
                if d.get('type') != 'module':
                    cjs.append(entry)

# Only the ones actually imported by the bundle matter. Intersect with the
# bundle's bare imports to avoid over-externalizing.
bundle = open('dist/cli.mjs', encoding='utf-8', errors='replace').read()
keep = [c for c in sorted(set(cjs)) if f'"{c}"' in bundle or f"'{c}'" in bundle or f"/{c}/" in bundle]
# always include the ones we saw in stack traces
for must in ('node-fetch', 'agentkeepalive', 'commander', '@commander-js/extra-typings'):
    if must not in keep:
        keep.append(must)

anchor = "    'node-fetch',"
lines = ''.join(f"    '{c}',\n" for c in sorted(set(keep)))
if anchor in src:
    src = src.replace(anchor, anchor + '\n' + lines, 1)
else:
    src = src.replace("    'console', 'process', 'v8', 'inspector',",
                      "    'console', 'process', 'v8', 'inspector',\n" + lines, 1)

open(p, 'w', encoding='utf-8').write(src)
print(f'marked {len(set(keep))} CJS packages external:', ', '.join(sorted(set(keep))))
