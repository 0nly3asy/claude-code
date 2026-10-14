import type { AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS } from '../../services/analytics/index.js'
import { isEnvTruthy } from '../envUtils.js'

export type APIProvider = 'firstParty' | 'bedrock' | 'vertex' | 'foundry' | 'atria'

export function getAPIProvider(): APIProvider {
  return isEnvTruthy(process.env.CLAUDE_CODE_USE_BEDROCK)
    ? 'bedrock'
    : isEnvTruthy(process.env.CLAUDE_CODE_USE_VERTEX)
      ? 'vertex'
      : isEnvTruthy(process.env.CLAUDE_CODE_USE_FOUNDRY)
        ? 'foundry'
        : isAtriaProvider()
          ? 'atria'
          : 'firstParty'
}

export function getAPIProviderForStatsig(): AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS {
  return getAPIProvider() as AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS
}

/**
 * Check if ANTHROPIC_BASE_URL is a first-party Anthropic API URL.
 * Returns true if not set (default API) or points at api.anthropic.com
 * (or api-staging.anthropic.com for ant users).
 */
export function isFirstPartyAnthropicBaseUrl(): boolean {
  const baseUrl = process.env.ANTHROPIC_BASE_URL
  if (!baseUrl) {
    return true
  }
  try {
    const host = new URL(baseUrl).host
    const allowedHosts = ['api.anthropic.com']
    if (process.env.USER_TYPE === 'ant') {
      allowedHosts.push('api-staging.anthropic.com')
    }
    return allowedHosts.includes(host)
  } catch {
    return false
  }
}

/**
 * Atria (Convergence fork) — the Atria Dawn model family served by the
 * Atria ASI API. It is Anthropic Messages-API compatible, so it reuses the
 * first-party client with a different base URL and API key.
 *
 * Activated when ATRIA_API_KEY is present. The base URL defaults to the
 * public Atria endpoint and can be overridden with ATRIA_BASE_URL. Note the
 * SDK appends /v1/messages itself, so the base URL must NOT include a /v1
 * suffix.
 */
export const ATRIA_DEFAULT_BASE_URL = 'https://api.atria-asi.ai'
export const ATRIA_DEFAULT_MODEL = 'Atria-Dawn'

export function getAtriaDefaultModel(): string {
  return process.env.ATRIA_MODEL || ATRIA_DEFAULT_MODEL
}

export function isAtriaProvider(): boolean {
  return !!process.env.ATRIA_API_KEY
}

export function getAtriaBaseUrl(): string {
  return process.env.ATRIA_BASE_URL || ATRIA_DEFAULT_BASE_URL
}
