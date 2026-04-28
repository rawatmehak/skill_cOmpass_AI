import express from "express";
import multer from "multer";

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/upload", upload.single("resume"), (req, res) => {
  console.log(req.file);

  res.json({
    skills: ["React", "Node.js", "MongoDB"]
  });
});

export default router;
console.log("Resume route loaded");