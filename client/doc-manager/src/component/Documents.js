import React, { useState, useEffect } from "react";
import { Container, Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { Tooltip } from "@mui/material"; // Import Tooltip
import { Download, Visibility } from "@mui/icons-material"; // Import icons
import config from "../config";

function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDocuments = async () => {
      const token = localStorage.getItem("authToken");
      if (!token) {
        setError("You must be logged in to view the document list.");
        return;
      }

      try {
        const response = await fetch(`${config.serverUrl}/api/file`, {
          method: "GET",
          headers: {
            Authorization: `token ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch documents.");
        }

        const data = await response.json();
        setDocuments(data);
      } catch (err) {
        setError(err.message || "An error occurred. Please try again.");
      }
    };

    fetchDocuments();
  }, []);

  const handleViewVersions = (id) => {
    navigate(`/file-versions?id=${id}`); // Redirect to file-versions with the id as a query parameter
  };

  const handleDownloadLatest = async (fileName) => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      setError("You must be logged in to download files.");
      return;
    }

    try {
      const response = await fetch(`${config.serverUrl}/api/document/${fileName}`, {
        method: "GET",
        headers: {
          Authorization: `token ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to download the file.");
      }

      // Convert response to blob
      const blob = await response.blob();

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName; // Set the file name for download
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url); // Clean up the URL object
    } catch (err) {
      setError(err.message || "An error occurred while downloading the file.");
    }
  };

  return (
    <Container maxWidth="md">
      <Box mt={4}>
        <Typography variant="h6" sx={{ textAlign: "left", mb: 2 }}>
          Document List
        </Typography>
        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ display: "none" }}>ID</TableCell> {/* Hidden ID column */}
                <TableCell>File Name</TableCell>
                <TableCell>Latest Version</TableCell>
                <TableCell>Total Versions</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((doc, index) => (
                <TableRow key={index}>
                  <TableCell sx={{ display: "none" }}>{doc.id}</TableCell> {/* Hidden ID value */}
                  <TableCell>{doc.file_name}</TableCell>
                  <TableCell>{doc.latest_version_number}</TableCell>
                  <TableCell>{doc.file_version_count}</TableCell>
                  <TableCell>
                    <Tooltip title="View Versions">
                        <Button
                        variant="contained"
                        color="primary"
                        onClick={() => handleViewVersions(doc.id)}
                        sx={{ mr: 1 }}
                        >
                        <Visibility />
                        </Button>
                    </Tooltip>
                    <Tooltip title="Download Latest">
                        <Button
                        variant="contained"
                        color="secondary"
                        onClick={() => handleDownloadLatest(doc.file_name)}
                        >
                        <Download />
                        </Button>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
}

export default DocumentList;