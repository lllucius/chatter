import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Box,
} from '@mui/material';

/**
 * Base dialog component that consolidates common dialog patterns
 * used across all form components
 */

export interface BaseDialogProps {
  open: boolean;
  title: string;
  onClose: () => void;
  onSubmit?: () => void | Promise<void>;
  onCancel?: () => void;
  children: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  fullScreen?: boolean;
  isSubmitting?: boolean;
  submitText?: string;
  cancelText?: string;
  disableSubmit?: boolean;
  hideActions?: boolean;
  submitButtonColor?:
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning';
  submitButtonVariant?: 'text' | 'outlined' | 'contained';
}

export const BaseDialog: React.FC<BaseDialogProps> = ({
  open,
  title,
  onClose,
  onSubmit,
  onCancel,
  children,
  maxWidth = 'sm',
  fullWidth = true,
  fullScreen = false,
  isSubmitting = false,
  submitText = 'Save',
  cancelText = 'Cancel',
  disableSubmit = false,
  hideActions = false,
  submitButtonColor = 'primary',
  submitButtonVariant = 'contained',
}) => {
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      onClose();
    }
  };

  const handleSubmit = async () => {
    if (onSubmit) {
      await onSubmit();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      fullScreen={fullScreen}
      aria-labelledby="dialog-title"
    >
      <DialogTitle id="dialog-title">{title}</DialogTitle>

      <DialogContent dividers>
        <Box sx={{ py: 1 }}>{children}</Box>
      </DialogContent>

      {!hideActions && (
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            onClick={handleCancel}
            disabled={isSubmitting}
            variant="outlined"
          >
            {cancelText}
          </Button>

          {onSubmit && (
            <Button
              onClick={handleSubmit}
              disabled={disableSubmit || isSubmitting}
              color={submitButtonColor}
              variant={submitButtonVariant}
              startIcon={
                isSubmitting ? (
                  <CircularProgress size={16} color="inherit" />
                ) : undefined
              }
            >
              {isSubmitting ? 'Saving...' : submitText}
            </Button>
          )}
        </DialogActions>
      )}
    </Dialog>
  );
};

/**
 * Form-specific dialog that adds common form functionality
 */
export interface FormDialogProps extends Omit<BaseDialogProps, 'onSubmit'> {
  mode: 'create' | 'edit';
  onSubmit: (event: React.FormEvent) => void | Promise<void>;
  entityName?: string;
}

export const FormDialog: React.FC<FormDialogProps> = ({
  mode,
  entityName = 'Item',
  title,
  submitText,
  onSubmit,
  ...props
}) => {
  const defaultTitle =
    mode === 'edit' ? `Edit ${entityName}` : `Add ${entityName}`;
  const defaultSubmitText = mode === 'edit' ? 'Update' : 'Create';

  return (
    <BaseDialog
      title={title || defaultTitle}
      submitText={submitText || defaultSubmitText}
      onSubmit={onSubmit as () => void | Promise<void>}
      {...props}
    />
  );
};

export default BaseDialog;
