import roles from "../data/roles.json" with { type: "json" };
import skillsData from "../data/skills.json" with { type: "json" };
import { calculateScore } from "../utils/scoring.js";
import User from "../models/User.js";
import { asyncHandler } from "../middleware/asyncHandler.js";

const createError = (message, statusCode = 400) => {
  const err = new Error(message);
  err.statusCode = statusCode;
  return err;
};

export const recommendCareer = asyncHandler(async (req, res) => {
  const userId = req.userId;
  const user = await User.findById(userId);

  if (!user || !user.skills || !user.skills.length) {
    throw createError("No skills found. Please update your skills first.", 400);
  }

  const userSkills = user.skills;
  const userSkillNames = userSkills.map((s) => s.name);

  // find the closest-matching role
  const matchedRole = roles
    .map((role) => {
      const matchedSkills = role.requiredSkills.filter((skill) =>
        userSkillNames.includes(skill)
      );
      return {
        role: role.role,
        matchCount: matchedSkills.length,
        totalRequired: role.requiredSkills.length,
      };
    })
    .sort((a, b) => b.matchCount - a.matchCount)[0];

  if (!matchedRole) {
    throw createError("No matching career found for given skills.", 404);
  }

  const targetRole = roles.find((r) => r.role === matchedRole.role);
  if (!targetRole) {
    throw createError("Target role not found.", 404);
  }

  // missing skills with score
  const missingSkills = targetRole.requiredSkills
    .filter((skill) => !userSkillNames.includes(skill))
    .map((skill) => {
      const skillInfo = skillsData.find((s) => s.name === skill);
      if (!skillInfo) {
        throw createError(`Skill info missing for ${skill}`, 500);
      }
      return {
        ...skillInfo,
        calculatedScore: calculateScore(skillInfo),
      };
    })
    .sort((a, b) => b.calculatedScore - a.calculatedScore)
    .slice(0, 3);

  // calculate match %
  const matchedSkillRatings = userSkills
    .filter((s) => targetRole.requiredSkills.includes(s.name))
    .reduce((acc, s) => acc + s.rating, 0);

  const maxPossibleRating = matchedRole.totalRequired * 10;
  const matchPercentage = Math.round(
    (matchedSkillRatings / maxPossibleRating) * 100
  );

  res.status(200).json({
    success: true,
    role: matchedRole.role,
    matchPercentage,
    recommendedSkills: missingSkills,
  });
});
