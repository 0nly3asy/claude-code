// scripts/build-bundle.ts
// Usage: bun scripts/build-bundle.ts [--watch] [--minify] [--no-sourcemap]
//
// Production build: bun scripts/build-bundle.ts --minify
// Dev build:        bun scripts/build-bundle.ts
// Watch mode:       bun scripts/build-bundle.ts --watch

import * as esbuild from 'esbuild'
import { resolve, dirname } from 'path'
import { chmodSync, readFileSync, writeFileSync, existsSync } from 'fs'
import { fileURLToPath } from 'url'

// Bun: import.meta.dir — Node 21+: import.meta.dirname — fallback
const __dir: string =
  (import.meta as any).dir ??
  (import.meta as any).dirname ??
  dirname(fileURLToPath(import.meta.url))

const ROOT = resolve(__dir, '..')
const watch = process.argv.includes('--watch')
const minify = process.argv.includes('--minify')
const noSourcemap = process.argv.includes('--no-sourcemap')

// Read version from package.json for MACRO injection
const pkg = JSON.parse(readFileSync(resolve(ROOT, 'package.json'), 'utf-8'))
const version = pkg.version || '0.0.0-dev'

// Convergence fork: redirect any bare import that cannot be resolved to a
// generated stub. The upstream tree imports a number of Anthropic-internal
// packages (@ant/*, the .napi native addons, optional cloud SDKs) that are not
// published to npm and are only reachable via default-off feature flags. Rather
// than listing them by hand, resolve-or-stub: if the package is installed we use
// it, otherwise we emit an inert stub so Node never sees an unresolvable import.
const builtinModules = new Set(
  require('module').builtinModules as unknown as string[],
)
const isBuiltin = (spec: string) =>
  builtinModules.has(spec) || spec.startsWith('node:')

const stubResolverPlugin: esbuild.Plugin = {
  name: 'convergence-stub-resolver',
  setup(build) {
    const fs = require('fs')
    const path = require('path')

    // Precompute the stub directory once.
    const stubRoot = path.resolve(ROOT, 'node_modules', '.convergence-stubs')
    fs.mkdirSync(stubRoot, { recursive: true })

    const ensureStub = (spec: string): string => {
      const pkgName = spec.startsWith('@')
        ? spec.split('/').slice(0, 2).join('/')
        : spec.split('/')[0]
      const pkgDir = path.resolve(stubRoot, pkgName)
      const index = path.resolve(pkgDir, 'index.mjs')
      const pkgJson = path.resolve(pkgDir, 'package.json')
      if (!fs.existsSync(pkgJson)) {
        fs.mkdirSync(pkgDir, { recursive: true })
        fs.writeFileSync(
          pkgJson,
          JSON.stringify(
            {
              name: pkgName + '.convergence-stub',
              version: '0.0.0',
              description:
                'Convergence fork auto-stub for an unresolvable Anthropic-internal/optional package.',
              type: 'module',
              main: './index.mjs',
              exports: { '.': './index.mjs' },
            },
            null,
            2,
          ),
        )
        fs.writeFileSync(
          index,
          [
            '// Convergence fork auto-generated stub for ' + pkgName + '.',
            '// The real package is not installable here and is only reachable',
            '// behind default-off feature flags. Exports are inert.',
            'const handler = { get: () => () => undefined }',
            'export default new Proxy({}, handler)',
            'export const __convergenceStub = true',
          ].join('\n') + '\n',
        )
      }
      return pkgDir
    }

    // Only intercept bare specifiers whose package is NOT installed under
    // node_modules. Installed packages resolve normally through esbuild.
    // Match bare specifiers: unscoped ('foo', 'foo/bar') and scoped ('@ant/x', '@ant/x/y').
    build.onResolve({ filter: /^(?:@[a-z0-9-]+\/)?[a-z0-9-]+/i }, (args) => {
      const spec = args.path
      if (isBuiltin(spec)) return undefined
      if (spec.startsWith('bun:')) return undefined
      const pkgName = spec.startsWith('@')
        ? spec.split('/').slice(0, 2).join('/')
        : spec.split('/')[0]
      const installedDir = path.resolve(ROOT, 'node_modules', pkgName)
      if (fs.existsSync(installedDir)) return undefined // let esbuild resolve it
      ensureStub(spec)
      return {
        path: path.resolve(stubRoot, pkgName, 'index.mjs'),
        external: false,
      }
    })
  },
}

const srcResolverPlugin: esbuild.Plugin = {
  name: 'src-resolver',
  setup(build) {
    build.onResolve({ filter: /^src\// }, (args) => {
      const basePath = resolve(ROOT, args.path)

      // Already exists as-is
      if (existsSync(basePath)) {
        return { path: basePath }
      }

      // Strip .js/.jsx and try TypeScript extensions
      const withoutExt = basePath.replace(/\.(js|jsx)$/, '')
      for (const ext of ['.ts', '.tsx', '.js', '.jsx']) {
        const candidate = withoutExt + ext
        if (existsSync(candidate)) {
          return { path: candidate }
        }
      }

      // Try as directory with index file
      const dirPath = basePath.replace(/\.(js|jsx)$/, '')
      for (const ext of ['.ts', '.tsx', '.js', '.jsx']) {
        const candidate = resolve(dirPath, 'index' + ext)
        if (existsSync(candidate)) {
          return { path: candidate }
        }
      }

      // Let esbuild handle it (will error if truly missing)
      return undefined
    })
  },
}

