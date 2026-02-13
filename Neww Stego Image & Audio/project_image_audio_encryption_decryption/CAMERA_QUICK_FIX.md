# 🎥 Camera Permission - Quick Fix (30 Seconds)

## ⚡ TL;DR - Do This First

```
❌ Getting "Camera permission"error?

✅ QUICK FIX:
1. Look at address bar → see 🔒 lock icon
2. Click the lock icon
3. Find "Camera" in dropdown
4. Change to "Allow"
5. Refresh page (F5)
6. Try camera again!
```

---

## 🧭 Find the Lock Icon (Browser Permission)

### Chrome / Edge / Brave
```
Address Bar:
[  localhost:5173    🔒  ☆    ]
                       ↑
                 Click here
```

**Steps:**
1. Click 🔒 lock icon
2. See dropdown with "Camera: Block" or "Camera: Ask"
3. Click the **Settings/Options icon** (⚙️ or gear)
4. Change Camera to **Allow**
5. Refresh page

### Firefox
```
Menu (☰) → Settings → Privacy & Security
→ Scroll to "Permissions"
→ Find "Camera"
→ Click "Allow for localhost:5173"
```

### Safari (Mac)
```
Safari → Settings
→ "Websites" tab
→ "Camera" in left sidebar
→ Find "localhost" entry
→ Change to "Allow"
```

---

## 🔌 Check Hardware (Camera Connected?)

**Windows:**
```
Windows Key + I → Settings
→ Privacy & Security → Camera
→ Make sure "Camera access" is ON
```

**Mac:**
```
System Preferences → Security & Privacy
→ Camera tab
→ Check if your browser is listed ✓
```

---

## 🔄 Close Other Apps Using Camera

Close these if open:
- Zoom
- Microsoft Teams
- Discord
- Google Meet
- Skype
- WhatsApp
- OBS Studio
- Streaming software

**Then refresh page and try again!**

---

## 🧹 Clear Cache & Retry

```
1. Press: Ctrl+Shift+Del (Windows) or Cmd+Shift+Del (Mac)
2. Select "All time" for time range
3. Check: Cookies, Cache, Site data
4. Click "Clear data"
5. Refresh page (F5)
6. Try camera again
```

---

## 🔄 Try Incognito/Private Mode

**Chrome:**
```
Ctrl+Shift+N → Open incognito window
→ Go to localhost:5173
→ Try camera (fresh permissions)
```

**Firefox:**
```
Ctrl+Shift+P → Open private window
→ Go to localhost:5173
→ Try camera (fresh permissions)
```

---

## 🔀 Try Different Browser

If Chrome doesn't work:
- Try **Firefox**
- Try **Edge**
- Try **Brave**
- Try **Safari** (on Mac)

Different browser = Different permissions = Might work!

---

## 🎥 Verify Camera Works

1. **Test with system app:**
   - Windows: Open "Camera" app
   - Mac: Open "Photo Booth"
   - Linux: Open "Cheese"

2. **Test with online tool:**
   - Visit: https://webcamtests.com
   - Click "Test camera"
   - Should show your video

3. **If system camera works but browser doesn't:**
   - Issue is browser permissions, not hardware
   - Follow steps above to fix permissions

---

## 📋 Decision Tree

```
See "Camera permission" error?
│
├─ Lock icon visible in address bar?
│  │
│  ├─ Yes → Click lock → Change Camera to Allow ✅
│  │
│  └─ No → Settings → Privacy → Camera → Allow
│
├─ Camera connected?
│  │
│  ├─ No → Plug in camera or use built-in
│  │
│  └─ Yes → Continue...
│
├─ Other apps using camera?
│  │
│  ├─ Yes (Zoom, Teams, etc) → Close them
│  │
│  └─ No → Continue...
│
├─ Correct URL?
│  │
│  ├─ Shows "localhost:5173" → Good!
│  │
│  └─ Shows IP address → Go to localhost:5173
│
├─ Still not working?
│  │
│  └─ Try different browser (Chrome → Firefox → Edge)
```

---

## ✅ What Success Looks Like

- ✅ See 🔒 lock icon in address bar
- ✅ Camera dropdown shows "Allow"
- ✅ See live video from your camera on screen
- ✅ Can click "📷 Capture Face"
- ✅ Photo captures successfully
- ✅ Can proceed with enrollment

---

## 🚨 Still Stuck?

1. **Open Browser Console** (F12)
2. Click "Console" tab
3. Try camera again
4. Look at error message
5. Match to detailed guide: [CAMERA_PERMISSION_FIX.md](CAMERA_PERMISSION_FIX.md)

**Console will show exactly which error:**
```
NotAllowedError = Permission denied
NotFoundError = No camera found
NotReadableError = Camera in use
SecurityError = Browser security issue
TypeError = Browser doesn't support
```

Each has specific fix in the detailed guide!

---

**Quick Fix Checklist:**
- [ ] Click 🔒 lock icon
- [ ] Change Camera to "Allow"
- [ ] Refresh page (F5)
- [ ] Close other apps
- [ ] Try camera again
- [ ] ✅ Success?

*If not, see detailed guide: CAMERA_PERMISSION_FIX.md*
