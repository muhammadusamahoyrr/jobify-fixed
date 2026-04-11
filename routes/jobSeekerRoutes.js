const express = require('express');
const Job = require('../models/job');
const CV = require('../models/cv');

const router = express.Router();

//Job seeker routes
//1-Fetch all jobs in website
router.get('/fetch-all-jobs', async (req, res) => {
  try {
    const allJobs = await Job.find();
    res.json(allJobs);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch all jobs', details: err.message });
  }
});

//2-Fetch all jobs the job seeker applied for
router.get('/applied-jobs',  async (req, res) => {
  try {
    const appliedJobs = await Job.find({ "applications.userId": req.user.id });
    res.json({AppliedJobs: appliedJobs, ApplyerID: req.user.id });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch applied jobs', details: err.message });
  }
});

//3-Remove application to a specific job
router.delete('/remove-application/:jobId',  async (req, res) => {
  try {
    await Job.findByIdAndUpdate(req.params.jobId, { $pull: { applications: { userId: req.user.id } } });
    res.json({ message: "Application removed successfully!" });
  } catch (err) {
    res.status(500).json({ error: 'Failed to remove application', details: err.message });
  }
});

//4-CRUD on CV
router.post('/create-cv',  async (req, res) => {
  try {
    const newCV = req.body;
    newCV.userId = req.user.id;
    const cv = new CV(newCV);
    await cv.save();
    res.json({message: 'CV created successfully!'});
  } catch (err) {
    res.status(500).json({ error: 'Failed to create CV', details: err.message });
  }
});

router.get('/fetch-cv',  async (req, res) => {
  try {
    const cv = await CV.findOne({ userId: req.user.id });
    res.json(cv);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch CV', details: err.message });
  }
});



router.put('/update-cv',  async (req, res) => {
  try {
    const updatedCV = await CV.findOneAndUpdate({ userId: req.user.id }, req.body, { new: true });
    res.json({message: 'CV updated successfully!'});
  } catch (err) {
    res.status(500).json({ error: 'Failed to update CV', details: err.message });
  }
});

router.delete('/delete-cv',  async (req, res) => {
  try {
    await CV.findOneAndDelete({ userId: req.user.id });
    res.json({ message: "CV deleted successfully!" });
  } catch (err) {
    res.status(500).json({ error: 'Failed to delete CV', details: err.message });
  }
});

// Job seeker applies for a job
router.post('/apply-job/:jobId',  async (req, res) => {
  try {
    const jobId = req.params.jobId;
    const userId = req.user.id;

    const job = await Job.findById(jobId);
    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }

    const alreadyApplied = job.applications.some((application) => application.userId.toString() === userId);
    if (alreadyApplied) {
      return res.status(400).json({ error: 'You have already applied for this job' });
    }
     
    const cvExists=await CV.findOne({userId:req.user.id});  //await is important
    console.log("DOES CV EXIST:",cvExists);
    if(!cvExists)
    {
        return res.status(400).json({error: "Create a CV first!"})
    }

    job.applications.push({ userId });
    await job.save();

    res.status(200).json({ message: 'Application submitted successfully!' });
  } catch (err) {
    res.status(500).json({ error: 'Failed to apply for job', details: err.message });
  }
});

router.delete('/remove-application/:jobId',  async (req, res) => {
  try {
    const jobId = req.params.jobId;
    const userId = req.user.id;

    const job = await Job.findById(jobId);
    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }


    job.applications = job.applications.filter((application) => {
      return application.userId.toString() !== userId.toString();
    });

    await job.save();

    res.status(200).json({ message: 'Application removed successfully!' });
  } catch (err) {
    res.status(500).json({ error: 'Failed to remove application', details: err.message });
  }
});





module.exports = router;
