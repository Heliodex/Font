// Convert to glyph interchange format (GLIF)

import type { SVGCommand } from "svg-pathdata"

export const transformName = (name: string) => {
	if (name.startsWith("_")) return `.${name.slice(1)}`
	if (name.endsWith("_")) return `${name.slice(0, -1)}.`
}

function indentStart(str: string) {
	return str
		.split("\n")
		.map(l => `\t${l}`)
		.join("\n")
}

export function toGlif(
	name: string,
	width: number,
	unicode: string,
	cmds: SVGCommand[][]
) {
	const format = `<?xml version="1.0" encoding="UTF-8"?>
<glyph name="${name}" format="2">
	<advance width="${width}" />
	<unicode hex="${unicode}" />
	<outline>
${indentStart(contours)}
	</outline>
</glyph>`
}
