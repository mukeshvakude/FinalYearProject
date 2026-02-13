# React Components Overview

## Component Breakdown

### 1. **App.jsx** - Main Application Entry Point
- Sets up React Router for navigation
- Defines all routes (login, home, info, encryption, decryption)
- Wraps components with Layout and PrivateRoute
- Imports all pages and routing logic

```jsx
// Key structure
<Router>
  <Routes>
    <Route path="/" element={<Layout><Login /></Layout>} />
    <Route path="/home" element={<Layout><PrivateRoute><Home /></PrivateRoute></Layout>} />
    // ... other routes
  </Routes>
</Router>
```

---

### 2. **Layout.jsx** - Navigation & Page Layout
- Displays sidebar navigation (only if logged in)
- Shows header and footer
- Manages user logout
- Renders child pages

**Features:**
- Conditional sidebar display
- Navigation menu with links
- User display and logout button
- Responsive layout

**Key Methods:**
```javascript
handleLogout()     // API call to logout endpoint
```

---

### 3. **Login.jsx** - User Authentication
- Login form with three fields: username, password, encryption password
- Form validation
- API call to `/api/login`
- Stores user session in localStorage
- Redirects to home on successful login
- Shows error messages for failed login
- Demo credentials display

**Form Fields:**
- Username
- Password
- Encode/Decode Password (AES password)

**Key Methods:**
```javascript
handleChange()      // Update form state
handleSubmit()      // Perform login
```

---

### 4. **Home.jsx** - Home Page
- Fetches content from `/api/home` endpoint
- Displays introduction, about, and architecture diagrams
- Shows background image
- Responsive card layout

**Content Sections:**
- Introduction (project overview)
- About The Project (steganography explanation)
- Architecture Diagram (block diagram)

---

### 5. **Info.jsx** - Information/About Page
- Fetches content from `/api/info` endpoint
- Displays abstract and motivation sections
- Similar layout to Home page

**Content Sections:**
- Abstract
- Motivation

---

### 6. **Encryption.jsx** - Message Encryption & Hiding
Most complex component with following features:

**File Type Selection:**
- Toggle between Image and Audio modes

**Image Mode:**
- Upload two images (photo and photo1)
- Image preview display
- Visual feedback after upload

**Audio Mode:**
- Single WAV file upload
- File selection UI

**Message Input:**
- Textarea for secret message
- Character limit feedback

**Encryption Process:**
1. User enters secret message
2. Clicks "Hide" button
3. Component calls `fileService.hideMessage()`
4. Backend encrypts with AES and embeds in image/audio
5. Displays cipher text (hex encoded)
6. Shows stego-image result

**Key Methods:**
```javascript
handleFiletypeChange()    // Switch between image/audio
handleImageUpload()       // Upload images
handleAudioUpload()       // Upload audio
handleHideMessage()       // Encrypt and hide message
```

---

### 7. **Decryption.jsx** - Message Decryption
- Textarea for cipher text input
- Password input for decryption
- Placeholder for decryption logic
- Display decrypted message

**Note:** Full decryption implementation pending

---

### 8. **PrivateRoute.jsx** - Route Protection
- Checks if user is authenticated
- Redirects to login if not authenticated
- Allows access if authenticated

**Logic:**
```javascript
if (!isAuthenticated) {
  return <Navigate to="/" />
}
return children
```

---

### 9. **apiService.js** - API Communication Service
Central service for all backend API calls using axios

**Features:**
- Base URL configuration
- Request/response interceptors
- Error handling (redirects to login on 401)
- Session credentials with cookies

**Service Groups:**

#### authService
```javascript
login(username, password, epass)     // POST /api/login
logout()                             // POST /api/logout
getSession()                         // GET /api/session
isAuthenticated()                    // Check localStorage
getCurrentUser()                     // Get user from localStorage
```

#### contentService
```javascript
getHome()                            // GET /api/home
getInfo()                            // GET /api/info
```

#### fileService
```javascript
uploadFiles(filetype, formData)      // POST /api/upload
hideMessage(message, filetype)       // POST /api/hide
```

#### Utilities
```javascript
healthCheck()                        // GET /api/health
```

---

## Component Data Flow

