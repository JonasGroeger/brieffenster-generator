#!/usr/bin/env python3

import hashlib
import logging
import os
from importlib.resources import files
from io import BytesIO

from flask import Flask, jsonify, make_response, request, render_template
from werkzeug.exceptions import HTTPException
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config.update(DEBUG=False, SECRET_KEY=os.environ["SECRET_KEY"])

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Register fonts at startup (once only, not per request)
def _register_fonts():
    """Register TrueType fonts from bundle and CJK fonts."""
    fonts = files("brieffenster_generator") / "fonts"
    pdfmetrics.registerFont(TTFont("LM", fonts / "lmroman10-regular.ttf"))
    pdfmetrics.registerFont(TTFont("LMBold", fonts / "lmroman10-bold.ttf"))
    pdfmetrics.registerFont(TTFont("LMItalic", fonts / "lmroman10-italic.ttf"))
    pdfmetrics.registerFont(TTFont("LMBoldItalic", fonts / "lmroman10-bolditalic.ttf"))

    # Register CJK font for Chinese, Japanese, Korean support
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    logger.info("Fonts registered successfully")


_register_fonts()


def has_cjk_characters(text):
    """Check if text contains CJK (Chinese, Japanese, Korean) characters."""
    for char in text:
        code_point = ord(char)
        # CJK Unified Ideographs range
        if 0x4E00 <= code_point <= 0x9FFF:
            return True
        # CJK Unified Ideographs Extension A
        if 0x3400 <= code_point <= 0x4DBF:
            return True
        # CJK Unified Ideographs Extension B
        if 0x20000 <= code_point <= 0x2A6DF:
            return True
    return False


def select_font(text, font_size):
    """Select appropriate font based on text content.

    Uses CJK font if text contains CJK characters, otherwise uses Latin font.
    Returns (font_name, font_size_adjusted) tuple.
    """
    if has_cjk_characters(text):
        # CJK fonts may need slightly different sizing
        return ("STSong-Light", font_size)
    return ("LM", font_size)

# Constants for input validation
MAX_FIELD_LENGTH = 200


def generate_pdf_data(abs_name, abs_addr, abs_city, empf_name, empf_addr, empf_city):
    """Generate PDF bytes for a letter header (Brieffenster).

    Args:
        abs_name: Sender name
        abs_addr: Sender street address
        abs_city: Sender postal code and city
        empf_name: Recipient name
        empf_addr: Recipient street address
        empf_city: Recipient postal code and city

    Returns:
        bytes: PDF data

    Raises:
        Exception: If PDF generation fails
    """
    try:

        ruecksendeangabe = "·".join([abs_name, abs_addr, abs_city])

        ABSTAND_LINKS = 25 * mm
        ABSTAND_OBEN = 45 * mm
        HOEHE_ABSTAND_VERMERKZONE = 17.7 * mm
        ZEILENHOEHE = 5 * mm

        pagesize = A4
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=pagesize)
        _, page_height = pagesize
        c.setLineWidth(0.15 * mm)

        # Rücksendeangabe
        rueck_font = "LM"
        rueck_font_size = 8
        c.setFont(rueck_font, rueck_font_size)
        c.drawString(
            ABSTAND_LINKS, page_height - (ABSTAND_OBEN + ZEILENHOEHE), ruecksendeangabe
        )

        # Rücksendeangabe Linie
        text_width = stringWidth(ruecksendeangabe, rueck_font, rueck_font_size)
        y_ruecksendeangabelinie = page_height - (ABSTAND_OBEN + ZEILENHOEHE + 1.5 * mm)
        c.line(
            ABSTAND_LINKS,
            y_ruecksendeangabelinie,
            ABSTAND_LINKS + text_width,
            y_ruecksendeangabelinie,
        )

        # Empfänger (recipient) - auto-detect font based on content
        font_name_name, font_size_name = select_font(empf_name, 12)
        c.setFont(font_name_name, font_size_name)
        c.drawString(
            ABSTAND_LINKS,
            page_height - (ABSTAND_OBEN + HOEHE_ABSTAND_VERMERKZONE + ZEILENHOEHE),
            empf_name,
        )

        font_name_addr, font_size_addr = select_font(empf_addr, 12)
        c.setFont(font_name_addr, font_size_addr)
        c.drawString(
            ABSTAND_LINKS,
            page_height - (ABSTAND_OBEN + HOEHE_ABSTAND_VERMERKZONE + 2 * ZEILENHOEHE),
            empf_addr,
        )

        font_name_city, font_size_city = select_font(empf_city, 12)
        c.setFont(font_name_city, font_size_city)
        c.drawString(
            ABSTAND_LINKS,
            page_height - (ABSTAND_OBEN + HOEHE_ABSTAND_VERMERKZONE + 3 * ZEILENHOEHE),
            empf_city,
        )

        c.save()
        return pdf_buffer.getvalue()
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise


@app.route("/generate/", methods=["POST"])
def generate():
    """Generate a PDF letter header from form data."""
    required_fields = [
        "abs_name", "abs_street", "abs_city",
        "empf_name", "empf_street", "empf_city"
    ]
    params = request.form.to_dict()

    # Validate required fields
    missing_fields = [f for f in required_fields if not params.get(f, "").strip()]
    if missing_fields:
        logger.warning(f"Form submission missing fields: {missing_fields}")
        return jsonify({
            "error": "Validation error",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    # Validate field lengths
    oversized_fields = [f for f in required_fields if len(params.get(f, "")) > MAX_FIELD_LENGTH]
    if oversized_fields:
        logger.warning(f"Form submission with oversized fields: {oversized_fields}")
        return jsonify({
            "error": "Validation error",
            "message": f"Fields exceed maximum length of {MAX_FIELD_LENGTH} characters: {', '.join(oversized_fields)}"
        }), 400

    # Sanitize input: strip whitespace
    params = {k: v.strip() for k, v in params.items()}

    try:
        # Generate PDF
        pdf_bytes = generate_pdf_data(
            params["abs_name"],
            params["abs_street"],
            params["abs_city"],
            params["empf_name"],
            params["empf_street"],
            params["empf_city"],
        )

        # Create filename with hash
        param_hash = hashlib.sha256(
            "|".join([
                params["abs_name"], params["abs_street"], params["abs_city"],
                params["empf_name"], params["empf_street"], params["empf_city"],
            ]).encode()
        ).hexdigest()[:8]
        filename_download = f"Briefkopf-{param_hash}.pdf"

        logger.info(f"Generated PDF: {filename_download} ({len(pdf_bytes)} bytes)")

        response = make_response(pdf_bytes)
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{filename_download}"'
        )
        response.headers["Content-Length"] = len(pdf_bytes)
        response.mimetype = "application/pdf"
        return response

    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({
            "error": "PDF generation failed",
            "message": "An error occurred while generating the PDF"
        }), 500


@app.route("/health")
def health():
    """Health check endpoint for deployment/monitoring."""
    return jsonify({"status": "ok"}), 200


@app.route("/")
def hello_world():
    return render_template("form.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
