# Face Recognition Integration - Flow Diagrams

## 1. User Registration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER REGISTRATION & FACE ENROLLMENT                            │
└─────────────────────────────────────────────────────────────────┘

Frontend                              Backend
┌──────────────────┐                 ┌────────────────────┐
│  Registration    │                 │   Flask App        │
│  Form            │                 │   (app.py)         │
└──────────────────┘                 └────────────────────┘
         │                                     │
         │  1. User enters:                    │
         │     - username                      │
         │     - password                      │
         │     - encryption_password           │
         │                                     │
         ├─── POST /api/register ────────────→│
         │     JSON: {username, password,      │
         │            epass}                   │
         │                                     │
         │                          2. Check if username exists
         │                             in users.csv
         │                          │
         │                          3. Create new user record
         │                             in users.csv
         │                          │
         │                          4. Create session with:
         │                             - session['user']
         │                             - session['aes_password']
         │                          │
         │  ←─── 201 Created ─────┤│ 5. Return success response
         │       {success: true,    │   with next_step:
         │        next_step:        │   "face_enrollment"
         │        "face_enrollment"}│
         │                          │
    5. Frontend shows:              │
       "Please Enroll Your Face"    │
       - Webcam capture button      │
       - Upload face image option   │
         │                          │
    6. User uploads face image      │
         │                          │
         ├─── POST /api/face/enroll────────→│
         │     Multipart Form:      │
         │     face_image: (PNG/JPG)        │
         │                          │
         │                          7. Load image using OpenCV
         │                             └─→ cv2.imread()
         │                          │
         │                          8. Convert BGR → RGB
         │                          │
         │                          9. Generate face encoding
         │                             using face_recognition lib
         │                             └─→ 128-dim numpy array
         │                          │
         │                         10. Validate image quality:
         │                             - Check brightness
         │                             - Verify 1 face detected
         │                             - Check face clarity
         │                          │
         │                         11. Convert encoding to list
         │                             └─→ JSON serializable
         │                          │
         │                         12. Store in faces.csv:
         │                             {username, face_encoding,
         │                              enrollment_date,
         │                              face_image_path,
         │                              authentication_count: 0}
         │                          │
         │  ←─── 200 OK ──────────┤│ 13. Delete temporary file
         │       {success: true,    │     (image not kept)
         │        message:          │
         │        "Face enrolled"}  │
         │                          │
    14. Frontend shows:             │
        "Registration Complete"     │
        - Redirects to Login        │
        - Can now login normally    │
         │                          │
         └──────────────────────────┘
```

---

## 2. User Login Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER LOGIN & FACE VERIFICATION                                 │
└─────────────────────────────────────────────────────────────────┘

Path 1: Face Already Enrolled
────────────────────────────────

Frontend                              Backend
┌──────────────┐                     ┌─────────────────┐
│  Login Form  │                     │   Flask Auth    │
└──────────────┘                     └─────────────────┘
     │                                      │
     │  1. User enters:                     │
     │     - username                       │
     │     - password                       │
     │     - encryption_password            │
     │                                      │
     ├─── POST /api/login ───────────────→│
     │     JSON: {username, password,       │
     │            epass}                    │
     │                        2. Validate username/password
     │                           from users.csv
     │                        │
     │                        3. Create session:
     │                           - session['user'] = username
     │                           - session['aes_password'] = epass
     │                        │
     │                        4. Check if face enrolled
     │                           in faces.csv
     │                        │
     │                        5. Detect: user_has_face = TRUE
     │                           ↓
     │  ←── 206 Partial ────┤│ 6. Return status:
     │      Content        │   {success: true,
     │      {requires_face_ │    face_enrolled: true,
     │       verification:  │    requires_face_verification: true,
     │       true,         │    next_step: "face_verification"}
     │       next_step:     │
     │       "face_verification"}
     │                       │
7. Frontend detects:        │
   Status 206 means more    │
   auth needed              │
                           │
8. Show face verification: │
   "Please Verify Your Face"│
   - Webcam capture button  │
   - Upload face image      │
                           │
9. User uploads face image │
   (for verification)      │
                           │
   ├─── POST /api/face/verify────────→│
   │     Multipart Form:    │
   │     face_image: (PNG/JPG)         │
   │                      │
   │                     10. Load verification image
   │                     │
   │                     11. Generate encoding from image
   │                        └─→ 128-dim array
   │                     │
   │                     12. Fetch stored encoding
   │                        from faces.csv for user
   │                     │
   │                     13. Compare encodings:
   │                        distance = face_distance()
   │                        match = (distance < tolerance)
   │                     │
   │                     14a. If MATCH:
   │                         - distance < 0.6 ✓
   │                        14b. If NO MATCH:
   │                         - distance >= 0.6 ✗
   │                     │
   │      ←─ 200 OK ────┤│ 15a. If match:
   │        {success: true,│    Set session['face_verified'] = true
   │         distance: 0.45,
   │         message: "Face verified"}
   │                     │
   │      ←─ 401 ────────┤│ 15b. If no match:
   │        {success: false,
   │         distance: 0.75,
   │         message: "Face does not match"}
   │                     │
16a. If verified:         │
    - Session marked      │
    - Can decrypt now     │
    - User logged in      │
                         │
16b. If not verified:     │
    - Show retry prompt   │
    - Clear verification  │
    - Can retry (max 3x)  │
     │                    │
     └────────────────────┘

Path 2: Face NOT Enrolled
──────────────────────────

Same as above, but at step 5:
  Detect: user_has_face = FALSE
           ↓
  Return status:
  {success: true,
   face_enrolled: false,
   requires_face_enrollment: true,
   next_step: "face_enrollment"}

Frontend shows:
  "Face Enrollment Recommended"
  "Enroll your face for secure authentication"
  → Redirects to face enrollment form
```

