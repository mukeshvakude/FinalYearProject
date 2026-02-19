# SecureVision Stego

A full-stack steganography and face-verification application that lets authenticated users:

- **Encode** a secret message (AES-256-CBC encrypted) into an image via LSB steganography
- **Decode** the hidden message from a stego image
- **Verify** whether two face photographs belong to the same person using DeepFace AI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router v6, Axios |
| Backend | Node.js, Express 4, Mongoose, JWT, Jimp, Multer |
| Face Service | Python 3, Flask, DeepFace, TensorFlow, OpenCV |
| Database | MongoDB |
| Crypto | AES-256-CBC (Node.js `crypto`), bcryptjs |

---

## Folder Structure

```
securevision/
├── client/            React Vite frontend
│   └── src/
│       ├── pages/     LoginPage, RegisterPage, DashboardPage, EncodePage, DecodePage, FaceVerifyPage
│       ├── components/Navbar
│       ├── context/   AuthContext
│       └── utils/     api (Axios instance)
├── server/            Node.js / Express API
│   ├── middleware/    auth.js (JWT guard)
│   ├── models/        User.js
│   ├── routes/        auth.js  stego.js  face.js
│   ├── utils/         crypto.js (AES helpers)
│   └── uploads/       saved images (gitignored)
├── face-service/      Python DeepFace microservice
│   ├── app.py
│   └── requirements.txt
└── README.md
```

---

## Prerequisites

- **Node.js** ≥ 18
- **MongoDB** running locally (or provide a MONGO_URI)
- **Python** ≥ 3.9

---

## Installation

### 1. Server

```bash
cd securevision/server
cp .env.example .env          # edit values
npm install
```

### 2. Client

```bash
cd securevision/client
npm install
```

### 3. Face Service

```bash
cd securevision/face-service
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Environment Variables

### `server/.env`

| Variable | Description | Default |
|---|---|---|
| `PORT` | Express server port | `5000` |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/securevision` |
| `JWT_SECRET` | Secret for signing JWTs | — |
| `AES_SECRET` | 32-char key for AES-256-CBC | — |
| `FACE_SERVICE_URL` | Base URL of the face microservice | `http://localhost:8000` |

---

## Running

Open three terminals:

```bash
# Terminal 1 – API server
cd securevision/server && npm run dev

# Terminal 2 – React client (http://localhost:3000)
cd securevision/client && npm run dev

# Terminal 3 – Face microservice (http://localhost:8000)
cd securevision/face-service
source venv/bin/activate
python app.py
```

---

## API Routes

### Auth (`/api/auth`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Register new user |
| POST | `/api/auth/login` | — | Login, receive JWT |
| GET | `/api/auth/me` | ✅ Bearer | Get current user info |

### Steganography (`/api/stego`)

| Method | Path | Auth | Body / Fields | Description |
|---|---|---|---|---|
| POST | `/api/stego/encode` | ✅ Bearer | `image` (file), `message` (text) | AES-encrypt message and hide in image LSB; returns download URL |
| POST | `/api/stego/decode` | ✅ Bearer | `image` (file) | Extract and decrypt hidden message |

### Face Verification (`/api/face`)

| Method | Path | Auth | Fields | Description |
|---|---|---|---|---|
| POST | `/api/face/verify` | ✅ Bearer | `image1`, `image2` (files) | Forward to face-service, return match result |

### Face Service (direct)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/verify-face` | DeepFace comparison |

---

## Building for Production

```bash
# Build client static assets
cd securevision/client && npm run build

# The Express server can serve the built dist/ folder by adding:
# app.use(express.static(path.join(__dirname, '../client/dist')))
# before the catch-all route.
```

Set environment variables via your hosting provider's secrets manager.  
Never commit `.env` files to source control.
