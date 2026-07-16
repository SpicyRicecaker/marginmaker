import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import FloatObject, NameObject, ArrayObject
from .remove_page_margins import remove_trash
from loguru import logger
import pikepdf

MARGIN_SIDE_PT = 500
MARGIN_TOP_AND_BOT_PT = 0


def copy_outline(reader, writer, outline, parent=None):
	last = None
	for item in outline:
		if isinstance(item, list):
			if last is not None:
				copy_outline(reader, writer, item, parent=last)
		else:
			page_num = reader.get_destination_page_number(item)
			last = writer.add_outline_item(item.title, page_num, parent=parent)


def return_transformed(A, tx, ty):
	i = 0
	A_prime = []

	if len(A) == 0:
		return ArrayObject([])
	else:
		if isinstance(A[0], (int, float)):
			for a in A:
				if i % 2 == 0:
					A_prime.append(FloatObject(a + tx))
				else:
					A_prime.append(FloatObject(a + ty))
				i += 1
		else:
			for a in A:
				A_prime.append(return_transformed(a, tx, ty))
	return ArrayObject(A_prime)


def expand_via_scale(input_pdf, output_pdf, mx, my):
	reader = PdfReader(input_pdf)
	writer = PdfWriter()

	for page in reader.pages:
		# get the page width and height
		logger.debug(f"input pdf dimensions {page.mediabox}")
		w, h = (
			float(page.mediabox.width) + mx,
			float(page.mediabox.height) + my,
		)
		# calculate how much we need to transform the page
		tx = mx / 2
		ty = my / 2
		# create a new page and merge all changes into it
		new_page = writer.add_blank_page(w, h)
		new_page.merge_transformed_page(page, Transformation().translate(tx, ty))
		logger.debug(f"output pdf dimensions {new_page.mediabox}")
		if "/Annots" in new_page:
			for annot_ref in new_page["/Annots"]:
				annot = annot_ref.get_object()

				if "/InkList" in annot:
					inklist = annot["/InkList"]
					inklist_key = NameObject("/InkList")
					new_inklist = return_transformed(inklist, tx, ty)
					annot[inklist_key] = new_inklist

				if "/Path" in annot:
					path = annot["/Path"]
					path_key = NameObject("/Path")
					new_path = return_transformed(path, tx, ty)
					annot[path_key] = new_path
	if reader.outline:
		# add metadatga
		copy_outline(reader, writer, reader.outline)

	with open(output_pdf, "wb") as f:
		writer.write(f)


def expand_box(box, rotation, mx, my):
	"""Return new [x0, y0, x1, y1] with margins added on the *visual* left/right."""
	x0, y0, x1, y1 = (float(v) for v in box)
	L = mx / 2
	if rotation == 0:
		x0 -= L
		x1 += L
	elif rotation == 90:
		y0 -= L
		y1 += L
	elif rotation == 180:
		x1 += L
		x0 -= L
	elif rotation == 270:
		y1 += L
		y0 -= L

	return [x0, y0, x1, y1]


def expand_via_mediabox(input_pdf, output_pdf, mx, my):
	with pikepdf.open(input_pdf) as pdf:
		for page in pdf.pages:
			rotation = page.rotation % 360  # effective rotation, handles inheritance

			# MediaBox always exists (possibly inherited); pikepdf resolves it
			page.MediaBox = expand_box(page.mediabox, rotation, mx, my)

			# Expand the other boxes too, if the page defines them
			for key in ("/CropBox", "/BleedBox", "/TrimBox", "/ArtBox"):
				if key in page:
					page[key] = expand_box(page[key], rotation, mx, my)

		pdf.save(output_pdf)
		pdf.close()


def expand(input_pdf, output_pdf, mx=MARGIN_SIDE_PT, my=MARGIN_TOP_AND_BOT_PT):
	expand_via_mediabox(input_pdf, output_pdf, mx, my)


def expand_and_remove_trash(
	input_pdf, output_pdf, mx=MARGIN_SIDE_PT, my=MARGIN_TOP_AND_BOT_PT
):
	tmp_pdf = "tmp.pdf"
	expand(input_pdf, tmp_pdf, mx, my)
	remove_trash(tmp_pdf, output_pdf, mx, my)
	logger.debug("finished conversion")


def main():
	args = [a for a in sys.argv[1:]]

	if not args:
		print("Usage: script.py input.pdf [output.pdf]")
		sys.exit(1)

	input_pdf = args[0]
	has_output = len(args) > 1 and not args[1].replace(".", "", 1).isdigit()
	output_pdf = args[1] if has_output else f"{'scaled'}_{Path(input_pdf).name}"

	expand_and_remove_trash(input_pdf, output_pdf)


if __name__ == "__main__":
	main()
