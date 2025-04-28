import './App.css';
import React, { useState } from "react";
import AppRoutes from "./Routes";

import { Link } from "react-router-dom";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import { UploadFile, Folder, Logout , Person} from "@mui/icons-material"; // Import icons
import { Divider } from "@mui/material"; // Import Divider
import { useTheme } from "@mui/material/styles"; // Import useTheme
import config from "./config"; // Import the config file
import { fetchWithRefresh } from "./utils/FetchWithRefresh"; // Import the fetchWithRefresh function

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();
  const theme = useTheme();
  const [error, setError] = useState("");

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = async () => {
    setIsLoggedIn(false);
    try {
      const response = await fetchWithRefresh(`${config.serverUrl}/api/logout/`, {
        method: "GET",
        credentials: "include",
      });
  
      const responseData = await response.json();
  
      if (response.status === 200 && responseData.responseCode === 202) {
        navigate("/login"); // Redirect to the login page
      } else {
        setError(responseData.responseMessage || "Failed to logout.");
      }
    } catch (err) {
      setError(err.message || "An error occurred during logout.");
    }
  };

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, textAlign: "left" }}>
            Document Manager
          </Typography>
          {isLoggedIn ? (
            <>
              <Divider
                orientation="vertical"
                flexItem
                sx={{ mx: 2, borderColor: theme.palette.divider  }} // Add spacing and color
              />
              <Button
                color="inherit"
                component={Link}
                to="/upload-file"
                startIcon={<UploadFile />} // Add UploadFile icon
              >
                Upload File
              </Button>
              <Divider
                orientation="vertical"
                flexItem
                sx={{ mx: 2, borderColor: theme.palette.divider }} // Add spacing and color
              />
              <Button
                color="inherit"
                component={Link}
                to="/file-versions"
                startIcon={<Folder />} // Add Folder icon
              >
                File Versions
              </Button>
              <Divider
                orientation="vertical"
                flexItem
                sx={{ mx: 2, borderColor: theme.palette.divider }} // Add spacing and color
              />
              <Button
                color="inherit"
                onClick={handleLogout}
                startIcon={<Logout />}
              >
                Logout
              </Button>
            </>
          ) : (
            <Button
              color="inherit"
              component={Link}
              to="/login"
              startIcon={<Person />} // Add Login icon
            >
              Login
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Box mt={2}>
        <AppRoutes isLoggedIn={isLoggedIn} handleLogin={handleLogin} />
      </Box>
    </div>
  );
}

export default App;