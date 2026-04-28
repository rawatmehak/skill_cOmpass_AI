import express from "express";
import { updateUserSkills } from "../controllers/userController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

// ✅ Save user skills (protected route)
router.post("/skills", authMiddleware, updateUserSkills);

export default router;