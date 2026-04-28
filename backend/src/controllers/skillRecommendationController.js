import { roleSkillMap } from "../data/roleSkillMap.js";
import Recommendation from "../models/Recommendation.js";
import { asyncHandler } from "../middleware/asyncHandler.js";

const createError = (message, statusCode = 400) => {
  const err = new Error(message);
  err.statusCode = statusCode;
  return err;
};

export const recommendCareer = asyncHandler(async (req, res) => {
  const userSkills = req.body.skills;
  const userId = req.userId; // from authMiddleware

  if (!userSkills || !userSkills.length) {
    throw createError("Skills required", 400);
  }

  const roleScores = [];

  // loop through roles to compute match percentage
  for (const roleName in roleSkillMap) {
    const { requiredSkills } = roleSkillMap[roleName];
    let score = 0;
    let maxScore = 0;

    requiredSkills.forEach((reqSkill) => {
      const userSkill = userSkills.find((s) => s.name === reqSkill.name);
      maxScore += reqSkill.weight * 10;
      if (userSkill) {
        score += userSkill.rating * reqSkill.weight;
      }
    });

    const percentage = Math.round((score / maxScore) * 100);

    roleScores.push({
      role: roleName,
      score: percentage,
    });
  }

  // sort by best match
  roleScores.sort((a, b) => b.score - a.score);
  const bestMatch = roleScores[0];

  if (!bestMatch) {
    throw createError("No matching role found", 404);
  }

  const roleConfig = roleSkillMap[bestMatch.role];
  if (!roleConfig) {
    throw createError("Role configuration not found", 500);
  }

  const userSkillNames = userSkills.map((s) => s.name);

  // find missing skills
  const missingSkills = roleConfig.requiredSkills
    .filter((s) => !userSkillNames.includes(s.name))
    .map((s) => s.name);

  // save recommendation if user is authenticated
  if (userId) {
    await Recommendation.create({
      userId,
      role: bestMatch.role,
      matchPercentage: bestMatch.score,
      recommendedSkills: missingSkills,
    });
  }

  // send response
  res.status(200).json({
    success: true,
    bestRole: bestMatch.role,
    matchPercentage: bestMatch.score,
    missingSkills,
    roadmap: roleConfig.roadmap,
  });
});
