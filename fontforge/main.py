import fontforge

font = fontforge.font()

print(font)

glyph = font.createMappedChar('A')
glyph.importOutlines("../glyphs/A_.svg")

font.generate("test.ttf")