import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginUser } from "../services/api.js";

export default function Login() {
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

async function handleLogin(e) {
  e.preventDefault();

  try {
    const res = await loginUser({ email, password });

    console.log("LOGIN RESPONSE:", res.data); // 🔥 ADD THIS

    const token = res.data.token;

    if (!token) {
      alert("Token not received!");
      return;
    }

    localStorage.setItem("token", token);

    console.log("TOKEN AFTER SAVE:", localStorage.getItem("token")); // 🔥 ADD THIS

    alert("Login successful!");
    navigate("/dashboard");

  } catch (error) {
    console.error(error);
    alert(error.response?.data?.message || "Login failed");
  }
}

  return (
    <div className="upload-page">
      <div className="upload-card">
        <h1>Login</h1>

        <form onSubmit={handleLogin} className="upload-form">
          <input
            type="email"
            placeholder="Enter email"
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Enter password"
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">Login</button>
        </form>

        <p className="note">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}
