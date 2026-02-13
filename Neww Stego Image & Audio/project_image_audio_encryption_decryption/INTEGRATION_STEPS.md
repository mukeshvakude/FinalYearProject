# Face Authentication - Integration Instructions

## 🎯 Goal
Apply the new face authentication system to your existing Flask project with **minimal changes**.

---

## ✅ Prerequisites

Before starting, ensure you have:

```bash
# Check these packages are installed
pip list | grep -i "face-recognition\|opencv\|mysql"

# If missing, install:
pip install face-recognition opencv-python-headless mysql-connector-python
```

---

## 📋 Step-by-Step Integration

### STEP 1: Add Three New Service Files ✅

**Copy these files to `backend/services/`:**

1. **`backend/services/face_authentication.py`** - Already created
2. **`backend/services/face_database.py`** - Already created
3. **`backend/routes/face_routes.py`** - Already created

**Verify they exist:**
```
backend/
├── services/
│   ├── face_authentication.py       ← NEW
│   ├── face_database.py             ← NEW
│   ├── auth_service.py              (existing)
│   ├── encryption_service.py        (existing)
│   ├── steganography_service.py     (existing)
│   └── ...
└── routes/
    └── face_routes.py               ← NEW
```

---

### STEP 2: Update Database Schema ✅

Run this SQL command to add the face encoding column:

```sql
USE your_database_name;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS face_encoding LONGTEXT NULL;
```

**Or in Python (one-time setup):**

```python
from services.face_database import add_face_encoding_column
from mysql.connector import connect

# Connect to your database
db_connection = connect(
    host="localhost",
    user="root",
    password="your_password",
    database="your_db"
)

# Add column (safe to run multiple times)
add_face_encoding_column(db_connection)
db_connection.close()
```

---

### STEP 3: Update `backend/app.py` ✅

Add imports at the top of your Flask app:

```python
# ============ ADD THESE IMPORTS ============
from services.face_authentication import face_auth_service
from services.face_database import add_face_encoding_column
from routes.face_routes import (
    register_face_endpoint,
    get_face_status_endpoint,
    delete_face_endpoint,
    decrypt_with_face_verification
)
# ===========================================
```

Initialize the database once at startup:

```python
app = Flask(__name__)

# ============ ADD THIS ============
@app.before_first_request
def initialize_database():
    """Initialize database schema on first request"""
    try:
        db_connection = create_connection()  # YOUR existing connection function
        add_face_encoding_column(db_connection)
        db_connection.close()
        print("✓ Face encoding column verified/created")
    except Exception as e:
        print(f"⚠ Database initialization warning: {e}")
# ==================================
```

Register the new routes:

```python
# ============ ADD THESE ROUTES ============
@app.route('/api/register-face', methods=['POST'])
def register_face():
    return register_face_endpoint()

@app.route('/api/face-status', methods=['GET'])
def face_status():
    return get_face_status_endpoint()

@app.route('/api/delete-face', methods=['POST'])
def delete_face():
    return delete_face_endpoint()
# =========================================
```

---

### STEP 4: Modify `/api/decrypt` Route ✅

**BEFORE (Current decrypt route):**
```python
@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    # Current decryption logic
    return jsonify({"success": True, "message": decrypted_content})
```

**AFTER (With face authentication):**
```python
@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    # Replaces existing decrypt route with face-aware version
    return decrypt_with_face_verification()
```

That's it! The `decrypt_with_face_verification()` function:
- ✓ Checks if user has face registered
- ✓ If yes: requires face verification (max 3 attempts)
- ✓ If no: does normal decryption
- ✓ Returns appropriate error messages

---

## 🔧 Configuration (Optional)

### Adjust Face Matching Sensitivity

In `face_routes.py`, modify tolerance:

```python
# In decrypt_with_face_verification():
is_match, distance = face_auth_service.verify_face(
    stored_encoding, 
    live_encoding,
    tolerance=0.5  # Adjust: lower = stricter, higher = looser
)
```

### Use Different Face Recognition Model

In `face_authentication.py`:

```python
class FaceAuthenticationService:
    def __init__(self, model='hog'):
        self.model = model  # 'hog' (fast) or 'cnn' (accurate)
```

---

## 🧪 Testing Your Integration

### Test 1: Check Server Starts
```bash
# Terminal
cd backend
python app.py

# Should see:
# ✓ Face encoding column verified/created
# * Running on http://localhost:5001
```

### Test 2: Test /register-face Endpoint
```bash
# Get auth token first (adjust for your login system)
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}' \
  -c cookies.txt

# Register a face
curl -X POST http://localhost:5001/api/register-face \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "face_image=@path_to_photo.jpg"

# Expected response (201):
# {"success": true, "message": "Face registered successfully!"}
```

### Test 3: Check Face Status
```bash
curl http://localhost:5001/api/face-status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected response (200):
# {"success": true, "has_face": true, "can_decrypt_with_face": true}
```

### Test 4: Test Decryption with Face
```bash
# Encrypt an image with a message first (your existing code)
# Then decrypt with face verification

curl -X POST http://localhost:5001/api/decrypt \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "cipherText": "your_encrypted_text",
    "password": "your_password",
    "face_image": "base64_encoded_image_data"
  }'

# If face matches (first time), expected response (200):
# {"success": true, "message": "Your hidden message", "face_used": true}

# If face doesn't match, expected response (401):
# {"success": false, "message": "Face mismatch. Attempts: 1/3", ...}
```

### Test 5: Verify Attempt Limiting
```bash
# Send wrong face 3 times
for i in 1 2 3; do
    curl -X POST http://localhost:5001/api/decrypt \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "cipherText": "...",
        "password": "...",
        "face_image": "wrong_face_base64"
      }'
done

# After 3rd attempt, should get:
# {"success": false, "error_code": "MAX_ATTEMPTS_EXCEEDED", ...}
```

