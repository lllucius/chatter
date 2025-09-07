import React, { useState, useEffect, ReactNode } from 'react';
import {
  Box,
  Card,
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
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  ListItemIcon,
  Fab,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { toastService } from '../services/toast-service';

export interface CrudColumn<T> {
  id: keyof T;
  label: string;
  width?: string;
  render?: (value: any, item: T) => ReactNode;
  sortable?: boolean;
}

export interface CrudAction<T> {
  icon: ReactNode;
  label: string;
  onClick: (item: T) => void;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
}

export interface CrudConfig<T> {
  entityName: string; // e.g., "Prompt", "Agent", "Model"
  entityNamePlural: string; // e.g., "Prompts", "Agents", "Models"
  columns: CrudColumn<T>[];
  actions?: CrudAction<T>[];
  enableCreate?: boolean;
  enableEdit?: boolean;
  enableDelete?: boolean;
  enableRefresh?: boolean;
  pageSize?: number;
  searchPlaceholder?: string;
}

export interface CrudService<T, TCreate, TUpdate> {
  list: (page: number, pageSize: number) => Promise<{ items: T[]; total: number }>;
  create?: (data: TCreate) => Promise<T>;
  update?: (id: string, data: TUpdate) => Promise<T>;
  delete?: (id: string) => Promise<void>;
  getById?: (id: string) => Promise<T>;
}

export interface CrudFormProps<TCreate, TUpdate> {
  open: boolean;
  mode: 'create' | 'edit';
  initialData?: TUpdate;
  onClose: () => void;
  onSubmit: (data: TCreate | TUpdate) => Promise<void>;
}

interface CrudDataTableProps<T, TCreate, TUpdate> {
  config: CrudConfig<T>;
  service: CrudService<T, TCreate, TUpdate>;
  FormComponent?: React.ComponentType<CrudFormProps<TCreate, TUpdate>>;
  getItemId: (item: T) => string;
}

export function CrudDataTable<T, TCreate, TUpdate>({
  config,
  service,
  FormComponent,
  getItemId,
}: CrudDataTableProps<T, TCreate, TUpdate>) {
  // State management
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(config.pageSize || 10);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedItem, setSelectedItem] = useState<T | null>(null);
  
  // Action menu state
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);
  const [actionMenuItem, setActionMenuItem] = useState<T | null>(null);

  // Load data
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await service.list(page, rowsPerPage);
      setItems(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      toastService.error(`Failed to load ${config.entityNamePlural.toLowerCase()}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [page, rowsPerPage]);

  // CRUD operations
  const handleCreate = () => {
    setDialogMode('create');
    setSelectedItem(null);
    setDialogOpen(true);
  };

  const handleEdit = (item: T) => {
    setDialogMode('edit');
    setSelectedItem(item);
    setDialogOpen(true);
  };

  const handleDelete = async (item: T) => {
    if (!service.delete) return;
    
    if (window.confirm(`Are you sure you want to delete this ${config.entityName.toLowerCase()}?`)) {
      try {
        await service.delete(getItemId(item));
        toastService.success(`${config.entityName} deleted successfully`);
        await loadData();
      } catch (err) {
        toastService.error(`Failed to delete ${config.entityName.toLowerCase()}`);
      }
    }
  };

  const handleFormSubmit = async (data: TCreate | TUpdate) => {
    try {
      if (dialogMode === 'create' && service.create) {
        await service.create(data as TCreate);
        toastService.success(`${config.entityName} created successfully`);
      } else if (dialogMode === 'edit' && service.update && selectedItem) {
        await service.update(getItemId(selectedItem), data as TUpdate);
        toastService.success(`${config.entityName} updated successfully`);
      }
      setDialogOpen(false);
      await loadData();
    } catch (err) {
      toastService.error(`Failed to ${dialogMode} ${config.entityName.toLowerCase()}`);
    }
  };

  // Action menu handlers
  const handleActionMenuOpen = (event: React.MouseEvent<HTMLElement>, item: T) => {
    setActionMenuAnchor(event.currentTarget);
    setActionMenuItem(item);
  };

  const handleActionMenuClose = () => {
    setActionMenuAnchor(null);
    setActionMenuItem(null);
  };

  const handleActionClick = (action: CrudAction<T>) => {
    if (actionMenuItem) {
      action.onClick(actionMenuItem);
    }
    handleActionMenuClose();
  };

  // Pagination handlers
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {config.entityNamePlural}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {config.enableRefresh && (
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadData}
              disabled={loading}
            >
              Refresh
            </Button>
          )}
          {config.enableCreate && service.create && FormComponent && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreate}
            >
              Add {config.entityName}
            </Button>
          )}
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Data Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {config.columns.map((column) => (
                  <TableCell key={String(column.id)} width={column.width}>
                    {column.label}
                  </TableCell>
                ))}
                {(config.enableEdit || config.enableDelete || config.actions) && (
                  <TableCell width="120px">Actions</TableCell>
                )}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell
                    colSpan={config.columns.length + 1}
                    sx={{ textAlign: 'center', py: 4 }}
                  >
                    <CircularProgress size={40} />
                  </TableCell>
                </TableRow>
              ) : items.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={config.columns.length + 1}
                    sx={{ textAlign: 'center', py: 4 }}
                  >
                    <Typography variant="body2" color="textSecondary">
                      No {config.entityNamePlural.toLowerCase()} found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                items.map((item, index) => (
                  <TableRow key={getItemId(item)} hover>
                    {config.columns.map((column) => (
                      <TableCell key={String(column.id)}>
                        {column.render
                          ? column.render((item as any)[column.id], item)
                          : String((item as any)[column.id] || '')
                        }
                      </TableCell>
                    ))}
                    {(config.enableEdit || config.enableDelete || config.actions) && (
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {config.enableEdit && service.update && FormComponent && (
                            <Tooltip title={`Edit ${config.entityName}`}>
                              <IconButton
                                size="small"
                                onClick={() => handleEdit(item)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {config.enableDelete && service.delete && (
                            <Tooltip title={`Delete ${config.entityName}`}>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDelete(item)}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {config.actions && config.actions.length > 0 && (
                            <Tooltip title="More actions">
                              <IconButton
                                size="small"
                                onClick={(e) => handleActionMenuOpen(e, item)}
                              >
                                <MoreVertIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                    )}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={handleActionMenuClose}
      >
        {config.actions?.map((action, index) => (
          <MenuItem key={index} onClick={() => handleActionClick(action)}>
            <ListItemIcon>{action.icon}</ListItemIcon>
            {action.label}
          </MenuItem>
        ))}
      </Menu>

      {/* Create/Edit Dialog */}
      {FormComponent && (
        <FormComponent
          open={dialogOpen}
          mode={dialogMode}
          initialData={selectedItem as TUpdate}
          onClose={() => setDialogOpen(false)}
          onSubmit={handleFormSubmit}
        />
      )}

      {/* Floating Action Button for mobile */}
      {config.enableCreate && service.create && FormComponent && (
        <Fab
          color="primary"
          aria-label="add"
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            display: { xs: 'flex', sm: 'none' },
          }}
          onClick={handleCreate}
        >
          <AddIcon />
        </Fab>
      )}
    </Box>
  );
}

export default CrudDataTable;