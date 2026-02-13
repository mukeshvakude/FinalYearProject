# 🔓 Decryption Guide

## Complete Step-by-Step Instructions

### Prerequisites
- ✅ Both servers running (Backend: http://localhost:5001, Frontend: http://localhost:5173)
- ✅ You must be **logged in** first
- ✅ You have **cipher text** from a previous encryption
- ✅ You have the **encryption password**

---

## 🚀 How to Decrypt a Message

### Step 1: Login
1. Go to **http://localhost:5173**
2. Enter your **username** and **password**
3. Click **Login**

### Step 2: Navigate to Decryption
1. From the menu, click **"Decryption"**
2. You should see the **Decrypt Message** form

### Step 3: Enter Cipher Text
1. Locate the **"Cipher Text"** textarea
2. **Copy and paste** your encrypted message (hex format)
3. Should look like: `a1b2c3d4e5f6g7h8...`

### Step 4: Enter Password
1. Locate the **"Encryption Password"** field
2. Enter the **EXACT same password** used during encryption
3. ⚠️ Password must match exactly (case-sensitive)

### Step 5: Click Decrypt
1. Click the **"Decrypt"** button
2. Wait for processing...
3. ✓ Success message appears
4. **Decrypted message displays** below in green box

---

## 📍 Where the Message Appears

After clicking **Decrypt**, the decrypted message will appear in:

```
┌──────────────────────────────────────┐
│     ✓ Decrypted Message              │
├──────────────────────────────────────┤
│                                      │
│  ┌────────────────────────────────┐  │
│  │  YOUR DECRYPTED MESSAGE HERE   │  │
│  │  (in white box with green border)  │
│  └────────────────────────────────┘  │
│                                      │
│  [📋 Copy Message] [🔄 Clear]       │
│                                      │
└──────────────────────────────────────┘
```

---

## ✨ Features

### Copy to Clipboard
- ✓ Click **"📋 Copy Message"** button
- ✓ Message copied automatically
- ✓ Alert confirms copy

### Clear Form
- ✓ Click **"🔄 Clear"** button
- ✓ Clears message, cipher text, and password
- ✓ Ready for new decryption

### Auto-Scroll
- ✓ Page automatically scrolls to show decrypted message
- ✓ No need to scroll manually

---

## ❌ Troubleshooting

### "Error: Cipher text is required"
- **Problem**: Cipher text field is empty
- **Solution**: Copy and paste your encrypted hex text

### "Error: Password is required"  
- **Problem**: Password field is empty
- **Solution**: Enter the encryption password

### "Decryption failed"
- **Possible causes**:
  1. ❌ Wrong password (most common)
  2. ❌ Corrupted cipher text
  3. ❌ Invalid hex format
- **Solution**:
  - Check password spelling (case-sensitive)
  - Verify cipher text wasn't modified
  - Try re-copying cipher text

### "Not authenticated"
- **Problem**: You're not logged in
- **Solution**: Login first at http://localhost:5173

### Message not displaying/scrolling
- **Fixed in latest version:**
  - ✓ Auto-scroll to message
  - ✓ Enhanced styling (larger text, green border)
  - ✓ Better visibility

---

## 📊 Example Workflow

### Encryption (Step 1)
```
Message: "Hello World"
Password: "mySecret123"
↓
Encrypts into hex:
a7f2b5c8d1e4f9g2h5i8j1k4l7m0n3o6p9
```

### Decryption (Step 2)
```
Cipher Text: a7f2b5c8d1e4f9g2h5i8j1k4l7m0n3o6p9
Password:    mySecret123
↓
Decrypts into:
"Hello World" ✓
```

---

## 🔍 Monitoring Decryption

### Browser Console Debug Info
Open **Developer Tools** (F12) to see:

```javascript
🔓 Decrypting message...
Cipher length: 64

✓ Decryption response: {
  success: true,
  message: "Your decrypted text here"
}

✓ Decryption successful, message: "Your decrypted text here"
```

---

## ✅ Verification Checklist

Before decrypting, verify:
- [ ] Logged in successfully
- [ ] On **Decryption** page
- [ ] Cipher text entered (hex format)
- [ ] Password entered (matches encryption password)
- [ ] Browser console shows no errors (F12)
- [ ] Both servers running (status 200)

---

## 📚 API Information

### Backend Endpoint
```
POST /api/decrypt
Content-Type: application/json

Request:
{
  "cipherText": "a7f2b5c8...",
  "password": "mySecret123"
}

Response (200 OK):
{
  "success": true,
  "message": "Decrypted text here"
}

Response (400 Error):
{
  "success": false,
  "error": "Decryption failed" or specific error message
}
```

---

## 🎯 Quick Tips

1. **Copy cipher hex exactly** - Don't modify or add spaces
2. **Case-sensitive password** - "Pass" ≠ "pass"
3. **Check decryption success** - Green message box appears
4. **Use copy button** - Ensures exact text is copied
5. **Clear between attempts** - Avoid mixing old & new data

---

## ❓ FAQ

**Q: Can I decrypt without a password?**
A: No, passwords are required for security.

**Q: What if I forgot the password?**
A: You cannot decrypt without the original password. It was used to generate the encryption key.

**Q: Does the message show in browser history?**
A: The message appears in memory. Close the page to clear it.

**Q: Can I decrypt multiple messages?**
A: Yes, clear the form and enter new cipher text + password.

**Q: Why does it take time to decrypt?**
A: The system is verifying the encryption and decryption process.

---

## 📞 Support

If decryption still isn't showing:

1. **Clear browser cache**: Ctrl+Shift+Delete
2. **Refresh page**: Ctrl+R
3. **Check console**: F12 → Console tab
4. **Verify servers**: Check both running (status 200)
5. **Test echo**: Try simple messages first

---

## ✨ Summary

| Step | Action | Result |
|------|--------|--------|
| 1 | Login | ✓ Access Decryption page |
| 2 | Enter cipher text | ✓ Hex validation |
| 3 | Enter password | ✓ Key validation |
| 4 | Click Decrypt | ✓ Processing... |
| 5 | See message | ✓ Green box, auto-scroll |

**Ready to decrypt! 🔓**
