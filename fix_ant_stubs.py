import os, json

NEEDED = {
    '@ant/computer-use-mcp': [
        'API_RESIZE_PARAMS', 'DEFAULT_GRANT_FLAGS', 'bindSessionContext',
        'buildComputerUseTools', 'createComputerUseMcpServer',
        'getSentinelCategory', 'targetImageSize',
    ],
    '@ant/claude-for-chrome-mcp': [
        'BROWSER_TOOLS', 'createClaudeForChromeMcpServer',
    ],
}

stubRoot = 'node_modules/.convergence-stubs'
for pkg, names in NEEDED.items():
    root = os.path.join(stubRoot, pkg)
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, 'package.json'), 'w') as f:
        json.dump({
            'name': pkg + '.convergence-stub',
            'version': '0.0.0',
            'description': 'Convergence fork stub: Anthropic-internal @ant package, gated behind USER_TYPE===ant which is pinned to external. Inert named exports so the bundle resolves.',
            'type': 'module',
            'main': './index.mjs',
            'exports': {'.': './index.mjs'},
        }, f, indent=2)
    lines = [
        '// Convergence fork auto-generated stub for ' + pkg + '.',
        '// Anthropic-internal package, not published. All importers are gated',
        '// behind USER_TYPE === "ant" which this build pins to "external", so',
        '// these are never called. Named exports satisfy the bundler.',
        '',
    ]
    for n in names:
        lines.append(f'export const {n} = undefined')
    lines.append('export const __convergenceStub = true')
    lines.append('')
    with open(os.path.join(root, 'index.mjs'), 'w') as f:
        f.write('\n'.join(lines))
    print(f'{pkg}: exported {len(names)} names')
