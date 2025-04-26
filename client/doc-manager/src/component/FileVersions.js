import React, { useState, useEffect } from "react";
import config from "../config"; // Import the config file
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Alert,
} from "@mui/material";
import { Download } from "@mui/icons-material"; 
import { useLocation } from "react-router-dom";

function FileVersionsList(props) {
  const file_versions = props.file_versions;
  const token = localStorage.getItem("authToken");

  const handleLinkClick = async (file_name, version_number) => {
    const apiUrl = `${config.serverUrl}/api/document/${file_name}?revision=${version_number}`;
    try {
      const response = await fetch(apiUrl, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `token ${token}`, // Use the token from localStorage
        },
      });

      // Convert response to blob
      const blob = await response.blob();

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file_name; // Set the file name for download
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url); // Clean up the URL object
    } catch (err) {
      console.error("Error downloading file:", err);
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>File Name</TableCell>
            <TableCell>Version</TableCell>
            <TableCell>Content</TableCell>
            <TableCell>Created At</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {file_versions.map((file_version) => (
            <TableRow key={file_version.id}>
              <TableCell>{file_version.file_name}</TableCell>
              <TableCell>{file_version.version_number}</TableCell>
              <TableCell>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() =>
                    handleLinkClick(
                      file_version.file_name,
                      file_version.version_number
                    )
                  }
                >      
                <Download />
                </Button>
              </TableCell>
              <TableCell>
                {new Date(file_version.created_at).toLocaleString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function FileVersions() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const id = params.get("id") || ""; // Extract the id from the query parameter

  useEffect(() => {
    const dataFetch = async () => {
      const token = localStorage.getItem("authToken");

      if (!token) {
        console.error("No token found in localStorage");
        setError("No token found in localStorage");
        return;
      }

      try {
        const response = await fetch(`${config.serverUrl}/api/document?id=${id}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `token ${token}`, // Use the token from localStorage
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setData(data);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError(err.message);
      }
    };

    dataFetch();
  }, []);

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
        <Typography variant="h6" sx={{ textAlign: "left", mb: 2 }}>
          Found {data.length} File Versions
        </Typography>
      <FileVersionsList file_versions={data} />
    </Container>
  );
}

export default FileVersions;