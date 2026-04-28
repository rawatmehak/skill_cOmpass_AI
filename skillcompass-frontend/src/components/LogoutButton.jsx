import { useNavigate } from "react-router-dom";
import { logout } from "../services/api";

export default function LogoutButton() {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    localStorage.removeItem("careerRecommendation");
    localStorage.removeItem("bestRole");
    localStorage.removeItem("matchPercentage");
    localStorage.removeItem("missingSkills");
    localStorage.removeItem("roadmap");
    navigate("/login");
  };

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition"
    >
      Logout
    </button>
  );
}
