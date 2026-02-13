# Face Authentication Integration Guide

## Overview

This guide shows how to add **face authentication as a SEPARATE, OPTIONAL feature** to your existing Flask project. Face authentication does NOT modify password login.

---

## Architecture

```
Password Login (Unchanged)
    ↓
User Authenticated
    ├─→ Option 1: /register-face (User enrolls face)
    ├─→ Option 2: Skip face registration
    ↓
/decrypt route
    ├─→ If face registered: Require face verification
    ├─→ If no face: Proceed normally
    ↓
Message Decrypted
```

---

## Files Created

| File | Purpose |
|------|---------|
| `backend/services/face_authentication.py` | Core face capture, encoding, verification logic |
| `backend/services/face_database.py` | MySQL database operations |
| `backend/routes/face_routes.py` | Flask endpoints and integration |

---

## Database Changes

### 1. Add Column to Users Table

Run this SQL once:

```sql
ALTER TABLE users 
ADD COLUMN face_encoding LONGTEXT NULL;
```

Or let the app do it automatically:

```python
from services.face_database import add_face_encoding_column

@app.before_request
def init_database():
    add_face_encoding_column(db_connection)
```

### Column Details

```
Column Name: face_encoding
Type: LONGTEXT
Content: JSON string of 128-element float array
Example: "[0.12, -0.34, 0.56, ..., 0.89]"  (128 floats total)
Nullable: YES (user can skip face registration)
```

---

## Integration Steps

### Step 1: Import Required Modules

In your `app.py` or initialization file:

```python
from services.face_authentication import face_auth_service
from services.face_database import (
    store_face_encoding, 
    get_face_encoding,
    user_has_face_encoding, 
    delete_face_encoding,
    add_face_encoding_column
)
from routes.face_routes import (
    register_face_endpoint,
    get_face_status_endpoint,
    delete_face_endpoint,
    decrypt_with_face_verification
)
```

### Step 2: Initialize Database Column

Add to your Flask app initialization:

```python
from flask import Flask

app = Flask(__name__)

# ... your existing config ...

@app.before_first_request
def initialize_database():
    """
    Initialize database schema.
    Add face_encoding column if not exists.
    """
    add_face_encoding_column(db_connection)
    logger.info('Database initialized')
```

### Step 3: Add Face Registration Route

```python
@app.route('/register-face', methods=['POST'])
def register_face():
    """
    Register user's face.
    
    User must be logged in (session['user_id'] exists)
    Accepts multipart form with face_image file
    
    Status Codes:
    - 201: Face registered
    - 400: Invalid image or face detection failed
    - 401: Not logged in
    - 500: Server error
    """
    return register_face_endpoint(request, session, db_connection)
```

### Step 4: Add Face Status Route

```python
@app.route('/face-status', methods=['GET'])
def face_status():
    """
    Check if user has registered face.
    
    Returns:
    {
        'success': bool,
        'has_face': bool,
        'can_decrypt_with_face': bool
    }
    """
    return get_face_status_endpoint(session, db_connection)
```

### Step 5: Add Delete Face Route

```python
@app.route('/delete-face', methods=['POST'])
def delete_face():
    """
    Delete user's face registration.
    Allows re-registration or account cleanup.
    """
    return delete_face_endpoint(request, session, db_connection)
```

### Step 6: Modify Decrypt Route (IMPORTANT)

**BEFORE** (existing implementation):
```python
@app.route('/decrypt', methods=['POST'])
def decrypt():
    # ... existing decrypt logic ...
```

**AFTER** (with face verification):
```python
@app.route('/decrypt', methods=['POST'])
def decrypt():
    """
    Decrypt message with optional face verification.
    
    If user has registered face:
    - Requires face verification before decryption
    - Max 3 attempts
    
    If user has NO face:
    - Proceeds with decryption normally
    
    Request JSON:
    {
        'cipherText': 'hex_string',
        'password': 'encryption_password',
        'face_image': 'base64_encoded_image' (optional, required if face registered)
    }
    """
    return decrypt_with_face_verification(
        request=request,
        session=session,
        db_connection=db_connection,
        encrypt_service=encryption_service,  # Your existing encryption service
        max_attempts=3  # Maximum face verification attempts
    )
```

