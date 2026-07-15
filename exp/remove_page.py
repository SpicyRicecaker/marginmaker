from asyncio.queues import QueueShutDown
from operator import eq
from random import weibullvariate

import pymupdf

input_pdf = "testpdfs/singlepage.pdf"
output_pdf = "singlepageconv.pdf"

doc_orig = pymupdf.open("testpdfs/singlepage.pdf")
doc_new = pymupdf.open()

i = 0
for page in doc_orig.pages():
	x, y = page.mediabox_size.x, page.mediabox_size.y

	page_new = doc_new.new_page(width=x, height=y)
	page_new.show_pdf_page(page.rect, doc_orig, i)

	page_new.add_redact_annot([0, 0, x / 2, y])
	page_new.apply_redactions()
	i += 1


doc_new.save("123.pdf")
