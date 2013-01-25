import qrencode
from pyPdf import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import tempfile
from StringIO import StringIO

def build_ticket(ticket, owner = None, \
                 background = "ticket-template.pdf", \
                 ticket_x = 2, ticket_y = 2, ticket_size = 5, \
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

	overlay.drawImage(tempName, ticket_x * cm, ticket_y * cm, ticket_size * cm, ticket_size * cm)
	overlay.save()

	page = PdfFileReader(file(background,"rb")).getPage(0)
	overlayPage = PdfFileReader(StringIO(overlayData.getvalue())).getPage(0)
	page.mergePage(overlayPage)

	outputFile = tempfile.mkstemp()
	output = PdfFileWriter()
	output.addPage(page)
	output.write(file(outputFile[1],"w"))

	#File.delete(tempName)
	return outputFile

if __name__ == "__main__":
	# TODO read command line (oder so)
	print build_ticket("12345-67890-12345-67890-12345-67890", "Bernd", ticket_x = 4, ticket_y = 10.9, ticket_size = 5.9, owner_x = 11.6, owner_y = 7.7)

