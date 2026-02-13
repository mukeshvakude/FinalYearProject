# Face Recognition Authentication System

**Final Year Project: Secure Communication using Multi-Image Steganography and Face Recognition**

## Overview

This document describes the face recognition-based authentication system integrated with the steganography application. Face recognition is **mandatory** before any decryption operations are allowed.

## System Architecture

### Components

#### Backend (Python/Flask)

1. **face_auth_service.py** - Face recognition and encoding service
   - Face detection and encoding generation using `face_recognition` library
   - Face matching and comparison
   - Image quality validation
   - Landmark detection

2. **face_database_manager.py** - Face data management
   - Store/retrieve face encodings from CSV database
   - User enrollment and authentication tracking
   - Statistical analytics

3. **app.py** - Flask endpoints (in `/api/face/` namespace)
   - `/api/face/enroll` - Register user's face
   - `/api/face/verify` - Authenticate face before decryption
   - `/api/face/check-enrollment` - Check enrollment status
   - `/api/face/delete` - Remove enrollment
   - `/api/face/stats` - Get authentication history

#### Frontend (React)

1. **FaceEnrollment.jsx** - Face enrollment component
   - Webcam access and face capture
   - Live preview
   - Image quality feedback

2. **FaceVerification.jsx** - Face verification component
   - Real-time face verification
   - Match distance display
   - Multiple attempt support

3. **FaceAuth.jsx** - Main orchestrator component
   - Enrollment/verification workflow management
   - Status tracking
   - User statistics display

4. **Decryption.jsx** - Updated to require face auth
   - Checks face enrollment
   - Enforces face verification
   - Blocks decryption if not verified

5. **FaceAuth.css** - Styling for all face auth components

## Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- Webcam/camera device
- Modern web browser with WebRTC support

### Backend Setup

1. **Install Python dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

**New dependencies added:**
- `face-recognition==1.3.5` - Face encoding and recognition
- `dlib==19.24.2` - Deep learning library (required by face_recognition)
- `numpy==1.24.3` - Numerical computing
- `scipy==1.11.2` - Scientific computing
- `scikit-image==0.21.0` - Image processing

2. **Create face data directory:**

```bash
mkdir backend/face_data
```

3. **Update config.py:**

The configuration has been updated with face recognition settings:

```python
FACE_RECOGNITION_ENABLED = True
FACE_RECOGNITION_MODEL = 'large'       # 'small' or 'large' accuracy
FACE_RECOGNITION_TOLERANCE = 0.6       # Lower = stricter matching
FACE_UPLOAD_FOLDER = 'face_data'
DATABASE_FACES = 'faces.csv'           # Face enrollment database
```

4. **Start backend server:**

```bash
python app.py
# Server runs on http://localhost:5001
```

### Frontend Setup

1. **Install dependencies (already done):**

```bash
cd frontend
npm install
```

2. **Start development server:**

```bash
npm run dev
# Server runs on http://localhost:5173
```

## User Workflows

### 1. User Registration & Face Enrollment

**Sequence:**

1. User creates account with username and password
2. System prompts for face enrollment
3. User grants webcam permissions
4. System captures face image from webcam
5. Face quality is validated (lighting, face detection, etc.)
6. Face encoding is generated (128-dimensional vector)
7. Encoding is stored in `faces.csv` database
8. User receives confirmation

**API Calls:**

```javascript
// Frontend
const formData = new FormData();
formData.append('face_image', imageBlob, 'face.png');
const response = await fileService.enrollFace(formData);

// Backend
POST /api/face/enroll
Response: { success: true, message: "Face enrolled successfully", enrollment_time: "..." }
```

### 2. User Login with Face Verification

**Sequence:**

1. User logs in with username/password
2. System checks if face is enrolled
3. User is prompted to verify face (capture face image)
4. System compares captured face with enrolled face
5. If match successful → session marked as verified
6. If match fails → user can retry
7. Session persists until logout

**API Calls:**

```javascript
// Frontend
const formData = new FormData();
formData.append('face_image', capturedBlob, 'verify.png');
const response = await fileService.verifyFace(formData);

// Backend
POST /api/face/verify
Response: { 
  success: true, 
  distance: 0.45,
  tolerance: 0.6,
  message: "Face verified successfully"
}
```

### 3. Decryption with Face Authentication

**Sequence (Modified):**

1. User submits cipher text and password
2. **NEW:** System checks if face is enrolled
3. **NEW:** System checks if face is verified in session
4. If not verified → return error: "Face verification required"
5. If verified → proceed with decryption
6. Return decrypted message

