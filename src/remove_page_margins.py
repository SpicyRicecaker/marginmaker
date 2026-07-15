from asyncio.queues import QueueShutDown
from operator import eq
from random import weibullvariate

import pymupdf

input_pdf = "testpdfs/singlepage.pdf"
output_pdf = "singlepageconv.pdf"

doc_orig = pymupdf.open("testpdfs/singlepage.pdf")
doc_new = pymupdf.open()


def rects(mx, my, w, h):
	# see https://drive.google.com/file/d/1mAiyMTr5tcUmGRUGz8F4qJTnHwXQOPae/view?usp=sharing
	L = mx / 2
	T = my / 2
	W = w - 2 * L
	H = h - 2 * T

	class P:
		A = (0, 0)
		B = (L + W, 0)
		C = (L + W + L, T)
		D = (L + W + L, T + H + T)
		E = (L, T + H + T)
		F = (0, T + H)

	p = P()

	return [
		[*p.A, *p.C],
		[*p.B, *p.D],
		[*p.F, *p.D],
		[*p.A, *p.E],
	]


mx = 200
my = 200

i = 0
for page in doc_orig.pages():
	x, y = page.mediabox_size.x, page.mediabox_size.y

	page_new = doc_new.new_page(width=x, height=y)
	page_new.show_pdf_page(page.rect, doc_orig, i)

	x, y = page_new.mediabox_size.x, page_new.mediabox_size.y
	for rect in rects(mx, my, x, y):
		print(rect)
		page_new.add_redact_annot(rect)
	page_new.apply_redactions()
	i += 1


doc_new.save("123.pdf")


def test_recta():
	rects_l = rects(200, 200, 800, 600)
