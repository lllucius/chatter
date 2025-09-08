import React, { useState, useContext, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Paper,
  LinearProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  GetApp as DownloadIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn } from '../components/CrudDataTable';
import DocumentForm from '../components/DocumentForm';
import CustomScrollbar from '../components/CustomScrollbar';
import {
  createStatusChipRenderer,
  createCategoryChipRenderer,
  createDateRenderer,
} from '../components/CrudRenderers';
import { chatterClient } from '../sdk/client';
import { toastService } from '../services/toast-service';
import { DocumentResponse, DocumentSearchRequest } from '../sdk';
import { ThemeContext } from '../App';
import { useSSE } from '../services/sse-context';
import { formatFileSize } from '../utils/common';
import {
  DocumentProcessingFailedEvent
} from '../services/sse-types';

interface DocumentCreateData {
  file: File;
  title?: string;
}

interface DocumentUpdateData {
  title?: string;
}

const DocumentsPage: React.FC = () => {
  const { darkMode } = useContext(ThemeContext);
  const { on } = useSSE();
  
  // Search dialog state
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  // State for force refresh after SSE events
  const [refreshKey, setRefreshKey] = useState(0);

  // SSE Event Listeners for real-time document updates
  useEffect(() => {
    // Attach listeners for real-time updates
    const unsubscribeDocumentUploaded = on('document.uploaded', () => {
      setRefreshKey(prev => prev + 1);
    });

    const unsubscribeProcessingStarted = on('document.processing_started', () => {
      setRefreshKey(prev => prev + 1);
    });

    const unsubscribeProcessingCompleted = on('document.processing_completed', () => {
      setRefreshKey(prev => prev + 1);
    });

    const unsubscribeProcessingFailed = on('document.processing_failed', (event) => {
      const docEvent = event as DocumentProcessingFailedEvent;
      toastService.error(`Document processing failed: ${docEvent.data.error}`);
      setRefreshKey(prev => prev + 1);
    });

    return () => {
      unsubscribeDocumentUploaded();
      unsubscribeProcessingStarted();
      unsubscribeProcessingCompleted();
      unsubscribeProcessingFailed();
    };
  }, [on]);

  // Custom file size renderer
  const createFileSizeRenderer = (): CrudColumn<DocumentResponse>['render'] => {
    return (value: number) => (
      <Typography variant="body2">
        {formatFileSize(value)}
      </Typography>
    );
  };

  // Custom chunk count renderer
  const createChunkCountRenderer = (): CrudColumn<DocumentResponse>['render'] => {
    return (value: number | undefined) => {
      if (!value) return '—';
      return (
        <Typography variant="body2" color="info.main">
          {value} chunks
        </Typography>
      );
    };
  };

  // Custom title renderer with filename fallback
  const createTitleRenderer = (): CrudColumn<DocumentResponse>['render'] => {
    return (value: string | undefined, item: DocumentResponse) => (
      <Box>
        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
          {value || item.filename}
        </Typography>
        {value && (
          <Typography variant="body2" color="text.secondary">
            {item.filename}
          </Typography>
        )}
      </Box>
    );
  };

  // Define columns
  const columns: CrudColumn<DocumentResponse>[] = [
    {
      id: 'title',
      label: 'Title',
      width: '250px',
      render: createTitleRenderer(),
    },
    {
      id: 'mime_type',
      label: 'Type',
      width: '120px',
      render: createCategoryChipRenderer<DocumentResponse>('secondary', 'outlined'),
    },
    {
      id: 'file_size',
      label: 'Size',
      width: '100px',
      render: createFileSizeRenderer(),
    },
    {
      id: 'chunk_count',
      label: 'Chunks',
      width: '100px',
      render: createChunkCountRenderer(),
    },
    {
      id: 'status',
      label: 'Status',
      width: '120px',
      render: createStatusChipRenderer<DocumentResponse>(),
    },
    {
      id: 'created_at',
      label: 'Created',
      width: '140px',
      render: createDateRenderer<DocumentResponse>('MMM dd, yyyy HH:mm'),
    },
  ];

  // Handle view document
  const handleViewDocument = async (document: DocumentResponse) => {
    try {
      // Try to get document chunks for content preview
      let contentPreview = '';

      try {
        const chunksResponse = await chatterClient.documents.getDocumentChunksApiV1DocumentsDocumentIdChunksGet({
          documentId: document.id,
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
      toastService.error(err, 'Failed to view document details');
    }
  };

  // Handle download document
  const handleDownloadDocument = async (document: DocumentResponse) => {
    try {
      const response = await chatterClient.documents.downloadDocumentApiV1DocumentsDocumentIdDownloadGet({
        documentId: document.id
      });

      // Create a blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.href = url;
      a.download = document.filename;
      window.document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      window.document.body.removeChild(a);
    } catch (err: any) {
      toastService.error(err, 'Failed to download document');
    }
  };

  // Handle search
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setSearching(true);
      const searchRequest: DocumentSearchRequest = {
        query: searchQuery,
        limit: 10,
      };
      const response = await chatterClient.documents.searchDocumentsApiV1DocumentsSearchPost({ 
        documentSearchRequest: searchRequest 
      });
      setSearchResults(response.results);
    } catch (err: any) {
      toastService.error(err, 'Failed to search documents');
    } finally {
      setSearching(false);
    }
  };

  // Define CRUD configuration
  const config: CrudConfig<DocumentResponse> = {
    entityName: 'Document',
    entityNamePlural: 'Documents',
    columns,
    actions: [
      {
        icon: <ViewIcon />,
        label: 'View Details',
        onClick: handleViewDocument,
      },
      {
        icon: <DownloadIcon />,
        label: 'Download',
        onClick: handleDownloadDocument,
      },
    ],
    enableCreate: true,
    enableEdit: false, // Documents can't really be "edited" in the traditional sense
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  // Define service methods
  const service: CrudService<DocumentResponse, DocumentCreateData, DocumentUpdateData> = {
    list: async (page: number, pageSize: number) => {
      const response = await chatterClient.documents.listDocumentsApiV1DocumentsGet({});
      const documents = response.documents || [];
      
      // Implement client-side pagination for now
      const startIndex = page * pageSize;
      const endIndex = startIndex + pageSize;
      const paginatedItems = documents.slice(startIndex, endIndex);
      
      return {
        items: paginatedItems,
        total: documents.length,
      };
    },

    create: async (data: DocumentCreateData) => {
      const response = await chatterClient.documents.uploadDocumentApiV1DocumentsUploadPost({
        file: data.file,
        title: data.title || undefined
      });
      return response.data;
    },

    delete: async (id: string) => {
      await chatterClient.documents.deleteDocumentApiV1DocumentsDocumentIdDelete({ 
        documentId: id 
      });
    },
  };

  const getItemId = (item: DocumentResponse) => item.id;

  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<SearchIcon />}
        onClick={() => setSearchDialogOpen(true)}
      >
        Semantic Search
      </Button>
    </>
  );

  return (
    <PageLayout title="Document Management" toolbar={toolbar}>
      <CrudDataTable
        key={refreshKey} // Force refresh on SSE events
        config={config}
        service={service}
        FormComponent={DocumentForm}
        getItemId={getItemId}
      />

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
                            <Typography variant="body2" color="text.secondary">
                              {result.source || 'Unknown'}
                            </Typography>
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
    </PageLayout>
  );
};

export default DocumentsPage;
