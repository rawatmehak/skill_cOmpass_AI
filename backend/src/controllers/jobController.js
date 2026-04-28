import { asyncHandler } from "../middleware/asyncHandler.js";

const createError = (message, statusCode = 400) => {
  const err = new Error(message);
  err.statusCode = statusCode;
  return err;
};

export const getJobsByRole = asyncHandler(async (req, res) => {
  const { role } = req.query;
  const { skills } = req.body; // user’s current skills array (strings)

  if (!role) {
    throw createError("Role is required", 400);
  }

  // mock job listings
  const jobDatabase = {
    "Frontend Developer": [
      {
        company: "TechNova Solutions",
        title: "Frontend Developer",
        location: "Bangalore, India",
        salary: "₹6–10 LPA",
        skills: ["React", "JavaScript", "HTML", "CSS"],
        type: "Remote",
      },
      {
        company: "Designify Labs",
        title: "Junior React Engineer",
        location: "Pune, India",
        salary: "₹5–8 LPA",
        skills: ["React", "Tailwind", "TypeScript"],
        type: "Hybrid",
      },
    ],
    "Backend Developer": [
      {
        company: "DataFlow Systems",
        title: "Backend Developer (Node.js)",
        location: "Hyderabad, India",
        salary: "₹8–12 LPA",
        skills: ["Node.js", "Express", "MongoDB"],
        type: "Remote",
      },
      {
        company: "CodeStack Technologies",
        title: "API Engineer",
        location: "Gurgaon, India",
        salary: "₹9–14 LPA",
        skills: ["Node.js", "GraphQL", "SQL"],
        type: "On-site",
      },
    ],
    "Data Analyst": [
      {
        company: "Insight Analytics Pvt Ltd",
        title: "Data Analyst",
        location: "Mumbai, India",
        salary: "₹5–9 LPA",
        skills: ["Python", "Excel", "Power BI"],
        type: "Hybrid",
      },
      {
        company: "DataVerse Global",
        title: "Junior Data Analyst",
        location: "Chennai, India",
        salary: "₹4–7 LPA",
        skills: ["SQL", "Tableau", "Python"],
        type: "Remote",
      },
    ],
  };

  const jobs = jobDatabase[role];
  if (!jobs) {
    throw createError("No jobs found for this role", 404);
  }

  // calculate fit score
  const enhancedJobs = jobs.map((job) => {
    const jobSkills = job.skills.map((s) => s.toLowerCase());
    const userSkillsLower = (skills || []).map((s) => s.toLowerCase());

    const matchedSkills = jobSkills.filter((s) =>
      userSkillsLower.includes(s)
    );

    const fitScore = Math.round(
      (matchedSkills.length / jobSkills.length) * 100
    );

    return {
      ...job,
      fitScore,
      matchedSkills,
    };
  });

  enhancedJobs.sort((a, b) => b.fitScore - a.fitScore);

  res.status(200).json({
    success: true,
    role,
    totalJobs: enhancedJobs.length,
    jobs: enhancedJobs,
  });
});
