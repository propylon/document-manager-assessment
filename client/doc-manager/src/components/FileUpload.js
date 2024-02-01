import React, { useState } from 'react';

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [url, setUrl] = useState('');
  const [fileName, setFileName] = useState('');

  const handleFileChange = (event) => setSelectedFile(event.target.files[0]);

  const handleURLChange = (event) => setUrl(event.target.value);

  const handleFileNameChange = (event) => setFileName(event.target.value);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      alert('Please select a file to upload');
      return;
    }

    // Create a FormData instance to hold the file
    const formData = new FormData();
    formData.append('file', selectedFile);

    // Replace this with the code to send a POST request to the FileView endpoint
    console.log('File to upload:', selectedFile);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col">
      <label htmlFor="fileUpload" className="mb-2">
        Select a file:
      </label>
      <input
        id="fileUpload"
        type="file"
        onChange={handleFileChange}
        className="mb-4"
      />
      <input
        type="text"
        id="fileName"
        placeholder="File Name"
        value={fileName}
        onChange={handleFileNameChange}
      />
      <input
        type="text"
        id="url"
        placeholder="URL"
        value={url}
        onChange={handleURLChange}
      />
      <button type="submit" className="py-2 px-4 bg-blue-500 text-white">
        Upload File
      </button>
    </form>
  );
};

export default FileUpload;