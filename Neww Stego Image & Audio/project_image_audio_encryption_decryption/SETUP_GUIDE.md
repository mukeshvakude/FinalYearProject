# Steganography Project - Complete Setup Guide

## 📁 Final Project Structure

```
project_image_audio_encryption_decryption/
│
├── backend/                           # Flask Python Backend
│   ├── mySite.py                     # Main Flask API application
│   ├── supportFile.py                # Steganography encoding/decoding
│   ├── requirements.txt              # Python dependencies
│   ├── README.md                     # Backend documentation
│   ├── users.csv                     # User credentials
│   ├── secrets.csv                   # Encryption secrets
│   ├── templates/                    # Original HTML (no longer used)
│   ├── static/                       # Static files (images, CSS)
│   │   ├── images/                  # Image assets
│   │   └── css/                     # Stylesheets
│   ├── uploads/                      # Uploaded image files
│   ├── upload_audio/                 # Uploaded audio files
│   └── venv/                         # Virtual environment (optional)
│
├── frontend/                          # React JS Frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── Layout.jsx          # Navigation & layout
│   │   │   ├── Layout.css
│   │   │   ├── Login.jsx           # Login page
│   │   │   ├── Home.jsx            # Home page
│   │   │   ├── Info.jsx            # About page
│   │   │   ├── Encryption.jsx      # Message encryption
│   │   │   ├── Components.css      # Component styles
│   │   │   ├── Decryption.jsx      # Message decryption
│   │   │   └── PrivateRoute.jsx    # Protected routes
│   │   ├── services/
│   │   │   └── apiService.js       # Flask API calls
│   │   ├── css/                    # Global styles
│   │   │   └── w3.css             # W3.CSS framework
│   │   ├── App.jsx                 # Main app with routing
│   │   ├── main.jsx                # React entry point
│   │   └── index.css               # Global styles
│   ├── public/
│   │   ├── images/                 # Static images
│   │   └── vite.svg
│   ├── package.json                # NPM dependencies
│   ├── vite.config.js              # Vite configuration
│   ├── index.html                  # HTML template
│   ├── README.md                   # Frontend documentation
│   └── node_modules/               # NPM packages
│
└── README.md (this file)            # Setup guide
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed and in PATH
- **Node.js 16+** and npm installed
- **Git** (optional, for version control)

### 1. Backend Setup (Flask)

#### Step 1: Navigate to backend directory
```bash
cd backend
```

#### Step 2: Create virtual environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Flask server
```bash
python mySite.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5001
 * WARNING in use a production WSGI server
```

The backend server is now running on `http://localhost:5001`

---

### 2. Frontend Setup (React)

#### Step 1: Navigate to frontend directory (In a new terminal)
```bash
cd frontend
```

#### Step 2: Install dependencies
```bash
npm install
```

#### Step 3: Run the development server
```bash
npm run dev
```

**Expected output:**
```
VITE v... dev server running at:

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

The frontend application is now running on `http://localhost:5173`

---

## 🌐 Access the Application

