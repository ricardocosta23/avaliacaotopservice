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

    # Add company logo without a banner background
    logo_path = os.path.join('static', 'images', 'pdfqr.png') # Using pdfqr.png as per your provided code

    # Create a dummy logo file for testing if it doesn't exist
    # In a real scenario, ensure 'static/images/pdfqr.png' exists
    if not os.path.exists(logo_path):
        os.makedirs(os.path.dirname(logo_path), exist_ok=True)
        # Create a dummy image that is larger than the desired max dimensions
        # to test the scaling down logic
        dummy_img = PILImage.new('RGB', (800, 400), color = 'blue')
        dummy_img.save(logo_path)
        print(f"Created dummy logo at: {logo_path} for testing.")


    if os.path.exists(logo_path):
        try:
            # Get original image dimensions using PIL
            pil_img = PILImage.open(logo_path)
            original_width_px, original_height_px = pil_img.size
            pil_img.close() # Close the image file after getting dimensions

            # Define maximum desired dimensions for the logo in inches
            # Adjust these values as needed for your desired logo size
            max_logo_width_inch = 7.5 * inch
            max_logo_height_inch = 4.5 * inch # A reasonable maximum height

            # Convert pixel dimensions to points (ReportLab works in points, 1 inch = 72 points)
            # Assuming a default DPI of 72 for pixel to point conversion if not explicitly known
            original_width_pt = original_width_px * (inch / 72.0)
            original_height_pt = original_height_px * (inch / 72.0)

            # Calculate scaling factor to fit within max dimensions while maintaining aspect ratio
            scale_factor = 1.0 # Default to no scaling

            # Only scale down if the original image is larger than the maximum desired dimensions
            if original_width_pt > max_logo_width_inch or original_height_pt > max_logo_height_inch:
                width_ratio = max_logo_width_inch / original_width_pt
                height_ratio = max_logo_height_inch / original_height_pt
                scale_factor = min(width_ratio, height_ratio) # Use the smaller ratio to fit within both constraints

            # Calculate the final scaled dimensions
            scaled_width = original_width_pt * scale_factor
            scaled_height = original_height_pt * scale_factor

            # Create logo with calculated scaled dimensions
            # ReportLab will use these precise dimensions, maintaining aspect ratio
            logo = Image(logo_path, width=scaled_width, height=scaled_height)
            logo.hAlign = 'CENTER' # Center the image horizontally

            elements.append(logo) # Append the image directly
            elements.append(Spacer(1, 20)) # Add a spacer after the logo
        except Exception as e:
            print(f"Error adding logo: {e}")
            pass  # Skip logo if there's an error loading it

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
    print(f"DEBUG: Survey URL provided: {survey_url}") # Debugging: Check the URL
    try:
        qr_buffer = generate_qr_code(survey_url)
        print(f"DEBUG: QR buffer size: {qr_buffer.getbuffer().nbytes} bytes") # Debugging: Check buffer size
        if qr_buffer.getbuffer().nbytes > 0:
            qr_image = Image(qr_buffer, width=3*inch, height=3*inch)
            qr_image.hAlign = 'CENTER'
            elements.append(qr_image)
            print("DEBUG: QR code image appended to elements.") # Debugging: Confirm append
        else:
            print("DEBUG: QR buffer is empty, QR code not generated.") # Debugging: Empty buffer
    except Exception as e:
        print(f"ERROR: Failed to generate or add QR code: {e}") # Debugging: Catch QR error

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
