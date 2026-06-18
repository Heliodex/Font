import json

import psMat

import fontforge

WIDTH_MUL = 42  # why this number in particular? eh, it closest matches the previous version of the font
KERN_DIV = 10

font = fontforge.font()

font.familyname = "Dex Display"
font.fontname = "Dex Display"

print(font)

ZBALERMORNA_BASE = 0xED00

zbalermornaMain = {
    0x89: "denpabu",
    0x8A: "yhy",
    0x8B: "cnimahobu",
    #
    0x80: "py",
    0x81: "ty",
    0x82: "ky",
    0x83: "fy",
    0x84: "ly",
    0x85: "sy",
    0x86: "cy",
    0x87: "my",
    0x88: "xy",
    0x90: "by",
    0x91: "dy",
    0x92: "gy",
    0x93: "vy",
    0x94: "ry",
    0x95: "zy",
    0x96: "jy",
    0x97: "ny",
}

zbalermornaDiacriticsTop = {
    0xA0: "abu",
    0xA1: "ebu",
    0xA2: "ibu",
    0xA3: "obu",
    0xA4: "ubu",
    0xA5: "ybu",
    0xA6: "aibu",
    0xA7: "eibu",
    0xA8: "oibu",
    0xA9: "aubu",
}

zbalermornaDiacriticsBottom = {
    0x8C: "patonga",
    0x8D: "retonga",
    0x8E: "citonga",
    0x8F: "votonga",
    0x98: "bahebu",
    0x9B: "tcenabu",
}

zbalermornaMatch = {
    **zbalermornaMain,
    **zbalermornaDiacriticsTop,
    **zbalermornaDiacriticsBottom,
    #
    # 0x9A: "slakabu",
    0x99: "smajibu",
}


def glyphZbalermorna(glyph: str) -> str:

    og = ord(glyph)
    ogbase = og - ZBALERMORNA_BASE
    if ogbase in zbalermornaMatch:
        return zbalermornaMatch[ogbase]

    raise Exception(f"Unknown Zbalermorna glyph: {glyph} (ord: {og})")


latinMatch = {
    ".": "period",
    ",": "comma",
    "!": "exclam",
    "-": "hyphen",
    "–": "endash",
    "—": "emdash",
    ":": "colon",
    ";": "semicolon",
    "|": "pipe",
}


def glyphFilename(glyph: str) -> str:
    if 0xED80 <= ord(glyph) < 0xEDC0:
        return glyphZbalermorna(glyph)

    if glyph in latinMatch:
        return latinMatch[glyph]

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


glyphs_latin = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.!-–—:;|"
glyphs_zbalermorna = "".join(chr(i + ZBALERMORNA_BASE) for i in zbalermornaMatch.keys())

glyphs = glyphs_latin + glyphs_zbalermorna

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

font.addLookup("kern", "gpos_pair", None, [("kern", [("dflt", ["dflt"])])])

glyphNames = [glyphFilename(glyph) for glyph in glyphs]

font.addKerningClass("kern", "kern-1", glyphNames, glyphNames, offsetsTuple)

### DIACRITICS

# each zbalermornaMain can be combined with each zbalermornaDiacritics

font.addLookup("mk", "gpos_mark2base", None, [("mark", [("dflt", ["dflt"])])])

font.addLookupSubtable("mk", "mk1")

font.addAnchorClass("mk1", "top")
font.addAnchorClass("mk1", "bottom")

for mainChar in zbalermornaMain.values():
    mainGlyph = font[mainChar]
    mainGlyph.addAnchorPoint("top", "base", 0, 0)
    mainGlyph.addAnchorPoint("bottom", "base", 0, 0)

for diacriticChar in zbalermornaDiacriticsTop.values():
    diacriticGlyph = font[diacriticChar]
    diacriticGlyph.glyphclass = "mark"
    diacriticGlyph.addAnchorPoint("top", "mark", 0, 0)

for diacriticChar in zbalermornaDiacriticsBottom.values():
    diacriticGlyph = font[diacriticChar]
    diacriticGlyph.glyphclass = "mark"
    diacriticGlyph.addAnchorPoint("bottom", "mark", 0, 0)


### FINISH

print("generating")
font.generate("test.ttf")
font.generate("test.woff2")
print("generated")
