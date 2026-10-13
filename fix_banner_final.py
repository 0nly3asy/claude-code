import sys
p = 'scripts/build-bundle.ts'
lines = open(p, encoding='utf-8').read().splitlines(keepends=True)

# Replace lines 217-222 (1-based) with a plain shebang banner.
# indices are 0-based -> 216..221 inclusive
start, end = 216, 222
assert 'require shim' in lines[start], f'unexpected line {start}: {lines[start]!r}'
assert lines[end-1].strip().startswith('},'), f'unexpected line {end-1}: {lines[end-1]!r}'

replacement = [
    "  // Banner: shebang for direct CLI execution\n",
    "  banner: {\n",
    "    js: '#!/usr/bin/env node\\n',\n",
    "  },\n",
]
lines[start:end] = replacement
open(p, 'w', encoding='utf-8').write(''.join(lines))
print('banner replaced with plain shebang')
