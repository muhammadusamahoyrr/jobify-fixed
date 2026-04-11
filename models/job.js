const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  title: { type: String, required: true },
  description: { type: String, required: true },
  datePosted: { type: Date, default: Date.now },
  city: { type: String, required: true },
  country: { type: String, required: true },
  salary: { type: Number },
  company: { type: String, required: true },
  jobType: { type: String, required: true },
  applications: [{
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    approvalStatus: { type: String, default: 'Awaiting Employer Response' },
    interviewDate: { type: String, default: 'Awaiting Employer Response' }
  }]
});

const Job = mongoose.model('Job', jobSchema);

module.exports = Job;
