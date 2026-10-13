// Convergence fork: injected at the top of the bundle so CommonJS dependencies
// inlined into this ESM output get a working require(). Pure JS (no TS syntax)
// so esbuild parses it without a loader.
import { createRequire as __cr } from 'node:module'
var __r = __cr(import.meta.url)
if (typeof globalThis.require === 'undefined') {
  globalThis.require = __r
}
