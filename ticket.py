import qrencode
import os
import shutil
from pyPdf import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import tempfile
from StringIO import StringIO

def build_ticket(ticket, owner = None, \
                 background = "ticket-template.pdf", \
                 ticket_x = 2, ticket_y = 2, ticket_size = 5, \
	         ticket_print_as_string = True, ticket_sx = 2, ticket_sy = 7.5,
                 owner_x = 10, owner_y = 3):

	tempImg = tempfile.mkstemp()
	tempName = tempImg[1]

	qr_item = qrencode.encode_scaled(ticket, 200, level=qrencode.QR_ECLEVEL_H)
	qr_item[2].save(tempName, "PNG")

	overlayData = StringIO()
	overlay = canvas.Canvas(overlayData, pagesize=A4, bottomup=0)

	if owner != None:
		overlay.setFont('Helvetica', 20)
		overlay.drawString(owner_x * cm, owner_y * cm, owner)

	if ticket_print_as_string:
		overlay.setFont('Helvetica', 8)
		overlay.drawString(ticket_sx * cm, ticket_sy * cm, ticket)

	overlay.drawImage(tempName, ticket_x * cm, ticket_y * cm, ticket_size * cm, ticket_size * cm)
	overlay.save()

	page = PdfFileReader(file(background,"rb")).getPage(0)
	overlayPage = PdfFileReader(StringIO(overlayData.getvalue())).getPage(0)
	page.mergePage(overlayPage)

	outputFile = tempfile.mkstemp()
	output = PdfFileWriter()
	output.addPage(page)
	output.write(file(outputFile[1],"w"))

	os.remove(tempName)
	return outputFile

if __name__ == "__main__":
	# TODO read command line (oder so)
	ticket_no = "12345-67890-12345-67890-12345-67890"
	ticket_owner = "Bernd"
	output_name = "output.pdf"

	result = build_ticket(ticket_no, ticket_owner, ticket_x = 2.58, ticket_y = 5.93, ticket_size = 3.14, owner_x = 7.2, owner_y = 7, ticket_sx = 7.2, ticket_sy = 7.5)
	shutil.move(result[1], output_name)

