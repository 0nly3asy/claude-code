import sys
p = 'scripts/build-bundle.ts'
lines = open(p, encoding='utf-8').read().splitlines(keepends=True)

# Find the start of the stray CJS list: the duplicated 'node-fetch' at ~line 183
# or the first entry of the big list ('@anthropic-ai/sdk' right after it).
start = None
for i, ln in enumerate(lines):
    if ln.strip() == "'@anthropic-ai/sdk',":
        start = i
        break
if start is None:
    print('BIG LIST START NOT FOUND'); sys.exit(1)

# Find where it ends: the next non-package line, i.e. a line that is not
# "    'pkg'," — the closing '],'
end = None
for j in range(start, len(lines)):
    s = lines[j].strip()
    if s == '],':
        end = j
        break
if end is None:
    print('BLOCK END NOT FOUND'); sys.exit(1)

# Also drop the duplicated 'node-fetch' line just before start (line 183)
if start > 0 and lines[start-1].strip() == "'node-fetch',":
    start -= 1
# and the blank line after, if any
print('removing lines', start+1, 'to', end+1)
print('first removed:', repr(lines[start]))
print('last removed:', repr(lines[end]))
del lines[start:end+1]

open(p, 'w', encoding='utf-8').write(''.join(lines))
print('removed stray CJS external list')