---

## 📝 Code Snippets for Your App

### Complete Integration Example

```python
# backend/app.py

from flask import Flask, jsonify, session, request
from mysql.connector import connect

# ==== IMPORTS FOR FACE AUTH ====
from services.face_authentication import face_auth_service
from services.face_database import add_face_encoding_column
from routes.face_routes import (
    register_face_endpoint,
    get_face_status_endpoint,
    delete_face_endpoint,
    decrypt_with_face_verification
)
# ==============================

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Your existing database connection function
def get_db_connection():
    return connect(
        host="localhost",
        user="root",
        password="password",
        database="your_db"
    )

# ==== SETUP FACE AUTH DATABASE ====
@app.before_first_request
def initialize():
    try:
        db = get_db_connection()
        add_face_encoding_column(db)
        db.close()
        print("✓ Face auth initialized")
    except Exception as e:
        print(f"⚠ Init error: {e}")
# ==================================

# Your existing routes (unchanged)
@app.route('/api/login', methods=['POST'])
def login():
    # Your existing login logic
    pass

@app.route('/api/register', methods=['POST'])
def register():
    # Your existing registration logic
    pass

# ==== NEW FACE AUTH ROUTES ====
@app.route('/api/register-face', methods=['POST'])
def register_face():
    """Allow user to register face after login"""
    return register_face_endpoint()

@app.route('/api/face-status', methods=['GET'])
def face_status():
    """Check if user has face registered"""
    return get_face_status_endpoint()

@app.route('/api/delete-face', methods=['POST'])
def delete_face():
    """Remove face registration"""
    return delete_face_endpoint()

# ==== MODIFIED DECRYPT (with face) ====
@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    """Decrypt with optional face verification"""
    return decrypt_with_face_verification()
# ======================================

# Error handlers (your existing ones)
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
```

---

## 🚨 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'face_recognition'"
**Solution:**
```bash
pip install face-recognition dlib
# Note: dlib might take a while to compile
```

### Issue: "face_encoding column already exists"
**Solution:** Safe to ignore! The code checks before adding.

### Issue: "No face detected in image"
**Solution:**
- Make sure image has clear front-facing face
- Good lighting
- Only one face in the image
- File must be PNG or JPG

### Issue: "/register-face returns 401 Unauthorized"
**Solution:**
- Check you're logged in first
- Verify session/auth token is valid
- Check `session['user_id']` is set

### Issue: Face doesn't match when it should
**Solution:**
- Different lighting conditions
- Adjust tolerance (make higher)
- Re-register with similar conditions
- Better camera quality

### Issue: TypeError in face_routes.py
**Solution:**
- Check MySQL is running
- Verify database connection info
- Ensure face_encoding column exists

---

## ✨ What's Now Available

### For Users
- ✅ Login with password (unchanged)
- ✅ **NEW**: Register face (after login)
- ✅ **NEW**: Check face status
- ✅ Decrypt (with optional face + max 3 attempts if face registered)
- ✅ **NEW**: Delete/reset face

### For Developers
- ✅ `face_auth_service` object with 5 methods
- ✅ `face_database` functions for persistence
- ✅ `face_routes` with complete endpoint logic
- ✅ Error codes for specific failures
- ✅ Attempt limiting built-in
- ✅ Session-based verification

---

## 🔒 Security Checklist

- ✓ No face images stored (encoding only)
- ✓ Encodings are 128-float vectors
- ✓ Session authentication required
- ✓ Max 3 verification attempts
- ✓ Clear error messages (no info leakage)
- ✓ HTTPS recommended for production
- ✓ Database column encrypted recommended

---

## 📊 Monitoring

### Check if working
```python
# In flask shell:
from services.face_database import user_has_face_encoding
db = get_db_connection()
has_face = user_has_face_encoding(db, user_id=1)
print(f"User 1 has face: {has_face}")
```

### View face encoding
```python
from services.face_database import get_face_encoding
db = get_db_connection()
encoding_json = get_face_encoding(db, user_id=1)
print(f"Encoding: {encoding_json[:50]}...")  # First 50 chars
```

### Delete face encoding
```python
from services.face_database import delete_face_encoding
db = get_db_connection()
deleted = delete_face_encoding(db, user_id=1)
print(f"Deleted: {deleted}")
```

---

## 🎓 Architecture

```
User sends face_image
         ↓
face_routes.py validates & decodes image
         ↓
face_authentication.py generates 128-dim encoding
         ↓
face_database.py stores encoding in MySQL
         ↓
On decrypt: retrieves encoding & verifies live image
         ↓
Returns success/failure with attempt info
```

---

## ☑️ Integration Checklist

- [ ] Copy `face_authentication.py` to `backend/services/`
- [ ] Copy `face_database.py` to `backend/services/`
- [ ] Copy `face_routes.py` to `backend/routes/`
- [ ] Add imports to `backend/app.py`
- [ ] Add `@before_first_request` initialization
- [ ] Register 3 new routes in `backend/app.py`
- [ ] Modify `/decrypt` route to call new function
- [ ] Add `face_encoding` column to users table
- [ ] Test with authentication token
- [ ] Test face registration
- [ ] Test face verification
- [ ] Test attempt limiting (3 fails → locked)
- [ ] Verify existing features still work

---

## 🚀 Next Steps

1. **Follow this guide** (should take 10-15 minutes)
2. **Run tests** to verify integration
3. **Create React components** for front-end (optional, can use curl to test)
4. **Deploy** with your existing infrastructure

**You're all set!** Questions? Check `FACE_AUTH_FULL_PACKAGE.md` for reference.
