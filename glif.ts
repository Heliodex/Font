// Convert to glyph interchange format (GLIF)

import { type SVGCommand, SVGPathData } from "svg-pathdata"

export function getUnicodeHex(name: string) {
	let num: number // if (name === "period
	switch (name) {
		case "period":
			num = 0x002e
			break
		default:
			num = name.codePointAt(0) || 0
	}

	return num.toString(16).toUpperCase().padStart(4, "0")
}

export const transformName = (name: string) => {
	if (name.startsWith("_")) return `.${name.slice(1)}`
	if (name.endsWith("_")) return `${name.slice(0, -1)}.`
}

const indentStart = (str: string, count: number) =>
	str
		.split("\n")
		.map(l => "\t".repeat(count) + l)
		.join("\n")

const round2dp = (num: number) => Math.round(num * 100) / 100

type Point = {
	x: number
	y: number
	t?: "line" | "qcurve"
}

const baseline = 16

function fixCoords({ x, y, t }: Point): Point {
	return { x, y: baseline - y, t }
}

function getPoints(cmds: SVGCommand[]) {
	// const pointstrings: string[] = []

	// for (const { x, y, t } of points)
	// 	pointstrings.push(
	// 		`<point x="${x}" y="${y}" ${t ? `type="${t}" ` : ""}/>`
	// 	)
	const points: Point[] = []

	for (const cmd of cmds)
		switch (cmd.type) {
			case SVGPathData.MOVE_TO:
				points.push({ x: cmd.x, y: cmd.y, t: "line" })
				break
			case SVGPathData.LINE_TO:
				points.push({ x: cmd.x, y: cmd.y, t: "line" })
				break
			case SVGPathData.CURVE_TO:
				points.push({ x: cmd.x1, y: cmd.y1 })
				points.push({ x: cmd.x2, y: cmd.y2 })
				points.push({ x: cmd.x, y: cmd.y, t: "qcurve" })
				break
			default:
				throw new Error(`Unexpected command type ${cmd.type}`)
		}

	const fixedPoints = points.map(fixCoords)

	return fixedPoints.map(
		({ x, y, t }) =>
			`<point x="${round2dp(x * 10)}" y="${round2dp(y * 10)}" ${t ? `type="${t}" ` : ""}/>`
	)
}

export function toGlif(
	name: string,
	width: number,
	unicode: string,
	cmds: SVGCommand[][]
) {
	const contours: string[] = []
	for (const shape of cmds) {
		const lines = getPoints(shape)

		contours.push(`<contour>
${indentStart(lines.join("\n"), 1)}	
</contour>`)
	}

	return `<?xml version="1.0" encoding="UTF-8"?>
<glyph name="${name}" format="2">
	<advance width="${round2dp(width * 10)}" />
	<unicode hex="${unicode}" />
	<outline>
${indentStart(contours.join("\n"), 2)}
	</outline>
</glyph>`
}
