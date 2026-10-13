import sys
p = 'scripts/build-bundle.ts'
lines = open(p, encoding='utf-8').read().splitlines(keepends=True)

# The external: [ array lost its closing '],'. Find 'commander,' then the
# blank lines, and insert '],' before 'jsx:'.
jsx = None
for i, ln in enumerate(lines):
    if ln.strip() == "jsx: 'automatic',":
        jsx = i
        break
if jsx is None:
    print('JSX NOT FOUND'); sys.exit(1)

# Walk back over blank lines to the last real external entry
j = jsx - 1
while j > 0 and lines[j].strip() == '':
    j -= 1
print('last external entry:', repr(lines[j]))
# insert '],' after position j
lines.insert(j+1, '  ],\n')
open(p, 'w', encoding='utf-8').write(''.join(lines))
print('restored external array closing bracket')
