# FastAPI UPI Payment QR Code Generator

A production-ready, high-performance QR code generation service built with FastAPI, featuring advanced styling options, logo integration, and comprehensive UPI payment support.

## ✨ Features

- **🎯 Advanced QR Code Generation**: Multiple styles (square, circle, rounded, diamond)
- **🎨 Custom Styling**: Colors, gradients, logos, and size customization
- **💳 UPI Payment Support**: Full UPI specification compliance
- **🚀 High Performance**: Async/await, optimized image processing
- **🔒 Production Ready**: Rate limiting, logging, error handling
- **📱 Responsive UI**: Modern web interface with real-time preview
- **🔧 Developer Friendly**: Comprehensive API documentation
- **🌐 CORS Support**: Cross-origin request handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or pipenv

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-upi-payment-qr
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   # Development mode
   python main.py
   
   # Or using uvicorn directly
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - Web UI: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📋 API Endpoints

### Generate Simple QR Code
```bash
GET /api/genqr?name=John%20Doe&id=john@paytm&amount=100
```

### Generate Advanced QR Code
```bash
GET /api/qrgen?upiid=john@paytm&name=John%20Doe&amount=100&size=500&fill_color=blue&style=rounded
```

### Generate with Full Customization
```bash
POST /api/generate
Content-Type: application/json

{
  "upi_id": "john@paytm",
  "name": "John Doe",
  "amount": 100,
  "size": 500,
  "fill_color": "#0066cc",
  "style": "rounded",
  "gradient": true
}
```

### Get Available Styles
```bash
GET /api/styles
```

## 🎨 Styling Options

### QR Code Styles
- **Square**: Standard square QR code
- **Circle**: Circular QR code elements
- **Rounded**: Rounded corners
- **Diamond**: Diamond-shaped QR code

### Color Options
- Hex colors: `#ff0000`, `#00ff00`
- Named colors: `red`, `blue`, `green`
- RGB values: `rgb(255,0,0)`

### Logo Integration
- URL-based logos: `logo_url` parameter
- File upload: POST endpoint with multipart form data
- Automatic sizing and positioning
- Circular masking for professional appearance

## 🔧 Configuration

### Environment Variables

```bash
# Application
DEBUG=True
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# QR Code Settings
QR_CODE_DEFAULT_SIZE=300
QR_CODE_DEFAULT_BORDER=4
QR_CODE_DEFAULT_BOX_SIZE=10

# File Upload
MAX_LOGO_SIZE_MB=5
ALLOWED_LOGO_EXTENSIONS=[".png", ".jpg", ".jpeg", ".gif", ".svg"]

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## 🏗️ Architecture

### Project Structure
```
fastapi-upi-payment-qr/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── qr_routes.py   # QR code generation endpoints
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── rate_limiter.py    # Rate limiting
│   │   └── logging.py         # Request logging
│   └── services/
│       ├── __init__.py
│       ├── qr_generator.py    # QR code generation logic
│       └── upi_validator.py   # UPI validation
├── templates/
│   ├── index.html         # Main web interface
│   └── api.html          # API documentation
├── static/
│   ├── uploads/          # Uploaded logos
│   └── generated/        # Generated QR codes
└── logs/                 # Application logs
```

### Key Components

1. **QR Code Generator**: Advanced QR code generation with multiple libraries
2. **UPI Validator**: Comprehensive UPI ID and payment validation
3. **Rate Limiter**: In-memory rate limiting for API protection
4. **Logging Middleware**: Request/response logging with correlation IDs
5. **Configuration Management**: Environment-based configuration

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables for Production

```bash
DEBUG=False
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret-key
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Comprehensive validation of all inputs
- **CORS Protection**: Configurable cross-origin policies
- **File Upload Security**: Size and type restrictions
- **Error Handling**: Secure error messages without sensitive info

## 📊 Performance

- **Async Processing**: Non-blocking I/O operations
- **Image Optimization**: Efficient image processing
- **Memory Management**: Proper cleanup of image resources
- **Caching**: In-memory caching for frequently accessed data

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📚 API Documentation

- **Interactive Docs**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc` (Alternative documentation)
- **OpenAPI Schema**: `/openapi.json`
- **Custom Docs**: `/api` (Styled documentation)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- PIL/Pillow for image processing
- qrcode and segno libraries for QR code generation
- The Python community for amazing libraries

## 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Made with ❤️ and Python**
