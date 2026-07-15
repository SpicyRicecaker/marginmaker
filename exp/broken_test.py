from pathlib import Path
from collections import defaultdict
from pypdf import PdfReader


def transform_point(matrix, x, y):
	"""
	Apply a PDF affine matrix [a, b, c, d, e, f] to a point.
	"""
	a, b, c, d, e, f = matrix
	return (
		a * x + c * y + e,
		b * x + d * y + f,
	)


def multiply_matrices(left, right):
	"""
	Return left * right for PDF affine matrices.

	The resulting matrix applies 'right' first, then 'left'.
	"""
	a1, b1, c1, d1, e1, f1 = left
	a2, b2, c2, d2, e2, f2 = right

	return (
		a1 * a2 + c1 * b2,
		b1 * a2 + d1 * b2,
		a1 * c2 + c1 * d2,
		b1 * c2 + d1 * d2,
		a1 * e2 + c1 * f2 + e1,
		b1 * e2 + d1 * f2 + f1,
	)


def estimate_text_width(text, font_size):
	"""
	Estimate the width of a text fragment.

	This is intentionally approximate. Exact character widths require
	interpreting the PDF font encoding and metrics.
	"""
	width_units = 0.0

	for character in text:
		if character.isspace():
			width_units += 0.25
		elif character in "ilI.,'`!:;|":
			width_units += 0.25
		elif character in "mwMW@#%&":
			width_units += 0.85
		elif character in "fjrt()[]{}":
			width_units += 0.35
		else:
			width_units += 0.50

	return width_units * font_size


def transformed_bbox(matrix, width, bottom, top):
	"""
	Return an axis-aligned bbox after transforming a local rectangle.

	The local rectangle is:
	    left   = 0
	    right  = width
	    bottom = bottom
	    top    = top
	"""
	corners = [
		transform_point(matrix, 0, bottom),
		transform_point(matrix, width, bottom),
		transform_point(matrix, 0, top),
		transform_point(matrix, width, top),
	]

	xs = [point[0] for point in corners]
	ys = [point[1] for point in corners]

	left = min(xs)
	right = max(xs)
	bottom = min(ys)
	top = max(ys)

	return {
		"x": left,
		"y": bottom,
		"width": right - left,
		"height": top - bottom,
	}


def extract_text_lines(page, line_tolerance=None):
	"""
	Extract approximate bounding boxes for lines of text on one page.

	Returns dictionaries of the form:

	    {
	        "text": "...",
	        "x": ...,
	        "y": ...,
	        "width": ...,
	        "height": ...
	    }

	Coordinates are in PDF page coordinates, with the origin at the
	bottom-left.
	"""
	fragments = []

	def visitor_text(text, cm, tm, font_dict, font_size):
		if not text or not text.strip():
			return

		if font_size is None or font_size <= 0:
			return

		# The text matrix describes the text's local placement.
		# The current transformation matrix places it in page space.
		effective_matrix = multiply_matrices(cm, tm)

		width = estimate_text_width(text, float(font_size))

		# Approximate font extents around the baseline.
		#
		# A common rough approximation is:
		#   descender: 20% of font size below baseline
		#   ascender: 80% of font size above baseline
		#
		# This is not the exact visible glyph boundary.
		local_bottom = -0.20 * float(font_size)
		local_top = 0.80 * float(font_size)

		bbox = transformed_bbox(
			effective_matrix,
			width,
			local_bottom,
			local_top,
		)

		# Transform the local baseline origin so that fragments can be
		# grouped into lines.
		baseline_x, baseline_y = transform_point(
			effective_matrix,
			0,
			0,
		)

		bbox["text"] = text
		bbox["baseline_x"] = baseline_x
		bbox["baseline_y"] = baseline_y
		bbox["font_size"] = float(font_size)

		fragments.append(bbox)

	page.extract_text(visitor_text=visitor_text)

	if not fragments:
		return []

	if line_tolerance is None:
		line_tolerance = 0.35 * max(fragment["font_size"] for fragment in fragments)

	# Sort approximately top-to-bottom, then left-to-right.
	fragments.sort(
		key=lambda fragment: (
			-fragment["baseline_y"],
			fragment["baseline_x"],
		)
	)

	lines = []

	for fragment in fragments:
		matching_line = None

		for line in lines:
			if abs(fragment["baseline_y"] - line["baseline_y"]) <= line_tolerance:
				matching_line = line
				break

		if matching_line is None:
			lines.append(
				{
					"fragments": [fragment],
					"baseline_y": fragment["baseline_y"],
				}
			)
		else:
			matching_line["fragments"].append(fragment)

	result = []

	for line in lines:
		line_fragments = sorted(
			line["fragments"],
			key=lambda fragment: fragment["baseline_x"],
		)

		left = min(fragment["x"] for fragment in line_fragments)
		bottom = min(fragment["y"] for fragment in line_fragments)

		right = max(fragment["x"] + fragment["width"] for fragment in line_fragments)

		top = max(fragment["y"] + fragment["height"] for fragment in line_fragments)

		text = "".join(fragment["text"] for fragment in line_fragments).strip()

		if not text:
			continue

		result.append(
			{
				"text": text,
				"x": left,
				"y": bottom,
				"width": right - left,
				"height": top - bottom,
			}
		)

	# Final top-to-bottom ordering.
	result.sort(
		key=lambda line: (
			-(line["y"] + line["height"]),
			line["x"],
		)
	)

	return result


reader = PdfReader("input.pdf")

for page_number, page in enumerate(reader.pages, start=1):
	lines = extract_text_lines(page)

	print(f"Page {page_number}")

	for line in lines:
		print(
			{
				"text": line["text"],
				"bbox": (
					line["x"],
					line["y"],
					line["width"],
					line["height"],
				),
			}
		)
