import { TextEncoder, TextDecoder } from 'util';

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import React from "react";

import App from './App';

describe('App Component', () => {
  test('renders the navigation bar with "Document Manager"', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    const navTitle = screen.getByText(/Document Manager/i);
    expect(navTitle).toBeInTheDocument();
  });

  test("renders login button when not logged in", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    const loginButton = screen.getByRole("button", { name: /login/i });
    expect(loginButton).toBeInTheDocument();
  });
});
