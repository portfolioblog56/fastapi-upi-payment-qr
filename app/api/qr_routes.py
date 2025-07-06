import io
import base64
import traceback
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger

from app.services.qr_generator import QRCodeGenerator, QRCodeStyle
from app.services.upi_validator import UPIValidator

router = APIRouter()
qr_generator = QRCodeGenerator()
upi_validator = UPIValidator()


class QRGenerationRequest(BaseModel):
    """Request model for advanced QR code generation."""
    upi_id: Optional[str] = Field(None, description="UPI ID for payment")
    name: str = Field(..., description="Payee name", min_length=1, max_length=100)
    amount: Optional[float] = Field(None, description="Payment amount", ge=0, le=1000000)
    account_number: Optional[str] = Field(None, description="Bank account number")
    ifsc_code: Optional[str] = Field(None, description="IFSC code")
    size: Optional[int] = Field(300, description="QR code size", ge=100, le=1000)
    border: Optional[int] = Field(4, description="QR code border", ge=0, le=20)
    box_size: Optional[int] = Field(10, description="QR code box size", ge=1, le=50)
    fill_color: Optional[str] = Field("black", description="Fill color")
    back_color: Optional[str] = Field("white", description="Background color")
    logo_url: Optional[str] = Field(None, description="URL to logo image")
    logo_size_ratio: Optional[float] = Field(0.3, description="Logo size ratio", ge=0.1, le=0.5)
    style: Optional[str] = Field("square", description="QR code style")
    gradient: Optional[bool] = Field(False, description="Enable gradient effect")


class QRResponse(BaseModel):
    """Response model for QR code generation."""
    qr_code_data_url: str = Field(..., description="Base64 encoded QR code image")
    upi_string: str = Field(..., description="Generated UPI payment string")
    size: int = Field(..., description="QR code size")
    format: str = Field(..., description="Image format")


