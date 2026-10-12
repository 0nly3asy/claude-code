import os, json

STUBS = {
    '@anthropic-ai/claude-agent-sdk': {
        'exports': ['QueryEngine', 'Tool', 'Task', 'AssistantSession', 'toolApi'],
        'note': 'Agent SDK; the fork re-implements its own loop.',
    },
    '@anthropic-ai/mcpb': {
        'exports': ['MCPBundleServer', 'bundleMcpServer', 'loadBundle'],
        'note': 'MCP bundle format (mcpb) loader.',
    },
}

for name, info in STUBS.items():
    root = os.path.join('node_modules', name)
    os.makedirs(root, exist_ok=True)
    pkg = {
        'name': name,
        'version': '0.0.0-convergence-stub',
        'description': f'Convergence fork stub: {name} is Anthropic-internal and not published. {info["note"]}',
        'type': 'module',
        'main': './index.js',
        'exports': {'.': './index.js'},
    }
    with open(os.path.join(root, 'package.json'), 'w') as f:
        json.dump(pkg, f, indent=2)
    lines = [
        f'// Convergence fork stub for {name}.',
        '// Anthropic-internal, not published to npm. Inert placeholder exports',
        '// so the bundled CLI can resolve the import. Not used in this fork.',
        '',
        'export class QueryEngine {',
        '  constructor(..._args) {}',
        '  async *query(..._args) { yield* [] }',
        '}',
        'export class Tool { constructor(..._args) {} }',
        'export class Task { constructor(..._args) {} }',
        'export class AssistantSession { constructor(..._args) {} }',
        'export class MCPBundleServer {',
        '  constructor(..._args) {}',
        '  async start() {}',
        '  async stop() {}',
        '}',
        'export async function bundleMcpServer(..._args) {',
        '  throw new Error("mcpb bundling is not supported in the Convergence fork")',
        '}',
        'export async function loadBundle(..._args) {',
        '  throw new Error("mcpb bundling is not supported in the Convergence fork")',
        '}',
        'export const toolApi = {}',
        '',
    ]
    with open(os.path.join(root, 'index.js'), 'w') as f:
        f.write('\n'.join(lines))
    print('stub written:', root)
