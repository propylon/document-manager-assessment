export interface User {
  email: string;
  token: string;
  name?: string;
}

export interface DocumentData {
  id: number;
  url_path: string;
  created_at: string;
}

export interface FileVersionData {
  id: number;
  document: number;
  file_name: string;
  version_number: number;
  file: string;
  content_hash: string;
  created_at: string;
  document_path: string;
}
