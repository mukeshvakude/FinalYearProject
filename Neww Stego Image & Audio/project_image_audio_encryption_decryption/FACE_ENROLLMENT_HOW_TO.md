# 👤 Face Enrollment Guide

## 🎯 Where to Find Face Enrollment

### Option 1: From the Sidebar Menu
1. After you log in, look at the **left sidebar**
2. Find the menu item: **👤 Face Enrollment** (orange/highlighted button)
3. Click it to go to the enrollment page

### Option 2: From the Home Page
1. After you log in, you're on the **Home** page by default
2. Scroll down to find the **"👤 Face Enrollment (Optional)"** card
3. Click the **"👤 Enroll Your Face Now"** button (orange button)
4. This takes you to the enrollment page

### Option 3: Direct Navigation
- Type in your browser: `http://localhost:5173/face-enrollment`

---

## 📸 Face Enrollment Step-by-Step

### Step 1: Start the Process
1. Click on **Face Enrollment** from the menu or home page
2. You'll see the enrollment form with instructions

### Step 2: Read the Instructions
The page shows:
```
📝 Instructions:
- Make sure you're in a well-lit area
- Position your face clearly in front of the camera
- Ensure your entire face is visible
- Click "Start Camera" to begin
- Click "Capture Face" when ready
- Review the captured image
- Click "Enroll" to save your face
```

### Step 3: Start the Camera
1. Click the **"📷 Start Camera"** button
2. Your browser will ask for camera permission
3. **Allow/Grant** the permission when prompted
4. Your webcam feed should appear on screen

### Step 4: Position Your Face
1. Look directly at the camera
2. Make sure your entire face is visible
3. Ensure good lighting (face should be clearly visible)
4. Try to be centered in the camera frame

### Step 5: Capture Your Face
1. When ready, click **"📷 Capture Face"** button
2. A snapshot will be taken
3. The camera will stop
4. Your captured face image will appear for review

### Step 6: Review the Capture
1. Look at the captured image
2. If it looks good, proceed to Step 7
3. If it doesn't look good, click **"🔄 Try Again"** and repeat from Step 3

### Step 7: Enroll Your Face
1. Click the **"✓ Enroll Face"** button
2. The system will process your face and extract facial features
3. Wait for the process to complete (takes a few seconds)
4. You'll see a **"✅ Face Enrollment Successful!"** message

### Step 8: All Done!
1. You'll be automatically redirected to the **Home** page after 3 seconds
2. Your face is now registered and ready to use!

---

## 📍 Sidebar Navigation Menu

After logging in, the sidebar shows:
```
Menu
├── Home              [Home page with overview]
├── About             [About the system]
├── Encryption        [Encrypt messages]
├── Decryption        [Decrypt messages]
└── 👤 Face Enrollment [ORANGE button - Face enrollment]
    Logout (username)
```

The **Face Enrollment** button is highlighted in **orange** to stand out from other options.

---

## ✨ What You Can Do After Enrollment

### Use Face Verification During Decryption
1. Go to **Decryption** tab
2. Enter your cipher text and password
3. Click **Decrypt**
4. The system will ask you to verify your face
5. Use your camera to capture a face image
6. The system compares it with your enrolled face
7. If it matches, your message is decrypted!

### Delete Your Face Data (Optional)
If you want to remove your enrolled face:
1. Go to the **Face Enrollment** page
2. Look for a **"🗑️ Delete Face Data"** option
3. Click to remove your face from the system
4. You can re-enroll anytime

---

## 🛠️ Troubleshooting

### Camera Not Showing Up
| Problem | Solution |
|---------+----------|
| "Unable to access camera" error | Check if browser has camera permission |
| No camera permission prompt | Manually enable camera in browser settings |
| Camera permission already denied | Reset browser permissions and reload page |
| Using HTTPS but no camera | Some browsers require HTTPS for camera |

**How to enable camera permission:**
1. **Chrome/Edge:** Settings → Privacy → Camera → Allow for localhost
2. **Firefox:** Preferences → Privacy → Permissions → Camera → Allow for localhost
3. **Safari:** System Preferences → Security & Privacy → Camera → Check your browser

