import json

import fontforge

WIDTH_MUL = 40
KERN_DIV = 10

font = fontforge.font()

font.familyname = "Dex Display"
font.fontname = "Dex Display"

print(font)


def glyphFilename(glyph: str) -> str:
    if glyph == ".":
        return "period"

    isUppercase = glyph.isupper()
    if isUppercase and filename:
        return f"{glyph}_"
    return glyph


def getWidth(line: str) -> int:
    # it will be <svg width="{width}" ...
    # hacky but cba importing xml and the glyphs are pretty samey in format
    p1 = 'width="'
    start = line.find(p1) + len(p1)
    end = line.find('"', start)
    return int(line[start:end])


kernpairs = json.load(open("./kerning.json", "r"))

glyphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.!"

for glyph in glyphs:
    filename = f"../glyphs/{glyphFilename(glyph)}.svg"
    file = open(filename, "r")
    width = getWidth(file.readline())

    c = font.createChar(ord(glyph))
    c.importOutlines(filename)

    # set character width
    c.width = width * WIDTH_MUL

# space
c = font.createChar(ord(" "))
c.width = 5 * WIDTH_MUL

# add kerning time
glyphsList = list(glyphs)

offsets = [0] * len(glyphsList) ** 2


def getKernpair(i1: int, i2: int) -> int:
    g1 = glyphsList[i1]
    g2 = glyphsList[i2]

    if g1 not in kernpairs or g2 not in kernpairs[g1]:
        return 0
    if g1 == "W":
        print(f"kerning for {g1} and {g2}")

    return int(-kernpairs[g1][g2] * WIDTH_MUL / KERN_DIV)


for i1 in range(len(glyphs)):
    for i2 in range(len(glyphs)):
        offsets[i1 * len(glyphs) + i2] = getKernpair(i1, i2)

offsetsTuple = tuple(offsets)

font.addLookup("kern", "gpos_pair", None, [("kern", [("latn", ["dflt"])])])
font.addKerningClass(
    "kern", "kern-1", tuple(glyphsList), tuple(glyphsList), tuple(offsetsTuple)
)

print("generating")
font.generate("test.ttf")
print("generated")