### In Your Browser:
1. Open **[http://localhost:5173](http://localhost:5173)**
2. You'll see the login page

### Default Credentials:
- **Username**: `admin`
- **Password**: `admin`
- **Encryption Password**: Any password you want (e.g., `secret123`)

---

## 📡 How Frontend and Backend Communicate

### Architecture

```
┌─────────────────────────────────────────┐
│         React Frontend                  │
│    (http://localhost:5173)              │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Browser/React Components      │   │
│  │  - Login.jsx                    │   │
│  │  - Home.jsx                     │   │
│  │  - Encryption.jsx               │   │
│  │  - Decryption.jsx               │   │
│  └────────────┬────────────────────┘   │
│               │                        │
│  ┌────────────▼─────────────────────┐  │
│  │  axioscall -> apiService.js      │  │
│  │  (with withCredentials: true)    │  │
│  └────────────┬────────────────────┘  │
└───────────────┼──────────────────────────┘
                │ HTTP Requests/Responses
                │ (JSON format)
┌───────────────▼──────────────────────────┐
│       Flask Backend API                  │
│   (http://localhost:5001/api)            │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  REST API Endpoints              │   │
│  │  - POST /api/login               │   │
│  │  - POST /api/logout              │   │
│  │  - GET /api/home                 │   │
│  │  - GET /api/info                 │   │
│  │  - POST /api/upload              │   │
│  │  - POST /api/hide                │   │
│  │  - GET /api/session              │   │
│  └──────────────┬───────────────────┘   │
│                 │                       │
│  ┌──────────────▼───────────────────┐   │
│  │ Business Logic (Python)          │   │
│  │  - AES Encryption (pyaes)        │   │
│  │  - Image Processing (OpenCV)     │   │
│  │  - LSB Steganography             │   │
│  │  - File handling                 │   │
│  │  - Session Management            │   │
│  └──────────────┬───────────────────┘   │
│                 │                       │
│  ┌──────────────▼───────────────────┐   │
│  │ Data Storage                     │   │
│  │  - users.csv (credentials)       │   │
│  │  - secrets.csv (passwords)       │   │
│  │  - uploads/ (image files)        │   │
│  │  - upload_audio/ (audio files)   │   │
│  │  - static/ (images, CSS)         │   │
│  └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

### Communication Flow - Login Example

```
1. User enters credentials in React Login form
   └─> Browser sends HTTP POST request

2. apiService.js sends JSON data
   └─> POST http://localhost:5001/api/login
   └─> Body: { username: "admin", password: "admin", epass: "secret123" }

3. Flask backend receives request in mySite.py
   └─> @app.route('/api/login', methods=['POST'])
   └─> Validates credentials against users.csv
   └─> Creates session
   └─> Saves encryption password to secrets.csv

4. Flask returns JSON response
   └─> { success: true, user: "admin", message: "Login successful" }

5. React component receives response
   └─> Stores user in localStorage
   └─> Redirects to /home page

6. All subsequent requests include session cookie (withCredentials: true)
   └─> Browser automatically sends session on all requests
   └─> Backend validates session on protected routes
```

---

## 📝 API Endpoints Reference

### Authentication Endpoints

#### Login
- **URL**: `POST /api/login`
- **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "admin",
    "epass": "encryption_password"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Login successful",
    "user": "admin"
  }
  ```

#### Logout
- **URL**: `POST /api/logout`
- **Response**:
  ```json
  {
    "success": true,
    "message": "Logout successful"
  }
  ```

#### Check Session
- **URL**: `GET /api/session`
- **Response**:
  ```json
  {
    "authenticated": true,
    "user": "admin"
  }
  ```

### Content Endpoints

#### Get Home Content
- **URL**: `GET /api/home`
- **Response**: JSON with introduction, about, and architecture info

#### Get Info Content
- **URL**: `GET /api/info`
- **Response**: JSON with abstract and motivation info

### File Operations

#### Upload Files
- **URL**: `POST /api/upload`
- **Form Data**:
  - `filetype`: "image" | "audio"
  - `photo`: File (for image)
  - `photo1`: File (for image)
  - `audiofile`: File (for audio)

#### Hide Message
- **URL**: `POST /api/hide`
- **Request Body**:
  ```json
  {
    "message": "Secret message to hide",
    "filetype": "image"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Message hidden successfully",
    "cipher": "encrypted_hex_string"
  }
  ```

---

## 🔐 Session & Authentication

### How Sessions Work

1. **Session Cookies**: Flask uses server-side sessions stored in-memory
2. **httponly Cookies**: Session cookies are automatically sent by the browser
3. **CORS Enabled**: Flask-CORS handles cross-origin requests
4. **withCredentials**: Axios is configured to send credentials with each request

### Authentication Flow

```
Login → Session created → Cookie stored → Protected routes check session → Logout → Cookie deleted
```

---

## 🛠️ Troubleshooting

### Issue 1: "Backend is not responding" or CORS Error

**Causes:**
- Backend server not running
- Wrong port number
- Firewall blocking connection

**Solution:**
```bash
# Check if backend is running
# Terminal 1 should show:
#  * Running on http://0.0.0.0:5001

# If not running, go to backend folder and:
python mySite.py
```

### Issue 2: "Cannot find module" errors on Frontend

**Causes:**
- Dependencies not installed
- Node modules corrupted

**Solution:**
```bash
# Delete node_modules and package-lock.json
rm -r node_modules  # (or del node_modules on Windows)
rm package-lock.json  # (or del package-lock.json on Windows)

# Reinstall
npm install
npm run dev
```

### Issue 3: Images not showing on Frontend

**Causes:**
- Images not copied to public folder
- Wrong image paths

**Solution:**
```bash
# Verify images exist in frontend/public/images/
# Check paths in React components match:
# /images/test_image.png (correct)
# images/test_image.png (incorrect - missing /)
```

### Issue 4: "Module not found" for CSS imports

**Causes:**
- CSS file not in correct location
- Incorrect import path

**Solution:**
```jsx
// Correct imports
import '../css/w3.css';           // w3.css in src/css/
import '../components/Layout.css'; // Layout.css in src/components/
```

---

## 📊 File Upload & Processing Flow

### Image Upload Example

```
User selects images in Encryption.jsx
         │
         ▼
React state updates (images preview)
         │
         ▼
User clicks "Upload" button
         │
         ▼
fileService.uploadFiles() called
         │
         ▼
axios POST to /api/upload
   FormData contains: filetype="image", photo, photo1
         │
         ▼
Flask @app.route('/api/upload') 
   Saves files to uploads/ folder
   Resizes images using OpenCV
   Writes to static/images/test_image.png
         │
         ▼
Returns JSON success response
         │
         ▼
React displays success message
Frontend displays images: /images/test_image.png
```

---

## 🔄 Message Encryption Flow

```
User enters message and clicks "Hide"
         │
         ▼
Encryption component validates input
         │
         ▼
fileService.hideMessage() called
   axios POST /api/hide
   Body: { message: "secret text", filetype: "image" }
         │
         ▼
Flask backend receives request
   Retrieves encryption password from session
   Derives AES-256 key using PBKDF2
   Encrypts message with AES-CTR mode
         │
         ▼
LSB Steganography encoding
   Embeds encrypted bytes into image pixels
   Creates stegoImage.png
         │
         ▼
Returns cipher text and confirmation
         │
         ▼
React displays:
   - Cipher text (for archival/decryption)
   - Stego image (/images/stegoImage.png)
```

---

## 📦 Dependencies

### Backend (Python)
- `Flask 2.3.3` - Web framework
- `Flask-CORS 4.0.0` - Cross-origin support
- `opencv-python` - Image processing
- `Pillow` - Image manipulation
- `pyaes` - AES encryption
- `pbkdf2` - Key derivation
- `pandas` - CSV data handling

### Frontend (JavaScript)
- `react` - UI library
- `react-router-dom` - Client routing
- `axios` - HTTP client
- `vite` - Build tool

---

## 🚀 Production Deployment

### Backend (Flask)
For production, use a proper WSGI server:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 mySite:app
```

### Frontend (React)
Build for production:

```bash
cd frontend
npm run build

# This creates dist/ folder with optimized files
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Axios Documentation](https://axios-http.com/)
- [W3.CSS Documentation](https://www.w3schools.com/w3css/)

---

## 📝 Notes

1. **Security**: The current implementation uses hardcoded IV and salt for demo purposes. In production, use random values and proper key management.

2. **Session Management**: Sessions are stored in Flask's memory. For production, use Redis or a database session backend.

3. **CORS**: Currently allows all origins. In production, restrict to your frontend domain.

4. **File Uploads**: Files are stored in the `uploads/` and `upload_audio/` directories. Implement proper cleanup and size limits in production.

5. **Database**: Currently uses CSV files. Consider migrating to SQLite or PostgreSQL for production.

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend runs on http://localhost:5001
- [ ] Frontend runs on http://localhost:5173
- [ ] Can login with admin/admin
- [ ] Can upload images
- [ ] Can hide messages
- [ ] View cipher text
- [ ] Logout works

---

**Created**: February 2026  
**Project**: Steganography - Multi-Image & Audio Encryption/Decryption  
**Architecture**: Separated React Frontend + Flask Backend API
