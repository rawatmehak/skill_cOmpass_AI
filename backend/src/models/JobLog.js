import mongoose from "mongoose";

const jobLogSchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    role: { type: String, required: true },
    company: String,
    title: String,
    fitScore: Number,
  },
  { timestamps: true }
);

export default mongoose.model("JobLog", jobLogSchema);
