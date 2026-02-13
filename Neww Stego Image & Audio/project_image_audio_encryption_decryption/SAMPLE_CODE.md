# Sample React Component Code & Usage Examples

## 1. Login Component Example

```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/apiService';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    epass: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await authService.login(
        formData.username,
        formData.password,
        formData.epass
      );
      if (result.success) {
        navigate('/home');
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <input 
        name="username" 
        value={formData.username} 
        onChange={handleChange}
      />
      {/* ... other inputs ... */}
      <button type="submit">Login</button>
      {error && <p>{error}</p>}
    </form>
  );
}

export default Login;
```

---

## 2. File Upload Component Example

```jsx
import React, { useState, useRef } from 'react';
import { fileService } from '../services/apiService';

function FileUpload() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  const handleImageUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('filetype', 'image');
    formData.append('photo', files[0]);

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await fileService.uploadFiles('image', formData);
      if (result.success) {
        setSuccess(result.message);
        // Image is now available at /images/test_image.png
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        disabled={loading}
      />
      {loading && <p>Uploading...</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
      {success && <p style={{color: 'green'}}>{success}</p>}
      <img src="/images/test_image.png" alt="Uploaded" />
    </div>
  );
}

export default FileUpload;
```

---

## 3. Message Encryption Component Example

```jsx
import React, { useState } from 'react';
import { fileService } from '../services/apiService';

function MessageEncryption() {
  const [message, setMessage] = useState('');
  const [cipher, setCipher] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleHideMessage = async (e) => {
    e.preventDefault();

    if (!message.trim()) {
      setError('Please enter a message');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await fileService.hideMessage(message, 'image');
      if (result.success) {
        setCipher(result.cipher);
        // Stego image is now available at /images/stegoImage.png
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Encryption failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleHideMessage}>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Enter message to hide..."
        rows="10"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Hide Message'}
      </button>
      
      {error && <p style={{color: 'red'}}>{error}</p>}
      
      {cipher && (
        <div>
          <h3>Encrypted Cipher Text:</h3>
          <pre>{cipher}</pre>
          <img src="/images/stegoImage.png" alt="Stego" />
        </div>
      )}
    </form>
  );
}

export default MessageEncryption;
```

---

## 4. Protected Route Component Example

```jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/apiService';

function PrivateRoute({ children }) {
  const isAuthenticated = authService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/" />
  }

  return children;
}

export default PrivateRoute;

// Usage in App.jsx:
// <Route path="/home" element={<PrivateRoute><Home /></PrivateRoute>} />
```

---

## 5. Async Data Fetching Component Example

```jsx
import React, { useEffect, useState } from 'react';
import { contentService } from '../services/apiService';

function Home() {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const data = await contentService.getHome();
        setContent(data);
      } catch (err) {
        setError('Failed to load content');
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, []); // Empty dependency array = run once on mount

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>{content?.introduction?.title}</h1>
      <p>{content?.introduction?.text}</p>
      <img src={content?.architecture?.image} alt="Architecture" />
    </div>
  );
}

export default Home;
```

---

## 6. API Service Usage Examples

### Login API Call
```javascript
// In apiService.js
export const authService = {
  login: async (username, password, epass) => {
    const response = await api.post('/login', {
      username,
      password,
      epass,
    });
    if (response.data.success) {
      localStorage.setItem('user', response.data.user);
    }
    return response.data;
  },
};

// In component
const result = await authService.login('admin', 'admin', 'secret');
if (result.success) {
  // User is authenticated
}
```

### File Upload API Call
```javascript
// In apiService.js
export const fileService = {
  uploadFiles: async (filetype, formData) => {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// In component
const formData = new FormData();
formData.append('filetype', 'image');
formData.append('photo', file);

const result = await fileService.uploadFiles('image', formData);
```

### Encryption API Call
```javascript
// In apiService.js
export const fileService = {
  hideMessage: async (message, filetype) => {
    const response = await api.post('/hide', {
      message,
      filetype,
    });
    return response.data;
  },
};

// In component
const result = await fileService.hideMessage('Secret message', 'image');
if (result.success) {
  setCipher(result.cipher);
}
```