```
App.jsx
  ├── Router Setup
  ├── Route Definitions
  │   └── Layout Wrapper
  │       ├── Login (Public)
  │       │   ├── Form Input
  │       │   ├── authService.login()
  │       │   └── Navigate to /home
  │       │
  │       ├── PrivateRoute
  │       │   ├── Home
  │       │   │   ├── contentService.getHome()
  │       │   │   └── Display Content
  │       │   │
  │       │   ├── Info
  │       │   │   ├── contentService.getInfo()
  │       │   │   └── Display Content
  │       │   │
  │       │   ├── Encryption
  │       │   │   ├── handleImageUpload()
  │       │   │   │   └── fileService.uploadFiles()
  │       │   │   │       └── POST /api/upload
  │       │   │   │
  │       │   │   └── handleHideMessage()
  │       │   │       └── fileService.hideMessage()
  │       │   │           └── POST /api/hide
  │       │   │               └── Display Cipher & Stego
  │       │   │
  │       │   └── Decryption
  │       │       └── handleDecrypt() (to implement)
  │       │
  │       └── Navigation (via Layout)
  │           ├── Home Link
  │           ├── Info Link
  │           ├── Encryption Link
  │           ├── Decryption Link
  │           └── Logout Button
```

---

## Styling & CSS

### W3.CSS Framework
Primary CSS framework used throughout the project

**Key Classes:**
- `w3-container` - Basic container
- `w3-card-4` - Card with shadow
- `w3-sidebar` - Sidebar navigation
- `w3-btn` - Buttons
- `w3-input` - Input fields
- `w3-select` - Select dropdowns
- `w3-textarea` - Textarea
- `w3-table` - Tables
- Colors: `w3-blue`, `w3-teal`, `w3-light-grey`, etc.

### Custom CSS Files
- `Layout.css` - Layout styling for sidebar and page content
- `Components.css` - Component-specific styles (images, cipher box)

---

## State Management

### Local Component State (useState)

**Login Component:**
```javascript
formData = { username, password, epass }
error = ""
loading = false
```

**Encryption Component:**
```javascript
filetype = "image" | "audio"
images = { photo, photo1 }
audioFile = null
message = ""
cipher = ""
loading = false
error = ""
success = ""
```

**Home/Info Components:**
```javascript
content = {}
loading = false
error = ""
```

### Session Storage (localStorage)

**Stored Data:**
```javascript
localStorage.user = "admin"  // User's username
```

### Cookies (via axios)

**Session Cookie:**
- Automatically managed by browser
- Sent with every request (withCredentials: true)
- Created by Flask on login
- Deleted on logout

---

## API Integration Pattern

### Typical API Call Flow

```javascript
// 1. Component calls API method
const result = await apiService.hideMessage(message, filetype)

// 2. apiService uses axios
const response = await api.post('/hide', {
  message,
  filetype,
})

// 3. axios sends request
// POST http://localhost:5001/api/hide
// Headers: { Cookie: session cookie }
// Body: { message, filetype }

// 4. Component handles response
if (result.success) {
  setCipher(result.cipher)
} else {
  setError(result.error)
}
```

---

## Error Handling

### Frontend Error Handling
- Try-catch blocks around API calls
- Error state management
- User-friendly error messages
- Console logging for debugging

### API-Level Error Handling
- 401 Unauthorized → Redirect to login
- 400 Bad Request → Display error message
- 500 Server Error → Display error message
- Network Error → Display connection error

---

## Future Enhancement Points

1. **Decryption Implementation**
   - Cipher text input
   - Password validation
   - AES decryption logic
   - Extracted file display

2. **User Management**
   - User registration
   - Password change
   - User profile

3. **File Management**
   - Download stego files
   - File history
   - Bulk operations

4. **Security Enhancements**
   - JWT authentication
   - HTTPS enforcement
   - Rate limiting

5. **UI/UX Improvements**
   - Dark mode
   - Mobile responsiveness
   - File drag-and-drop
   - Real-time file preview

6. **Testing**
   - Unit tests (Jest)
   - Integration tests
   - E2E tests (Cypress)

---

## Performance Considerations

1. **Lazy Loading** - Consider lazy loading routes
2. **Code Splitting** - Use dynamic imports for large components
3. **Image Optimization** - Compress images before display
4. **Memoization** - Use React.memo for expensive components
5. **API Caching** - Cache frequently accessed endpoints

---

## Accessibility Features

- Semantic HTML elements
- ARIA labels on form inputs
- Keyboard navigation support
- Color contrast compliance
- Screen reader support through W3.CSS

---

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

**Last Updated:** February 2026  
**React Version:** 18.3+  
**Vite Version:** 5.0+  
**Node Version:** 16+
