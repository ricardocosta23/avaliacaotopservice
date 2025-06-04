import os
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.flowables import HRFlowable
# Removed Table, TableStyle, HexColor imports as they are no longer needed for the banner
from PIL import Image as PILImage # Import PIL for image dimension inspection

def generate_qr_code(url):
    """Generate QR code for the survey URL"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return img_buffer
    except Exception as e:
        print(f"Error generating QR code: {e}")
        # Return empty buffer if QR generation fails
        return BytesIO()

def create_survey_pdf(survey_data, survey_url):
    """Create a PDF with company logo and QR code for the survey"""
    buffer = BytesIO()

    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=18,
        bottomMargin=18
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#667eea')
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4a5568')
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#2d3748')
    )

    # Add company logo - simplified for serverless environment
    logo_path = os.path.join('static', 'images', 'pdfqr.png')

    if os.path.exists(logo_path):
        try:
            # Simple logo sizing - fixed dimensions for reliability
            logo = Image(logo_path, width=6*inch, height=3*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error adding logo: {e}")
            # Continue without logo if there's an error

    # Add title
    title = Paragraph("Pesquisa de Experiência de Viagem", title_style)
    elements.append(title)

    # Add subtitle
    subtitle = Paragraph("Escaneie o QR Code para acessar a pesquisa", subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # Add trip details
    details = [
        f"<b>Empresa:</b> {survey_data.get('company_name', 'N/A')}",
        f"<b>Destino:</b> {survey_data.get('location', 'N/A')}",
        f"<b>Data:</b> {survey_data.get('date', 'N/A')}",
        f"<b>Viagem:</b> {survey_data.get('trip_name', 'N/A')}"
    ]

    for detail in details:
        elements.append(Paragraph(detail, normal_style))

    elements.append(Spacer(1, 30))

    # Add horizontal line
    line = HRFlowable(width="100%", thickness=2, color=colors.HexColor('#667eea'))
    elements.append(line)
    elements.append(Spacer(1, 20))

    # Generate and add QR code
    try:
        qr_buffer = generate_qr_code(survey_url)
        if qr_buffer.getbuffer().nbytes > 0:
            qr_image = Image(qr_buffer, width=3*inch, height=3*inch)
            qr_image.hAlign = 'CENTER'
            elements.append(qr_image)
            print("QR code successfully added to PDF")
        else:
            # Add placeholder text if QR code fails
            qr_placeholder = Paragraph("QR Code não pôde ser gerado", subtitle_style)
            elements.append(qr_placeholder)
            print("QR code generation failed, added placeholder text")
    except Exception as e:
        print(f"Error with QR code: {e}")
        # Add placeholder text if QR code fails
        qr_placeholder = Paragraph("QR Code não pôde ser gerado", subtitle_style)
        elements.append(qr_placeholder)

    elements.append(Spacer(1, 20))

    # Add QR code instructions
    instructions = [

    ]

    for instruction in instructions:
        elements.append(Paragraph(instruction, normal_style))

    elements.append(Spacer(1, 20))

    # Add URL as text (backup)
    url_text = f"<b>Link direto:</b> {survey_url}"
    elements.append(Paragraph(url_text, normal_style))

    # Build PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and return
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data
