import pymupdf
import os
from loguru import logger
import numpy as np
import shutil


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
	shutil.copy2(input, output)
	doc = pymupdf.open(output)
	logger.debug(f"opening {output}")

	for page in doc.pages():
		x, y = mediabox_size(page.mediabox)

		o = np.array([page.mediabox[0], page.mediabox[1]])
		for rect in rects(o, mx, my, x, y):
			# print(rect)
			page.add_redact_annot(rect)
		page.apply_redactions()

	doc.save(output, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
	doc.close()


# def test_cut_1():
# remove_trash("testpdfs/singlepage.pdf", "123.pdf", mx=200, my=200)
