import sys
p = 'src/utils/model/providers.ts'
src = open(p, encoding='utf-8').read()

if 'export function getAtriaDefaultModel' in src:
    print('ALREADY PATCHED'); sys.exit(0)

anchor = "export function isAtriaProvider(): boolean {"
if anchor not in src:
    print('ANCHOR NOT FOUND'); sys.exit(1)

addition = """export function getAtriaDefaultModel(): string {
  return process.env.ATRIA_MODEL || ATRIA_DEFAULT_MODEL
}

"""
src = src.replace(anchor, addition + anchor, 1)
open(p, 'w', encoding='utf-8').write(src)
print('PATCHED providers.ts with getAtriaDefaultModel')