**Example Error Response (Without Face Verification):**

```json
{
  "error": "Face verification required before decryption. Please verify your face."
}
```

## Face Encoding & Comparison

### Face Encoding

- **Model:** Deep Learning model from `face_recognition` library (based on ResNet)
- **Encoding:** 128-dimensional vector representing unique facial features
- **Generation:** Extracting facial landmarks and encoding patterns
- **Storage:** JSON-serialized arrays in CSV database

### Face Comparison

- **Distance Metric:** Euclidean distance between encodings
- **Tolerance Threshold:** 0.6 (default)
  - Distance < 0.6 → **Match**
  - Distance ≥ 0.6 → **No Match**
- **Strictness:** Adjustable via `Config.FACE_RECOGNITION_TOLERANCE`

### Quality Validation

Before face enrollment, system validates:

- ✓ **Face Detection:** At least one face visible
- ✓ **Brightness:** Adequate lighting (brightness 50-200)
- ✓ **Image Format:** PNG, JPG, JPEG, BMP supported
- ✓ **File Size:** Max 5 MB

## Database Schema

### faces.csv

```csv
username,face_encoding,enrollment_date,face_image_path,last_authenticated,authentication_count,encoding_version
alice,[0.12,0.45,-0.23,...128 values...],2024-02-13T10:30:00,face_data/alice_face_1707826200.png,2024-02-13T14:30:00,5,1.0
bob,[0.34,-0.12,0.56,...128 values...],2024-02-13T11:00:00,face_data/bob_face_1707826800.png,,,1.0
```

**Columns:**

- `username` - User identifier
- `face_encoding` - JSON array of 128 floats
- `enrollment_date` - ISO timestamp of enrollment
- `face_image_path` - Path to stored face image
- `last_authenticated` - ISO timestamp of last successful verification
- `authentication_count` - Number of successful authentications
- `encoding_version` - Model version used

## API Endpoints Reference

### 1. Enroll Face

```
POST /api/face/enroll
Content-Type: multipart/form-data

Body:
- face_image: [image file]

Response (200):
{
  "success": true,
  "message": "Face enrolled successfully",
  "username": "alice",
  "enrollment_time": "2024-02-13T10:30:00"
}

Error (400):
{
  "error": "No face detected in image. Please upload a clear face image."
}

Error (409):
{
  "error": "Face already enrolled for this user. Delete previous enrollment first."
}
```

### 2. Verify Face

```
POST /api/face/verify
Content-Type: multipart/form-data

Body:
- face_image: [image file]

Response (200):
{
  "success": true,
  "message": "Face verified successfully",
  "username": "alice",
  "distance": 0.45,
  "tolerance": 0.6,
  "verification_time": "2024-02-13T10:35:00"
}

Error (401 - Face Doesn't Match):
{
  "success": false,
  "message": "Face does not match enrolled face",
  "distance": 0.72,
  "tolerance": 0.6
}
```

### 3. Check Enrollment Status

```
GET /api/face/check-enrollment

Response (200):
{
  "username": "alice",
  "face_enrolled": true,
  "face_required": true,
  "stats": {
    "username": "alice",
    "enrolled": "2024-02-13T10:30:00",
    "last_authenticated": "2024-02-13T14:30:00",
    "authentication_count": 5,
    "encoding_version": "1.0"
  }
}
```

### 4. Delete Face Enrollment

```
POST /api/face/delete

Response (200):
{
  "success": true,
  "message": "Face enrollment deleted successfully",
  "username": "alice"
}
```

### 5. Get Face Statistics

```
GET /api/face/stats

Response (200):
{
  "success": true,
  "username": "alice",
  "face_stats": {
    "username": "alice",
    "enrolled": "2024-02-13T10:30:00",
    "last_authenticated": "2024-02-13T14:30:00",
    "authentication_count": 5,
    "encoding_version": "1.0"
  }
}
```

## Security Considerations

### Face Encoding Privacy

- ✓ Face encodings are 128-dimensional numerical arrays (not images)
- ✓ Cannot be reversed to recreate original face
- ✓ Stored securely in local database
- ✓ Do not transmit over network during verification

### Verification Flow

- ✓ Face verification must succeed before decryption allowed
- ✓ Verification tied to session (must re-verify after logout)
- ✓ Multiple verification attempts supported
- ✓ Failed attempts logged for security audit

### Tolerance Settings

- ⚠ Default tolerance: 0.6 (reasonable balance)
- **Stricter:** 0.4 - 0.5 (fewer false positives, more false negatives)
- **Lenient:** 0.7 - 0.8 (more false positives, easier to spoof)

