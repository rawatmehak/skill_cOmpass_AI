
import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:3000/api",
  withCredentials: true,
});

function authConfig(token) {
  return token
    ? {
        headers: { Authorization: `Bearer ${token}` },
      }
    : {};
}

// ------------------ AUTH ------------------

export function loginUser(data) {
  return api.post("/auth/login", data);
}

export function registerUser(data) {
  return api.post("/auth/register", data);
}

// ------------------ SKILLS ------------------

export function updateSkills(data, token) {
  return api.post("/user/skills", data, authConfig(token));
}

// ------------------ CAREER RECOMMENDATION ------------------

export function getCareerRecommendation(skills, token) {
  return api.post("/skills/recommendation", { skills }, authConfig(token));
}

// ------------------ TRENDING SKILLS ------------------

export function getTrendingSkills() {
  return api.get("/skills/trending");
}

export function getCareerInsights(role) {
  return api.get("/insights", { params: { role } });
}

export function getJobMatches(role, skills = []) {
  return api.post("/jobs", { skills }, { params: { role } });
}

// ------------------ LOGOUT (FRONTEND ONLY) ------------------

export function logout() {
  localStorage.removeItem("token");
}
