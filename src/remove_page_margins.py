import pymupdf
import os
from loguru import logger
import numpy as np
import shutil


# given an old mediabox and a new mediabox
# generates all redaction squares necessary to remove all
# content between the two mediaboxes
class P:
	def __init__(self, mediabox, mx, my):
		"""
		o - a 4d rect, representing the coordinates of the new mediabox
		mx - representing the side margins that were added to the original mediabox
		my - representing the top&bot margins that were added to the origin mediabox
		"""
		x0, y0, x1, y1 = mediabox
		w = x1 - x0
		h = y1 - y0

		L = mx / 2
		T = my / 2
		W = w - 2 * L
		H = h - 2 * T

		o = np.array([x0, y0])

		self.A = o
		self.B = o + np.array([L + W, 0])
		self.C = o + np.array([L + W + L, T])
		self.D = o + np.array([L + W + L, T + H + T])
		self.E = o + np.array([L, T + H + T])
		self.F = o + np.array([0, T + H])

		self.A = self.A.tolist()
		self.B = self.B.tolist()
		self.C = self.C.tolist()
		self.D = self.D.tolist()
		self.E = self.E.tolist()
		self.F = self.F.tolist()

		self.e = 50

	def redaction_rects(self):
		# add slight margin between rect and original media page, to prevent content we care about
		# getting deleted
		return [
			[*(self.A + np.array([0, 0])), *(self.C + np.array([0, -self.e]))],
			[*(self.B + np.array([self.e, 0])), *(self.D + np.array([0, 0]))],
			[*(self.F + np.array([0, self.e])), *(self.D + np.array([0, 0]))],
			[*(self.A + np.array([0, 0])), *(self.E + np.array([-self.e, 0]))],
		]


def rects(mediabox, mx, my):
	# see https://drive.google.com/file/d/1mAiyMTr5tcUmGRUGz8F4qJTnHwXQOPae/view?usp=sharing

	p = P(mediabox, mx, my)
	return p.redaction_rects()


def mediabox_size(mediabox):
	return mediabox[2] - mediabox[0], mediabox[3] - mediabox[1]


def remove_trash(input, output, mx, my):
	shutil.copy2(input, output)
	doc = pymupdf.open(output)
	logger.debug(f"opening {output}")

	for i, page in enumerate(doc.pages(), 1):
		for rect in rects(page.mediabox, mx, my):
			# print(rect)
			page.add_redact_annot(rect)
		logger.info(f"adding redactions to page {i}")
		page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE)

	doc.save(output, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
	doc.close()


def test_cut_1():
	p = P(np.array([0, 0, 1000, 800]), mx=200, my=200)
	assert p.A == [0, 0]
	assert p.B == [900, 0]
	assert p.C == [1000, 100]
	assert p.D == [1000, 800]
	assert p.E == [100, 800]
	assert p.F == [0, 700]

	for prop in "ABCDEF":
		print(prop)
		print(p.__dict__[prop])


def test_cut_2():
	p = P(np.array([-100, 0, 900, 600]), mx=200, my=0)
	assert p.A == [-100, 0]
	assert p.B == [800, 0]
	assert p.C == [900, 0]
	assert p.D == [900, 600]
	assert p.E == [0, 600]
	assert p.F == [-100, 600]

	for prop in "ABCDEF":
		print(prop)
		print(p.__dict__[prop])


# remove_trash("testpdfs/singlepage.pdf", "123.pdf", mx=200, my=200)
