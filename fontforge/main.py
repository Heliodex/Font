import fontforge

font = fontforge.font()

print(font)


def glyphName(glyph: str) -> str:
    if glyph == ".":
        return "period"

    isUppercase = glyph.isupper()
    if isUppercase:
        return f"{glyph}_"
    return glyph


glyphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.!"

for glyph in glyphs:
    name = glyphName(glyph)
    print(f"Adding glyph: {glyph}, name: {name}")

font.generate("test.ttf")
