#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pypdf"]
# ///
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import FloatObject, NameObject, ArrayObject
from tkinter import Entry

MARGIN_SIDE_PT = 500
MARGIN_TOP_AND_BOT_PT = 0

global dumpfile
dumpfile = "dumpfile.txt"


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


def dump(path, p, metadata):
	with open(path, "a") as f:
		f.write(f"--------[{metadata}]------------\n")
		f.write("mediabox\n")
		f.write(f"{str(p.mediabox)}\n")
		for key in ("/CropBox", "/BleedBox", "/TrimBox", "/ArtBox"):
			if key in p:
				f.write(f"{key}\n")
				f.write(f"{str(p[key])}\n")

		f.close()


def site1_old(p):
	global dumpfile
	dump(dumpfile, p, "old file")
	pass


def site2_blank(p):
	global dumpfile
	dump(dumpfile, p, "blank file")
	pass


def site3_new(p):
	global dumpfile
	dump(dumpfile, p, "new file")
	pass


def convert(input_pdf, output_pdf):
	reader = PdfReader(input_pdf)
	writer = PdfWriter()

	for page in reader.pages:
		site1_old(page)
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
		site2_blank(new_page)
		new_page.merge_transformed_page(page, Transformation().translate(tx, ty))
		new_page.MediaBox = [500, 0, 1151.969, 824.882]
		site3_new(new_page)
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
	input_pdf = "testpdfs/singlepage.pdf"
	output_pdf = "singlepageconv.pdf"
	global dumpfile
	with open(dumpfile, "w") as f:
		f.write("")
		f.close()
	convert(input_pdf, output_pdf)


if __name__ == "__main__":
	main()

	Entry()
