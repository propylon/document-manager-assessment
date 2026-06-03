import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  CircularProgress,
  Snackbar,
  Alert,
  Tooltip,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import type { GridColDef } from "@mui/x-data-grid";
import {
  CloudUpload,
  Visibility,
  GetApp,
  UploadFile,
  Star,
  StarBorder,
  ContentCopy,
  Check,
  Delete,
} from "@mui/icons-material";
import {
  getFiles,
  uploadFile,
  uploadNewVersion,
  downloadLatest,
  getVersions,
  deleteDocument,
  deleteFileVersion,
} from "../api/files";
import type { FileVersionData } from "../types";

export const MyFilesPage: React.FC = () => {
  // Grid Data & Loading states
  const [rows, setRows] = useState<FileVersionData[]>([]);
  const [rowCount, setRowCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  // Pagination state (MUI DataGrid page is 0-indexed)
  const [paginationModel, setPaginationModel] = useState({
    page: 0,
    pageSize: 5,
  });

  // Favorites state (persists in localStorage by document_path)
  const [favorites, setFavorites] = useState<string[]>(() => {
    const saved = localStorage.getItem("favorites");
    return saved ? JSON.parse(saved) : [];
  });

  // Upload Document Dialog states
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadFileSelected, setUploadFileSelected] = useState<File | null>(null);
  const [uploadUrlPath, setUploadUrlPath] = useState("");
  const [uploading, setUploading] = useState(false);

  // View Versions Dialog states
  const [versionsDialogOpen, setVersionsDialogOpen] = useState(false);
  const [selectedRow, setSelectedRow] = useState<FileVersionData | null>(null);
  const [versionsList, setVersionsList] = useState<FileVersionData[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);
  const [copiedVersionId, setCopiedVersionId] = useState<number | null>(null);

  // Upload New Version Dialog states
  const [newVersionDialogOpen, setNewVersionDialogOpen] = useState(false);
  const [newVersionFile, setNewVersionFile] = useState<File | null>(null);
  const [uploadingNewVersion, setUploadingNewVersion] = useState(false);

  // Toast / Feedback Snackbar states
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState<"success" | "error" | "info">("success");

  // Show status feedback helper
  const showSnackbar = (message: string, severity: "success" | "error" | "info") => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  // Toggle favorite helper
  const handleToggleFavorite = (row: FileVersionData) => {
    const isFav = favorites.includes(row.document_path);
    const updated = isFav
      ? favorites.filter((path) => path !== row.document_path)
      : [...favorites, row.document_path];

    setFavorites(updated);
    localStorage.setItem("favorites", JSON.stringify(updated));
    showSnackbar(
      isFav ? "Removed from favorites." : "Added to favorites.",
      "success"
    );
  };

  // Fetch documents from backend API
  const fetchFiles = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === 1) {
        // Favorites tab: fetch all files (no pagination) and filter
        const data = await getFiles(1, 100, true);
        const allFiles = Array.isArray(data) ? data : data.results || [];
        const favoritedFiles = allFiles.filter((file: FileVersionData) =>
          favorites.includes(file.document_path)
        );
        setRows(favoritedFiles);
        setRowCount(favoritedFiles.length);
      } else {
        // All Documents tab: server-side paginated
        const page = paginationModel.page + 1; // DRF is 1-indexed
        const data = await getFiles(page, paginationModel.pageSize, false);
        setRows(data.results || []);
        setRowCount(data.count || 0);
      }
    } catch (err) {
      console.error(err);
      showSnackbar("Failed to fetch documents from server.", "error");
    } finally {
      setLoading(false);
    }
  }, [activeTab, paginationModel.page, paginationModel.pageSize, favorites]);

  // Load files when page, tab, or favorites changes
  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setPaginationModel((prev) => ({ ...prev, page: 0 }));
  };

  // File Download handler
  const handleDownload = async (id: number, filename: string) => {
    try {
      const blob = await downloadLatest(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
      showSnackbar(`Downloading ${filename}...`, "success");
    } catch (err) {
      console.error(err);
      showSnackbar("Failed to download file.", "error");
    }
  };

  // View Versions handler
  const handleOpenVersions = async (row: FileVersionData) => {
    setSelectedRow(row);
    setVersionsDialogOpen(true);
    setLoadingVersions(true);
    try {
      const versions = await getVersions(row.document);
      setVersionsList(versions);
    } catch (err) {
      console.error(err);
      showSnackbar("Failed to load versions.", "error");
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleDeleteDocument = async (row: FileVersionData) => {
    if (!window.confirm(`Are you sure you want to delete the document "${row.file_name}" and all its versions?`)) return;
    try {
      await deleteDocument(row.document_path);
      showSnackbar("Document deleted successfully.", "success");
      fetchFiles();
    } catch (err) {
      console.error(err);
      showSnackbar("Failed to delete document.", "error");
    }
  };

  const handleDeleteVersion = async (version: FileVersionData) => {
    if (!window.confirm(`Are you sure you want to delete version v${version.version_number}?`)) return;
    try {
      await deleteFileVersion(version.id);
      showSnackbar("Version deleted successfully.", "success");
      if (selectedRow) {
        const versions = await getVersions(selectedRow.document);
        setVersionsList(versions);
        fetchFiles();
      }
    } catch (err) {
      console.error(err);
      showSnackbar("Failed to delete version.", "error");
    }
  };

  // Copy shareable link helper
  const handleCopyLink = (version: FileVersionData) => {
    const cleanPath = version.document_path.startsWith("/")
      ? version.document_path
      : `/${version.document_path}`;
    const link = `http://localhost:8001/documents${cleanPath}?revision=${version.version_number}`;
    navigator.clipboard.writeText(link);
    setCopiedVersionId(version.id);
    showSnackbar("Shareable link copied to clipboard!", "info");
    setTimeout(() => setCopiedVersionId(null), 2000);
  };

  // Upload Document helpers
  const handleUploadFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadFileSelected(file);
      if (!uploadUrlPath) {
        setUploadUrlPath(`/${file.name.replace(/\s+/g, '-')}`);
      }
    }
  };

  const handleUploadSubmit = async () => {
    if (!uploadFileSelected || !uploadUrlPath) return;
    setUploading(true);
    try {
      await uploadFile(uploadFileSelected, uploadUrlPath);
      setUploadDialogOpen(false);
      setUploadFileSelected(null);
      setUploadUrlPath("");
      showSnackbar("Document uploaded successfully!", "success");
      fetchFiles();
    } catch (err) {
      console.error(err);
      showSnackbar("Failed to upload document.", "error");
    } finally {
      setUploading(false);
    }
  };

  // Upload New Version helpers
  const handleOpenUploadNewVersion = (row: FileVersionData) => {
    setSelectedRow(row);
    setNewVersionDialogOpen(true);
  };

  const handleUploadNewVersionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setNewVersionFile(e.target.files[0]);
    }
  };

  const handleUploadNewVersionSubmit = async () => {
    if (!selectedRow || !newVersionFile) return;
    setUploadingNewVersion(true);
    try {
      await uploadNewVersion(selectedRow.document_path, newVersionFile);
      setNewVersionDialogOpen(false);
      setNewVersionFile(null);
      showSnackbar("Uploaded new document version!", "success");
      fetchFiles();
    } catch (err) {
      console.error(err);
      showSnackbar("Failed to upload new version.", "error");
    } finally {
      setUploadingNewVersion(false);
    }
  };

  // Grid columns configuration
  const columns = useMemo<GridColDef[]>(
    () => [
      {
        field: "file_name",
        headerName: "File Name",
        flex: 1,
        minWidth: 180,
      },
      {
        field: "document_path",
        headerName: "URL Path",
        flex: 1.5,
        minWidth: 220,
      },
      {
        field: "version_number",
        headerName: "Version",
        width: 100,
        align: "center",
        headerAlign: "center",
        valueGetter: (value: any) => `v${value}`,
      },
      {
        field: "created_at",
        headerName: "Created",
        width: 180,
        valueFormatter: (value: any) => {
          if (!value) return "";
          return new Date(value).toLocaleDateString("en-IE", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          });
        },
      },
      {
        field: "actions",
        headerName: "Actions",
        width: 220,
        sortable: false,
        filterable: false,
        renderCell: (params: any) => {
          const row = params.row as FileVersionData;
          return (
            <Box sx={{ display: "flex", gap: 1, alignItems: "center", height: "100%" }}>
              <Button
                size="small"
                variant="outlined"
                onClick={() => handleOpenVersions(row)}
                startIcon={<Visibility />}
                sx={{
                  fontSize: "0.75rem",
                  textTransform: "none",
                  py: 0.5,
                  borderColor: "rgba(255, 255, 255, 0.15)",
                  color: "#9ca3af",
                  "&:hover": {
                    borderColor: "#6366f1",
                    color: "#a5b4fc",
                    background: "rgba(99, 102, 241, 0.05)",
                  },
                }}
              >
                Versions
              </Button>
              <Tooltip title="Download">
                <IconButton
                  size="small"
                  onClick={() => handleDownload(row.id, row.file_name)}
                  sx={{
                    color: "#9ca3af",
                    background: "rgba(255, 255, 255, 0.05)",
                    "&:hover": {
                      color: "#34d399",
                      background: "rgba(16, 185, 129, 0.15)",
                    },
                  }}
                >
                  <GetApp fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Update">
                <IconButton
                  size="small"
                  onClick={() => handleOpenUploadNewVersion(row)}
                  sx={{
                    color: "#9ca3af",
                    background: "rgba(255, 255, 255, 0.05)",
                    "&:hover": {
                      color: "#93c5fd",
                      background: "rgba(59, 130, 246, 0.15)",
                    },
                  }}
                >
                  <UploadFile fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete">
                <IconButton
                  size="small"
                  onClick={() => handleDeleteDocument(row)}
                  sx={{
                    color: "#9ca3af",
                    background: "rgba(255, 255, 255, 0.05)",
                    "&:hover": {
                      color: "#fb7185",
                      background: "rgba(244, 63, 94, 0.15)",
                    },
                  }}
                >
                  <Delete fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          );
        },
      },
      {
        field: "favorite",
        headerName: "Fav",
        width: 80,
        sortable: false,
        filterable: false,
        align: "center",
        headerAlign: "center",
        renderCell: (params: any) => {
          const row = params.row as FileVersionData;
          const isFav = favorites.includes(row.document_path);
          return (
            <IconButton
              onClick={() => handleToggleFavorite(row)}
              sx={{
                color: isFav ? "#fbbf24" : "rgba(255, 255, 255, 0.2)",
                transition: "color 0.15s",
                "&:hover": {
                  color: isFav ? "#f59e0b" : "rgba(255, 255, 255, 0.6)",
                },
              }}
            >
              {isFav ? <Star /> : <StarBorder />}
            </IconButton>
          );
        },
      },
    ],
    [favorites]
  );

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "radial-gradient(ellipse at top left, #1e1b4b 0%, #0b0f19 50%)",
        px: { xs: 2, sm: 4, md: 6 },
        py: 4,
      }}
    >
      <Box sx={{ maxWidth: 1400, mx: "auto" }}>
        {/* Header toolbar */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 4,
          }}
        >
          <Typography
            variant="h4"
            component="h1"
            sx={{
              fontWeight: 800,
              background: "linear-gradient(90deg, #ffffff 0%, #a5b4fc 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            My Files
          </Typography>

          <Button
            variant="contained"
            onClick={() => setUploadDialogOpen(true)}
            startIcon={<CloudUpload />}
            sx={{
              background: "linear-gradient(135deg, #6366f1 0%, #ec4899 100%)",
              color: "#ffffff",
              fontWeight: 600,
              textTransform: "none",
              px: 3,
              py: 1,
              borderRadius: "8px",
              boxShadow: "0 4px 14px rgba(99, 102, 241, 0.4)",
              "&:hover": {
                background: "linear-gradient(135deg, #4f46e5 0%, #db2777 100%)",
                boxShadow: "0 6px 20px rgba(99, 102, 241, 0.6)",
              },
            }}
          >
            Upload Document
          </Button>
        </Box>

        {/* Tab Selection */}
        <Box sx={{ borderBottom: 1, borderColor: "rgba(255, 255, 255, 0.08)", mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            textColor="inherit"
            sx={{
              "& .MuiTabs-indicator": {
                background: "linear-gradient(90deg, #6366f1 0%, #ec4899 100%)",
                height: "3px",
              },
              "& .MuiTab-root": {
                textTransform: "none",
                fontWeight: 600,
                color: "#9ca3af",
                minWidth: 120,
                "&.Mui-selected": {
                  color: "#ffffff",
                },
              },
            }}
          >
            <Tab label="All Documents" />
            <Tab label={`Favorites (${favorites.length})`} />
          </Tabs>
        </Box>

        {/* Grid panel */}
        <Box
          sx={{
            borderRadius: 3,
            overflow: "hidden",
            border: "1px solid rgba(255, 255, 255, 0.06)",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)",
            "& .MuiDataGrid-root": {
              border: "none",
              fontFamily: '"Inter", "Roboto", sans-serif',
            },
            "& .MuiDataGrid-columnHeaders": {
              background: "rgba(255, 255, 255, 0.02)",
              borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
            },
            "& .MuiDataGrid-columnHeaderTitle": {
              fontWeight: 700,
              fontSize: "0.8rem",
              letterSpacing: "0.03em",
              textTransform: "uppercase",
              color: "#9ca3af",
            },
            "& .MuiDataGrid-cell": {
              borderBottom: "1px solid rgba(255, 255, 255, 0.04)",
              color: "#e5e7eb",
              fontSize: "0.875rem",
            },
            "& .MuiDataGrid-row": {
              background: "rgba(17, 24, 39, 0.4)",
            },
            "& .MuiDataGrid-row:hover": {
              background: "rgba(99, 102, 241, 0.04)",
            },
            "& .MuiDataGrid-footerContainer": {
              borderTop: "1px solid rgba(255, 255, 255, 0.06)",
              background: "rgba(255, 255, 255, 0.02)",
            },
            "& .MuiTablePagination-root": {
              color: "#9ca3af",
            },
          }}
        >
          <DataGrid
            rows={rows}
            columns={columns}
            loading={loading}
            paginationMode={activeTab === 1 ? "client" : "server"}
            rowCount={rowCount}
            paginationModel={paginationModel}
            onPaginationModelChange={setPaginationModel}
            pageSizeOptions={[5, 10, 25]}
            disableRowSelectionOnClick
            autoHeight
            sx={{
              bgcolor: "rgba(17, 24, 39, 0.7)",
              backdropFilter: "blur(8px)",
            }}
          />
        </Box>
      </Box>

      {/* 1. Upload Document Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => !uploading && setUploadDialogOpen(false)}
        sx={{
          "& .MuiDialog-paper": {
            background: "rgba(17, 24, 39, 0.95)",
            backdropFilter: "blur(16px)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: 2,
            color: "#f3f4f6",
            width: "100%",
            maxWidth: 500,
          },
        }}
      >
        <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>Upload Document</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 1 }}>
            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUpload />}
              sx={{
                py: 2,
                borderStyle: "dashed",
                borderColor: "rgba(255, 255, 255, 0.2)",
                color: "#cbd5e1",
                textTransform: "none",
                "&:hover": {
                  borderColor: "#6366f1",
                  background: "rgba(99, 102, 241, 0.05)",
                },
              }}
            >
              {uploadFileSelected ? uploadFileSelected.name : "Select File"}
              <input type="file" hidden onChange={handleUploadFileChange} />
            </Button>

            <TextField
              label="Logical URL Path"
              value={uploadUrlPath}
              onChange={(e) => setUploadUrlPath(e.target.value.replace(/\s+/g, '-'))}
              placeholder="e.g. /oireachtas/bill/2024/commons/001"
              fullWidth
              variant="outlined"
              slotProps={{
                inputLabel: { shrink: true },
              }}
              sx={{
                "& .MuiOutlinedInput-root": {
                  color: "#ffffff",
                  "& fieldset": { borderColor: "rgba(255, 255, 255, 0.15)" },
                  "&:hover fieldset": { borderColor: "rgba(255, 255, 255, 0.3)" },
                  "&.Mui-focused fieldset": { borderColor: "#6366f1" },
                },
                "& .MuiInputLabel-root": {
                  color: "#9ca3af",
                  "&.Mui-focused": { color: "#818cf8" },
                },
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button
            onClick={() => setUploadDialogOpen(false)}
            disabled={uploading}
            sx={{ color: "#9ca3af", textTransform: "none" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUploadSubmit}
            disabled={uploading || !uploadFileSelected || !uploadUrlPath}
            variant="contained"
            sx={{
              background: "linear-gradient(135deg, #6366f1 0%, #ec4899 100%)",
              color: "#ffffff",
              textTransform: "none",
              px: 3,
              fontWeight: 600,
              "&:hover": {
                background: "linear-gradient(135deg, #4f46e5 0%, #db2777 100%)",
              },
            }}
          >
            {uploading ? <CircularProgress size={20} color="inherit" /> : "Upload"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 2. View Versions Dialog */}
      <Dialog
        open={versionsDialogOpen}
        onClose={() => setVersionsDialogOpen(false)}
        maxWidth="md"
        fullWidth
        sx={{
          "& .MuiDialog-paper": {
            background: "rgba(17, 24, 39, 0.95)",
            backdropFilter: "blur(16px)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: 2,
            color: "#f3f4f6",
          },
        }}
      >
        <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>
          Document History: {selectedRow?.file_name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: "#9ca3af", mb: 2 }}>
            Logical Path: {selectedRow?.document_path}
          </Typography>
          {loadingVersions ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
              <CircularProgress color="primary" />
            </Box>
          ) : (
            <Box
              sx={{
                width: "100%",
                border: "1px solid rgba(255, 255, 255, 0.06)",
                borderRadius: 1,
                overflow: "hidden",
              }}
            >
              <table style={{ width: "100%", borderCollapse: "collapse", color: "#e5e7eb" }}>
                <thead>
                  <tr style={{ background: "rgba(255, 255, 255, 0.02)", textAlign: "left" }}>
                    <th style={{ padding: "12px", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>Version</th>
                    <th style={{ padding: "12px", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>Filename</th>
                    <th style={{ padding: "12px", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>Uploaded On</th>
                    <th style={{ padding: "12px", borderBottom: "1px solid rgba(255, 255, 255, 0.06)", textAlign: "center" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {versionsList.map((version) => (
                    <tr
                      key={version.id}
                      style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.04)" }}
                    >
                      <td style={{ padding: "12px", fontWeight: 600 }}>v{version.version_number}</td>
                      <td style={{ padding: "12px" }}>{version.file_name}</td>
                      <td style={{ padding: "12px" }}>{new Date(version.created_at).toLocaleString("en-IE")}</td>
                      <td style={{ padding: "12px", display: "flex", gap: 8, justifyContent: "center" }}>
                        <Tooltip title="Copy Shareable Link">
                          <IconButton
                            size="small"
                            onClick={() => handleCopyLink(version)}
                            sx={{
                              color: copiedVersionId === version.id ? "#34d399" : "#a5b4fc",
                              background: "rgba(99, 102, 241, 0.08)",
                              "&:hover": { background: "rgba(99, 102, 241, 0.15)" },
                            }}
                          >
                            {copiedVersionId === version.id ? <Check fontSize="small" /> : <ContentCopy fontSize="small" />}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download version">
                          <IconButton
                            size="small"
                            onClick={() => handleDownload(version.id, version.file_name)}
                            sx={{
                              color: "#34d399",
                              background: "rgba(16, 185, 129, 0.08)",
                              "&:hover": { background: "rgba(16, 185, 129, 0.15)" },
                            }}
                          >
                            <GetApp fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete version">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteVersion(version)}
                            sx={{
                              color: "#fb7185",
                              background: "rgba(244, 63, 94, 0.08)",
                              "&:hover": { background: "rgba(244, 63, 94, 0.15)" },
                            }}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </td>
                    </tr>
                  ))}
                  {versionsList.length === 0 && (
                    <tr>
                      <td colSpan={4} style={{ padding: "20px", textAlign: "center", color: "#9ca3af" }}>
                        No versions found for this document.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setVersionsDialogOpen(false)} sx={{ color: "#9ca3af", textTransform: "none" }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* 3. Upload New Version Dialog */}
      <Dialog
        open={newVersionDialogOpen}
        onClose={() => !uploadingNewVersion && setNewVersionDialogOpen(false)}
        sx={{
          "& .MuiDialog-paper": {
            background: "rgba(17, 24, 39, 0.95)",
            backdropFilter: "blur(16px)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: 2,
            color: "#f3f4f6",
            width: "100%",
            maxWidth: 500,
          },
        }}
      >
        <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>Upload New Version</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            <Typography variant="body2" sx={{ color: "#9ca3af" }}>
              Uploading a new revision for: <strong style={{ color: "#f3f4f6" }}>{selectedRow?.document_path}</strong>
            </Typography>
            <Typography variant="caption" sx={{ color: "#cbd5e1" }}>
              This will automatically become the next available version (v{selectedRow ? selectedRow.version_number + 1 : "?"}).
            </Typography>

            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUpload />}
              sx={{
                py: 2,
                mt: 1,
                borderStyle: "dashed",
                borderColor: "rgba(255, 255, 255, 0.2)",
                color: "#cbd5e1",
                textTransform: "none",
                "&:hover": {
                  borderColor: "#6366f1",
                  background: "rgba(99, 102, 241, 0.05)",
                },
              }}
            >
              {newVersionFile ? newVersionFile.name : "Select File"}
              <input type="file" hidden onChange={handleUploadNewVersionChange} />
            </Button>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button
            onClick={() => setNewVersionDialogOpen(false)}
            disabled={uploadingNewVersion}
            sx={{ color: "#9ca3af", textTransform: "none" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUploadNewVersionSubmit}
            disabled={uploadingNewVersion || !newVersionFile}
            variant="contained"
            sx={{
              background: "linear-gradient(135deg, #6366f1 0%, #ec4899 100%)",
              color: "#ffffff",
              textTransform: "none",
              px: 3,
              fontWeight: 600,
              "&:hover": {
                background: "linear-gradient(135deg, #4f46e5 0%, #db2777 100%)",
              },
            }}
          >
            {uploadingNewVersion ? <CircularProgress size={20} color="inherit" /> : "Upload Version"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Toast feedback alerts */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbarSeverity}
          sx={{
            width: "100%",
            bgcolor:
              snackbarSeverity === "success"
                ? "#065f46"
                : snackbarSeverity === "error"
                  ? "#991b1b"
                  : "#1e3a8a",
            color: "#ffffff",
            "& .MuiAlert-icon": { color: "#ffffff" },
          }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};
