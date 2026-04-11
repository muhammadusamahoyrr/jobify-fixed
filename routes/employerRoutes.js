const express = require('express');
const Job = require('../models/job');
const CV = require('../models/cv');

const router = express.Router();

// Employer routes
router.post('/post-job', async (req, res) => {
  try {
    const { title, description, city, country, salary, company, jobType } = req.body;

    if (!title || !description || !city || !country || !salary || !company || !jobType) {
      return res.status(400).json({ error: 'All fields are required' });
    }

    const newJob = {
      userId: req.user.id,
      title,
      description,
      city,
      country,
      salary,
      company,
      jobType,
    };

    const job = new Job(newJob);
    await job.save();
    res.status(201).json({ message: 'Job successfully created!', job });
  } catch (err) {
    res.status(500).json({ error: 'Failed to post job', details: err.message });
  }
});

// Employer delete job
router.delete('/delete-job/:id', async (req, res) => {
  try {
    await Job.findByIdAndDelete(req.params.id);
    res.json({ message: "Job deleted successfully!" });
  } catch (err) {
    res.status(500).json({ error: 'Failed to delete job', details: err.message });
  }
});

// Employer update job
router.put('/update-job/:id', async (req, res) => {
  try {
    const fetchJob = req.body;
    const updatedJob = await Job.findByIdAndUpdate(req.params.id, fetchJob, { new: true });
    res.json({ message: "Job Updated successfully!" });
  } catch (err) {
    res.status(500).json({ error: 'Failed to update job', details: err.message });
  }
});

// Fetch jobs created by employer
router.get('/get-jobs', async (req, res) => {
  try {
    const myJobs = await Job.find({ userId: req.user.id });
    if (myJobs.length === 0) {
      return;
    }
    res.json(myJobs);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch jobs', details: err.message });
  }
});

// Fetch CV
router.get('/fetch-cv/:cvId', async (req, res) => {
  try {
    const cv = await CV.findOne({ userId: req.params.cvId });
    res.json(cv);
  } catch (err) {
    res.status(500).json({ error: 'CV not found!', details: err.message });
  }
});

router.put('/give-approval/:jobId/:userId', async (req, res) => {
  const { jobId, userId } = req.params;
  const { approvalStatus, interviewDate } = req.body;

  try {
    const updatedJob = await Job.findOneAndUpdate(
      { _id: jobId, "applications.userId": userId }, 
      {
        $set: {
          "applications.$.approvalStatus": approvalStatus, 
          "applications.$.interviewDate": interviewDate     //$ means the specific element in the applications array that matched the query condition 
        }
      },
      { new: true }
    );

    console.log("Updated Job:", updatedJob);

    if (updatedJob) {
      res.status(200).json({ message: "Updated Approval Successfully" });
    } else {
      res.status(404).json({ error: 'Job or application not found' });
    }

  } catch (err) {
    console.log('Error setting approval status:', err);
    res.status(500).json({ error: 'Setting approval status failed', details: err.message });
  }
});

router.get('/get-status/:jobId/:userId',async (req,res)=>{

  try
  {
       const obj=await CV.findOne({ _id: jobId, "applications.userId": userId })
       res.status(200).json({approvalStatus: obj.approvalStatus, interviewDate: obj.interviewDate})

  }
  catch(err)
  {
      console.log(err)
      res.status(500).json({error: "Error fetching approval status and interview date", details: err.message})
  }


})


module.exports = router;
