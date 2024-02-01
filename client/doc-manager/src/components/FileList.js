import React, { useEffect, useState } from 'react';

const FileList = () => {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    // Replace this with the code to send a GET request to the FileView endpoint
    const fetchFiles = async () => {
      const response = await fetch('/api/files'); // replace with your actual API endpoint
      const data = await response.json();
      setFiles(data);
    };

    fetchFiles();
  }, []);

  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            File Name
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Actions
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {files.map((file) => (
          <tr key={file.id}>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {file.name}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <button className="text-indigo-600 hover:text-indigo-900 mr-2">Read</button>
              <button className="text-green-600 hover:text-green-900 mr-2">Upload New Revision</button>
              <button className="text-red-600 hover:text-red-900">Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default FileList;