import React, { useState } from 'react';
import {
  TextField,
  Box,
  Typography,
  LinearProgress,
  Alert,
  AlertTitle,
} from '../utils/mui';
import { CrudFormProps } from './CrudDataTable';
import { FormDialog } from './BaseDialog';
import { useBaseForm } from '../hooks/useBaseForm';
import { formatFileSize } from '../utils/common';

interface DocumentCreateData {
  file: File;
  title?: string;
}

interface DocumentUpdateData {
  title?: string;
}

const defaultDocumentData = {
  title: '',
};

const DocumentForm: React.FC<
  CrudFormProps<DocumentCreateData, DocumentUpdateData>
> = ({ open, mode, initialData, onClose, onSubmit }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const { formData, updateFormData, isSubmitting, handleSubmit, handleClose } =
    useBaseForm(
      {
        defaultData: defaultDocumentData,
        transformInitialData: (data: DocumentUpdateData): void => ({
          title: data.title || '',
        }),
      },
      open,
      mode,
      initialData
    );

  const handleFormSubmit = handleSubmit(async (data) => {
    try {
      setUploadError(null); // Clear any previous error
      if (mode === 'create') {
        if (!file) return;
        await onSubmit({
          file,
          title: data.title || undefined,
        });
      } else {
        await onSubmit({
          title: data.title || undefined,
        });
      }
    } catch (error: unknown) {
      // Check if this is a duplicate document error
      let errorMessage = '';
      if (error && typeof error === 'object') {
        const errorObj = error as {
          response?: { data?: { detail?: string } };
          message?: string;
        };
        errorMessage =
          errorObj.response?.data?.detail || errorObj.message || '';
      } else if (typeof error === 'string') {
        errorMessage = error;
      }

      if (
        errorMessage.includes(
          'Document with identical content already exists'
        ) ||
        errorMessage.includes('This file has already been uploaded')
      ) {
        setUploadError(
          'This file has already been uploaded. Documents are identified by their content, so the same file cannot be uploaded twice. Please check your existing documents or upload a different file.'
        );
      } else {
        // Let the error propagate to the global handler for other types of errors
        throw error;
      }
    }
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadError(null); // Clear any previous error when selecting a new file
      // Auto-fill title from filename if not already set
      if (!formData.title && selectedFile.name) {
        const nameWithoutExtension = selectedFile.name.replace(/\.[^/.]+$/, '');
        updateFormData({ title: nameWithoutExtension });
      }
    }
  };

  const handleCustomClose = handleClose(() => {
    setFile(null);
    setUploadError(null); // Clear error when closing
    onClose();
  });

  return (
    <FormDialog
      open={open}
      mode={mode}
      entityName="Document"
      onClose={handleCustomClose}
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting}
      disableSubmit={mode === 'create' && !file}
      submitText={mode === 'create' ? 'Upload' : 'Update'}
    >
      <TextField
        fullWidth
        label="Document Title (optional)"
        value={formData.title}
        onChange={(e) => updateFormData({ title: e.target.value })}
        sx={{ mb: 3 }}
      />

      {mode === 'create' && (
        <>
          <input
            type="file"
            accept=".pdf,.txt,.doc,.docx,.md,.csv,.json"
            onChange={handleFileSelect}
            style={{
              width: '100%',
              padding: '10px',
              border: '2px dashed #ccc',
              borderRadius: '4px',
            }}
          />
          {file && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2">
                Selected: {file.name} ({formatFileSize(file.size)})
              </Typography>
            </Box>
          )}

          {uploadError && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <AlertTitle>Duplicate File</AlertTitle>
              {uploadError}
            </Alert>
          )}
        </>
      )}

      {isSubmitting && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {mode === 'create'
              ? 'Uploading and processing document...'
              : 'Updating document...'}
          </Typography>
        </Box>
      )}
    </FormDialog>
  );
};

export default DocumentForm;
