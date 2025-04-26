import React from "react";
import {Route, Routes, Navigate } from "react-router-dom";
import Login from "./component/Login";
import FileVersions from "./component/FileVersions";
import UploadFile from "./component/UploadFile";
import DocumentList from "./component/Documents";

const AppRoutes = ({ isLoggedIn, handleLogin }) => {
  return (
    <Routes>
      <Route
        path="/"
        element={
          isLoggedIn ? <FileVersions /> : <Navigate to="/login" replace />
        }
      />
      <Route
        path="/upload-file"
        element={
          isLoggedIn ? <UploadFile /> : <Navigate to="/login" replace />
        }
      />
      <Route 
        path="/document-list" 
        element={
          isLoggedIn ? <DocumentList /> : <Navigate to="/login" replace />
        }
      />
      <Route
        path="/file-versions"
        element={
          isLoggedIn ? <FileVersions /> : <Navigate to="/login" replace />
        }
      />
      <Route path="/login" element={<Login onLogin={handleLogin} />} />
    </Routes>
  );
};

export default AppRoutes;