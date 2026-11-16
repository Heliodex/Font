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

# Diphthongs are typed as two separate vowel diacritics, but written as a single combined diacritic. Map each combination to the glyph that should replace it.
zbalermornaDiphthongs = {
    "aibu": ("abu", "ibu"),
    "eibu": ("ebu", "ibu"),
    "oibu": ("obu", "ibu"),
    "aubu": ("abu", "ubu"),
}

# Multiple stress dots are drawn as one of the combined dynamics glyphs.
zbalermornaBahebuLigatures = {
    "bahebu_bahebu_bahebu": ("bahebu", "bahebu", "bahebu"),
    "bahebu_bahebu": ("bahebu", "bahebu"),
}

# Below-base marks use different horizontal offsets from the vowel diacritics.
# These keep the marks clear of the descenders on these letters.
zbalermornaBottomOffsets = {
    "by": 2,
    "dy": 2,
    "gy": 2,
    "zy": 0,
    "jy": 0,
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
glyphs_zbalermorna = "".join(chr(i + ZBALERMORNA_BASE) for i in zbalermornaMatch)

glyphs = glyphs_latin + glyphs_zbalermorna

for glyph in glyphs:
    filename = f"../glyphs/{glyphFilename(glyph)}.svg"
    with open(filename, "r") as file:
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

### SYMBOLS

# Make the silence line fill its advance so consecutive lines join up.
smajibu = font["smajibu"]
smajibuWidth = smajibu.width
smajibu.transform(psMat.scale(smajibuWidth / smajibu.boundingBox()[2], 1))
smajibu.width = smajibuWidth

# The stress dot gains combined two- and three-dot forms.
bahebuDotSeparation = 1.5 * WIDTH_MUL
bahebuDotDrop = 2.5 * WIDTH_MUL
bahebuLigaturePositions = {
    "bahebu_bahebu": ((-bahebuDotSeparation, 0), (bahebuDotSeparation, 0)),
    "bahebu_bahebu_bahebu": (
        (-bahebuDotSeparation, 0),
        (bahebuDotSeparation, 0),
        (0, -bahebuDotDrop),
    ),
}
for name, positions in bahebuLigaturePositions.items():
    combined = font.createChar(-1, name)
    combined.width = font["bahebu"].width
    for dx, dy in positions:
        combined.addReference("bahebu", (1, 0, 0, 1, dx, dy))

# The stretch underline spans a full cell. It stays at underline height and
# leaves a gap where a descender would cross it.
tcenabu = font["tcenabu"]
tcenabuBarWidth = 10 * WIDTH_MUL
tcenabu.transform(psMat.scale(tcenabuBarWidth / tcenabu.boundingBox()[2], 1))
tcenabu.width = tcenabuBarWidth
tcenabu.transform(psMat.translate(0, -0.5 * WIDTH_MUL))


def createTcenabuVariant(
    name: str, segments: list[tuple[float, float]], width: float
) -> None:
    variant = font.createChar(-1, name)
    variant.width = width

    for start, end in segments:
        variant.addReference(
            "tcenabu",
            ((end - start) / tcenabuBarWidth, 0, 0, 1, start, 0),
        )


# Narrow letters need narrower underlines so they still meet the next one.
for name, units in {"tcenabu.narrow": 4, "tcenabu.mid": 9}.items():
    createTcenabuVariant(name, [(0, units * WIDTH_MUL)], units * WIDTH_MUL)

# Skip over the descenders on the right- and left-sided letters.
rightDescenderGap = (5.25 * WIDTH_MUL, 8.75 * WIDTH_MUL)
leftDescenderGapEnd = 2.75 * WIDTH_MUL
createTcenabuVariant(
    "tcenabu.skipRight",
    [(0, rightDescenderGap[0]), (rightDescenderGap[1], tcenabuBarWidth)],
    tcenabuBarWidth,
)
createTcenabuVariant(
    "tcenabu.skipLeft",
    [(leftDescenderGapEnd, tcenabuBarWidth)],
    tcenabuBarWidth,
)

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
font.addAnchorClass("mk1", "extension")

diacriticpos = json.load(open("./diacritics.json", "r"))


def getDiacriticOffset(d: str) -> int:
    if d not in diacriticpos:
        return 0

    return int(diacriticpos[d] * WIDTH_MUL)


def getBottomDiacriticOffset(d: str) -> int:
    if d in zbalermornaBottomOffsets:
        return int(zbalermornaBottomOffsets[d] * WIDTH_MUL)

    return getDiacriticOffset(d)


OFFSET = 2 * WIDTH_MUL
BOTTOM_DROP = 0.5 * WIDTH_MUL

for mc in zbalermornaMain.values():
    mg = font[mc]
    wTop = (mg.width - OFFSET) / 2 - getDiacriticOffset(mc)
    wBottom = (mg.width - OFFSET) / 2 - getBottomDiacriticOffset(mc)

    mg.addAnchorPoint("top", "base", wTop, 0)
    mg.addAnchorPoint("bottom", "base", wBottom, -BOTTOM_DROP)
    mg.addAnchorPoint("extension", "base", 0, 0)

for dc in zbalermornaDiacriticsTop.values():
    dg = font[dc]
    w = (dg.width - OFFSET) / 2 - getDiacriticOffset(dc)

    dg.glyphclass = "mark"
    dg.addAnchorPoint("top", "mark", w, 0)

for dc in [*zbalermornaDiacriticsBottom.values(), *zbalermornaBahebuLigatures]:
    if dc == "tcenabu":
        continue

    dg = font[dc]
    w = (dg.width - OFFSET) / 2 - getDiacriticOffset(dc)

    dg.glyphclass = "mark"
    dg.addAnchorPoint("bottom", "mark", w, 0)

for name in [
    "tcenabu",
    "tcenabu.narrow",
    "tcenabu.mid",
    "tcenabu.skipRight",
    "tcenabu.skipLeft",
]:
    tcenabuVariant = font[name]
    tcenabuVariant.glyphclass = "mark"
    tcenabuVariant.addAnchorPoint("extension", "mark", 0, 0)

### LIGATURES

# Replace a pair of stacked vowel diacritics with the combined diphthong glyph. ccmp is always applied for combining marks; liga is included too so that the substitution also happens in shapers which only apply standard ligatures.
font.addLookup(
    "diphthongs",
    "gsub_ligature",
    None,
    (("ccmp", (("dflt", ("dflt")),)), ("liga", (("dflt", ("dflt")),))),
)
font.addLookupSubtable("diphthongs", "diphthongs1")

for ligature, components in zbalermornaDiphthongs.items():
    font[ligature].addPosSub("diphthongs1", components)

# Combine consecutive stress dots into the two- and three-dot glyphs. The
# three-dot ligature comes first so that it wins over the two-dot one.
font.addLookup(
    "bahebuLigatures",
    "gsub_ligature",
    None,
    (("ccmp", (("dflt", ("dflt")),)), ("liga", (("dflt", ("dflt")),))),
)
font.addLookupSubtable("bahebuLigatures", "bahebuLigatures1")

for ligature, components in zbalermornaBahebuLigatures.items():
    font[ligature].addPosSub("bahebuLigatures1", components)

# Pick an underline width that matches the letter it follows.
font.addLookup("tcenabuNarrow", "gsub_single", None, ())
font.addLookupSubtable("tcenabuNarrow", "tcenabuNarrow1")
font["tcenabu"].addPosSub("tcenabuNarrow1", "tcenabu.narrow")

font.addLookup("tcenabuMid", "gsub_single", None, ())
font.addLookupSubtable("tcenabuMid", "tcenabuMid1")
font["tcenabu"].addPosSub("tcenabuMid1", "tcenabu.mid")

font.addLookup("tcenabuSkipRight", "gsub_single", None, ())
font.addLookupSubtable("tcenabuSkipRight", "tcenabuSkipRight1")
font["tcenabu"].addPosSub("tcenabuSkipRight1", "tcenabu.skipRight")

font.addLookup("tcenabuSkipLeft", "gsub_single", None, ())
font.addLookupSubtable("tcenabuSkipLeft", "tcenabuSkipLeft1")
font["tcenabu"].addPosSub("tcenabuSkipLeft1", "tcenabu.skipLeft")

font.addLookup(
    "tcenabuContext",
    "gsub_contextchain",
    None,
    (("ccmp", (("dflt", ("dflt")),)), ("liga", (("dflt", ("dflt")),))),
)

vowels = " ".join(zbalermornaDiacriticsTop.values())
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxNarrow1",
    "coverage",
    f"[denpabu yhy] [{vowels}] | [tcenabu] @<tcenabuNarrow>",
)
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxNarrow2",
    "coverage",
    "[denpabu yhy] | [tcenabu] @<tcenabuNarrow>",
)
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxMid1",
    "coverage",
    f"[ly ry cnimahobu] [{vowels}] | [tcenabu] @<tcenabuMid>",
)
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxMid2",
    "coverage",
    "[ly ry cnimahobu] | [tcenabu] @<tcenabuMid>",
)
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxSkipRight1",
    "coverage",
    f"[by dy gy] [{vowels}] | [tcenabu] @<tcenabuSkipRight>",
)
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxSkipRight2",
    "coverage",
    "[by dy gy] | [tcenabu] @<tcenabuSkipRight>",
)
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxSkipLeft1",
    "coverage",
    f"[zy jy] [{vowels}] | [tcenabu] @<tcenabuSkipLeft>",
)
font.addContextualSubtable(
    "tcenabuContext",
    "tcenabuCtxSkipLeft2",
    "coverage",
    "[zy jy] | [tcenabu] @<tcenabuSkipLeft>",
)


### FINISH

print("generating")
font.generate("test.ttf")
font.generate("test.woff2")
print("generated")
