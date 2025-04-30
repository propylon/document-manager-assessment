import React from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("authToken"); // Remove the token from localStorage
    navigate("/login"); // Redirect to the login page
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-6 rounded shadow-md">
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
        <div className="mb-4">
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Navigation</h2>
          <ul className="list-disc pl-5">
            <li>
              <button
                onClick={() => navigate("/file-versions")}
                className="text-blue-500 hover:underline"
              >
                Browse File Versions
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;