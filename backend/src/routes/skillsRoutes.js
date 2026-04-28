import express from "express";
import { getTrendingSkills } from "../controllers/skillsController.js";

const router = express.Router();

router.get("/trending", getTrendingSkills);

export default router;
