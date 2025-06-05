from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import os

def generate_qr_code_image(url, size=400):
    """Generate QR code image for the survey URL"""
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

        # Resize to desired size
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)

        return qr_img
    except Exception as e:
        print(f"Error generating QR code image: {e}")
        return None

def create_survey_image(survey_data, survey_url):
    """Create a square image with QR code centered on background"""
    try:
        # Image dimensions (square)
        img_size = 800

        # Load background image
        background_path = os.path.join('static', 'images', 'fundoqrpng.png')
        if os.path.exists(background_path):
            try:
                background = Image.open(background_path)
                # Resize background to fit the square image
                background = background.resize((img_size, img_size), Image.Resampling.LANCZOS)
                img = background.copy()
            except Exception as e:
                print(f"Error loading background image: {e}")
                # Fallback to white background
                img = Image.new('RGB', (img_size, img_size), color='white')
        else:
            # Fallback to white background
            img = Image.new('RGB', (img_size, img_size), color='white')

        # Generate and add QR code (centered)
        qr_img = generate_qr_code_image(survey_url, 400)  # Larger QR code
        if qr_img:
            # Center the QR code
            qr_x = (img_size - 500) // 2
            qr_y = (img_size - 500) // 2
            img.paste(qr_img, (qr_x, qr_y))

        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', quality=95)
        img_data = img_buffer.getvalue()
        img_buffer.close()

        return img_data

    except Exception as e:
        print(f"Error creating survey image: {e}")
        return None
