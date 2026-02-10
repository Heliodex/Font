import { readdir } from "node:fs/promises"
import { Font, type Glyph } from "opentype.js"
import { type SVGCommand, SVGPathData, SVGPathDataParser } from "svg-pathdata"
import { fromXml } from "xast-util-from-xml"

const glyphs: Glyph[] = []
const glyphsPath = "./glyphs"
// const glyphSVGs: string[][] = []

function round2dp(n: number) {
	return Math.round(n * 100) / 100
}

const parser = new SVGPathDataParser().transform(cmd => {
	const ncmd = cmd as { [_: string]: boolean | number }

	for (const k in ncmd)
		if (typeof ncmd[k] === "number")
			// round to 2 decimal places
			ncmd[k] = round2dp(ncmd[k])

	return ncmd as SVGCommand
})

for (const dirent of await readdir(glyphsPath, { withFileTypes: true })) {
	if (!dirent.isFile() || !dirent.name.endsWith(".svg")) continue

	const svg = await Bun.file(`${glyphsPath}/${dirent.name}`).text()
	// parse svg

	const p = fromXml(svg)
	if (p.type !== "root") throw new Error("Expected root node")

	const node = p.children[0]
	if (!node) throw new Error("Expected child node")
	if (node.type !== "element" || node.name !== "svg")
		throw new Error("Expected svg element")

	// wdc
	const {
		attributes: { width, height },
		children,
	} = node

	// filter out text nodes (mostly just newlines)
	const cs = children.filter(c => c.type !== "text") as unknown as {
		attributes: { d: string }
	}[]
	const paths = cs.map(c => c.attributes.d).map(d => parser.parse(d))

	console.log(`${width} x ${height}`)
	console.log(paths)
	console.log()
}

const font = new Font({
	familyName: "Dex Display",
	styleName: "Regular",
	unitsPerEm: 1000,
	ascender: 800,
	descender: -200,
	glyphs,
})

await Bun.write("out.otf", font.toArrayBuffer())
