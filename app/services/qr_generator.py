import io
import os
from typing import Optional, Union
from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageColor import getcolor
import qrcode
from qrcode.image.pil import PilImage
import httpx
from fastapi import UploadFile, HTTPException
from loguru import logger
from dataclasses import dataclass

from app.config import settings


@dataclass
class QRCodeStyle:
    """QR Code styling configuration."""
    
    size: int = 300
    border: int = 4
    box_size: int = 10
    fill_color: str = "black"
    back_color: str = "white"
    logo_url: Optional[str] = None
    logo_path: Optional[str] = None
    logo_size_ratio: float = 0.3
    style: str = "square"  # square, circle, rounded, diamond
    gradient: bool = False
    format: str = "png"


class QRCodeGenerator:
    """Advanced QR Code generator with styling capabilities."""
    
    def __init__(self):
        # No need for persistent storage directories
        pass
    
    async def generate_qr_code(self, data: str, style: QRCodeStyle) -> io.BytesIO:
        """Generate a styled QR code."""
        try:
            logger.info(f"Generating QR code with style: {style.style}")
            
            # For now, use only standard QR generation
            return await self._generate_standard_qr(data, style)
                
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise HTTPException(status_code=500, detail=f"QR generation failed: {str(e)}")
    
    async def _generate_standard_qr(self, data: str, style: QRCodeStyle) -> io.BytesIO:
        """Generate standard QR code using qrcode library."""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=style.box_size,
                border=style.border,
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(
                fill_color=self._parse_color(style.fill_color),
                back_color=self._parse_color(style.back_color)
            ).convert('RGB')
            
            # Resize to desired size
            qr_img = qr_img.resize((style.size, style.size), Image.Resampling.LANCZOS)
            
            # Add logo if provided
            if style.logo_url or style.logo_path:
                qr_img = await self._add_logo(qr_img, style)
            
            # Apply styling effects
            if style.style == "rounded":
                qr_img = self._apply_rounded_corners(qr_img)
            elif style.style == "circle":
                qr_img = self._apply_circle_shape(qr_img)
            elif style.style == "diamond":
                qr_img = self._apply_diamond_shape(qr_img)
            
            if style.gradient:
                qr_img = self._apply_gradient(qr_img, style)
            
            # Convert to buffer
            buffer = io.BytesIO()
            qr_img.save(buffer, format=style.format.upper(), quality=95, optimize=True)
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error in _generate_standard_qr: {str(e)}")
            raise e
    
    async def _add_logo(self, qr_img: Image.Image, style: QRCodeStyle) -> Image.Image:
        """Add logo to QR code center."""
        try:
            # Download or load logo
            if style.logo_url:
                logo_img = await self._download_logo(style.logo_url)
            elif style.logo_path:
                # Handle BytesIO object from in-memory upload
                if isinstance(style.logo_path, io.BytesIO):
                    style.logo_path.seek(0)
                    logo_img = Image.open(style.logo_path).convert('RGBA')
                else:
                    logo_img = Image.open(style.logo_path).convert('RGBA')
            else:
                return qr_img
            
            # Calculate logo size
            qr_size = qr_img.size[0]
            logo_size = int(qr_size * style.logo_size_ratio)
            
            # Resize logo
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create circular mask for logo
            mask = Image.new('L', (logo_size, logo_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, logo_size, logo_size), fill=255)
            
            # Apply mask to logo
            logo_img.putalpha(mask)
            
            # Create white background circle
            logo_bg = Image.new('RGBA', (logo_size + 20, logo_size + 20), (255, 255, 255, 255))
            logo_bg_mask = Image.new('L', (logo_size + 20, logo_size + 20), 0)
            draw_bg = ImageDraw.Draw(logo_bg_mask)
            draw_bg.ellipse((0, 0, logo_size + 20, logo_size + 20), fill=255)
            logo_bg.putalpha(logo_bg_mask)
            
            # Calculate position to center the logo
            qr_center = (qr_size // 2, qr_size // 2)
            bg_pos = (qr_center[0] - (logo_size + 20) // 2, qr_center[1] - (logo_size + 20) // 2)
            logo_pos = (qr_center[0] - logo_size // 2, qr_center[1] - logo_size // 2)
            
            # Paste background and logo
            qr_img = qr_img.convert('RGBA')
            qr_img.paste(logo_bg, bg_pos, logo_bg)
            qr_img.paste(logo_img, logo_pos, logo_img)
            
            return qr_img.convert('RGB')
            
        except Exception as e:
            logger.warning(f"Failed to add logo: {str(e)}")
            return qr_img
    
    async def _download_logo(self, url: str) -> Image.Image:
        """Download logo from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > settings.MAX_LOGO_SIZE_MB * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Logo file too large")
            
            return Image.open(io.BytesIO(response.content)).convert('RGBA')
    
    async def save_uploaded_logo(self, logo_file: UploadFile) -> Optional[io.BytesIO]:
        """Process uploaded logo file in memory without saving to disk."""
        try:
            # Validate file
            if not logo_file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Check file size
            content = await logo_file.read()
            if len(content) > settings.MAX_LOGO_SIZE_MB * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Logo file too large")
            
            # Validate file extension
            file_extension = os.path.splitext(logo_file.filename)[1].lower()
            if file_extension not in settings.ALLOWED_LOGO_EXTENSIONS:
                raise HTTPException(status_code=400, detail="Unsupported file format")
            
            # Return the image content as BytesIO for in-memory processing
            return io.BytesIO(content)
            
        except Exception as e:
            logger.warning(f"Failed to process uploaded logo: {str(e)}")
            return None

    def _parse_color(self, color: str) -> tuple:
        """Parse color string to RGB tuple."""
        try:
            if color.startswith('#'):
                return getcolor(color, 'RGB')
            else:
                # Named colors
                color_map = {
                    'black': (0, 0, 0),
                    'white': (255, 255, 255),
                    'red': (255, 0, 0),
                    'green': (0, 255, 0),
                    'blue': (0, 0, 255),
                    'yellow': (255, 255, 0),
                    'purple': (128, 0, 128),
                    'orange': (255, 165, 0),
                    'pink': (255, 192, 203),
                    'brown': (165, 42, 42),
                    'gray': (128, 128, 128)
                }
                return color_map.get(color.lower(), (0, 0, 0))
        except Exception:
            return (0, 0, 0)
    
    def _apply_rounded_corners(self, img: Image.Image) -> Image.Image:
        """Apply rounded corners to image."""
        try:
            size = img.size
            radius = size[0] // 20  # 5% radius
            
            # Create mask
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
            
            # Apply mask
            img = img.convert('RGBA')
            img.putalpha(mask)
            
            # Create background
            background = Image.new('RGB', size, (255, 255, 255))
            background.paste(img, (0, 0), img)
            
            return background
        except Exception:
            return img
    
    def _apply_circle_shape(self, img: Image.Image) -> Image.Image:
        """Apply circular shape to image."""
        try:
            size = img.size
            
            # Create circular mask
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            
            # Apply mask
            img = img.convert('RGBA')
            img.putalpha(mask)
            
            # Create background
            background = Image.new('RGB', size, (255, 255, 255))
            background.paste(img, (0, 0), img)
            
            return background
        except Exception:
            return img
    
    def _apply_diamond_shape(self, img: Image.Image) -> Image.Image:
        """Apply diamond shape to image."""
        try:
            size = img.size
            
            # Create diamond mask
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            
            # Diamond coordinates
            center = size[0] // 2
            points = [
                (center, 10),  # top
                (size[0] - 10, center),  # right
                (center, size[1] - 10),  # bottom
                (10, center)  # left
            ]
            draw.polygon(points, fill=255)
            
            # Apply mask
            img = img.convert('RGBA')
            img.putalpha(mask)
            
            # Create background
            background = Image.new('RGB', size, (255, 255, 255))
            background.paste(img, (0, 0), img)
            
            return background
        except Exception:
            return img
    
    def _apply_gradient(self, img: Image.Image, style: QRCodeStyle) -> Image.Image:
        """Apply gradient effect to QR code."""
        try:
            size = img.size
            
            # Create gradient overlay
            gradient = Image.new('RGB', size, (255, 255, 255))
            
            for y in range(size[1]):
                # Calculate gradient factor
                factor = y / size[1]
                
                # Interpolate colors
                start_color = self._parse_color(style.fill_color)
                end_color = self._parse_color(style.back_color)
                
                r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)
                
                # Draw gradient line
                draw = ImageDraw.Draw(gradient)
                draw.line([(0, y), (size[0], y)], fill=(r, g, b))
            
            # Blend with original image
            img = img.convert('RGB')
            return Image.blend(img, gradient, 0.3)
        except Exception:
            return img