---

## 7. Error Handling Pattern

```jsx
import React, { useState } from 'react';
import { authService } from '../services/apiService';

function SecureComponent() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAction = async () => {
    setError('');
    setLoading(true);

    try {
      // API call
      const result = await authService.login('user', 'pass', 'epass');
      
      // Handle different response scenarios
      if (result.success) {
        // Success case
        console.log('Action successful');
      } else {
        // API returned error in response
        setError(result.error || 'Unknown error occurred');
      }
    } catch (err) {
      // Network error or other exception
      setError(err.response?.data?.error || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleAction} disabled={loading}>
        {loading ? 'Processing...' : 'Perform Action'}
      </button>
      {error && (
        <div style={{ color: 'red', padding: '10px', marginTop: '10px' }}>
          {error}
        </div>
      )}
    </div>
  );
}

export default SecureComponent;
```

---

## 8. Form Validation Example

```jsx
import React, { useState } from 'react';
import { fileService } from '../services/apiService';

function ValidatedForm() {
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    const newErrors = {};

    if (!message.trim()) {
      newErrors.message = 'Message is required';
    }

    if (message.length < 5) {
      newErrors.message = 'Message must be at least 5 characters';
    }

    if (message.length > 1000) {
      newErrors.message = 'Message must not exceed 1000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const result = await fileService.hideMessage(message, 'image');
      if (result.success) {
        setMessage('');
        setErrors({});
      }
    } catch (err) {
      setErrors({ api: 'Failed to process message' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Enter message..."
      />
      {errors.message && <p style={{ color: 'red' }}>{errors.message}</p>}
      <p>{message.length} / 1000 characters</p>
      <button type="submit" disabled={loading}>
        Submit
      </button>
      {errors.api && <p style={{ color: 'red' }}>{errors.api}</p>}
    </form>
  );
}

export default ValidatedForm;
```

---

## 9. Custom Hook for API Calls

```javascript
// hooks/useApi.js
import { useState, useCallback } from 'react';

export function useApi(apiFunction) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError('');

    try {
      const result = await apiFunction(...args);
      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message;
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunction]);

  return { data, loading, error, execute };
}

// Usage in component
import { useApi } from '../hooks/useApi';
import { authService } from '../services/apiService';

function MyComponent() {
  const { data, loading, error, execute } = useApi(authService.login);

  const handleLogin = async () => {
    await execute('admin', 'admin', 'secret');
  };

  return (
    <div>
      <button onClick={handleLogin} disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
      {error && <p>{error}</p>}
      {data && <p>Welcome {data.user}</p>}
    </div>
  );
}
```

---

## 10. Context API for Global State (Optional Enhancement)

```javascript
// context/AuthContext.js
import React, { createContext, useState, useCallback } from 'react';
import { authService } from '../services/apiService';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => authService.getCurrentUser());
  const [loading, setLoading] = useState(false);

  const login = useCallback(async (username, password, epass) => {
    setLoading(true);
    try {
      const result = await authService.login(username, password, epass);
      if (result.success) {
        setUser(result.user);
      }
      return result;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// hooks/useAuth.js
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export function useAuth() {
  return useContext(AuthContext);
}

// Usage in component
function MyComponent() {
  const { user, login } = useAuth();
  
  return (
    <div>
      {user ? <p>Welcome {user}</p> : <p>Not logged in</p>}
    </div>
  );
}
```

---

## Performance Tips

1. **Use useCallback for event handlers**
   ```javascript
   const handleClick = useCallback(() => {
     // handler code
   }, []);
   ```

2. **Use useMemo for expensive computations**
   ```javascript
   const computedValue = useMemo(() => {
     return expensiveFunction(data);
   }, [data]);
   ```

3. **Lazy load routes**
   ```javascript
   const Home = lazy(() => import('./pages/Home'));
   <Suspense fallback={<Loading />}>
     <Home />
   </Suspense>
   ```

4. **Optimize re-renders**
   ```javascript
   export default React.memo(MyComponent);
   ```

---

**Last Updated:** February 2026
