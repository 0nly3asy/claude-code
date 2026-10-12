import sys
p = 'src/services/api/client.ts'
src = open(p, encoding='utf-8').read()

if "ATRIA_PROVIDER_ID" in src or 'getAtriaBaseUrl' in src:
    print('ALREADY PATCHED'); sys.exit(0)

# 1) import the atria helpers
old_import = """import {
  getAPIProvider,
  isFirstPartyAnthropicBaseUrl,
} from 'src/utils/model/providers.js'"""
new_import = """import {
  getAPIProvider,
  getAtriaBaseUrl,
  isFirstPartyAnthropicBaseUrl,
  isAtriaProvider,
} from 'src/utils/model/providers.js'"""
assert old_import in src, 'import anchor not found'
src = src.replace(old_import, new_import, 1)

# 2) insert the atria branch right after the bedrock early return
anchor = """    return new AnthropicBedrock(bedrockArgs) as unknown as Anthropic
  }
"""
assert anchor in src, 'bedrock anchor not found'
atria_block = """    return new AnthropicBedrock(bedrockArgs) as unknown as Anthropic
  }

  // Atria (Convergence fork): Anthropic Messages-API compatible provider.
  // When ATRIA_API_KEY is present we talk to the Atria ASI endpoint with the
  // Atria key instead of an Anthropic key. The base URL must NOT include a
  // trailing /v1 because the SDK appends /v1/messages itself.
  if (isAtriaProvider()) {
    logForDebugging(
      `[API:request] Using Atria provider, baseUrl: ${getAtriaBaseUrl()}, model: ${model ?? '(unset)'}`,
    )
    const atriaArgs: ConstructorParameters<typeof Anthropic>[0] = {
      apiKey: process.env.ATRIA_API_KEY,
      baseURL: getAtriaBaseUrl(),
      ...ARGS,
      ...(isDebugToStdErr() && { logger: createStderrLogger() }),
    }
    return new Anthropic(atriaArgs)
  }
"""
src = src.replace(anchor, atria_block, 1)
open(p, 'w', encoding='utf-8').write(src)
print('PATCHED client.ts with Atria provider branch')
