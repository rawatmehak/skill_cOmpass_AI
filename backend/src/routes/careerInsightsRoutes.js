import express from "express";
import { getCareerInsights } from "../controllers/careerInsightsController.js";

const router = express.Router();

router.get("/", getCareerInsights);

export default router;
