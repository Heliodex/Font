import { readdir } from "node:fs/promises"
import { type SVGCommand, SVGPathData } from "svg-pathdata"
import { fromXml } from "xast-util-from-xml"
import { getUnicodeHex, toGlif } from "./glif"

const glyphsPath = "./glyphs"

const types = {}

const excludeTypes: number[] = [
	SVGPathData.CLOSE_PATH, // no actual data
]

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
	const { children, attributes } = node
	if (!attributes.width) throw new Error("Expected width attribute")
	const width = +attributes.width

	// filter out text nodes (mostly just newlines)
	const cs = children.filter(c => c.type !== "text") as unknown as {
		attributes: { d: string }
	}[]
	const paths = cs.map(c => c.attributes.d)

	const fontPaths: SVGCommand[][] = []

	for (const p of paths) {
		if (!p) continue // might be ok if it's at the end, but sometimes appears in the middle O_O

		const pd = new SVGPathData(p)
		if (!pd.commands)
			throw new Error(`Expected commands from ${p}, got ${pd.commands}`)

		const cmds = pd
			.round(100)
			.commands.filter(c => !excludeTypes.includes(c.type))

		for (let i = 1; i < cmds.length; i++) {
			const prev = cmds[i - 1]
			if (!prev) continue
			const cmd = cmds[i]
			if (!cmd) continue

			if (
				prev.type !== SVGPathData.LINE_TO &&
				prev.type !== SVGPathData.CURVE_TO &&
				prev.type !== SVGPathData.MOVE_TO
			)
				continue

			if (cmd.type === SVGPathData.HORIZ_LINE_TO)
				cmds[i] = {
					relative: false,
					type: SVGPathData.LINE_TO,
					x: cmd.x,
					y: prev.y,
				}
			else if (cmd.type === SVGPathData.VERT_LINE_TO)
				cmds[i] = {
					relative: false,
					type: SVGPathData.LINE_TO,
					x: prev.x,
					y: cmd.y,
				}
		}
		// .filter(c => c.type === SVGPathData.MOVE_TO)

		fontPaths.push(cmds)
		for (const cmd of cmds) types[cmd.type] = true
	}

	const name = dirent.name.replace(/\.svg$/, "")

	// console.log(name, fontPaths)
	const glif = toGlif(name, width, getUnicodeHex(name), fontPaths)
	// console.log(glif)

	await Bun.write(`./python/main.ufo/glyphs/${name}.glif`, glif)
}

console.log(types)
