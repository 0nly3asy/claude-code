import sys
p = 'scripts/build-bundle.ts'
lines = open(p, encoding='utf-8').read().splitlines(keepends=True)

# FIX 1: line 246 '}}' -> '}'
for i, ln in enumerate(lines):
    if ln.rstrip().endswith('}}') and i > 230:
        lines[i] = ln.rstrip()[:-1] + '\n'
        print(f'fixed double brace at line {i+1}')
        break

src = ''.join(lines)

# FIX 2: close the external array before the inject: line
# The external: [ array at ~169 lost its '],'. Insert it before the inject comment.
marker = '  // Convergence fork: give the ESM bundle a working require()'
idx = src.find(marker)
if idx != -1:
    # insert the closing bracket + blank line before the marker
    src = src[:idx] + '  ],\n\n' + src[idx:]
    print('closed external array before inject:')
open(p, 'w', encoding='utf-8').write(src)
print('syntax fixes applied')
