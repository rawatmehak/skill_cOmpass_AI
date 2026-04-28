import express from "express";
import cors from "cors";
import morgan from "morgan";
import { errorHandler } from "./middleware/errorHandler.js";
import careerRoutes from "./routes/careerRoutes.js";
import authRoutes from "./routes/authRoutes.js";
import userRoutes from "./routes/userRoutes.js";
import recommendationRoutes from "./routes/recommendationRoute.js";
import skillRoutes from "./routes/skillsRoutes.js";
import careerInsightsRoutes from "./routes/careerInsightsRoutes.js";
import jobRoutes from "./routes/jobRoutes.js";
import recommendationHistoryRoutes from "./routes/recommendationHistoryRoutes.js";
import resumeRoutes from "./routes/resumeRoutes.js";

const app = express();

app.use(cors({
  origin: "http://localhost:5173",
  credentials: true
}));

app.use(morgan("dev"));
app.use(express.json());

// ✅ YAHAN ADD KARO
app.get("/", (req, res) => {
  res.send("Backend working ✅");
});

// routes
app.use("/api/careers", careerRoutes);
app.use("/api/auth", authRoutes);
app.use("/api/user", userRoutes);
app.use("/api/skills", recommendationRoutes);
app.use("/api/skills", skillRoutes);
app.use("/api/insights", careerInsightsRoutes);
app.use("/api/jobs", jobRoutes);
app.use("/api/recommendation", recommendationHistoryRoutes);
app.use("/api/resume", resumeRoutes);

// error handler (always last)
app.use(errorHandler);

export default app;