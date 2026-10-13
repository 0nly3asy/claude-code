import os
p = 'node_modules/.convergence-stubs/@ant/claude-for-chrome-mcp/index.mjs'
os.makedirs(os.path.dirname(p), exist_ok=True)
with open(p, 'w', encoding='utf-8') as f:
    f.write(
        "// Convergence fork auto-generated stub for @ant/claude-for-chrome-mcp.\n"
        "// Anthropic-internal package, not published. Importers are gated behind\n"
        "// USER_TYPE === 'ant' (pinned to 'external' in this build), so these are\n"
        "// never meaningfully used. BROWSER_TOOLS is a real empty array so\n"
        "// .map() callers do not crash at import time.\n"
        "export const BROWSER_TOOLS = []\n"
        "export const createClaudeForChromeMcpServer = undefined\n"
        "export const __convergenceStub = true\n"
    )
print('BROWSER_TOOLS now an empty array')
