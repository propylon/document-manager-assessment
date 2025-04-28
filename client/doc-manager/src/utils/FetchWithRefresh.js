import config from "../config";

export const fetchWithRefresh = async (url, options = {}) => {
  const response = await fetch(url, {
    ...options,
    credentials: "include", // Include cookies in the request
  });

  if (response.status === 401) {
    // Access token expired, try to refresh it
    const refreshResponse = await fetch(`${config.serverUrl}/api/refresh-token/`, {
      method: "POST",
      credentials: "include", // Include cookies in the request
    });

    if (refreshResponse.ok) {
      // Retry the original request after refreshing the token
      return fetch(url, {
        ...options,
        credentials: "include",
      });
    } else {
      // Refresh token is invalid or expired, redirect to login
      window.location.href = "/login";
      throw new Error("Session expired. Please log in again.");
    }
  }

  return response;
};