## Configuration Options

### Backend Config (config.py)

```python
# Enable/disable face recognition
FACE_RECOGNITION_ENABLED = True

# Model accuracy: 'small' (faster) or 'large' (more accurate)
FACE_RECOGNITION_MODEL = 'large'

# Tolerance threshold (0.0 to 1.0)
# Lower = stricter matching
FACE_RECOGNITION_TOLERANCE = 0.6

# Directory for storing face images
FACE_UPLOAD_FOLDER = 'face_data'

# Database file for face encodings
DATABASE_FACES = 'faces.csv'

# Face encoding version (for model updates)
FACE_ENCODING_VERSION = '1.0'
```

## Adjusting Tolerance

### How to Adjust

1. Edit `backend/config.py`
2. Modify `FACE_RECOGNITION_TOLERANCE` value
3. Restart backend server

### Recommended Values

```python
# Very Strict (High Security)
FACE_RECOGNITION_TOLERANCE = 0.40

# Strict (Default)
FACE_RECOGNITION_TOLERANCE = 0.60

# Moderate
FACE_RECOGNITION_TOLERANCE = 0.75

# Very Lenient (May accept similar faces)
FACE_RECOGNITION_TOLERANCE = 0.85
```

## Troubleshooting

### Issue: "No face detected in image"

**Causes:**
- Poor lighting
- Face partially obscured
- Image quality too low
- Multiple faces in image

**Solutions:**
- Move to well-lit area
- Remove hats/glasses during enrollment
- Use clear, front-facing image
- Ensure only one face in image

### Issue: "Face does not match"

**Causes:**
- Different lighting conditions
- Different facial expressions
- Different camera angle
- Face obscured

**Solutions:**
- Use similar lighting as enrollment
- Match facial expression from enrollment
- Face camera directly
- Remove glasses/hats if worn during enrollment

### Issue: "Camera not accessible"

**Causes:**
- Browser permissions not granted
- Camera already in use
- Device has no camera

**Solutions:**
- Check browser camera permissions
- Close other apps using camera
- Use device with camera

### Issue: dlib installation fails

**Cause:**
- Complex dependency requiring compilation

**Solution:**
```bash
# On Windows, may need Microsoft C++ build tools
pip install cmake
pip install face-recognition
```

## Performance Optimization

### Face Model Selection

```python
# SMALL MODEL (faster, less accurate)
face_auth_service = FaceAuthService(model='small')
# ~50ms per encoding generation

# LARGE MODEL (slower, more accurate - default)
face_auth_service = FaceAuthService(model='large')
# ~100-150ms per encoding generation
```

### Batch Verification

For multiple faces:

```python
# Compare one test face against multiple known faces
known_encodings = [enc1, enc2, enc3]
test_encoding = test_enc

distances = face_auth_service.batch_distance(known_encodings, test_encoding)
best_match_idx, distance = face_auth_service.get_best_match(known_encodings, test_encoding)
```

## Future Enhancements

1. **Liveness Detection** - Detect if face is live (not photo/video)
2. **Multi-Face Support** - Each user can enroll multiple faces
3. **Age/Gender Estimation** - Additional biometric data
4. **Face Obfuscation** - Blur stored face images
5. **Encryption at Rest** - Encrypt face encodings in database
6. **Biometric Templates** - Use proprietary face encoding formats
7. **Distributed Face Recognition** - Cloud-based verification
8. **3D Face Recognition** - Support depth-based capture devices

## References

- [face_recognition Library](https://github.com/ageitgey/face_recognition)
- [dlib C++ Toolkit](http://dlib.net/)
- [Biometric Authentication Standards](https://en.wikipedia.org/wiki/Biometric_authentication)
- [Face Recognition Security](https://www.nist.gov/programs/frvt/)

## Project Documentation

**Related Files:**
- Backend: `backend/services/face_auth_service.py`
- Backend: `backend/services/face_database_manager.py`
- Backend: `backend/app.py` (face endpoints)
- Backend: `backend/config.py` (face settings)
- Frontend: `frontend/src/components/FaceAuth.jsx`
- Frontend: `frontend/src/components/FaceEnrollment.jsx`
- Frontend: `frontend/src/components/FaceVerification.jsx`
- Frontend: `frontend/src/css/FaceAuth.css`
- Frontend: `frontend/src/services/apiService.js` (face API)

---

**Version:** 1.0
**Last Updated:** February 2024
**Author:** [Your Name]
**Status:** Production Ready