---

## Usage Examples

### 1. Register Face

**Frontend:**
```javascript
// Capture face image from webcam or file upload
const formData = new FormData();
formData.append('face_image', imageFile);  // PNG, JPG, etc.

fetch('/register-face', {
    method: 'POST',
    body: formData,
    credentials: 'include'  // Include session cookie
})
.then(r => r.json())
.then(data => {
    if (data.success) {
        alert('Face registered successfully!');
    } else {
        alert('Error: ' + data.message);
    }
});
```

**Response (Success - 201):**
```json
{
    "success": true,
    "message": "Face registered successfully! Your face can now be used for verification.",
    "face_registration_complete": true,
    "timestamp": "2024-02-13T10:30:00.000Z"
}
```

**Response (Error - No face detected):**
```json
{
    "success": false,
    "message": "Face detection failed. Possible reasons:\n1. No face detected in image\n2. Multiple faces detected\n3. Poor image quality\nPlease try a clear photo with only your face.",
    "error_code": "FACE_DETECTION_FAILED"
}
```

### 2. Check Face Status

**Frontend:**
```javascript
fetch('/face-status', {
    credentials: 'include'
})
.then(r => r.json())
.then(data => {
    console.log('User has face registered:', data.has_face);
});
```

**Response:**
```json
{
    "success": true,
    "has_face": true,
    "can_decrypt_with_face": true
}
```

### 3. Decrypt with Face Verification

**Frontend:**
```javascript
const faceImage = canvasToBase64(webcamCanvas);

fetch('/decrypt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        'cipherText': 'a1b2c3d4e5f6...',
        'password': 'encryption_key',
        'face_image': faceImage  // Base64 encoded
    }),
    credentials: 'include'
})
.then(r => r.json())
.then(data => {
    if (data.success) {
        console.log('Decrypted:', data.message);
    } else {
        console.log('Error:', data.message);
    }
});
```

**Response (Success - 200):**
```json
{
    "success": true,
    "message": "The hidden message content...",
    "face_used_for_verification": true
}
```

**Response (Face Mismatch - 401):**
```json
{
    "success": false,
    "message": "Face does not match. Please try again. Attempts: 1/3",
    "attempts_remaining": 2,
    "distance": 0.75,
    "error_code": "FACE_MISMATCH"
}
```

**Response (Max Attempts - 401):**
```json
{
    "success": false,
    "message": "Maximum face verification attempts exceeded (3)",
    "error_code": "MAX_ATTEMPTS_EXCEEDED"
}
```

---

## Error Codes

| Code | Meaning | HTTP | Solution |
|------|---------|------|----------|
| `NOT_AUTHENTICATED` | User not logged in | 401 | Login first |
| `MISSING_IMAGE` | No face_image in request | 400 | Provide face image |
| `INVALID_FORMAT` | Wrong file type | 400 | Use PNG/JPG only |
| `IMAGE_ERROR` | Can't read image file | 400 | Try another image |
| `FACE_DETECTION_FAILED` | No or multiple faces | 400 | Use clear photo with 1 face |
| `DATABASE_ERROR` | Can't save to DB | 500 | Retry or contact support |
| `FACE_VERIFICATION_REQUIRED` | Face verification needed | 405 | Provide face image for decrypt |
| `FACE_DETECTION_FAILED` | Can't detect live face | 401 | Try again, clear photo |
| `FACE_MISMATCH` | Face doesn't match | 401 | Try again or re-register face |
| `MAX_ATTEMPTS_EXCEEDED` | 3 failed attempts | 401 | Wait and try again |
| `SERVER_ERROR` | General server error | 500 | Contact support |

