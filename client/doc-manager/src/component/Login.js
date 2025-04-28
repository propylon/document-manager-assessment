import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import config from "../config"; // Import the config file
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Alert,
} from "@mui/material";

function Login({ onLogin }) {
  const [email, setUsername] = useState("admin@example.com");
  const [password, setPassword] = useState("admin@123");
  const [error, setError] = useState("");
  const navigate = useNavigate(); 

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Simple validation
    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }

    try {
      // Call the API
      const response = await fetch(`${config.serverUrl}/api/token/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({email, password }),
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error("Invalid email or password.");
      }

      const data = await response.json();

      // Save the token to localStorage
      // localStorage.setItem("authToken", data.token);

      // Notify parent component about successful login
      onLogin(data.user);
      navigate("/upload-file"); 
    } catch (err) {
      setError(err.message || "An error occurred. Please try again.");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
      >
        <Box
          p={4}
          bgcolor="white"
          boxShadow={3}
          borderRadius={2}
          width="100%"
        >
          <Typography variant="h4" component="h1" gutterBottom>
            Login
          </Typography>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <form onSubmit={handleSubmit}>
            <Box mb={3}>
              <TextField
                label="Username"
                variant="outlined"
                fullWidth
                value={email}
                onChange={(e) => setUsername(e.target.value)}
              />
            </Box>
            <Box mb={3}>
              <TextField
                label="Password"
                type="password"
                variant="outlined"
                fullWidth
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Box>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
            >
              Login
            </Button>
          </form>
        </Box>
      </Box>
    </Container>
  );
}

export default Login;