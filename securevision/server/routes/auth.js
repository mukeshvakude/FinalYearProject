const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const auth = require('../middleware/auth');

const JWT_EXPIRY = '7d';

function signToken(user) {
  return jwt.sign(
    { id: user._id, username: user.username, email: user.email },
    process.env.JWT_SECRET || 'fallback_secret',
    { expiresIn: JWT_EXPIRY }
  );
}

// POST /api/auth/register
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'username, email and password are required' });
    }

    const existingUser = await User.findOne({ $or: [{ email }, { username }] });
    if (existingUser) {
      return res.status(409).json({ error: 'Username or email already in use' });
    }

    const user = await User.create({ username, email, password });
    const token = signToken(user);
    return res.status(201).json({ token, user: { id: user._id, username: user.username, email: user.email } });
  } catch (err) {
    console.error('Register error:', err);
    return res.status(500).json({ error: 'Server error during registration' });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: 'email and password are required' });
    }

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const match = await user.comparePassword(password);
    if (!match) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = signToken(user);
    return res.json({ token, user: { id: user._id, username: user.username, email: user.email } });
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ error: 'Server error during login' });
  }
});

// GET /api/auth/me  (protected)
router.get('/me', auth, (req, res) => {
  res.json({ user: req.user });
});

module.exports = router;
