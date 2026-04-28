import skillsData from "../data/skills.json" with { type: "json" };
import { asyncHandler } from "../middleware/asyncHandler.js";

const createError = (message, statusCode = 400) => {
  const err = new Error(message);
  err.statusCode = statusCode;
  return err;
};

export const getCareerInsights = asyncHandler(async (req, res) => {
  const { role } = req.query; // ?role=Frontend Developer

  if (!role) {
    throw createError("Role is required", 400);
  }

  // simplified static insights
  const insightsMap = {
    "Frontend Developer": {
      avgSalary: "6-10 LPA",
      saturationLevel: "Medium",
      jobGrowth: "8%",
      keyTrends: ["React", "TypeScript", "Next.js"],
    },
    "Backend Developer": {
      avgSalary: "8-14 LPA",
      saturationLevel: "Low",
      jobGrowth: "10%",
      keyTrends: ["Node.js", "GraphQL", "Cloud Integration"],
    },
    "Data Analyst": {
      avgSalary: "5-9 LPA",
      saturationLevel: "High",
      jobGrowth: "6%",
      keyTrends: ["Python", "Power BI", "SQL", "Tableau"],
    },
  };

  const data = insightsMap[role];
  if (!data) {
    throw createError("Role not found", 404);
  }

  // average growth/demand from skills.json
  const relatedSkills = skillsData.filter((skill) =>
    data.keyTrends.includes(skill.name)
  );

  const avgGrowth = Math.round(
    relatedSkills.reduce((acc, s) => acc + s.growth, 0) /
      (relatedSkills.length || 1)
  );

  const avgDemand = Math.round(
    relatedSkills.reduce((acc, s) => acc + s.demand, 0) /
      (relatedSkills.length || 1)
  );

  res.status(200).json({
    success: true,
    role,
    avgSalary: data.avgSalary,
    saturationLevel: data.saturationLevel,
    jobGrowth: data.jobGrowth,
    avgDemand,
    avgGrowth,
    keyTrends: data.keyTrends,
  });
});
