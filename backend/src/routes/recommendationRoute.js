import express from "express";
import { recommendCareer } from "../controllers/skillRecommendationController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

router.post("/recommendation", authMiddleware, recommendCareer);

export default router;
