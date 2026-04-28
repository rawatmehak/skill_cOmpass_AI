import React, { useState } from "react";
import "./UploadResume.css";

function UploadResume() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");

  // ✅ ONLY ONE FUNCTION
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);           // file store
      setFileName(selectedFile.name);  // name show
    }
  };

  return (
  <div className="upload-page">
    <div className="upload-card">

      <h1>Upload Your Resume</h1>

      <p className="subtitle">
        Our AI will scan your resume and extract insights.
      </p>

      <input
        type="file"
        id="fileUpload"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      <label htmlFor="fileUpload" className="file-box">
        {fileName ? fileName : "Choose your resume"}
      </label>

      <button className="upload-btn">Upload & Analyze</button>

    </div>
  </div>
);
  
}

export default UploadResume;