import mongoose from "mongoose";

const recommendationSchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    role: { type: String, required: true },
    matchPercentage: { type: Number, required: true },
    recommendedSkills: [{ type: String }],
  },
  { timestamps: true }
);

export default mongoose.model("Recommendation", recommendationSchema);
