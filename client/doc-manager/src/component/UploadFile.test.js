import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import UploadAndDocumentList from "./UploadFile";
import { MemoryRouter } from "react-router";
import React from "react";

// Mock fetchWithRefresh
jest.mock("../utils/FetchWithRefresh", () => ({
  fetchWithRefresh: jest.fn(),
}));

describe("UploadAndDocumentList Component", () => {
  const mockDocuments = [
    { id: 1, fileName: "Document1.pdf", latestVersionNumber: 3, fileVersionCount: 5 },
    { id: 2, fileName: "Document2.docx", latestVersionNumber: 2, fileVersionCount: 3 },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders the upload form and document list", async () => {
    // Mock fetchWithRefresh for fetching documents
    require("../utils/FetchWithRefresh").fetchWithRefresh.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: mockDocuments }),
    });

    render(
      <MemoryRouter>
        <UploadAndDocumentList />
      </MemoryRouter>
    );

    // Check if the upload form is rendered
    const uploadForm = screen.getByText(/Upload File/i);
    expect(uploadForm).toBeInTheDocument();

    // Wait for the document list to load
    await waitFor(() => {
      const document1 = screen.getByText(/Document1.pdf/i);
      const document2 = screen.getByText(/Document2.docx/i);
      expect(document1).toBeInTheDocument();
      expect(document2).toBeInTheDocument();
    });
  });

  test("displays an error message when no file is selected for upload", () => {
    render(
      <MemoryRouter>
        <UploadAndDocumentList />
      </MemoryRouter>
    );

    // Click the upload button without selecting a file
    const uploadButton = screen.getByRole("button", { name: /upload file/i });
    fireEvent.click(uploadButton);

    // Check for the error message
    const errorMessage = screen.getByText(/Please select a file to upload./i);
    expect(errorMessage).toBeInTheDocument();
  });

  test("displays a message when no documents are available", async () => {
    // Mock fetchWithRefresh to return an empty document list
    require("../utils/FetchWithRefresh").fetchWithRefresh.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: [] }),
    });

    render(
      <MemoryRouter>
        <UploadAndDocumentList />
      </MemoryRouter>
    );

    // Wait for the document list to load
    await waitFor(() => {
      const noDocumentsMessage = screen.getByText(/Found 0 Document\(s\)/i);
      expect(noDocumentsMessage).toBeInTheDocument();
    });
  });
});