import json

import psMat

import fontforge

WIDTH_MUL = 42  # why this number in particular? eh, it closest matches the previous version of the font
KERN_DIV = 10

font = fontforge.font()

font.familyname = "Dex Display"
font.fontname = "Dex Display"

print(font)


def glyphFilename(glyph: str) -> str:
    if glyph == ".":
        return "period"
    if glyph == ",":
        return "comma"
    if glyph == "!":
        return "exclam"
    if glyph == "-":
        return "hyphen"
    if glyph == "–":
        return "endash"
    if glyph == "—":
        return "emdash"
    if glyph == ":":
        return "colon"
    if glyph == ";":
        return "semicolon"
    if glyph == "|":
        return "pipe"

    isUppercase = glyph.isupper()
    if isUppercase:
        return f"{glyph}_"
    return glyph


def getWidth(line: str) -> int:
    # it will be <svg width="{width}" ...
    # hacky but cba importing xml and the glyphs are pretty samey in format
    p1 = 'width="'
    start = line.find(p1) + len(p1)
    end = line.find('"', start)
    return int(line[start:end])


glyphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.!-–—:;|"

for glyph in glyphs:
    filename = f"../glyphs/{glyphFilename(glyph)}.svg"
    file = open(filename, "r")
    width = getWidth(file.readline())

    c = font.createChar(ord(glyph))
    c.glyphname = glyphFilename(glyph)
    c.importOutlines(filename)

    # set character width
    c.width = width * WIDTH_MUL

    # move glyph down a bit to make it look better
    c.transform(psMat.translate(0, -3.5 * WIDTH_MUL))

# space
c = font.createChar(ord(" "))
c.width = 5 * WIDTH_MUL

### KERNING

offsets = [0] * len(glyphs) ** 2

kernpairs = json.load(open("./kerning.json", "r"))


def getKernpair(i1: int, i2: int) -> int:
    g1 = glyphs[i1]
    g2 = glyphs[i2]

    if g1 not in kernpairs or g2 not in kernpairs[g1]:
        return 0

    return int(-kernpairs[g1][g2] * WIDTH_MUL / KERN_DIV)


for i1 in range(len(glyphs)):
    for i2 in range(len(glyphs)):
        offsets[i1 * len(glyphs) + i2] = getKernpair(i1, i2)

offsetsTuple = tuple(offsets)

font.addLookup("kern", "gpos_pair", None, [("kern", [("latn", ["dflt"])])])

glyphNames = [glyphFilename(glyph) for glyph in glyphs]

font.addKerningClass(
    "kern", "kern-1", tuple(glyphNames), tuple(glyphNames), tuple(offsetsTuple)
)

print("generating")
font.generate("test.ttf")
font.generate("test.woff2")
print("generated")
