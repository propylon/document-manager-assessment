import React, { useEffect, useState } from 'react';

const FileVersionList = ({ fileId }) => {
  const [versions, setVersions] = useState([]);

  useEffect(() => {
    // Replace this with the code to send a GET request to the FileVersionView endpoint
    const fetchVersions = async () => {
      const response = await fetch(`/api/files/${fileId}/versions`); // replace with your actual API endpoint
      const data = await response.json();
      setVersions(data);
    };

    fetchVersions();
  }, [fileId]);

  return (
    <ul className="border p-2">
      {versions.map((version) => (
        <li key={version.id} className="mb-2">
          Version {version.version} - {new Date(version.timestamp).toLocaleString()}
          {/* Replace this with the FileVersionDelete component */}
          <button className="ml-2 py-1 px-2 bg-red-500 text-white">Delete</button>
        </li>
      ))}
    </ul>
  );
};

export default FileVersionList;