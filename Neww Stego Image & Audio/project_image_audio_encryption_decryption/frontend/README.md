# React Frontend - Steganography Application

## Overview
This is the React JS frontend for the Steganography application. It provides a modern UI for user authentication, file uploads, encryption, and image/audio steganography operations.

## Project Structure
```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Layout.jsx       # Main layout with navigation
│   │   ├── Login.jsx        # Login page
│   │   ├── Home.jsx         # Home page
│   │   ├── Info.jsx         # Information page
│   │   ├── Encryption.jsx   # Encryption/encoding page
│   │   ├── Decryption.jsx   # Decryption/decoding page
│   │   ├── PrivateRoute.jsx # Protected route component
│   │   └── *.css            # Component styles
│   ├── services/
│   │   └── apiService.js    # API communication logic
│   ├── css/                 # Global styles (w3.css)
│   ├── App.jsx              # Main app component with routing
│   ├── main.jsx             # React entry point
│   └── index.css            # Global styles
├── public/
│   └── images/              # Static images
├── package.json             # Dependencies
├── vite.config.js           # Vite configuration
├── index.html               # HTML entry point
└── README.md                # This file
```

## Installation

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

### Development Server
```bash
npm run dev
```
Runs the app in development mode with hot module replacement (HMR).

### Build for Production
```bash
npm run build
```
Creates an optimized production build in the `dist` folder.

### Preview Production Build
```bash
npm run preview
```
Preview the production build locally.

## API Configuration

The frontend communicates with the Flask backend via REST API. The API base URL is configured in:
- **File**: `src/services/apiService.js`
- **Default URL**: `http://localhost:5001/api`

To change the backend URL, edit the `API_BASE_URL` variable in `apiService.js`.

## Features

### Authentication
- User login with username, password, and encryption password
- Session management
- Protected routes (requires login)
- Automatic logout on authentication failure

### File Operations
- Image upload (dual image support)
- Audio file upload (WAV format)
- File type switching (image/audio)

### Encryption
- AES-based message encryption
- LSB steganography for images
- Steganography support for audio files
- Display of encrypted cipher text

### Decryption
- Message decryption (to be implemented)
- Cipher text input
- Password-based decryption

### UI/UX
- W3.CSS framework for responsive design
- Sidebar navigation
- Card-based layout
- Real-time loading and error states
- Success/error messaging

## API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/login` | User authentication |
| POST | `/api/logout` | User logout |
| GET | `/api/session` | Check authentication status |
| GET | `/api/home` | Fetch home content |
| GET | `/api/info` | Fetch info content |
| POST | `/api/upload` | Upload image/audio files |
| POST | `/api/hide` | Encrypt and hide message |
| GET | `/api/health` | API health check |

## Component Hierarchy

```
App
├── Router
│   ├── Route: / (Login)
│   │   └── Layout
│   │       └── Login
│   ├── Route: /home
│   │   └── Layout
│   │       └── PrivateRoute
│   │           └── Home
│   ├── Route: /info
│   │   └── Layout
│   │       └── PrivateRoute
│   │           └── Info
│   ├── Route: /encryption
│   │   └── Layout
│   │       └── PrivateRoute
│   │           └── Encryption
│   └── Route: /decryption
│       └── Layout
│           └── PrivateRoute
│               └── Decryption
```

## Environment Variables

Currently, no environment variables are required. The backend URL is hardcoded in `apiService.js`.

To make it configurable, you can create a `.env` file:
```
VITE_API_BASE_URL=http://localhost:5001/api
```

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### CORS Errors
If you see CORS errors, ensure:
- Backend is running on `http://localhost:5001`
- Backend has CORS enabled (Flask-CORS)
- Check `apiService.js` for correct API URL

### 404 Images
If images don't load:
- Ensure images are in `public/images/` folder
- Check that backend is serving static files correctly
- Verify file paths in components

### Login Issues
- Verify backend is running
- Check credentials (admin/admin by default)
- Check browser console for error messages

## Performance Optimization

The app uses:
- Vite for fast development and optimized builds
- React Router for efficient client-side routing
- Axios for optimized API requests
- W3.CSS for minimal CSS footprint

## Future Enhancements

- [ ] Implement decryption functionality
- [ ] Add user registration
- [ ] Implement JWT authentication
- [ ] Add file download for stego files
- [ ] Add image preview before encryption
- [ ] Implement dark mode
- [ ] Add unit tests
- [ ] Add E2E tests
