# Flask Backend - Steganography API

## Overview
This is the REST API backend for the Steganography application. It handles user authentication, file uploads, encryption, and image/audio steganography operations.

## Project Structure
```
backend/
├── mySite.py              # Main Flask application with REST API endpoints
├── supportFile.py         # Steganography encoding/decoding functions
├── requirements.txt       # Python dependencies
├── users.csv             # User credentials (created automatically)
├── secrets.csv          # Encryption passwords
├── static/              # Static files (CSS, images)
├── templates/           # Original HTML templates (no longer used)
├── uploads/             # Uploaded image files
└── upload_audio/        # Uploaded audio files
```

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

## Running the Backend

### Start the Flask Server
```bash
python mySite.py
```

The server will start on `http://localhost:5001`

## API Endpoints

### Authentication
- **POST `/api/login`** - User login
  - Request body: `{ "username": "string", "password": "string", "epass": "string" }`
  - Response: `{ "success": bool, "message": "string", "user": "string" }`

- **POST `/api/logout`** - User logout
  - Response: `{ "success": bool, "message": "string" }`

- **GET `/api/session`** - Check authentication status
  - Response: `{ "authenticated": bool, "user": "string" (optional) }`

### Content APIs
- **GET `/api/home`** - Get home page content
  - Response: JSON with introduction, about, and architecture info

- **GET `/api/info`** - Get info/about page content
  - Response: JSON with abstract and motivation

### File Operations
- **POST `/api/upload`** - Upload image or audio files
  - Form data: `filetype` (image/audio), `photo`, `photo1` (for images), `audiofile` (for audio)
  - Response: `{ "success": bool, "message": "string" }`

- **POST `/api/hide`** - Encrypt and hide message
  - Request body: `{ "message": "string", "filetype": "image|audio" }`
  - Response: `{ "success": bool, "message": "string", "cipher": "string" }`

### Health Check
- **GET `/api/health`** - Check API status
  - Response: `{ "status": "ok" }`

## Default Credentials
- **Username**: `admin`
- **Password**: `admin`
- **Encryption Password**: Any string (set during login)

## CORS Configuration
CORS is enabled for all origins to allow the React frontend to communicate with this API.

## Security Notes
- The IV and salt values are hardcoded for demo purposes only
- In production, use secure key derivation and random IVs
- Use HTTPS in production environments
- Implement proper authentication with JWT or similar

## Dependencies
- Flask 2.3.3 - Web framework
- Flask-CORS 4.0.0 - Cross-origin resource sharing
- OpenCV (opencv-python) - Image processing
- Pillow - Image manipulation
- pyaes - AES encryption
- pbkdf2 - Key derivation
- pandas - CSV data handling
