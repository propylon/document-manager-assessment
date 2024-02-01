import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { LOGIN_API_ENDPOINT } from '../constants';


function Login({currentUser, setCurrentUser}) {
  // Define state variables for username and password
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Use the useNavigate hook from react-router-dom to programmatically navigate after successful login
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
        // Send a POST request to the login API
      const response = await fetch(LOGIN_API_ENDPOINT, {
        method: "POST",
        mode: "cors",
        referrerPolicy: "same-origin",
        // credentials: "same-origin",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      console.log(response);
      console.log(response.headers.get('Set-Cookie'))
      if (response.ok) {
        // If the response is OK, parse the JSON from the response
        const data = await response.json();
        console.log(data);
        // Navigate to the home page
        navigate("/dashboard");
      } else {
        throw new Error("Login failed");
      }
    } catch (error) {
      // Handle login error
      console.error("Login failed:", error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <input type="hidden" name="remember" value="true" />
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;