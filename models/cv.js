const mongoose = require('mongoose');

const cvSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  name: { type: String, required: true },
  description: { type: String, required: true }
}, { timestamps: true });

const CV = mongoose.model('CV', cvSchema);

module.exports = CV;