---

## 3. Decrypt Message Flow (Protected by Face)

```
┌─────────────────────────────────────────────────────────────────┐
│  MESSAGE DECRYPTION WITH FACE AUTHENTICATION                    │
└─────────────────────────────────────────────────────────────────┘

Frontend                              Backend
┌───────────────┐                    ┌──────────────────┐
│  Decrypt Form │                    │  Decrypt Route   │
└───────────────┘                    └──────────────────┘
     │                                      │
     │  1. User already logged in            │
     │     and face verified                 │
     │                                      │
     │  2. User enters:                     │
     │     - cipher text (hex)               │
     │     - decryption password             │
     │                                      │
     ├─── POST /api/decrypt ────────────────→│
     │     JSON: {cipherText: "a1b2c3...",   │
     │            password: "key"}           │
     │                        3. Check session['user'] exists
     │                           (user logged in?)
     │                        │
     │                        4. security_checks = [
     │                             - User logged in ✓
     │                             - Has enrolled face ✓
     │                             - Face currently verified ✓
     │                           ]
     │                        │
     │                        5. If all checks pass:
     │                           ✓ Decrypt AES message
     │                           ✓ Return plaintext
     │                        │
     │  ←─── 200 OK ────────┤│ 6. Response:
     │       {success: true,  │   {success: true,
     │        message:        │    message: "Hidden secret
     │        "Hidden secret  │              revealed"}
     │        revealed"}      │
     │                        │
 7. Frontend displays:        │
    Decrypted message         │
    ✓ Can read secret         │
                             │
─────────────────────────────────────

ERROR SCENARIOS:
────────────────

├─ 401 "Not authenticated"
│  User not logged in
│  └→ Frontend redirects to login
│
├─ 401 "Face enrollment required"
│  User logged in but NO face enrolled
│  └→ Frontend prompts to enroll face
│
├─ 401 "Face verification required"
│  User logged in but hasn't verified face
│  └→ Frontend prompts to verify face
│
└─ 400 "Invalid cipher text"
   Malformed hex string
   └→ Frontend shows format error
```

---

## 4. Database Operations Flow

```
┌─────────────────────────────────────────────────────┐
│         DATABASE OPERATIONS DIAGRAM                 │
└─────────────────────────────────────────────────────┘

users.csv                    faces.csv
┌──────────────────┐         ┌─────────────────────────────────┐
│ username | password         │ username | face_encoding | ...  │
├──────────────────┤         ├─────────────────────────────────┤
│ john_doe | pass1 │         │ john_doe | [0.12,-0.34,...] | ... │
│ jane    | pass2  │         │ jane    | [0.21, 0.45,...] | ... │
│ bob     | pass3  │         │          (empty for bob)        │
└──────────────────┘         └─────────────────────────────────┘

Registration Flow:
──────────────────

POST /register {john_doe, password}
         │
         ├→ Write to users.csv
         │   username: john_doe
         │   password: password
         │
         └→ Wait for face enrollment

POST /face/enroll {face_image}
         │
         ├→ Generate encoding from image
         │
         ├→ Write to faces.csv
         │   username: john_doe
         │   face_encoding: "[0.12, -0.34, ..., 0.89]"
         │   enrollment_date: "2024-02-13T10:00:00Z"
         │   authentication_count: 0
         │
         └→ Delete temp image file
            (No image stored!)

Login & Verify Flow:
────────────────────

POST /login {john_doe, password}
         │
         ├→ Read from users.csv
         │   Check: john_doe:password exists?
         │   ✓ YES
         │
         └→ Check faces.csv
            Is john_doe in face database?
            ✓ YES → Require face verification

POST /face/verify {face_image}
         │
         ├→ Generate encoding from image
         │
         ├→ Read from faces.csv
         │   Get encoding for john_doe
         │
         ├→ Compare encodings
         │   distance = 0.45
         │   tolerance = 0.6
         │   match? 0.45 < 0.6 → YES ✓
         │
         └→ Update faces.csv
            authentication_count: 1
            last_authenticated: "2024-02-13T14:30:00Z"
```

