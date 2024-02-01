import React, { useState } from 'react';import './App.css';
import {
  BrowserRouter as Router,
  Route,
  Routes,
} from "react-router-dom";
import FileList from './components/FileList';
import FileUpload from './components/FileUpload';
import Login from './components/Login';
import Dashboard from './components/Dashboard';


function App() {
  const [currentUser, setCurrentUser] = useState();
  // );
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login currentUser={currentUser} setCurrentUser={(user) => setCurrentUser(user)}/>} />
        <Route
          path="/dashboard"
          element={<Dashboard currentUser={currentUser}/>}
        />
        <Route
          path="/upload"
          element={<FileUpload currentUser={currentUser}/>}
        />
        <Route
          path="/list"
          element={<FileList currentUser={currentUser}/>}
        />
      </Routes>
    </Router>
  );
}

export default App;
