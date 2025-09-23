import React from 'react';
import {
  Toolbar,
  ButtonGroup,
  Button,
  Divider,
  Tooltip,
  Chip,
  Box,
  Typography,
  IconButton,
} from '@mui/material';
import {
  Undo as UndoIcon,
  Redo as RedoIcon,
  ContentCopy as CopyIcon,
  ContentPaste as PasteIcon,
  CheckCircle as ValidIcon,
  Error as ErrorIcon,
  Save as SaveIcon,
  Clear as ClearIcon,
  GridOn as GridIcon,
  Settings as PropertiesIcon,
  Analytics as AnalyticsIcon,
  LibraryBooks as TemplateIcon,
  GetApp as ExampleIcon,
  Menu as MenuIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  CenterFocusStrong as FitViewIcon,
} from '@mui/icons-material';
import { WorkflowToolbarProps } from './types';

const WorkflowToolbar: React.FC<WorkflowToolbarProps> = ({
  onUndo,
  onRedo,
  onCopy,
  onPaste,
  onValidate,
  onSave,
  onClear,
  canUndo,
  canRedo,
  canPaste,
  isValid,
  isSaving = false,
  readOnly = false,
  onToggleGrid,
  onToggleProperties,
  onToggleAnalytics,
  onToggleTemplates,
  onZoomIn,
  onZoomOut,
  onFitView,
  onLoadExamples,
  snapToGrid = false,
  showProperties = false,
  showAnalytics = false,
  showTemplates = false,
  validationStatus,
  isMobile = false,
  onToggleNodePalette,
}) => {
  return (
    <Toolbar
      variant="dense"
      sx={{
        minHeight: 56,
        bgcolor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider',
        justifyContent: 'space-between',
        gap: 2,
        px: 2,
      }}
    >
      {/* Left side - Main actions */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {/* Mobile Node Palette Toggle */}
        {isMobile && onToggleNodePalette && !readOnly && (
          <Tooltip title="Toggle Node Palette">
            <IconButton onClick={onToggleNodePalette} size="small">
              <MenuIcon />
            </IconButton>
          </Tooltip>
        )}

        <Typography variant="h6" component="h1" sx={{ mr: 2 }}>
          Workflow Builder
        </Typography>

        {!readOnly && (
          <>
            {/* Edit actions */}
            <ButtonGroup size="small" variant="outlined">
              <Tooltip title="Undo (Ctrl+Z)">
                <span>
                  <Button
                    onClick={onUndo}
                    disabled={!canUndo}
                    startIcon={<UndoIcon />}
                  >
                    Undo
                  </Button>
                </span>
              </Tooltip>
              <Tooltip title="Redo (Ctrl+Shift+Z)">
                <span>
                  <Button
                    onClick={onRedo}
                    disabled={!canRedo}
                    startIcon={<RedoIcon />}
                  >
                    Redo
                  </Button>
                </span>
              </Tooltip>
            </ButtonGroup>

            <Divider orientation="vertical" flexItem />

            {/* Clipboard actions */}
            <ButtonGroup size="small" variant="outlined">
              <Tooltip title="Copy Selection (Ctrl+C)">
                <Button onClick={onCopy} startIcon={<CopyIcon />}>
                  Copy
                </Button>
              </Tooltip>
              <Tooltip title="Paste (Ctrl+V)">
                <span>
                  <Button
                    onClick={onPaste}
                    disabled={!canPaste}
                    startIcon={<PasteIcon />}
                  >
                    Paste
                  </Button>
                </span>
              </Tooltip>
            </ButtonGroup>

            <Divider orientation="vertical" flexItem />
          </>
        )}

        {/* View controls */}
        <ButtonGroup size="small" variant="outlined">
          <Tooltip title="Zoom In">
            <Button onClick={onZoomIn} startIcon={<ZoomInIcon />}>
              Zoom In
            </Button>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <Button onClick={onZoomOut} startIcon={<ZoomOutIcon />}>
              Zoom Out
            </Button>
          </Tooltip>
          <Tooltip title="Fit to View">
            <Button onClick={onFitView} startIcon={<FitViewIcon />}>
              Fit View
            </Button>
          </Tooltip>
        </ButtonGroup>
      </Box>

      {/* Right side - Panel toggles and actions */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {/* Panel toggles */}
        <ButtonGroup size="small" variant="outlined">
          <Tooltip title="Toggle Grid Snap">
            <Button
              onClick={onToggleGrid}
              variant={snapToGrid ? 'contained' : 'outlined'}
              startIcon={<GridIcon />}
            >
              Grid
            </Button>
          </Tooltip>
          <Tooltip title="Toggle Properties Panel">
            <Button
              onClick={onToggleProperties}
              variant={showProperties ? 'contained' : 'outlined'}
              startIcon={<PropertiesIcon />}
            >
              Properties
            </Button>
          </Tooltip>
          <Tooltip title="Toggle Analytics Panel">
            <Button
              onClick={onToggleAnalytics}
              variant={showAnalytics ? 'contained' : 'outlined'}
              startIcon={<AnalyticsIcon />}
            >
              Analytics
            </Button>
          </Tooltip>
        </ButtonGroup>

        <Divider orientation="vertical" flexItem />

        {/* Templates and examples */}
        <ButtonGroup size="small" variant="outlined">
          <Tooltip title="Browse Templates">
            <Button
              onClick={onToggleTemplates}
              variant={showTemplates ? 'contained' : 'outlined'}
              startIcon={<TemplateIcon />}
            >
              Templates
            </Button>
          </Tooltip>
          <Tooltip title="Load Example Workflow">
            <Button onClick={onLoadExamples} startIcon={<ExampleIcon />}>
              Examples
            </Button>
          </Tooltip>
        </ButtonGroup>

        <Divider orientation="vertical" flexItem />

        {/* Validation status */}
        <Tooltip title="Validate Workflow">
          <Button
            onClick={onValidate}
            variant="outlined"
            size="small"
            startIcon={
              validationStatus === 'valid' ? (
                <ValidIcon color="success" />
              ) : validationStatus === 'invalid' ? (
                <ErrorIcon color="error" />
              ) : (
                <ValidIcon color="action" />
              )
            }
            sx={{
              borderColor:
                validationStatus === 'valid'
                  ? 'success.main'
                  : validationStatus === 'invalid'
                  ? 'error.main'
                  : 'grey.300',
            }}
          >
            Validate
          </Button>
        </Tooltip>

        {!readOnly && (
          <>
            <Divider orientation="vertical" flexItem />

            {/* Save and clear */}
            <ButtonGroup size="small">
              <Tooltip title="Save Workflow (Ctrl+S)">
                <Button
                  onClick={onSave}
                  variant="contained"
                  disabled={isSaving}
                  startIcon={<SaveIcon />}
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </Button>
              </Tooltip>
              <Tooltip title="Clear Workflow">
                <Button
                  onClick={onClear}
                  variant="outlined"
                  color="error"
                  startIcon={<ClearIcon />}
                >
                  Clear
                </Button>
              </Tooltip>
            </ButtonGroup>
          </>
        )}
      </Box>

      {/* Validation status indicator */}
      {validationStatus && (
        <Box sx={{ position: 'absolute', bottom: -8, right: 16 }}>
          <Chip
            size="small"
            icon={
              validationStatus === 'valid' ? (
                <ValidIcon />
              ) : (
                <ErrorIcon />
              )
            }
            label={
              validationStatus === 'valid'
                ? 'Valid'
                : validationStatus === 'invalid'
                ? 'Invalid'
                : 'Unknown'
            }
            color={
              validationStatus === 'valid'
                ? 'success'
                : validationStatus === 'invalid'
                ? 'error'
                : 'default'
            }
            variant="filled"
          />
        </Box>
      )}
    </Toolbar>
  );
};

export default WorkflowToolbar;