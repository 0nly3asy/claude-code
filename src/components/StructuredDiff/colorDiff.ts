import {
  ColorDiff,
  ColorFile,
  getSyntaxTheme as nativeGetSyntaxTheme,
  type SyntaxTheme,
} from 'color-diff-napi'
import { isEnvDefinedFalsy } from '../../utils/envUtils.js'

export type ColorModuleUnavailableReason = 'env'

/**
 * Returns a static reason why the color-diff module is unavailable, or null if available.
 * 'env' = disabled via CLAUDE_CODE_SYNTAX_HIGHLIGHT
 *
 * The TS port of color-diff works in all build modes, so the only way to
 * disable it is via the env var.
 */
export function getColorModuleUnavailableReason(): ColorModuleUnavailableReason | null {
  if (isEnvDefinedFalsy(process.env.CLAUDE_CODE_SYNTAX_HIGHLIGHT)) {
    return 'env'
  }
  return null
}

// Convergence fork: the module is not installable here and resolves to the
// auto-stub, whose Proxy get-trap returns a no-op function for EVERY named
// import. That value is truthy and constructable, so a plain truthiness guard
// passes and `new ColorDiff(...).render(...)` throws inside the TUI renderer.
// Duck-type the real class instead: no prototype.render => unavailable, and the
// callers render StructuredDiffFallback (the designed degradation path).
const colorModuleUsable =
  typeof ColorDiff === 'function' &&
  typeof ColorDiff?.prototype?.render === 'function'

export function expectColorDiff(): typeof ColorDiff | null {
  return getColorModuleUnavailableReason() === null && colorModuleUsable
    ? ColorDiff
    : null
}

export function expectColorFile(): typeof ColorFile | null {
  return getColorModuleUnavailableReason() === null && colorModuleUsable
    ? ColorFile
    : null
}

export function getSyntaxTheme(themeName: string): SyntaxTheme | null {
  return getColorModuleUnavailableReason() === null && colorModuleUsable
    ? nativeGetSyntaxTheme(themeName)
    : null
}

