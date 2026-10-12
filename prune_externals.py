import sys
p = 'scripts/build-bundle.ts'
src = open(p, encoding='utf-8').read()

# Remove external entries that are not installed and therefore break at runtime.
# The stubResolverPlugin now intercepts any bare import whose package is missing
# and substitutes an inert stub, so these no longer need to be external.
REMOVE_EXACT = {
    "    'sharp',",
    "    'image-processor-napi',",
    "    '@anthropic-ai/sandbox-runtime',",
    "    '@anthropic-ai/claude-agent-sdk',",
    "    '@anthropic-ai/mcpb',",
    "    'audio-capture-napi',",
    "    'color-diff-napi',",
    "    'modifiers-napi',",
    "    '@ant/*',",
}
# remove the whole cloud/telemetry block too
start = src.find("    // Convergence fork: optional cloud/telemetry providers")
end_marker = "    'vscode-jsonrpc/node.js',\n"
if start != -1:
    end = src.find(end_marker, start)
    if end != -1:
        end += len(end_marker)
        src = src[:start] + src[end:]

removed = []
for line in REMOVE_EXACT:
    if line in src:
        src = src.replace(line, '', 1)
        removed.append(line.strip())
open(p, 'w', encoding='utf-8').write(src)
print('removed external entries:', len(removed))
for r in removed: print('  -', r)
