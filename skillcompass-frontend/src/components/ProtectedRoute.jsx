import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");

  // If no token → go to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Otherwise load the requested page
  return children;
}
