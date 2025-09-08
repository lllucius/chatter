import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  LinearProgress,
} from '@mui/material';
import { CloudUpload as UploadIcon } from '@mui/icons-material';
import { CrudFormProps } from './CrudDataTable';
import { formatFileSize } from '../utils/common';

interface DocumentCreateData {
  file: File;
  title?: string;
}

interface DocumentUpdateData {
  title?: string;
}

const DocumentForm: React.FC<CrudFormProps<DocumentCreateData, DocumentUpdateData>> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState(initialData?.title || '');
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async () => {
    if (mode === 'create') {
      if (!file) return;
      
      setUploading(true);
      try {
        await onSubmit({
          file,
          title: title || undefined,
        });
        handleClose();
      } finally {
        setUploading(false);
      }
    } else {
      await onSubmit({
        title: title || undefined,
      });
      handleClose();
    }
  };

  const handleClose = () => {
    setFile(null);
    setTitle('');
    setUploading(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {mode === 'create' ? 'Upload Document' : 'Edit Document'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          <TextField
            fullWidth
            label="Document Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            sx={{ mb: 3 }}
          />
          
          {mode === 'create' && (
            <>
              <input
                type="file"
                accept=".pdf,.txt,.doc,.docx,.md,.csv,.json"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                style={{ 
                  width: '100%', 
                  padding: '10px', 
                  border: '2px dashed #ccc', 
                  borderRadius: '4px' 
                }}
              />
              {file && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Selected: {file.name} ({formatFileSize(file.size)})
                  </Typography>
                </Box>
              )}
            </>
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
        <Button onClick={handleClose} disabled={uploading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={(mode === 'create' && !file) || uploading}
          startIcon={mode === 'create' ? <UploadIcon /> : undefined}
        >
          {mode === 'create' ? 'Upload' : 'Update'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentForm;