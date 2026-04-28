import express from "express";
import Recommendation from "../models/Recommendation.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

router.get("/history", authMiddleware, async (req, res) => {
  try {
    const history = await Recommendation.find({ userId: req.userId })
      .sort({ createdAt: -1 })
      .limit(10);
    res.json({ history });
  } catch (error) {
    console.error("Error fetching recommendation history:", error);
    res.status(500).json({ message: "Server error" });
  }
});

export default router;
