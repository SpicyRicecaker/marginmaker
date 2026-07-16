import pymupdf
import os
from loguru import logger
import numpy as np


def rects(o, mx, my, w, h):
	# see https://drive.google.com/file/d/1mAiyMTr5tcUmGRUGz8F4qJTnHwXQOPae/view?usp=sharing
	L = mx / 2
	T = my / 2
	W = w - 2 * L
	H = h - 2 * T

	class P:
		A = o
		B = o + np.array([L + W, 0])
		C = o + np.array([L + W + L, T])
		D = o + np.array([L + W + L, T + H + T])
		E = o + np.array([L, T + H + T])
		F = o + np.array([0, T + H])

	p = P()

	return [
		[*p.A, *p.C],
		[*p.B, *p.D],
		[*p.F, *p.D],
		[*p.A, *p.E],
	]


def mediabox_size(mediabox):
	return mediabox[2] - mediabox[0], mediabox[3] - mediabox[1]


def remove_trash(input, output, mx, my):
	doc_orig = pymupdf.open(input)
	doc_new = pymupdf.open()
	logger.debug(f"opening {input}")

	i = 0
	for page in doc_orig.pages():
		logger.debug(f"input pdf mediabox {page.mediabox}")
		x, y = mediabox_size(page.mediabox)
		logger.debug(f"final pdf size, x: {x}, y: {y}")

		page_new = doc_new.new_page(width=x, height=y)
		logger.debug(f"pasting onto {page.rect}")
		page_new.show_pdf_page(page.rect, doc_orig, i, clip=[-250.0, 0.0, 862.0, 792.0])

		# x, y = page_new.mediabox_size.x, page_new.mediabox_size.y
		# o = np.array([page.mediabox[0], page.mediabox[1]])
		# for rect in rects(o, mx, my, x, y):
		# 	# print(rect)
		# 	page_new.add_redact_annot(rect)
		# page_new.apply_redactions()
		break
		# i += 1
	doc_new.save(output)
	doc_new.close()


# def test_cut_1():
# remove_trash("testpdfs/singlepage.pdf", "123.pdf", mx=200, my=200)
