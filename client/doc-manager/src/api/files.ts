import client from "./client";
import type { FileVersionData } from "../types";

export interface PaginatedFilesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: FileVersionData[];
}

/**
 * Fetch files (latest versions of each document) with server-side pagination.
 */
export const getFiles = async (
  page: number,
  pageSize: number,
  noPagination = false
): Promise<any> => {
  const params: any = { latest: true };
  if (noPagination) {
    params.no_pagination = true;
  } else {
    params.page = page;
    params.page_size = pageSize;
  }
  const response = await client.get("/api/file_versions/", { params });
  return response.data;
};

/**
 * Upload a new file (creates a new Document with version 0).
 */
export const uploadFile = async (file: File, urlPath: string): Promise<FileVersionData> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("url_path", urlPath);

  const response = await client.post<FileVersionData>("/api/file_versions/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

/**
 * Upload a new version of an existing document (referenced by its logical urlPath).
 */
export const uploadNewVersion = async (urlPath: string, file: File): Promise<FileVersionData> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("url_path", urlPath);

  const response = await client.post<FileVersionData>("/api/file_versions/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

/**
 * Download the file associated with a specific FileVersion ID.
 * Returns a Blob that can be saved locally.
 */
export const downloadLatest = async (id: number): Promise<Blob> => {
  const response = await client.get(`/api/file_versions/${id}/download/`, {
    responseType: "blob",
  });
  return response.data;
};

/**
 * Get all versions for a specific document ID.
 */
export const getVersions = async (documentId: number): Promise<FileVersionData[]> => {
  const response = await client.get<FileVersionData[]>("/api/file_versions/", {
    params: {
      document: documentId,
    },
  });
  return response.data;
};
