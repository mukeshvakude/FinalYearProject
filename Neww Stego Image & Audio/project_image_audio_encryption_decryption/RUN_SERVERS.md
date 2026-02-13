# How to Run Both Servers

This guide will help you start the Flask backend and React frontend servers.

## Prerequisites

Ensure you have installed all dependencies:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Method 1: Using Provided Scripts (Windows)

### Option 1A: Both in One Command

```bash
# From project root
start_servers.bat
```

This runs:
- Flask backend on `http://localhost:5001`
- React frontend on `http://localhost:5173`

### Option 1B: Separate PowerShell Windows

```bash
# Terminal 1: Backend
./start_servers.bat
```

```bash
# Terminal 2: Frontend (in separate PowerShell)
./start_frontend.ps1
```

---

## Method 2: Manual Terminal Commands

### Terminal 1: Start Flask Backend

```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5001
 * Debug mode: off
```

### Terminal 2: Start React Frontend

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

---

## Method 3: Using VS Code Terminal

### Setup

1. Open VS Code with workspace folder
2. Open integrated terminal: `Ctrl + ~`
3. Split terminal: Click split icon or `Ctrl + \`

### Terminal 1: Backend
```
cd backend
python app.py
```

### Terminal 2: Frontend
```
cd frontend  
npm run dev
```

---

## Access the Application

Once both servers are running:

1. **Frontend**: Open http://localhost:5173 in browser
2. **Backend API**: http://localhost:5001/api/
3. **Health Check**: http://localhost:5001/api/health

---

## Testing the Integration

### 1. Register New User
```bash
curl -X POST http://localhost:5001/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "epass": "encryptionpass"
  }'
```

Expected response (201):
```json
{
  "success": true,
  "user": "testuser",
  "message": "User registered successfully. Please enroll your face...",
  "next_step": "face_enrollment"
}
```

### 2. Login User
```bash
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "epass": "encryptionpass"
  }'
```

---

## Troubleshooting

### Backend issues

**Port already in use (5001)**
```bash
# Find process using port 5001
netstat -ano | findstr :5001

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port - modify in backend/app.py line: app.run(port=5002)
```

**Face recognition library error**
```bash
# Install dlib wheel (pre-built, faster)
pip install backend/dlib-20.0.0-cp312-cp312-win_amd64.whl
pip install face-recognition
```

**Missing dependencies**
```bash
pip install -r backend/requirements.txt --upgrade
```

### Frontend issues

**Port already in use (5173)**
```bash
# Kill process or change port in vite.config.js
```

**Node modules issue**
```bash
cd frontend
rm -r node_modules package-lock.json
npm install
```

**Module not found errors**
```bash
npm install
npm run dev
```

---

## Stopping Servers

### In Terminals
Press `Ctrl + C` in each terminal

### Kill Processes (if stuck)
```bash
# Kill Python Flask
taskkill /F /IM python.exe

# Kill Node  
taskkill /F /IM node.exe
```

---

## Checking Server Status

### Backend Health
```bash
curl http://localhost:5001/api/health
```

Should return:
```json
{"status": "healthy", "timestamp": "...", "service": "Steganography API"}
```

### Frontend Status
Visit http://localhost:5173 in browser

---

## Server Logs

### Backend Logs
Location: `backend/logs/steganography.log`

View real-time:
```bash
# Windows PowerShell
Get-Content backend/logs/steganography.log -Wait
```

### Frontend Logs
Check browser Console: `F12` or `Ctrl + Shift + I`

---

## Complete Project Structure

```
project_root/
├── backend/
│   ├── app.py                          (Main Flask app)
│   ├── config.py                       (Configuration)
│   ├── requirements.txt                (Python dependencies)
│   ├── services/
│   │   ├── auth_service.py             (User authentication)
│   │   ├── face_auth_service.py        (Face recognition)
│   │   ├── face_database_manager.py    (Face data storage)
│   │   ├── encryption_service.py       (AES encryption)
│   │   └── steganography_service.py    (LSB encoding)
│   ├── users.csv                       (User database)
│   ├── faces.csv                       (Face encodings database)
│   └── logs/                           (Application logs)
│
├── frontend/
│   ├── package.json                    (Dependencies)
│   ├── vite.config.js                  (Vite config)
│   ├── src/
│   │   ├── App.jsx                     (Main component)
│   │   ├── components/
│   │   │   ├── Login.jsx               (Login form)
│   │   │   ├── Home.jsx                (Home page)
│   │   │   ├── Encryption.jsx          (Hide message)
│   │   │   ├── Decryption.jsx          (Recover message)
│   │   │   └── FaceAuth.jsx            (Face authentication)
│   │   └── services/
│   │       └── apiService.js           (API calls)
│   └── public/                         (Static assets)
│
├── start_servers.bat                   (Windows batch script)
├── start_frontend.ps1                  (PowerShell script)
└── README.md                           (Project overview)
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start both | `start_servers.bat` |
| Start backend only | `cd backend && python app.py` |
| Start frontend only | `cd frontend && npm run dev` |
| Check backend health | `curl http://localhost:5001/api/health` |
| Backend logs | `type backend\logs\steganography.log` |
| Stop all | `Ctrl + C` in terminals |
| Kill stuck process | `taskkill /F /IM python.exe` |

---

## Environment Variables (Optional)

Create `.env` file in backend directory:

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
DATABASE_USERS=users.csv
DATABASE_FACES=faces.csv
FACE_RECOGNITION_ENABLED=True
FACE_RECOGNITION_TOLERANCE=0.6
```

---

## Additional Notes

- **Session Cookie**: Automatically managed by Flask
- **CORS**: Enabled for localhost:5173 to localhost:5001
- **Database**: CSV-based, stays in `backend/` directory
- **Face Images**: Stored in `backend/face_data/` folder
- **Logs**: Stored in `backend/logs/` folder

Both servers are now ready to run! Start them and access http://localhost:5173 to begin.
