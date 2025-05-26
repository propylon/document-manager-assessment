import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./FileVersions.css";

function FileVersionsList({ file_versions }) {
  return file_versions.length === 0 ? (
    <p>No file versions match your search.</p>
  ) : (
    file_versions.map((file_version) => {
      const isEven = file_version.version_number % 2 === 0;
      const colorStyle = {
        border: "2px solid",
        borderColor: isEven ? "green" : "red",
        background: isEven ? "#e5ffe5" : "#ffe5e5",
        padding: "1em",
        marginBottom: "1em",
      };
      return (
        <div className="file-version" key={file_version.id} style={colorStyle}>
          <h2>
            File Name: {file_version.file_name} &nbsp;
            <span style={{ color: isEven ? "green" : "red" }}>
              v{file_version.version_number}
            </span>
          </h2>
          {file_version.file_url && (
            <a
              href={file_version.file_url}
              target="_blank"
              rel="noopener noreferrer"
              download
              style={{
                display: "inline-block",
                margin: "0.5em 0",
                fontWeight: "bold",
              }}
            >
              Download/View
            </a>
          )}
          <div>ID: {file_version.id}</div>
        </div>
      );
    })
  );
}

function FileVersions() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [customPath, setCustomPath] = useState("");
  const [uploadStatus, setUploadStatus] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const debounceTimeout = useRef(null);

  // Fetch data (file versions) with optional search
  const fetchData = async (search = "") => {
  try {
    const access = localStorage.getItem("access");
    if (!access) {
      setError("Not authenticated. Please log in.");
      return;
    }
    let url = "http://localhost:8000/api/file_versions/";
    if (search) {
      if (/^\d+$/.test(search.trim())) {
        // All digits = version search
        url += `?version=${encodeURIComponent(search.trim())}`;
      } else {
        // Not all digits = file name search
        url += `?filename=${encodeURIComponent(search.trim())}`;
      }
    }
    const response = await axios.get(url, {
      headers: {
        Authorization: `Bearer ${access}`,
      },
    });
    setData(response.data);
    setError(null);
  } catch (err) {
    setError(
      err.response?.data?.detail ||
        "Error fetching file versions. You may need to log in again."
    );
  }
};
  useEffect(() => {
    fetchData();
  }, []);

  // Debounced search effect
  useEffect(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }
    debounceTimeout.current = setTimeout(() => {
      fetchData(searchTerm);
    }, 400);
    return () => clearTimeout(debounceTimeout.current);
    // eslint-disable-next-line
  }, [searchTerm]);

  // Upload handler
  const handleUpload = async (e) => {
    e.preventDefault();
    setUploadStatus(null);
    setError(null);
    const access = localStorage.getItem("access");
    if (!access) {
      setError("Not authenticated. Please log in.");
      return;
    }
    if (!file) {
      setError("No file selected.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("file_name", file.name);
    formData.append("custom_path", customPath);

    try {
      await axios.post(
        "http://localhost:8000/api/file_versions/",
        formData,
        {
          headers: {
            Authorization: `Bearer ${access}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setUploadStatus("File uploaded successfully!");
      setFile(null);
      setCustomPath("");
      fetchData(searchTerm); // Refresh list (with current search)
    } catch (err) {
      setUploadStatus(null);
      setError(err.response?.data?.detail || "Upload failed.");
    }
  };

  return (
    <div>
      <h1>Found {data.length} File Versions</h1>
      {error && <div style={{ color: "red" }}>{error}</div>}

      {/* --- Upload Form --- */}
      <form
        onSubmit={handleUpload}
        style={{
          marginBottom: "2em",
          border: "1px solid #ccc",
          padding: "1em",
        }}
      >
        <h3>Upload New File Version</h3>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <input
          type="text"
          placeholder="Custom Path (e.g. reports/2024/myfile.pdf)"
          value={customPath}
          onChange={(e) => setCustomPath(e.target.value)}
          style={{ marginLeft: 10 }}
        />
        <button type="submit" style={{ marginLeft: 10 }}>
          Upload
        </button>
        {uploadStatus && (
          <div style={{ color: "green", marginTop: 10 }}>{uploadStatus}</div>
        )}
      </form>

      {/* --- Search bar --- */}
      <input
        type="text"
        placeholder="Search by file name or version..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{ width: "60%", padding: "0.5em", marginBottom: "2em" }}
      />

      <div>
        <FileVersionsList file_versions={data} />
      </div>
    </div>
  );
}

export default FileVersions;
