import React, { useState, useEffect } from "react";
import {
  Container,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  TextField,
  Alert,
  Tooltip,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { Download, Visibility, UploadFile } from "@mui/icons-material";
import config from "../config";
import { fetchWithRefresh } from "../utils/FetchWithRefresh";

function UploadAndDocumentList() {
  const [file, setFile] = useState(null);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const [documents, setDocuments] = useState([]);
  const navigate = useNavigate();

  // Handle file upload
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    // const token = localStorage.getItem("authToken");
    // if (!token) {
    //   setError("You must be logged in to upload a file.");
    //   return;
    // }

    const formData = new FormData();
    formData.append("content", file);

    try {
      const response = await fetchWithRefresh(`${config.serverUrl}/api/document`, {
        method: "POST",
        credentials: 'include',
        body: formData,
      });

      const responseData = await response.json();

      if (response.status === 200 && responseData.responseCode === 200) {
        setSuccess("File uploaded successfully!");
        setFile(null);
        setError("");
        fetchDocuments(); // Refresh the document list after upload
      } else {
        setSuccess("");
        setError(responseData.responseMessage);
      }
    } catch (err) {
      setError(err.message || "An error occurred. Please try again.");
      setSuccess("");
    }
  };

  // Fetch document list
  const fetchDocuments = async () => {
    // const token = localStorage.getItem("authToken");
    // if (!token) {
    //   setError("You must be logged in to view the document list.");
    //   return;
    // }

    try {
      const response = await fetchWithRefresh(`${config.serverUrl}/api/file`, {
        method: "GET",
        credentials: 'include'
      });

      if (!response.ok && response.responseCode !== 200) {
        throw new Error("Failed to fetch documents.");
      }

      const data = await response.json();
      setDocuments(data["data"]);
    } catch (err) {
      setError(err.message || "An error occurred. Please try again.");
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleViewVersions = (id) => {
    navigate(`/file-versions?id=${id}`);
  };

  const handleDownloadLatest = async (fileName) => {
    // const token = localStorage.getItem("authToken");
    // if (!token) {
    //   setError("You must be logged in to download files.");
    //   return;
    // }

    try {
      const response = await fetchWithRefresh(`${config.serverUrl}/api/document/${fileName}`, {
        method: "GET",
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error("Failed to download the file.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "An error occurred while downloading the file.");
    }
  };

  return (
    <Container maxWidth="md">
      {/* Upload Form */}
      <Box mt={4} mb={4}>
        <Typography variant="h6" sx={{ textAlign: "left", mb: 2 }}>
          Upload File
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}
        <form onSubmit={handleUpload}>
          <Box mb={3} display="flex" alignItems="center" justifyContent="space-between">
            <TextField
              type="file"
              fullWidth
              onChange={handleFileChange}
              InputLabelProps={{ shrink: true }}
              sx={{ flex: 1, mr: 2 }} // Add margin-right to create space between the input and button
            />
            <Tooltip title="Upload File" arrow>
              <Button 
                type="submit" 
                variant="contained" 
                color="primary"
                sx={{
                  borderRadius: "50%", // Make the button round
                  minWidth: "48px", // Set a minimum width for the button
                  minHeight: "48px", // Set a minimum height for the button
                  padding: "12px", // Add padding for better spacing
                }}
              >
                <UploadFile/>
              </Button>
            </Tooltip>
          </Box>
        </form>
      </Box>

      {/* Document List */}
      <Box>
        <Typography variant="h6" sx={{ textAlign: "left", mb: 2 }}>
          Found {documents.length} Document(s)
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>File Name</TableCell>
                <TableCell>Latest Version</TableCell>
                <TableCell>Total Versions</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((doc, index) => (
                <TableRow 
                  key={index}
                  sx={{
                    backgroundColor: index % 2 === 0 ? "white" : "grey.100", // Alternate row colors
                  }}
                >
                  <TableCell>
                    <Tooltip title="View Versions" arrow>
                      <a
                        href="#"
                        onClick={(e) => {
                          e.preventDefault(); // Prevent default link behavior
                          handleViewVersions(doc.id); // Trigger the download
                        }}
                        style={{textDecoration: "underline",color: "black", cursor: "pointer", fontWeight: "bold"}}
                      >
                      {doc.fileName}
                      </a>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{doc.latestVersionNumber}</TableCell>
                  <TableCell>{doc.fileVersionCount}</TableCell>
                  <TableCell>
                    <Tooltip title="Download Latest" arrow>
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={() => handleDownloadLatest(doc.fileName)}
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

export default UploadAndDocumentList;