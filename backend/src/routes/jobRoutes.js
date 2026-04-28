import express from "express";
import { getJobsByRole } from "../controllers/jobController.js";

const router = express.Router();

router.post("/", getJobsByRole); // GET /api/jobs?role=Frontend Developer

export default router;