const buildOptions: esbuild.BuildOptions = {
  entryPoints: [resolve(ROOT, 'src/entrypoints/cli.tsx')],
  bundle: true,
  platform: 'node',
  target: ['node20', 'es2022'],
  format: 'esm',
  outdir: resolve(ROOT, 'dist'),
  outExtension: { '.js': '.mjs' },

  // Single-file output — no code splitting for CLI tools
  splitting: false,

  plugins: [srcResolverPlugin, stubResolverPlugin],

  // Use tsconfig for baseUrl / paths resolution (complements plugin above)
  tsconfig: resolve(ROOT, 'tsconfig.json'),

  // Alias bun:bundle to our runtime shim
  alias: {
    'bun:bundle': resolve(ROOT, 'src/shims/bun-bundle.ts'),
  },

  // Don't bundle node built-ins or problematic native packages
  external: [
    // Node built-ins (with and without node: prefix)
    'fs', 'path', 'os', 'crypto', 'child_process', 'http', 'https',
    'net', 'tls', 'url', 'util', 'stream', 'events', 'buffer',
    'querystring', 'readline', 'zlib', 'assert', 'tty', 'worker_threads',
    'perf_hooks', 'async_hooks', 'dns', 'dgram', 'cluster',
    'string_decoder', 'module', 'vm', 'constants', 'domain',
    'console', 'process', 'v8', 'inspector',
    // CJS packages that call require() at load time; must stay external
    // so Node loads them natively instead of being inlined into the ESM bundle.
    'node-fetch',
    'agentkeepalive',
    'commander',
    '@commander-js/extra-typings',
    'jsonc-parser',
  ],

  // Convergence fork: give the ESM bundle a working require() for inlined CJS deps
  inject: [resolve(ROOT, 'scripts/require-shim.js')],

  jsx: 'automatic',

  // Source maps for production debugging (external .map files)
  sourcemap: noSourcemap ? false : 'external',

  // Minification for production
  minify,

  // Tree shaking (on by default, explicit for clarity)
  treeShaking: true,

  // Define replacements — inline constants at build time
  // MACRO.* — originally inlined by Bun's bundler at compile time
  // process.env.USER_TYPE — eliminates 'ant' (Anthropic-internal) code branches
  define: {
    'MACRO.VERSION': JSON.stringify(version),
    // Convergence fork: getBuildAgeMinutes() reads MACRO.BUILD_TIME. esbuild
    // only substitutes exact `define` matches, so provide it or it throws
    // at runtime on the first real API query.
    'MACRO.BUILD_TIME': 'Date.now()',
    'MACRO.PACKAGE_URL': JSON.stringify('@anthropic-ai/claude-code'),
    'MACRO.ISSUES_EXPLAINER': JSON.stringify(
      'report issues at https://github.com/anthropics/claude-code/issues'
    ),
    'process.env.USER_TYPE': '"external"',
    'process.env.NODE_ENV': minify ? '"production"' : '"development"',
  },

  // Banner: shebang for direct CLI execution
  banner: {
    js: '#!/usr/bin/env node\n',
  },

  // Handle the .js → .ts resolution that the codebase uses
  // Convergence fork: import .md/.txt/.markdown skill docs as plain strings.
  // Bun's bundler handles this natively; esbuild needs an explicit loader.
  loader: {
    '.md': 'text',
    '.markdown': 'text',
    '.txt': 'text',
  },

  resolveExtensions: ['.tsx', '.ts', '.jsx', '.js', '.json'],

  logLevel: 'info',

  // Metafile for bundle analysis
  metafile: true,
}

// Convergence fork: esbuild's CJS shim throws "Dynamic require of X is not
// supported" when a CommonJS dependency inlined into the ESM bundle calls
// require('fs') at load time. Rewrite the throwing branch to fall back to
// createRequire(import.meta.url) instead.
function patchRequireShim(outPath: string): void {
  const code = readFileSync(outPath, 'utf8')
  const marker = `throw Error('Dynamic require of "' + x3 + '" is not supported');`
  if (!code.includes(marker)) {
    return
  }
  // Replace the throwing branch with a createRequire fallback. The marker line
  // is unique in the bundle, so a direct replace is safe.
  const replacement = `const __cr = (await import('node:module')).createRequire(import.meta.url)
    return __cr(x3)`
  writeFileSync(outPath, code.replace(marker, replacement))
  console.log('[convergence] patched require shim for inlined CJS dependencies')
}

async function main() {
  if (watch) {
    const ctx = await esbuild.context(buildOptions)
    await ctx.watch()
    console.log('Watching for changes...')
  } else {
    const startTime = Date.now()
    const result = await esbuild.build(buildOptions)

    if (result.errors.length > 0) {
      console.error('Build failed')
      process.exit(1)
    }

    // Make the output executable

    const outPath = resolve(ROOT, 'dist/cli.mjs')
    try {
      chmodSync(outPath, 0o755)
    } catch {

  patchRequireShim(outPath)
  // Convergence fork: give inlined CJS deps a working require().
      // chmod may fail on some platforms, non-fatal
    }

    const elapsed = Date.now() - startTime

    // Print bundle size info
    if (result.metafile) {
      const text = await esbuild.analyzeMetafile(result.metafile, { verbose: false })
      const outFiles = Object.entries(result.metafile.outputs)
      for (const [file, info] of outFiles) {
        if (file.endsWith('.mjs')) {
          const sizeMB = ((info as { bytes: number }).bytes / 1024 / 1024).toFixed(2)
          console.log(`\n  ${file}: ${sizeMB} MB`)
        }
      }
      console.log(`\nBuild complete in ${elapsed}ms → dist/`)

      // Write metafile for further analysis
      const { writeFileSync } = await import('fs')
      writeFileSync(
        resolve(ROOT, 'dist/meta.json'),
        JSON.stringify(result.metafile),
      )
      console.log('  Metafile written to dist/meta.json')
    }
  }
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
