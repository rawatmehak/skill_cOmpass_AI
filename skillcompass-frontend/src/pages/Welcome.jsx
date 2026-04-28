import React from "react";
import { Link } from "react-router-dom";
import "./Welcome.css"; // 👈 create this file below


function Welcome() {
  return (
    <div className="welcome-page">
      <div className="welcome-card">
        <h1>🎯 Welcome to SkillCompass AI</h1>
        <p className="subtitle">
          Discover your ideal tech career path — powered by AI insights.
        </p>

        <div className="button-group">
          <Link to="/upload" className="btn primary">
            Upload Resume
          </Link>

          <Link to="/skills" className="btn secondary">
            Enter Skills Manually
          </Link>
        </div>

        <p className="note">
          🚀 Let’s analyze your skills and find your perfect career direction.
        </p>
      </div>
    </div>
  );
}

export default Welcome;
