#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pypdf"]
# ///
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import FloatObject, NameObject, ArrayObject
from pprint import pprint


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

# inklists = []
# should_break = False

def return_transformed(A, tx, ty):
    # print('---------------------------------------')
    # pprint(A)
    # print('---------------------------------------')

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
        # global should_break
        # if should_break:
        #     break
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
        # --- FIX: Use NameObject for keys and ArrayObject for lists ---
        if "/Annots" in new_page:
            for annot_ref in new_page["/Annots"]:
                annot = annot_ref.get_object()
                
                # Shift /Rect using NameObject and ArrayObject
                if "/Rect" in annot:
                    rect = annot["/Rect"]
                    rect_key = NameObject("/Rect")
                    rect_values = ArrayObject([
                        FloatObject(float(rect[0]) + tx),
                        FloatObject(float(rect[1]) + ty),
                        FloatObject(float(rect[2]) + tx),
                        FloatObject(float(rect[3]) + ty)
                    ])
                    annot[rect_key] = rect_values

                if "/InkList" in annot:
                    # global inklists
                    # inklists.append(annot["/InkList"])
                    # pprint(annot["/InkList"])
                    # print("-----------------")
                    # for a in annot["/InkList"]:
                    #     print(a)
                    inklist = annot["/InkList"]
                    inklist_key = NameObject("/InkList")
                    new_inklist = return_transformed(inklist, tx, ty)
                    # print(new_inklist)
                    annot[inklist_key] = new_inklist
                    # pprint(return_transformed(annot["/InkList"], tx, ty))
                    # exit()
                    # pprint(len(inklists))
                    # if len(inklists) > 5:
                    #     should_break = True
                    #     break

                # Shift /QuadPoints using NameObject and ArrayObject
                # global test
                # for k in dict.keys(annot):
                #     test.add(k)
                # if "/QuadPoints" in annot:
                #     qp = annot["/QuadPoints"]
                #     qp_key = NameObject("/QuadPoints")
                #     new_qp = []
                #     for i, coord in enumerate(qp):
                #         if i % 2 == 0:
                #             new_qp.append(FloatObject(float(coord) + tx))
                #         else:
                #             new_qp.append(FloatObject(float(coord) + ty))
                #     annot[qp_key] = ArrayObject(new_qp)
                # if "/AP" in annot:
                #     del annot["/AP"]
    # pprint(inklists)
    # exit()
    # -----------------------------------------------------------
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