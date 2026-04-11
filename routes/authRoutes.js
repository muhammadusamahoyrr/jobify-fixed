const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/user');

const router = express.Router();

// Sign up route
router.post('/signup', async (req, res) => {
  try {
    const newUser = req.body;
    const hashedPassword = await bcrypt.hash(newUser.password, 10);
    newUser.password = hashedPassword;

    const doc = new User(newUser);
    await doc.save();
    res.status(200).json({ message: "User created successfully! Press SignIn Now!" });
  } catch (err) {
    res.status(500).json({ error: 'User creation failed', details: err.message });
  }
});

// Sign in route
router.post('/signin', async (req, res) => {
  try {
    const { email, password, role } = req.body;
    const user = await User.findOne({ email, role });
    if (!user) return res.status(400).json({ error: `${role} with this email not found` });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ error: 'Invalid password' });

    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRE });
    res.status(200).json({ token });
  } catch (err) {
    res.status(500).json({ error: 'User signin failed', details: err.message });
  }
});

module.exports = router;
