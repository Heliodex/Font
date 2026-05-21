import fontforge

WIDTH_MUL = 42

font = fontforge.font()

font.familyname = "Dex Display"
font.fontname = "Dex Display"

print(font)


def glyphFilename(glyph: str) -> str:
    if glyph == ".":
        return "period"

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


glyphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.!"

for glyph in glyphs:
    name = glyphFilename(glyph)
    filename = f"../glyphs/{name}.svg"
    file = open(filename, "r")
    width = getWidth(file.readline())

    c = font.createChar(ord(glyph))
    c.importOutlines(filename)

    # set character width
    c.width = width * WIDTH_MUL

# space
c = font.createChar(ord(" "))
c.width = 4 * WIDTH_MUL


font.generate("test.ttf")
