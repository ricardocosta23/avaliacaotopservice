
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import os

def generate_qr_code_image(url, size=200):
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
    """Create a square image with survey details and QR code"""
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
        
        # Create a semi-transparent white overlay (like the form style)
        overlay = Image.new('RGBA', (img_size, img_size), (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create rounded rectangle for the white layer
        margin = 120
        border_radius = 20
        
        # Draw rounded rectangle on overlay
        overlay_draw.rounded_rectangle(
            [margin, margin, img_size - margin, img_size - margin],
            radius=border_radius,
            fill=(255, 255, 255, 240)  # Semi-transparent white
        )
        
        # Composite the overlay onto the background
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        draw = ImageDraw.Draw(img)
        
        # Colors
        primary_color = (102, 126, 234)  # #667eea
        text_color = (45, 55, 72)       # #2d3748
        gray_color = (74, 85, 104)      # #4a5568
        
        # Try to load fonts - tripled sizes
        try:
            # Try to load a system font
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 180)  # 36 * 3
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 120)  # 24 * 3
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 280)  # 56 * 3
        except:
            try:
                # Fallback fonts
                title_font = ImageFont.truetype("arial.ttf", 180)
                subtitle_font = ImageFont.truetype("arial.ttf", 120)
                text_font = ImageFont.truetype("arial.ttf", 280)
            except:
                # Use default font if no system fonts available
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
        
        # Add company logo if available
        logo_path = os.path.join('static', 'images', 'pdfqr.png')
        y_offset = 60  # Start within the white layer
        
        if os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                # Resize logo to fit width with aspect ratio
                logo_width = 300  # Smaller to fit in the white layer
                logo_height = int((logo_width * logo.height) / logo.width)
                logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                
                # Center logo horizontally
                logo_x = (img_size - logo_width) // 2
                img.paste(logo, (logo_x, y_offset))
                y_offset += logo_height + 20
            except Exception as e:
                print(f"Error adding logo to image: {e}")
                y_offset += 30
        else:
            y_offset += 30
        
        # Add title
        title_text = "Pesquisa de Experiência de Viagem"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (img_size - title_width) // 2
        draw.text((title_x, y_offset), title_text, fill=primary_color, font=title_font)
        y_offset += 120  # Reduced spacing
        
        # Add trip details without icons
        details = [
            f"Empresa: {survey_data.get('company_name', 'N/A')}",
            f"Destino: {survey_data.get('location', 'N/A')}",
            f"Data: {survey_data.get('date', 'N/A')}",
            f"Viagem: {survey_data.get('trip_name', 'N/A')}"
        ]
        
        for detail in details:
            detail_bbox = draw.textbbox((0, 0), detail, font=text_font)
            detail_width = detail_bbox[2] - detail_bbox[0]
            detail_x = (img_size - detail_width) // 2
            draw.text((detail_x, y_offset), detail, fill=text_color, font=text_font)
            y_offset += 20  # Much reduced spacing between lines
        
        y_offset += 30
        
        # Add horizontal line
        line_margin = 100
        draw.line([(line_margin, y_offset), (img_size - line_margin, y_offset)], fill=primary_color, width=3)
        y_offset += 40
        
        # Generate and add QR code
        qr_img = generate_qr_code_image(survey_url, 300)  # Smaller QR code
        if qr_img:
            qr_x = (img_size - 300) // 2
            img.paste(qr_img, (qr_x, y_offset))
            y_offset += 320  # QR code height + spacing
            
            # Add subtitle below QR code
            subtitle_text = "Escaneie o QR Code para acessar"
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (img_size - subtitle_width) // 2
            draw.text((subtitle_x, y_offset), subtitle_text, fill=gray_color, font=subtitle_font)
        else:
            # Add placeholder text if QR code fails
            placeholder_text = "QR Code não pôde ser gerado"
            placeholder_bbox = draw.textbbox((0, 0), placeholder_text, font=subtitle_font)
            placeholder_width = placeholder_bbox[2] - placeholder_bbox[0]
            placeholder_x = (img_size - placeholder_width) // 2
            draw.text((placeholder_x, y_offset + 100), placeholder_text, fill=gray_color, font=subtitle_font)
        
        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', quality=95)
        img_data = img_buffer.getvalue()
        img_buffer.close()
        
        return img_data
        
    except Exception as e:
        print(f"Error creating survey image: {e}")
        return None
