import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = "http://localhost:8000";

export default function AuthForm({ onAuthSuccess }) {
  const [mode, setMode] = useState("login"); // "login" or "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      if (mode === "register") {
        await axios.post(`${API_BASE}/api/register/`, { email, password, name });
        setMode("login");
        setError("Registered! Now login.");
      } else {
        const res = await axios.post(`${API_BASE}/api/token/`, { email, password });
        localStorage.setItem('access', res.data.access);
        localStorage.setItem('refresh', res.data.refresh);
        onAuthSuccess();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Auth failed.");
    }
  };

  return (
    <div>
      <h2>{mode === "login" ? "Login" : "Register"}</h2>
      <form onSubmit={handleSubmit}>
        <input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="Email" required />
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Password" required />
        {mode === "register" && (
          <input value={name} onChange={e => setName(e.target.value)} type="text" placeholder="Name (optional)" />
        )}
        <button type="submit">{mode === "login" ? "Login" : "Register"}</button>
      </form>
      <div>
        {mode === "login"
          ? <span>Don't have an account? <button onClick={() => setMode("register")}>Register</button></span>
          : <span>Already have an account? <button onClick={() => setMode("login")}>Login</button></span>
        }
      </div>
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
}
