import { readdir } from "node:fs/promises"
import { type SVGCommand, SVGPathData, SVGPathDataParser } from "svg-pathdata"
import { fromXml } from "xast-util-from-xml"
import { Font, Glyph, Path } from "./opentype.js/src/opentype.mjs"

const glyphs: Glyph[] = []
const glyphsPath = "./glyphs"

function round2dp(n: number) {
	return Math.round(n * 100) / 100
}

function roundCmd(cmd: SVGCommand): SVGCommand {
	const ncmd = cmd as { [_: string]: boolean | number }

	for (const k in ncmd)
		if (typeof ncmd[k] === "number")
			// round to 2 decimal places
			ncmd[k] = round2dp(ncmd[k])

	return ncmd as SVGCommand
}

for (const dirent of await readdir(glyphsPath, { withFileTypes: true })) {
	if (!dirent.isFile() || !dirent.name.endsWith(".svg")) continue

	const svg = await Bun.file(`${glyphsPath}/${dirent.name}`).text()
	// parse svg

	const parsed = fromXml(svg)
	if (parsed.type !== "root") throw new Error("Expected root node")

	const node = parsed.children[0]
	if (!node) throw new Error("Expected child node")
	if (node.type !== "element" || node.name !== "svg")
		throw new Error("Expected svg element")

	// wdc
	const {
		attributes: { width },
		children,
	} = node

	// filter out text nodes (mostly just newlines)
	const cs = children.filter(c => c.type !== "text") as unknown as {
		attributes: { d: string }
	}[]
	const paths = cs.map(c => c.attributes.d)

	// console.log(`${width} x ${height}`)
	// console.log(paths)
	// console.log()

	const fontPaths = []

	for (const p of paths) {
		const np = new SVGPathData(p).transform(roundCmd).encode()
		// console.log("rounded path\n", p, "\n", np)

		fontPaths.push(Path.fromSVG(np, {}))
	}

	const name = dirent.name.replace(/\.svg$/, "")

	const advanceWidth = width ? +width : 0

	const gl = new Glyph({
		advanceWidth,
		name,
		path: fontPaths[0],
	})

	glyphs.push(gl)
}

const notdefGlyph = new Glyph({
	name: ".notdef",
	advanceWidth: 10,
	path: new Path(),
})

const font = new Font({
	familyName: "Dex Display",
	styleName: "Regular",
	unitsPerEm: 140,
	ascender: 50,
	descender: -40,
	glyphs: [notdefGlyph, ...glyphs],
})

await Bun.write("out.otf", font.toArrayBuffer())
