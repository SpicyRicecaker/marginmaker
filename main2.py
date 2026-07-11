#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pypdf"]
# ///
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation

MARGIN_SIDE_PT = 500

def copy_outline(reader, writer, outline, parent=None):
    last = None
    for item in outline:
        if isinstance(item, list):
            if last is not None:
                copy_outline(reader, writer, item, parent=last)
        else:
            page_num = reader.get_destination_page_number(item)
            last = writer.add_outline_item(item.title, page_num, parent=parent)


def convert(input_pdf, output_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        # get the page width and height
        w, h = float(page.mediabox.width) + MARGIN_SIDE_PT, float(page.mediabox.height)
        # calculate how much we need to transform the page
        tx = MARGIN_SIDE_PT / 2
        ty = 0
        # create a new page and merge all changes into it
        new_page = writer.add_blank_page(w, h)
        new_page.merge_transformed_page(
            page, Transformation().translate(tx, ty)
        )

    if reader.outline:
        # add metadatga
        copy_outline(reader, writer, reader.outline)

    with open(output_pdf, "wb") as f:
        writer.write(f)


def main():
    args = [a for a in sys.argv[1:]]

    if not args:
        print(
            "Usage: script.py input.pdf [output.pdf]"
        )
        sys.exit(1)

    input_pdf = args[0]
    has_output = len(args) > 1 and not args[1].replace(".", "", 1).isdigit()
    output_pdf = (
        args[1]
        if has_output
        else f"{'scaled'}_{Path(input_pdf).name}"
    )

    convert(input_pdf, output_pdf)


if __name__ == "__main__":
    main()