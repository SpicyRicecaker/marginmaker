#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pypdf"]
# ///
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import DecodedStreamObject, ArrayObject, NameObject

A4 = (595, 842)
A3_LANDSCAPE = (1190, 842)

LINE_SPACING_MM = 8
LINE_COLOR = (0.7, 0.8, 1.0)
LINE_WIDTH = 0.5
MARGIN_TOP_MM = 0
MARGIN_BOTTOM_MM = 0
MARGIN_SIDE_MM = 10


def mm_to_pt(mm):
    return mm * 72 / 25.4


def build_line_bytes(x_start, x_end, page_h):
    spacing = mm_to_pt(LINE_SPACING_MM)
    margin_top = mm_to_pt(MARGIN_TOP_MM)
    margin_bottom = mm_to_pt(MARGIN_BOTTOM_MM)
    r, g, b = LINE_COLOR

    lines = [
        f"{r:.3f} {g:.3f} {b:.3f} RG",
        f"{LINE_WIDTH} w",
    ]
    y = page_h - margin_top
    while y >= margin_bottom:
        lines.append(f"{x_start:.2f} {y:.2f} m {x_end:.2f} {y:.2f} l S")
        y -= spacing

    return "\n".join(lines).encode()


def copy_outline(reader, writer, outline, parent=None):
    last = None
    for item in outline:
        if isinstance(item, list):
            if last is not None:
                copy_outline(reader, writer, item, parent=last)
        else:
            page_num = reader.get_destination_page_number(item)
            last = writer.add_outline_item(item.title, page_num, parent=parent)


def convert(input_pdf, output_pdf, margin_mm=40, horizontal=False, lines=True):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    if horizontal:
        page_w, page_h = A3_LANDSCAPE
        x_start = mm_to_pt(MARGIN_SIDE_MM) + A4[0]
        x_end = page_w - mm_to_pt(MARGIN_SIDE_MM)

        for page in reader.pages:
            new_page = writer.add_blank_page(page_w, page_h)

            if lines:
                stream = DecodedStreamObject()
                stream.set_data(build_line_bytes(x_start, x_end, page_h))
                stream_ref = writer._add_object(stream)
                new_page[NameObject("/Contents")] = ArrayObject([stream_ref])

            new_page.merge_transformed_page(page, Transformation())

    else:
        page_w, page_h = A4
        margin = mm_to_pt(margin_mm)
        target_w = page_w - 2 * margin
        target_h = page_h - 2 * margin
        for page in reader.pages:
            w, h = float(page.mediabox.width), float(page.mediabox.height)
            scale = min(target_w / w, target_h / h)
            tx = (page_w - w * scale) / 2
            ty = (page_h - h * scale) / 2
            new_page = writer.add_blank_page(page_w, page_h)
            new_page.merge_transformed_page(
                page, Transformation().scale(scale).translate(tx, ty)
            )

    if reader.outline:
        copy_outline(reader, writer, reader.outline)

    with open(output_pdf, "wb") as f:
        writer.write(f)


def main():
    args = [a for a in sys.argv[1:] if a not in ("--horizontal", "--no-lines")]
    horizontal = "--horizontal" in sys.argv
    no_lines = "--no-lines" in sys.argv

    if not args:
        print(
            "Usage: script.py input.pdf [output.pdf] [margin_mm] [--horizontal] [--no-lines]"
        )
        sys.exit(1)

    input_pdf = args[0]
    has_output = len(args) > 1 and not args[1].replace(".", "", 1).isdigit()
    output_pdf = (
        args[1]
        if has_output
        else f"{'horizon' if horizontal else 'scaled'}_{Path(input_pdf).name}"
    )
    margin = (
        float(args[2 if has_output else 1])
        if len(args) > (2 if has_output else 1)
        else 40
    )

    convert(input_pdf, output_pdf, margin, horizontal, lines=not no_lines)


if __name__ == "__main__":
    main()