### Face Not Being Detected
| Problem | Solution |
|---------+----------|
| "No face detected" error | Move closer to camera, ensure full face visible |
| Face is too dark | Improve lighting, face should be well-lit |
| Face is tilted | Face camera directly, keep head straight |
| Multiple faces detected | Make sure only your face is visible |

### Enrollment Fails
| Problem | Solution |
|---------+----------|
| "Backend error" | Check backend server is running on port 5001 |
| Enrollment takes too long | Wait longer, face_recognition library is processing |
| "Enrollment already exists" | Your face is already enrolled, delete it first to re-enroll |

---

## 🔒 Privacy & Security

### What Information is Stored?
- ✅ Facial encoding (128-dimensional vector, NOT an image)
- ✅ Enrollment timestamp
- ❌ NOT storing: Face images, photos, or visual data

### Where is it Stored?
- Data stored in: `faces.csv` (encrypted format)
- Location: `backend/faces.csv`
- Only accessible from your local system

### Can I Delete It?
- Yes! Go to the enrollment page and click "Delete Face Data"
- Your face is instantly removed from the system
- You can re-enroll anytime

### Is it Safe?
- Your facial encoding is specific to your face
- It cannot be reverse-engineered to recreate your face
- It's only compared against captured images during verification
- Never shared or transmitted outside the system

---

## 📋 Face Enrollment Status Check

### How to Check If You're Enrolled
1. Go to **Decryption** page
2. If you see a **Face Verification** section, you're enrolled
3. The system shows: **"✓ Face Verified"** (if already verified)

### Check Enrollment Details
1. Frontend automatically checks enrollment status
2. If enrolled, system enables face verification
3. If not enrolled, face verification is skipped

---

## 🎯 Quick Reference

| Action | Location | Steps |
|--------|----------|-------|
| **Enroll Face** | Home page or Sidebar | Home → Click "Enroll Your Face Now" button |
| **Use Face Auth** | Decryption | Decrypt → Verify Face → Enter face image |
| **View Status** | Decryption page | Check if Face Verification section appears |
| **Delete Face** | Face Enrollment | Go to enrollment page → Delete option |

---

## ✅ Success Indicators

### Enrollment is Working ✅
1. Camera starts and shows your video
2. Face capture button works
3. Captured image displays for review
4. Green success message appears after enrollment
5. System redirects to home page

### Face Verification Works ✅
1. Decryption page shows face verification option
2. Camera opens when verification needed
3. Face is detected and compared
4. Message decrypts after successful verification

---

## 📚 Additional Information

### Face Recognition Technology
- Uses: `face_recognition` library by Adam Geitgey
- Algorithm: Deep learning + face encoding
- Accuracy: 99.38% on standard benchmarks
- Speed: Takes 1-3 seconds per face

### Facial Encoding Explained
- Each face produces a **128-dimensional vector**
- This vector represents unique facial features
- Two similar faces have similar vectors
- Comparison calculates distance between vectors
- If distance < threshold, faces match

### System Configuration
- Tolerance: 0.6 (stricter matching)
- Model: HOG (faster) or CNN (more accurate)
- Processing: Local only, no cloud transmission

---

## 📞 Need Help?

### Common Questions

**Q: Do I have to enroll my face?**
A: No! Face enrollment is completely optional. You can use the system with just a password.

**Q: What if face verification fails?**
A: You can still decrypt with just your password. Face auth is an additional security layer.

**Q: Can I enroll multiple times?**
A: You can delete and re-enroll, but only one face per account is stored.

**Q: Is my face image saved?**
A: No! Only a mathematical encoding is saved. The original image is never stored.

**Q: What if my lighting is poor?**
A: Enrollment works best with good lighting. Try again in a brighter location.

---

**Last Updated:** February 14, 2026  
**Status:** ✅ Ready to Use

*Face Enrollment: Optional Security, Maximum Privacy*
