import React, { useState } from 'react';
import './App.css';
import FileVersions from './FileVersions';
import AuthForm from './AuthForm';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access'));

  const handleAuthSuccess = () => setIsLoggedIn(true);

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    setIsLoggedIn(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        {!isLoggedIn ? (
          <AuthForm onAuthSuccess={handleAuthSuccess} />
        ) : (
          <>
            <button style={{ position: 'absolute', right: 20, top: 20 }} onClick={handleLogout}>Logout</button>
            <FileVersions />
          </>
        )}
      </header>
    </div>
  );
}

export default App;
