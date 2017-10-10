#!/usr/bin/env python3

from flask import Flask, make_response, request
from flask import Response
from flask.templating import render_template
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config.update(
    DEBUG=False,
    SECRET_KEY='...'
)


def generate_pdf_data(abs_name, abs_addr, abs_city, empf_name, empf_addr, empf_city):
    pdfmetrics.registerFont(TTFont('LM', 'fonts/lmroman10-regular.ttf'))
    pdfmetrics.registerFont(TTFont('LMBold', 'fonts/lmroman10-bold.ttf'))
    pdfmetrics.registerFont(TTFont('LMItalic', 'fonts/lmroman10-italic.ttf'))
    pdfmetrics.registerFont(TTFont('LMBoldItalic', 'fonts/lmroman10-bolditalic.ttf'))

    ruecksendeangabe = '·'.join([abs_name, abs_addr, abs_city])

    ABSTAND_LINKS = 25 * mm
    ABSTAND_OBEN = 45 * mm
    HOEHE_ABSTAND_VERMERKZONE = 17.7 * mm
    ZEILENHOEHE = 5 * mm

    pagesize = A4
    c = canvas.Canvas('Brieffenster.pdf', pagesize=pagesize)
    page_width, page_height = pagesize
    c.setLineWidth(0.15 * mm)

    # canvas.rect(20 * mm, h - (45 * mm + 40 * mm), 85 * mm, 40 * mm)

    # Rücksendeangabe
    rueck_font = 'LM'
    rueck_font_size = 8
    c.setFont(rueck_font, rueck_font_size)
    c.drawString(ABSTAND_LINKS, page_height - (ABSTAND_OBEN + ZEILENHOEHE), ruecksendeangabe)

    # Rücksendeangabe Linie
    text_width = stringWidth(ruecksendeangabe, rueck_font, rueck_font_size)
    y_ruecksendeangabelinie = page_height - (ABSTAND_OBEN + ZEILENHOEHE + 1.5 * mm)
    c.line(ABSTAND_LINKS, y_ruecksendeangabelinie, ABSTAND_LINKS + text_width, y_ruecksendeangabelinie)

    # Empfänger
    c.setFont('LM', 12)
    c.drawString(ABSTAND_LINKS, page_height - (ABSTAND_OBEN + HOEHE_ABSTAND_VERMERKZONE + ZEILENHOEHE), empf_name)
    c.drawString(ABSTAND_LINKS, page_height - (ABSTAND_OBEN + HOEHE_ABSTAND_VERMERKZONE + 2 * ZEILENHOEHE), empf_addr)
    c.drawString(ABSTAND_LINKS, page_height - (ABSTAND_OBEN + HOEHE_ABSTAND_VERMERKZONE + 3 * ZEILENHOEHE), empf_city)

    return c.getpdfdata()


@app.route('/generate/', methods=['POST'])
def generate():
    params = request.form.to_dict()
    if not params:
        return Response('These POST parameters must be set:\n'
                        'abs_name\n'
                        'abs_street\n'
                        'abs_city\n'
                        'empf_name\n'
                        'empf_street\n'
                        'empf_city', 400)

    for k, v in params.items():
        if not v:
            return Response(k + ' must be set!', 400)
        params[k] = v.replace('\\', '')

    # Render
    pdf_bytes = generate_pdf_data(
        request.form['abs_name'],
        request.form['abs_street'],
        request.form['abs_city'],
        request.form['empf_name'],
        request.form['empf_street'],
        request.form['empf_city'],
    )

    filename_download = 'Briefkopf_{}.pdf'.format(request.form['empf_name'])

    print("Creating Briefkopf ({} bytes) in {}".format(len(pdf_bytes), filename_download))

    response = make_response(pdf_bytes)
    response.headers['Content-Disposition'] = "attachment; filename=" + filename_download + '.pdf'
    response.mimetype = 'application/pdf'
    return response


@app.route('/')
def hello_world():
    return render_template('form.html')


if __name__ == '__main__':
    app.run()
