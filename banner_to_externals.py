import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

# Remove the banner shim (it collides with esbuild's own createRequire import
# inside bundled CJS modules). Instead keep CJS deps external so Node loads
# them natively with a real require().
old_banner = """  // Banner: shebang for direct CLI execution, plus a require shim so CJS
  // dependencies inlined into this ESM bundle (node-fetch, agentkeepalive, ...)
  // can call require('http') at load time instead of throwing.
  banner: {
    js: '#!/usr/bin/env node\\nimport { createRequire as __createRequire } from \\'module\\'\\nglobalThis.require ??= __createRequire(import.meta.url)\\n',
  },"""
new_banner = """  // Banner: shebang for direct CLI execution
  banner: {
    js: '#!/usr/bin/env node\\n',
  },"""
if old_banner in src:
    src = src.replace(old_banner, new_banner, 1)
else:
    # try to strip any banner shim we added, falling back to original
    import re
    src2 = re.sub(r"  // Banner: shebang for direct CLI execution.*?js: '#!/usr/bin/env node\\\\n',\n\  \},",
                  "  // Banner: shebang for direct CLI execution\n  banner: {\n    js: '#!/usr/bin/env node\\n',\n  },", src, flags=re.S)
    src = src2

# Ensure the CJS deps that require() at load time stay external.
CJS = ['node-fetch', 'agentkeepalive']
for c in CJS:
    if f"    '{c}'," not in src:
        anchor = "    'node-fetch',"
        if anchor in src:
            src = src.replace(anchor, anchor + f"\n    '{c}',", 1)
        else:
            src = src.replace("    'console', 'process', 'v8', 'inspector',",
                              "    'console', 'process', 'v8', 'inspector',\n    'node-fetch',\n    'agentkeepalive',", 1)

open(p, 'w', encoding='utf-8').write(src)
print('reverted banner to plain shebang; node-fetch + agentkeepalive external')
