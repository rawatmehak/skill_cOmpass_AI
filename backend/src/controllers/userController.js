import User from "../models/User.js";
import { asyncHandler } from "../middleware/asyncHandler.js";

const createError = (message, statusCode = 400) => {
  const err = new Error(message);
  err.statusCode = statusCode;
  return err;
};

export const updateUserSkills = asyncHandler(async (req, res) => {
  const userId = req.userId; // comes from authMiddleware
  const { skills } = req.body;

  if (!skills || !Array.isArray(skills) || skills.length === 0) {
    throw createError("Skills are required", 400);
  }

  const user = await User.findById(userId);
  if (!user) {
    throw createError("User not found", 404);
  }

  user.skills = skills; // replace old skill list
  await user.save();

  res.status(200).json({
    success: true,
    message: "Skills updated successfully",
    skills: user.skills,
  });
});
