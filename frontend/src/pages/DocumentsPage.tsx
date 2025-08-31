import React, { useState, useEffect, useContext } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  InputAdornment,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  Fab,
  Menu,
  MenuItem,
  ListItemIcon,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  GetApp as DownloadIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { DocumentResponse, DocumentSearchRequest } from '../sdk';
import { ThemeContext } from '../App';
import { useSSE } from '../services/sse-context';
import CustomScrollbar from '../components/CustomScrollbar';
import {
  DocumentUploadedEvent,
  DocumentProcessingStartedEvent,
  DocumentProcessingCompletedEvent,
  DocumentProcessingFailedEvent
} from '../services/sse-types';

const DocumentsPage: React.FC = () => {
  // SSE hook
  const { on } = useSSE();

  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const { darkMode } = useContext(ThemeContext);

  // Actions menu
  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionDocument, setActionDocument] = useState<DocumentResponse | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  // SSE Event Listeners for real-time document updates
  useEffect(() => {
    // Attach listeners regardless of current connection; they will receive events when the stream is open
    const unsubscribeDocumentUploaded = on('document.uploaded', (event) => {
      const docEvent = event as DocumentUploadedEvent;
      console.log('Document uploaded:', docEvent.data);
      loadDocuments();
    });

    const unsubscribeProcessingStarted = on('document.processing_started', (event) => {
      const docEvent = event as DocumentProcessingStartedEvent;
      console.log('Document processing started:', docEvent.data);
      setDocuments(prev => prev.map(doc =>
        String(doc.id) === String(docEvent.data.document_id)
          ? { ...doc, status: 'processing' as any }
          : doc
      ));
    });

    const unsubscribeProcessingCompleted = on('document.processing_completed', (event) => {
      const docEvent = event as DocumentProcessingCompletedEvent;
      console.log('Document processing completed:', docEvent.data);
      setDocuments(prev => prev.map(doc =>
        String(doc.id) === String(docEvent.data.document_id)
          ? { 
              ...doc, 
              status: 'processed' as any,
              chunk_count: docEvent.data.result?.chunks_created ?? doc.chunk_count
            }
          : doc
      ));
      loadDocuments();
    });

    const unsubscribeProcessingFailed = on('document.processing_failed', (event) => {
      const docEvent = event as DocumentProcessingFailedEvent;
      console.log('Document processing failed:', docEvent.data);
      setDocuments(prev => prev.map(doc =>
        String(doc.id) === String(docEvent.data.document_id)
          ? { ...doc, status: 'failed' as any }
          : doc
      ));
      setError(`Document processing failed: ${docEvent.data.error}`);
    });

    return () => {
      unsubscribeDocumentUploaded();
      unsubscribeProcessingStarted();
      unsubscribeProcessingCompleted();
      unsubscribeProcessingFailed();
    };
  }, [on]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await chatterSDK.documents.listDocumentsApiV1DocumentsGet({});
      setDocuments(response.data.documents);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!uploadFile) return;

    try {
      setUploading(true);
      const response = await chatterSDK.documents.uploadDocumentApiV1DocumentsUploadPost({
        file: uploadFile,
        title: uploadTitle || undefined
      });
      setDocuments(prev => [response.data, ...prev]);
      setUploadDialogOpen(false);
      setUploadFile(null);
      setUploadTitle('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await chatterSDK.documents.deleteDocumentApiV1DocumentsDocumentIdDelete({ documentId: documentId });
      setDocuments(prev => prev.filter(d => d.id !== documentId));
    } catch (err: any) {
      setError('Failed to delete document');
    }
  };

  const handleViewDocument = async (documentId: string) => {
    try {
      const response = await chatterSDK.documents.getDocumentApiV1DocumentsDocumentIdGet({ documentId });
      const document = response.data;

      // Try to get document chunks for content preview
      let contentPreview = '';

      try {
        const chunksResponse = await chatterSDK.documents.getDocumentChunksApiV1DocumentsDocumentIdChunksGet({
          documentId,
          limit: 3,
          offset: 0
        });
        if (chunksResponse.data && chunksResponse.data.chunks && chunksResponse.data.chunks.length > 0) {
          contentPreview = chunksResponse.data.chunks
            .map(chunk => chunk.content)
            .join('\n\n')
            .substring(0, 1000);
          if (contentPreview.length >= 1000) {
            contentPreview += '...';
          }
        }
      } catch {
        contentPreview = `Document is processed into ${document.chunk_count || 0} chunks for vector search. Chunk content not available for preview.`;
      }

      // Create themed preview window
      const backgroundColor = darkMode ? '#121212' : '#ffffff';
      const textColor = darkMode ? '#ffffff' : '#000000';
      const borderColor = darkMode ? '#333333' : '#dddddd';

      const newWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
      if (newWindow) {
        newWindow.document.write(`
          <html>
            <head>
              <title>Document: ${document.title || document.filename}</title>
              <style>
                body {
                  font-family: 'Roboto', Arial, sans-serif;
                  padding: 20px;
                  background-color: ${backgroundColor};
                  color: ${textColor};
                  margin: 0;
                }
                .header {
                  border-bottom: 2px solid ${borderColor};
                  padding-bottom: 15px;
                  margin-bottom: 20px;
                }
                .metadata {
                  background-color: ${darkMode ? '#1e1e1e' : '#f5f5f5'};
                  padding: 15px;
                  border-radius: 8px;
                  margin: 15px 0;
                  border: 1px solid ${borderColor};
                }
                .content-preview {
                  background-color: ${darkMode ? '#2d2d2d' : '#fafafa'};
                  padding: 15px;
                  border-radius: 8px;
                  border: 1px solid ${borderColor};
                  font-family: 'Monaco', 'Consolas', monospace;
                  white-space: pre-wrap;
                  max-height: 400px;
                  overflow-y: auto;
                  line-height: 1.4;
                }
                .tag {
                  background-color: ${darkMode ? '#444444' : '#e0e0e0'};
                  color: ${textColor};
                  padding: 2px 8px;
                  border-radius: 12px;
                  font-size: 12px;
                  margin-right: 5px;
                }
              </style>
            </head>
            <body>
              <div class="header">
                <h1>${document.title || document.filename}</h1>
                <div>
                  <span class="tag">${document.mime_type}</span>
                  <span class="tag">${formatFileSize(document.file_size)}</span>
                  <span class="tag">${document.status}</span>
                </div>
              </div>

              <div class="metadata">
                <h3>Document Information</h3>
                <p><strong>Created:</strong> ${format(new Date(document.created_at), 'MMM dd, yyyy HH:mm')}</p>
                <p><strong>Processing Status:</strong> ${document.status}</p>
                <p><strong>Chunks:</strong> ${document.chunk_count || 0}</p>
                ${document.extra_metadata ? `<p><strong>Metadata:</strong> ${JSON.stringify(document.extra_metadata, null, 2)}</p>` : ''}
              </div>

              <div>
                <h3>Content Preview</h3>
                <div class="content-preview">${contentPreview || 'No content preview available for this document type.'}</div>
              </div>
            </body>
          </html>
        `);
        newWindow.document.close();
      }
    } catch (err: any) {
      setError('Failed to view document details');
    }
  };

  const handleDownloadDocument = async (documentId: string, filename: string) => {
    try {
      const response = await chatterSDK.documents.downloadDocumentApiV1DocumentsDocumentIdDownloadGet({
        documentId
      });

      // Create a blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError('Failed to download document');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setSearching(true);
      const searchRequest: DocumentSearchRequest = {
        query: searchQuery,
        limit: 10,
      };
      const response = await chatterSDK.documents.searchDocumentsApiV1DocumentsSearchPost({ documentSearchRequest: searchRequest });
      setSearchResults(response.data.results);
    } catch (err: any) {
      setError('Failed to search documents');
    } finally {
      setSearching(false);
    }
  };

  const filteredDocuments = documents.filter(document =>
    (document.title?.toLowerCase() ?? '').includes(searchTerm.toLowerCase()) ||
    document.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    document.mime_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const paginatedDocuments = filteredDocuments.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'processed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  // More options menu handlers
  const openActionsMenu = (e: React.MouseEvent<HTMLElement>, doc: DocumentResponse) => {
    setActionAnchorEl(e.currentTarget);
    setActionDocument(doc);
  };

  const closeActionsMenu = () => {
    setActionAnchorEl(null);
    setActionDocument(null);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Document Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<SearchIcon />}
            onClick={() => setSearchDialogOpen(true)}
          >
            Semantic Search
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDocuments}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={() => setUploadDialogOpen(true)}
          >
            Upload Document
          </Button>
        </Box>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                {documents.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Documents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="secondary">
                {documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Chunks
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                {formatFileSize(documents.reduce((sum, doc) => sum + doc.file_size, 0))}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Size
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="info.main">
                {documents.filter(doc => doc.status === 'processed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Processed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search documents by title, filename, or content type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            size="small"
          />
        </CardContent>
      </Card>
      {/* Documents Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>Chunks</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedDocuments.map((document) => (
                <TableRow key={document.id} hover>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {document.title}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={document.mime_type}
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatFileSize(document.file_size)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {document.chunk_count ? (
                      <Chip
                        label={document.chunk_count}
                        color="info"
                        variant="outlined"
                        size="small"
                      />
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={document.status}
                      color={getStatusColor(document.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(new Date(document.created_at), 'MMM dd, yyyy HH:mm')}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      color="primary"
                      title="More actions"
                      aria-label="More actions"
                      onClick={(e) => openActionsMenu(e, document)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {paginatedDocuments.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                      No documents found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredDocuments.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Card>

      {/* Actions Menu */}
      <Menu
        anchorEl={actionAnchorEl}
        open={Boolean(actionAnchorEl)}
        onClose={closeActionsMenu}
      >
        <MenuItem
          onClick={() => {
            if (actionDocument) handleViewDocument(actionDocument.id);
            closeActionsMenu();
          }}
        >
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          View Details
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (actionDocument) handleDownloadDocument(actionDocument.id, actionDocument.filename);
            closeActionsMenu();
          }}
        >
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          Download
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (actionDocument) handleDeleteDocument(actionDocument.id);
            closeActionsMenu();
          }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Document Title (optional)"
              value={uploadTitle}
              onChange={(e) => setUploadTitle(e.target.value)}
              sx={{ mb: 2 }}
            />
            <input
              type="file"
              accept=".pdf,.txt,.doc,.docx,.md,.csv,.json"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              style={{ width: '100%', padding: '10px', border: '2px dashed #ccc', borderRadius: '4px' }}
            />
            {uploadFile && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Selected: {uploadFile.name} ({formatFileSize(uploadFile.size)})
                </Typography>
              </Box>
            )}
          </Box>
          {uploading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Uploading and processing document...
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)} disabled={uploading}>
            Cancel
          </Button>
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!uploadFile || uploading}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>

      {/* Semantic Search Dialog */}
      <Dialog open={searchDialogOpen} onClose={() => setSearchDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Semantic Document Search</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Search Query"
              placeholder="Enter your search query to find relevant document chunks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={!searchQuery.trim() || searching}
              startIcon={<SearchIcon />}
              fullWidth
            >
              {searching ? 'Searching...' : 'Search'}
            </Button>
          </Box>

          {searching && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
            </Box>
          )}

          {searchResults.length > 0 && (
            <Paper sx={{ mt: 3, maxHeight: 400 }}>
              <CustomScrollbar>
                <List>
                  {searchResults.map((result, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="subtitle2" sx={{ mr: 1 }}>
                              Score: {(result.score || 0).toFixed(3)}
                            </Typography>
                            <Chip label={result.source || 'Unknown'} size="small" />
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                            {result.content || result.text || 'No content available'}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CustomScrollbar>
            </Paper>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSearchDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="upload"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setUploadDialogOpen(true)}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default DocumentsPage;
