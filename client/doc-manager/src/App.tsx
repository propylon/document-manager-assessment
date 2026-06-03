import { Routes, Route, Navigate } from "react-router-dom";
import { LoginPage } from "./pages/LoginPage";
import { MyFilesPage } from "./pages/MyFilesPage";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/files" element={<MyFilesPage />} />
      <Route path="*" element={<Navigate to="/files" replace />} />
    </Routes>
  );
}

export default App;