---

## Security Features

### Attempt Limiting

```python
max_attempts = 3

# After 3 failed face verifications:
# - Error: "Maximum attempts exceeded"
# - User must wait/retry
# - Configured in decrypt_with_face_verification()
```

### No Image Storage

- Only 128-dimensional encoding stored (tiny, safe)
- Original face images are never saved
- Prevents privacy leaks

### Error Handling

- Specific error messages for each failure
- Clear guidance on what user should do
- Secure logging (no sensitive data logged)

---

## Configuration

### Adjust Face Matching Tolerance

In `backend/services/face_authentication.py`:

```python
# Stricter matching (fewer false matches)
face_auth_service = FaceAuthenticationService(tolerance=0.4)

# Looser matching (fewer false fails)
face_auth_service = FaceAuthenticationService(tolerance=0.8)

# Default: 0.6
```

### Adjust Processing Speed

In `FaceAuthenticationService.__init__`:

```python
# Fast but less accurate
self.model = 'hog'

# Slow but more accurate
self.model = 'cnn'
```

### Adjust Max Attempts

In `decrypt_with_face_verification()`:

```python
# Current: 3 attempts max
max_attempts = 3

# Change as needed in app.py route
```

---

## Testing

### Manual Test Flow

**1. Register Face**
```bash
curl -X POST http://localhost:5001/register-face \
  -F "face_image=@your_face.jpg" \
  -b "session=your_session_cookie"
```

**2. Check Status**
```bash
curl http://localhost:5001/face-status \
  -b "session=your_session_cookie"
```

**3. Decrypt with Face**
```bash
curl -X POST http://localhost:5001/decrypt \
  -H "Content-Type: application/json" \
  -d '{
    "cipherText": "a1b2c3...",
    "password": "key",
    "face_image": "iVBORw0KGgo..." 
  }' \
  -b "session=your_session_cookie"
```

**4. Delete Face**
```bash
curl -X POST http://localhost:5001/delete-face \
  -b "session=your_session_cookie"
```

---

## Dependencies

Add to `requirements.txt`:

```
face-recognition==1.3.5
dlib==19.24.2
opencv-python==4.8.0.76
numpy==1.24.3
Pillow==10.0.0
```

Install:
```bash
pip install -r requirements.txt
```

---

## Key Design Principles

✅ **Separate from Login**
- Password login unchanged
- Face auth is optional

✅ **Backward Compatible**
- Existing users not affected
- Face registration is optional

✅ **Clean Modular Functions**
- `capture_face()` - Solo function
- `generate_encoding()` - Solo function
- `verify_face()` - Solo function
- Easy to test independently

✅ **Clear Error Messages**
- User knows what went wrong
- Guidance on how to fix

✅ **Attempt Limiting**
- Max 3 per request
- Prevents brute force

✅ **No Security Regression**
- No face images stored
- Encodings only (128 floats)
- Database column is optional
- Can disable face auth entirely

---

## Disabling Face Authentication

To disable face authentication:

1. Don't register the face routes
2. Keep existing `/decrypt` route as-is
3. Users can't register faces
4. Decryption works normally without faces

---

## Troubleshooting

### "Face detection failed"
- Use clear front-facing photo
- Good lighting
- Only your face in image
- PNG or JPG format

### "Face does not match"
- Take new photo in similar lighting
- Similar facial expression
- Check tolerance setting

### "face_recognition library not available"
```bash
pip install dlib face-recognition
```

### "Database column doesn't exist"
```python
from services.face_database import add_face_encoding_column
add_face_encoding_column(db_connection)
```

---

## Summary

This implementation provides:

- ✅ Clean modular functions
- ✅ Separate face auth (doesn't touch login)
- ✅ Optional for users
- ✅ Attempt limiting (3 max)
- ✅ Clear error handling
- ✅ Secure (no images stored)
- ✅ Easy integration
- ✅ Backward compatible

Face authentication is now ready to integrate!
