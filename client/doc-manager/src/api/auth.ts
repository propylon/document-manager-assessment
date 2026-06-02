import client from "./client";
import type { User } from "../types";

export const login = async (email: string, password: string): Promise<User> => {
  // DRF obtain_auth_token expects 'username' even when email is used
  const response = await client.post<{ token: string }>("/auth-token/", {
    username: email,
    password: password,
  });
  return {
    email: email,
    token: response.data.token,
  };
};
