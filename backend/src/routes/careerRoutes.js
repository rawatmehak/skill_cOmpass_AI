import express from "express";
import { recommendCareer } from "../controllers/careerController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

router.post("/recommend",authMiddleware, recommendCareer);

export default router;