---

## 5. Security Checkpoints

```
┌──────────────────────────────────────────────────────┐
│         SECURITY CHECKPOINT FLOW                     │
└──────────────────────────────────────────────────────┘

              Request → Decrypt Message
                 │
                 ▼
         ┌─────────────────┐
         │ Checkpoint 1:   │
         │ Session exists? │
         └────────┬────────┘
                  │
            ✓ YES │  ✗ NO
                  │  └──→ 401 "Not authenticated"
                  │
                  ▼
         ┌─────────────────────────┐
         │ Checkpoint 2:           │
         │ Face enrolled for user? │
         └────────┬────────────────┘
                  │
            ✓ YES │  ✗ NO
                  │  └──→ 401 "Face not enrolled"
                  │       "Please enroll your face"
                  │
                  ▼
         ┌──────────────────────────┐
         │ Checkpoint 3:            │
         │ Face verified in session?│ (session['face_verified'])
         └────────┬─────────────────┘
                  │
            ✓ YES │  ✗ NO
                  │  └──→ 401 "Face verification required"
                  │       "Please verify your face"
                  │
                  ▼
         ┌──────────────────────┐
         │ All Checks Passed ✓  │
         │                      │
         │ Proceed with:        │
         │ - Validate cipher    │
         │ - Decrypt message    │
         │ - Return plaintext   │
         └──────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Return plaintext   │
         │ message to user    │
         └────────────────────┘
```

---

## 6. Face Encoding Generation

```
┌────────────────────────────────────────────┐
│  FACE ENCODING GENERATION PROCESS          │
└────────────────────────────────────────────┘

User's Face Image
       │
       ▼
    [PNG/JPG file]
       │
       ├─→ cv2.imread(path)
       │   Load image into memory
       │   Shape: (height, width, 3) - BGR format
       │
       ▼
    [OpenCV Image Array]
       │
       ├─→ cv2.cvtColor(BGR → RGB)
       │   Convert color space for face_recognition
       │
       ▼
    [RGB Image Array]
       │
       ├─→ face_recognition.face_locations()
       │   Detect face regions using dlib
       │   Returns: [(top, right, bottom, left)]
       │
       ▼
    [Face Location(s)]
       │
       ├── Check count:
       │   0 faces → ERROR "No face detected"
       │   1 face → ✓ CONTINUE
       │   2+ faces → ERROR "Multiple faces detected"
       │
       ▼
    [Single Face Verified]
       │
       ├─→ face_recognition.face_encodings()
       │   Generate 128-dimensional feature vector
       │   Uses dlib's CNN model
       │   Encodes facial features
       │
       ▼
    [128-dim numpy array]
    [e.g., [-0.12, 0.34, 0.56, ...]]
       │
       ├─→ encoding.tolist()
       │   Convert to Python list
       │   Now JSON-serializable
       │
       ▼
    [List of 128 floats]
    [JSON format: "[0.12, -0.34, ..., 0.89]"]
       │
       ├─→ json.dumps()
       │   Convert to JSON string
       │
       ▼
    [JSON String in Database]
       │
       Store in faces.csv:
       username: john_doe
       face_encoding: "[0.12, -0.34, ..., 0.89]"

Comparison Process:
───────────────────

Stored Encoding        New Encoding
(user's face)         (for verification)
     │                    │
     ├─→ json.loads()     │
     │   Convert back     │
     │   to list          ├─→ np.array()
     │                    │   Convert to array
     ▼                    ▼
  numpy array        numpy array
     │                    │
     └────────┬───────────┘
              │
              ▼
      face_recognition.face_distance()
      │
      ├─ Calculate Euclidean distance
      │  between 128-dim vectors
      │  Formula: sqrt(sum((a-b)^2))
      │
      ▼
    Distance Score
    (float, e.g., 0.45)
      │
      ├─ Compare to tolerance (0.6)
      │  If distance < tolerance → MATCH ✓
      │  If distance >= tolerance → NO MATCH ✗
      │
      ▼
   Verification Result
   (True or False)
```

---

## Summary Diagrams

### Request Flow
```
User Browser ──→ React Frontend ──→ Flask Backend ──→ Services
                                         │
                                    auth_service
                                    face_auth_service
                                    face_database_manager
                                         │
                                    (CSV Files)
                                    users.csv
                                    faces.csv
```

### Security Layers
```
Layer 1: Session Authentication
    ├─ session['user'] must exist
    └─ Logged in users only

Layer 2: Face Enrollment Check
    ├─ User must have enrolled face
    └─ Prevents access for non-enrolled users

Layer 3: Face Verification
    ├─ session['face_verified'] must be True
    └─ Fresh verification required
    
Layer 4: Encryption Password
    ├─ Required for AES decryption
    └─ Even with valid face
```

All diagrams complete! 🎯