@router.get("/genqr", response_model=QRResponse)
async def generate_qr_simple(
    name: str = Query(..., description="Payee name"),
    id: str = Query(..., description="UPI ID", alias="id"),
    amount: Optional[float] = Query(None, description="Payment amount"),
    size: Optional[int] = Query(300, description="QR code size"),
    format: Optional[str] = Query("png", description="Image format")
):
    """Generate a simple QR code for UPI payment."""
    try:
        logger.info(f"Generating QR code for UPI ID: {id}, Name: {name}")
        
        # Validate UPI ID
        if not upi_validator.validate_upi_id(id):
            raise HTTPException(status_code=400, detail="Invalid UPI ID format")
        
        # Create UPI payment string
        upi_string = f"upi://pay?pa={id}&pn={name}"
        if amount:
            upi_string += f"&am={amount}"
        
        # Generate QR code
        qr_buffer = await qr_generator.generate_qr_code(
            data=upi_string,
            style=QRCodeStyle(size=size or 300, format=format or "png")
        )
        
        # Convert to base64
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        data_url = f"data:image/{format or 'png'};base64,{qr_base64}"
        
        return QRResponse(
            qr_code_data_url=data_url,
            upi_string=upi_string,
            size=size or 300,
            format=format or "png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"QR generation failed: {str(e)}")


@router.get("/qrgen")
async def generate_qr_advanced(
    upiid: Optional[str] = Query(None, description="UPI ID"),
    name: str = Query(..., description="Payee name"),
    amount: Optional[float] = Query(None, description="Payment amount"),
    ifsccode: Optional[str] = Query(None, description="IFSC code"),
    accountnum: Optional[str] = Query(None, description="Account number"),
    size: Optional[int] = Query(300, description="QR code size"),
    fill_color: Optional[str] = Query("black", description="Fill color"),
    back_color: Optional[str] = Query("white", description="Background color"),
    logo_url: Optional[str] = Query(None, description="Logo URL"),
    style: Optional[str] = Query("square", description="QR code style"),
    format: Optional[str] = Query("png", description="Image format")
):
    """Generate an advanced QR code with styling options."""
    try:
        logger.info(f"Generating advanced QR code for: {name}")
        
        # Validate size parameter
        if size and (size < 100 or size > 1000):
            raise HTTPException(status_code=400, detail="Size must be between 100 and 1000 pixels")
        
        # Create UPI payment string
        if upiid and name:
            if not upi_validator.validate_upi_id(upiid):
                raise HTTPException(status_code=400, detail="Invalid UPI ID format")
            upi_string = f"upi://pay?pa={upiid}&pn={name}"
        elif ifsccode and accountnum and name:
            if not upi_validator.validate_ifsc(ifsccode):
                raise HTTPException(status_code=400, detail="Invalid IFSC code format")
            upi_string = f"upi://pay?pa={accountnum}@{ifsccode}.ifsc.npci&pn={name}"
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either UPI ID or both IFSC code and account number must be provided"
            )
        
        if amount:
            upi_string += f"&am={amount}"
        
        # Generate styled QR code
        qr_buffer = await qr_generator.generate_qr_code(
            data=upi_string,
            style=QRCodeStyle(
                size=size or 300,
                fill_color=fill_color or "black",
                back_color=back_color or "white",
                logo_url=logo_url,
                style=style or "square",
                format=format or "png"
            )
        )
        
        # Return as image
        qr_buffer.seek(0)
        return StreamingResponse(
            io.BytesIO(qr_buffer.getvalue()),
            media_type=f"image/{format or 'png'}",
            headers={"Content-Disposition": f"inline; filename=qr_code.{format or 'png'}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating advanced QR code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"QR generation failed: {str(e)}")


@router.post("/generate")
async def generate_qr_post(qr_request: QRGenerationRequest):
    """Generate QR code with full customization options."""
    try:
        logger.info(f"Generating custom QR code for: {qr_request.name}")
        
        # Validate input
        if not qr_request.upi_id and not qr_request.account_number:
            raise HTTPException(
                status_code=400, 
                detail="Either UPI ID or account number must be provided"
            )
        
        # Create UPI payment string
        if qr_request.upi_id:
            if not upi_validator.validate_upi_id(qr_request.upi_id):
                raise HTTPException(status_code=400, detail="Invalid UPI ID format")
            upi_string = f"upi://pay?pa={qr_request.upi_id}&pn={qr_request.name}"
        else:
            if not upi_validator.validate_ifsc(qr_request.ifsc_code):
                raise HTTPException(status_code=400, detail="Invalid IFSC code format")
            upi_string = f"upi://pay?pa={qr_request.account_number}@{qr_request.ifsc_code}.ifsc.npci&pn={qr_request.name}"
        
        if qr_request.amount:
            upi_string += f"&am={qr_request.amount}"
        
        # Generate styled QR code
        qr_buffer = await qr_generator.generate_qr_code(
            data=upi_string,
            style=QRCodeStyle(
                size=qr_request.size,
                border=qr_request.border,
                box_size=qr_request.box_size,
                fill_color=qr_request.fill_color,
                back_color=qr_request.back_color,
                logo_url=qr_request.logo_url,
                logo_size_ratio=qr_request.logo_size_ratio,
                style=qr_request.style,
                gradient=qr_request.gradient
            )
        )
        
        # Convert to base64
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        data_url = f"data:image/png;base64,{qr_base64}"
        
        return QRResponse(
            qr_code_data_url=data_url,
            upi_string=upi_string,
            size=qr_request.size,
            format="png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating custom QR code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"QR generation failed: {str(e)}")


@router.get("/styles")
async def get_available_styles():
    """Get available QR code styles and options."""
    return {
        "styles": ["square", "circle", "rounded", "diamond"],
        "colors": [
            "black", "white", "red", "green", "blue", "yellow", 
            "purple", "orange", "pink", "brown", "gray"
        ],
        "formats": ["png", "jpeg"],
        "size_range": {"min": 100, "max": 1000, "default": 300},
        "logo_ratio_range": {"min": 0.1, "max": 0.5, "default": 0.3}
    }
