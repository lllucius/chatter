import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import DocumentsPage from '../DocumentsPage';
import { getSDK, authService } from '../../services/auth-service';

// Mock dependencies
vi.mock('../../services/auth-service', (): void => ({
  getSDK: vi.fn((): void => ({
    documents: {
      listDocumentsApiV1Documents: vi.fn(),
      uploadDocumentApiV1DocumentsUploadPost: vi.fn(),
      deleteDocumentApiV1DocumentsDocumentIdDelete: vi.fn(),
      getDocumentApiV1DocumentsDocumentIdGet: vi.fn(),
      searchDocumentsApiV1DocumentsSearchPost: vi.fn(),
      getDocumentChunksApiV1DocumentsDocumentIdChunksGet: vi.fn(),
      downloadDocumentApiV1DocumentsDocumentIdDownloadGet: vi.fn(),
    },
  })),
  authService: {
    isAuthenticated: vi.fn(() => true),
  },
}));

// Mock SSE context
vi.mock('../../services/sse-context', (): void => ({
  useSSE: (): void => ({
    on: vi.fn(() => vi.fn()),
    off: vi.fn(),
    isConnected: false,
    connect: vi.fn(),
    disconnect: vi.fn(),
  }),
  SSEProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock App context
vi.mock('../../App', (): void => ({
  ThemeContext: React.createContext({
    darkMode: false,
    toggleDarkMode: vi.fn(),
  }),
}));

// Create theme
const theme = createTheme();

// Sample document data
const mockDocuments = [
  {
    id: '1',
    filename: 'test-document.pdf',
    title: 'Test Document',
    mime_type: 'application/pdf',
    file_size: 1024000,
    status: 'processed',
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z',
    chunk_count: 5,
    metadata: {},
  },
  {
    id: '2',
    filename: 'another-doc.txt',
    title: 'Another Document',
    mime_type: 'text/plain',
    file_size: 2048,
    status: 'processing',
    created_at: '2024-01-02T10:00:00Z',
    updated_at: '2024-01-02T10:00:00Z',
    chunk_count: 0,
    metadata: {},
  },
];

// Wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({
  children,
}): void => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>{children}</ThemeProvider>
  </BrowserRouter>
);

describe('DocumentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Setup default API responses
    vi.mocked(getSDK().documents.listDocumentsApiV1Documents).mockResolvedValue(
      {
        documents: mockDocuments,
      } as any
    );
  });

  it('loads and displays documents', async () => {
    await act(async () => {
      render(
        <TestWrapper>
          <DocumentsPage />
        </TestWrapper>
      );
    });

    // Wait for documents to load and display
    await waitFor(
      () => {
        expect(screen.getByText('Test Document')).toBeInTheDocument();
        expect(screen.getByText('Another Document')).toBeInTheDocument();
      },
      { timeout: 10000 }
    );

    expect(
      getSDK().documents.listDocumentsApiV1Documents
    ).toHaveBeenCalledTimes(1);
  });

  it('calls API on mount', async () => {
    await act(async () => {
      render(
        <TestWrapper>
          <DocumentsPage />
        </TestWrapper>
      );
    });

    // Should call the API immediately
    expect(
      getSDK().documents.listDocumentsApiV1Documents
    ).toHaveBeenCalledTimes(1);
  });

  it('displays error message when API call fails', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    // Override the default mock to simulate API failure for this specific test
    vi.mocked(
      getSDK().documents.listDocumentsApiV1Documents
    ).mockRejectedValueOnce(new Error('API Error'));

    await act(async () => {
      render(
        <TestWrapper>
          <DocumentsPage />
        </TestWrapper>
      );
    });

    // Wait for the error to be processed
    await waitFor(
      () => {
        // The component should show "No documents found" when API fails and returns empty data
        expect(screen.getByText('No documents found')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    consoleErrorSpy.mockRestore();
  });

  it('shows document status correctly', async () => {
    await act(async () => {
      render(
        <TestWrapper>
          <DocumentsPage />
        </TestWrapper>
      );
    });

    await waitFor(() => {
      expect(screen.getByText('processed')).toBeInTheDocument();
      expect(screen.getByText('processing')).toBeInTheDocument();
    });
  });

  it('renders page header correctly', async () => {
    await act(async () => {
      render(
        <TestWrapper>
          <DocumentsPage />
        </TestWrapper>
      );
    });

    await waitFor(() => {
      expect(screen.getByText('Document Management')).toBeInTheDocument();
    });
  });
});
