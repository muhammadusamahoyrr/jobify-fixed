const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/user');
const router = express.Router();

// Sign up route
router.post('/signup', async (req, res) => {
  try {
    const { name, email, password, role } = req.body;

    // FIX: Validate required fields before doing anything
    if (!name || !email || !password || !role) {
      return res.status(400).json({ error: 'All fields (name, email, password, role) are required' });
    }

    // FIX: Check if user already exists
    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(400).json({ error: 'User with this email already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const doc = new User({ name, email, password: hashedPassword, role });
    await doc.save();

    res.status(200).json({ message: "User created successfully! Press SignIn Now!" });
  } catch (err) {
    console.error('Signup error:', err.message);
    res.status(500).json({ error: 'User creation failed', details: err.message });
  }
});

// Sign in route
router.post('/signin', async (req, res) => {
  try {
    const { email, password, role } = req.body;

    // FIX: Validate required fields
    if (!email || !password || !role) {
      return res.status(400).json({ error: 'Email, password, and role are required' });
    }

    const user = await User.findOne({ email, role });
    if (!user) return res.status(400).json({ error: `${role} with this email not found` });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ error: 'Invalid password' });

    // FIX: Guard against missing JWT_SECRET env variable
    if (!process.env.JWT_SECRET) {
      console.error('JWT_SECRET is not set in environment variables!');
      return res.status(500).json({ error: 'Server configuration error' });
    }

    const token = jwt.sign(
      { id: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRE || '1d' }
    );

    res.status(200).json({ token });
  } catch (err) {
    console.error('Signin error:', err.message);
    res.status(500).json({ error: 'User signin failed', details: err.message });
  }
});

module.exports = router;
