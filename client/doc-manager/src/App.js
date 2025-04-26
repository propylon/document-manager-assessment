import './App.css';
import React, { useState } from "react";
import AppRoutes from "./Routes";

import { Link } from "react-router-dom";
import { Logout } from "@mui/icons-material"; // Import the Logout icon
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { useNavigate } from "react-router-dom"; // Import useNavigate

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem("authToken"); // Clear token on logout
    navigate("/login"); // Redirect to login page
  };

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 , textAlign: "left" }}>
            Document Manager
          </Typography>
          {isLoggedIn ? (
            <>
              <Button color="inherit" component={Link} to="/upload-file">
                Upload File
              </Button>
              {/* <Button color="inherit" component={Link} to="/document-list">
                Document List
              </Button> */}
              <Button color="inherit" component={Link} to="/file-versions">
                File Versions
              </Button>
              <Button color="inherit" onClick={handleLogout} startIcon={<Logout />}>
                Logout
              </Button>
            </>
          ) : (
            <Button color="inherit" component={Link} to="/login">
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