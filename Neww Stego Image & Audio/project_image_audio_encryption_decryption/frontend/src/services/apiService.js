import axios from 'axios';

// Configure API base URL
const API_BASE_URL = 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 5000, // 5 second timeout for all requests
});

// Add a request interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // For 401 errors, clear local state but do not force a reload.
    // Components should handle unauthenticated state to avoid reload loops.
    if (error.response?.status === 401) {
      try {
        localStorage.removeItem('user');
      } catch (e) {
        // ignore storage errors
      }
    }
    return Promise.reject(error);
  }
);

// Authentication Services
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

  logout: async () => {
    const response = await api.post('/logout');
    localStorage.removeItem('user');
    return response.data;
  },

  getSession: async () => {
    const response = await api.get('/session');
    return response.data;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('user');
  },

  getCurrentUser: () => {
    return localStorage.getItem('user');
  },
};

// Content Services
export const contentService = {
  getHome: async () => {
    const response = await api.get('/home');
    return response.data;
  },

  getInfo: async () => {
    const response = await api.get('/info');
    return response.data;
  },
};

// File Services
export const fileService = {
  uploadFiles: async (filetype, formData) => {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  hideMessage: async (message, filetype) => {
    const response = await api.post('/hide', {
      message,
      filetype,
    });
    return response.data;
  },

  decryptMessage: async (cipherText, password) => {
    console.log('📤 API: Sending decrypt request');
    console.log('Cipher:', cipherText.substring(0, 50) + '...');
    console.log('Password length:', password.length);
    
    try {
      const response = await api.post('/decrypt', {
        cipherText,
        password,
      });
      
      console.log('📥 API: Decrypt response received');
      console.log('Status:', response.status);
      console.log('Data:', response.data);
      
      return response.data;
    } catch (error) {
      console.error('❌ API: Decrypt request failed');
      console.error('Status:', error.response?.status);
      console.error('Data:', error.response?.data);
      console.error('Message:', error.message);
      throw error;
    }
  },

  getAudioList: async () => {
    const response = await api.get('/audio-list');
    return response.data;
  },

  // Face Authentication API calls
  enrollFace: async (formData) => {
    const response = await api.post('/face/enroll', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 10000 // Longer timeout for file upload
    });
    return response.data;
  },

  verifyFace: async (formData) => {
    const response = await api.post('/face/verify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 10000 // Longer timeout for file upload
    });
    return response.data;
  },

  checkFaceEnrollment: async () => {
    try {
      const response = await api.get('/face/check-enrollment', {
        timeout: 5000 // 5 second timeout for status check (increased from 3s)
      });
      return response;
    } catch (error) {
      // Return null response if face auth check fails
      // This allows app to continue without face auth
      throw error;
    }
  },

  deleteFace: async () => {
    const response = await api.post('/face/delete');
    return response.data;
  },

  getFaceStats: async () => {
    const response = await api.get('/face/stats');
    return response.data;
  },
};

// Health Check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    return { status: 'error', error: error.message };
  }
};

export default api;
