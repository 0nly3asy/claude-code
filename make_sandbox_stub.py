import os, json

ROOT = 'node_modules/@anthropic-ai/sandbox-runtime'
os.makedirs(ROOT, exist_ok=True)

pkg = {
    "name": "@anthropic-ai/sandbox-runtime",
    "version": "0.0.0-convergence-stub",
    "description": "Convergence fork stub: sandbox-runtime is Anthropic-internal and not published. Provides inert runtime exports so the bundle loads. Sandboxing is disabled in this fork.",
    "type": "module",
    "main": "./index.js",
    "exports": { ".": "./index.js" },
}
with open(os.path.join(ROOT, 'package.json'), 'w') as f:
    json.dump(pkg, f, indent=2)

index = """// Convergence fork stub for @anthropic-ai/sandbox-runtime.
// The real package is Anthropic-internal and not published to npm. This stub
// provides the three runtime values that src/utils/sandbox/sandbox-adapter.ts
// imports, in inert form, so the bundled CLI can load. Sandboxing is disabled.
export class SandboxManager {
  constructor(..._args) {}
  async start() {}
  async stop() {}
  isRunning() { return false }
}
export const SandboxRuntimeConfigSchema = {
  type: 'object',
  properties: {},
  additionalProperties: true,
}
export class SandboxViolationStore {
  constructor(..._args) {}
  record(..._args) {}
  getAll() { return [] }
  clear() {}
}
"""
with open(os.path.join(ROOT, 'index.js'), 'w') as f:
    f.write(index)
print('stub written to', ROOT)
