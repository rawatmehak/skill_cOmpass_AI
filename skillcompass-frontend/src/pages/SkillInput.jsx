import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { updateSkills, getCareerRecommendation } from "../services/api";
import"./Skillinput.css";

export default function SkillInput() {
  const [skills, setSkills] = useState([]);
  const [input, setInput] = useState("");
  const [rating, setRating] = useState(1);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const addSkill = () => {
    if (input.trim()) {
      setSkills([...skills, { name: input.trim(), rating }]);
      setInput("");
      setRating(3);
    }
  };

  const handleSubmit = async () => {
    if (skills.length === 0) {
      alert("Add at least one skill");
      return;
    }

    try {
      setLoading(true);

      await updateSkills({ skills }, token);
      const res = await getCareerRecommendation(skills, token);

      localStorage.setItem("careerRecommendation", JSON.stringify(res.data));
      localStorage.setItem("bestRole", res.data.bestRole);
      localStorage.setItem("matchPercentage", String(res.data.matchPercentage));
      localStorage.setItem("missingSkills", JSON.stringify(res.data.missingSkills));
      localStorage.setItem("roadmap", JSON.stringify(res.data.roadmap));

      alert("Skills analyzed successfully.");
      navigate("/dashboard");
    } catch (error) {
      console.error(error);
      alert("Error processing skills");
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="skills-page">
    <div className="skills-card">

      <h1>Add Your Skills</h1>

      <input
        type="text"
        placeholder="e.g. React, Python"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <div className="slider-box">
        <label>Rating: {rating}/5</label>
        <input
          type="range"
          min="1"
          max="5"
          value={rating}
          onChange={(e) => setRating(Number(e.target.value))}
        />
      </div>

      <button onClick={addSkill}>Add Skill</button>

      <h3>Your Skills:</h3>
      <ul className="skill-list">
        {skills.map((skill, index) => (
          <li key={index}>
            {skill.name} - {skill.rating}
          </li>
        ))}
      </ul>

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Processing..." : "Submit"}
      </button>

    </div>
  </div>
);
}
