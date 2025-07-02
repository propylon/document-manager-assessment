import React, { useState, useEffect } from "react";
import "./FileVersions.css";

// 👇 Replace with your real token for testing
const AUTH_TOKEN = localStorage.getItem("token");

function FileVersionsList({ file_versions, loginToken }) {
  if (!Array.isArray(file_versions)) {
    return <p>No file versions found.</p>;
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th style={{ border: "1px solid #ccc" }}>File Name</th>
          <th style={{ border: "1px solid #ccc" }}>URL Path</th>
          <th style={{ border: "1px solid #ccc" }}>Version</th>
          <th style={{ border: "1px solid #ccc" }}>Uploaded At</th>
          <th style={{ border: "1px solid #ccc" }}>Hash</th>
          <th style={{ border: "1px solid #ccc" }}>Download</th>
        </tr>
      </thead>
      <tbody>
        {file_versions.map((file_version) => (
          <tr key={file_version.id}>
            <td style={{ border: "1px solid #ccc", padding: "5px" }}>{file_version.file_name}</td>
            <td style={{ border: "1px solid #ccc", padding: "5px" }}>{file_version.url_path}</td>
            <td style={{ border: "1px solid #ccc", padding: "5px" }}>{file_version.version_number}</td>
            <td style={{ border: "1px solid #ccc", padding: "5px" }}>{new Date(file_version.uploaded_at).toLocaleString()}</td>
            <td style={{ border: "1px solid #ccc", padding: "5px" }}>
              <code style={{ fontSize: "10px" }}>
                {file_version.content_hash ? `${file_version.content_hash.slice(0, 12)}...` : "N/A"}
              </code>
            </td>
            <td style={{ border: "1px solid #ccc", padding: "5px" }}>
              <a href={`http://localhost:8000${file_version.file}`} target="_blank" rel="noreferrer">Download</a>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function FileVersions() {
  const [data, setData] = useState([]);
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [urlPath, setUrlPath] = useState("");
  const [downloadPath, setDownloadPath] = useState("");
  const [revision, setRevision] = useState("");
  const [selectedPath, setSelectedPath] = useState("");
  const [selectedRevision, setSelectedRevision] = useState("");


  useEffect(() => {
    fetch("http://localhost:8000/api/upload/", {
      headers: {
        Authorization: `Token ${AUTH_TOKEN}`,
      },
    })
      .then((res) => res.json())
      .then((data) => setData(data));
  }, []);

  const handleDownloadByPath = () => {
    if (!downloadPath) return alert("Please enter a virtual path!");

    const path = downloadPath.replace(/^\/+|\/+$/g, ""); // trim slashes
    const versionParam = revision ? `?revision=${revision}` : "";
    const downloadURL = `http://localhost:8000/api/documents/${path}${versionParam}`;

    window.open(downloadURL, "_blank");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !fileName || !urlPath) {
      alert("Please fill all fields.");
      return;
    }

    const formData = new FormData();
    formData.append("file_name", fileName);
    formData.append("url_path", urlPath);
    formData.append("file", file);

    const response = await fetch("http://localhost:8000/api/upload/", {
      method: "POST",
      headers: {
        Authorization: `Token ${AUTH_TOKEN}`,
      },
      body: formData,
    });

    if (response.ok) {
      alert("Uploaded successfully!");
      const newFile = await response.json();
      setData([newFile, ...data]); // prepend to list
    } else {
      alert("Upload failed");
      console.error(await response.text());
    }
  };

  const handleDropdownDownload = () => {
    if (!selectedPath) {
      alert("Please select a file path.");
      return;
    }

    const matchingVersion = data.find(
      (item) =>
        item.url_path === selectedPath &&
        (selectedRevision === "" || item.version_number === parseInt(selectedRevision))
    );

    if (!matchingVersion) {
      alert("Selected file/version not found.");
      return;
    }

    const contentHash = matchingVersion.content_hash;

    if (!contentHash) {
      alert("No content hash found for this version.");
      return;
    }

    const casURL = `http://localhost:8000/api/cas/${contentHash}`;
    const token = localStorage.getItem("token");

    fetch(casURL, {
      method: "GET",
      headers: {
        Authorization: `Token ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("File not found or unauthorized");
        return Promise.all([res.blob(), res.headers.get("Content-Disposition")]);
      })
      .then(([blob, contentDisposition]) => {
        const match = contentDisposition?.match(/filename="(.+)"/);
        const filename = match ? match[1] : "download";

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        a.remove();
      })
      .catch((err) => {
        console.error("Download error:", err);
        alert("Download failed. Check console.");
      });
  };

  return (
    <div>
      <button
        onClick={() => {
          localStorage.removeItem("token");
          window.location.reload(); // force redirect to login page
        }}
        style={{ position: "absolute", top: 10, right: 10 }}
      >
        Logout
      </button>
      <h1>Upload a File</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: "30px" }}>
        <input
          type="text"
          placeholder="File Name (e.g., test.pdf)"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
        />
        <br /><br />
        <input
          type="text"
          placeholder="URL Path (e.g., /documents/reviews/test.pdf)"
          value={urlPath}
          onChange={(e) => setUrlPath(e.target.value)}
        />
        <br /><br />
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <br /><br />
        <button type="submit">Upload</button>
      </form>
      <h2>Download Existing File Version</h2>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleDropdownDownload();
        }}
        style={{ marginBottom: "30px" }}
      >
        <label>Select File Path:</label>
        <br />
        <select
          onChange={(e) => setSelectedPath(e.target.value)}
          value={selectedPath}
          style={{ width: "300px" }}
        >
          <option value="">-- Select a file path --</option>
          {[...new Set(data.map((item) => item.url_path))].map((path) => (
            <option key={path} value={path}>
              {path}
            </option>
          ))}
        </select>
        <br /><br />

        {selectedPath && (
          <>
            <label>Select Version:</label>
            <br />
            <select
              onChange={(e) => setSelectedRevision(e.target.value)}
              value={selectedRevision}
              style={{ width: "300px" }}
            >
              {/* Default to 'latest' */}
              <option value="">Latest Version</option>
              {data
                .filter((item) => item.url_path === selectedPath)
                .sort((a, b) => b.version_number - a.version_number)
                .map((item) => (
                  <option key={item.id} value={item.version_number}>
                    v{item.version_number}
                  </option>
                ))}
            </select>
            <br /><br />

            <button type="submit">Download Version</button>
          </>
        )}
      </form>

      <h2>Found {data.length} File Versions</h2>
      <FileVersionsList file_versions={data} />
    </div>
  );
}

export default FileVersions;