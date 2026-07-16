#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pypdf"]
# ///
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import FloatObject, NameObject, ArrayObject
from tkinter import Entry
from remove_page_margins import cut

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


def convert(input_pdf, output_pdf):
	reader = PdfReader(input_pdf)
	writer = PdfWriter()

	for page in reader.pages:
		# get the page width and height
		w, h = (
			float(page.mediabox.width) + MARGIN_SIDE_PT,
			float(page.mediabox.height) + MARGIN_TOP_AND_BOT_PT,
		)
		# calculate how much we need to transform the page
		tx = MARGIN_SIDE_PT / 2
		ty = MARGIN_TOP_AND_BOT_PT / 2
		# create a new page and merge all changes into it
		new_page = writer.add_blank_page(w, h)
		new_page.merge_transformed_page(page, Transformation().translate(tx, ty))
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


def main():
	args = [a for a in sys.argv[1:]]

	if not args:
		print("Usage: script.py input.pdf [output.pdf]")
		sys.exit(1)

	input_pdf = args[0]
	has_output = len(args) > 1 and not args[1].replace(".", "", 1).isdigit()
	output_pdf = args[1] if has_output else f"{'scaled'}_{Path(input_pdf).name}"

	tmp_pdf = "tmp.pdf"
	convert(input_pdf, tmp_pdf)
	cut(tmp_pdf, output_pdf, mx=MARGIN_SIDE_PT, my=MARGIN_TOP_AND_BOT_PT)


if __name__ == "__main__":
	main()
