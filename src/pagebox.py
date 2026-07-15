#!/usr/bin/env python3
"""Add left/right margins to a PDF by expanding the page boxes.

Content, annotations, highlights, bookmarks, and metadata are untouched.
"""

import argparse
import pikepdf


def expand_box(box, rotation, left, right):
	"""Return new [x0, y0, x1, y1] with margins added on the *visual* left/right."""
	x0, y0, x1, y1 = (float(v) for v in box)

	if rotation == 0:
		x0 -= left
		x1 += right
	elif rotation == 90:
		y0 -= left
		y1 += right
	elif rotation == 180:
		x1 += left
		x0 -= right
	elif rotation == 270:
		y1 += left
		y0 -= right

	return [x0, y0, x1, y1]


def add_margins(input_path, output_path, left, right):
	with pikepdf.open(input_path) as pdf:
		for page in pdf.pages:
			rotation = page.rotation % 360  # effective rotation, handles inheritance

			# MediaBox always exists (possibly inherited); pikepdf resolves it
			page.MediaBox = expand_box(page.mediabox, rotation, left, right)

			# Expand the other boxes too, if the page defines them
			for key in ("/CropBox", "/BleedBox", "/TrimBox", "/ArtBox"):
				if key in page:
					page[key] = expand_box(page[key], rotation, left, right)

		pdf.save(output_path)


def main():
	parser = argparse.ArgumentParser(description="Add left/right margins to a PDF.")
	parser.add_argument("input", help="input PDF")
	parser.add_argument("output", help="output PDF")
	parser.add_argument(
		"--left",
		type=float,
		default=72.0,
		help="left margin in points (72 pt = 1 inch, default: 72)",
	)
	parser.add_argument(
		"--right", type=float, default=72.0, help="right margin in points (default: 72)"
	)
	args = parser.parse_args()

	add_margins(args.input, args.output, args.left, args.right)
	print(f"Saved {args.output} with margins: left={args.left}pt, right={args.right}pt")


if __name__ == "__main__":
	main()
