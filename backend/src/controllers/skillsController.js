import skillsData from "../data/skills.json" with { type: "json" };
import { asyncHandler } from "../middleware/asyncHandler.js";

const createError = (message, statusCode = 400) => {
  const err = new Error(message);
  err.statusCode = statusCode;
  return err;
};

export const getTrendingSkills = asyncHandler(async (req, res) => {
  if (!skillsData || !Array.isArray(skillsData) || skillsData.length === 0) {
    throw createError("No skill data found", 404);
  }

  const trending = skillsData
    .map((skill) => ({
      name: skill.name,
      demand: skill.demand,
      growth: skill.growth,
      score: skill.demand * 0.6 + skill.growth * 0.4,
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  res.status(200).json({
    success: true,
    trendingSkills: trending,
  });
});
