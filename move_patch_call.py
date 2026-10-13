import sys
p = 'scripts/build-bundle.ts'
lines = open(p, encoding='utf-8').read().splitlines(keepends=True)

# The call sits before the definition; move it after chmodSync.
call_idx = None
def_idx = None
chmod_idx = None
for i, ln in enumerate(lines):
    if ln.strip() == 'patchRequireShim(outPath)':
        call_idx = i
    if ln.strip() == 'const outPath = resolve(ROOT, \'dist/cli.mjs\')':
        def_idx = i
    if 'chmodSync(outPath, 0o755)' in ln:
        chmod_idx = i
if None in (call_idx, def_idx, chmod_idx):
    print('anchors not all found', call_idx, def_idx, chmod_idx); sys.exit(1)
if call_idx < def_idx:
    # remove the misplaced call (and its preceding comment line)
    remove_from = call_idx
    # also drop the comment line above it
    if lines[call_idx-1].strip().startswith('// Convergence fork: give inlined CJS'):
        remove_from = call_idx - 1
    # capture the call + comment
    block = lines[remove_from:call_idx+1]
    del lines[remove_from:call_idx+1]
    # recompute chmod index after deletion
    chmod_idx = None
    for i, ln in enumerate(lines):
        if 'chmodSync(outPath, 0o755)' in ln:
            chmod_idx = i
            break
    # insert the call right after chmodSync block's try/catch close
    # find the closing '}' after chmod
    j = chmod_idx
    # advance past the try { chmod } catch { } construct
    insert_at = None
    depth = 0
    for k in range(chmod_idx, len(lines)):
        if '{' in lines[k]: depth += lines[k].count('{')
        if '}' in lines[k]:
            depth -= lines[k].count('}')
            if depth <= 0:
                insert_at = k + 1
                break
    if insert_at is None:
        insert_at = chmod_idx + 1
    lines.insert(insert_at, '\n')
    for b in block:
        lines.insert(insert_at+1, b)
    open(p, 'w', encoding='utf-8').write(''.join(lines))
    print('moved patchRequireShim call to after chmodSync at line', insert_at+1)
else:
    print('call already after definition; no change')
