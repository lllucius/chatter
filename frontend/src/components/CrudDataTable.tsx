import React, {
  useState,
  useEffect,
  ReactNode,
  useCallback,
  useImperativeHandle,
  forwardRef,
} from 'react';
import {
  Box,
  Card,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  CircularProgress,
  Menu,
  MenuItem,
  ListItemIcon,
  Fab,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';

export interface CrudColumn<T> {
  id: keyof T;
  label: string;
  width?: string;
  render?: (value: unknown, item: T) => ReactNode;
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
  list: (
    page: number,
    pageSize: number
  ) => Promise<{ items: T[]; total: number }>;
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

export interface CrudDataTableRef {
  handleCreate: () => void;
  handleRefresh: () => void;
}

interface CrudDataTableProps<T, TCreate, TUpdate> {
  config: CrudConfig<T>;
  service: CrudService<T, TCreate, TUpdate>;
  FormComponent?: React.ComponentType<CrudFormProps<TCreate, TUpdate>>;
  getItemId: (item: T) => string;
  externalDialogOpen?: boolean;
  onExternalDialogClose?: () => void;
}

function CrudDataTableInner<T, TCreate, TUpdate>(
  {
    config,
    service,
    FormComponent,
    getItemId,
    externalDialogOpen,
    onExternalDialogClose,
  }: CrudDataTableProps<T, TCreate, TUpdate>,
  ref: React.ForwardedRef<CrudDataTableRef>
) {
  // State management
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(config.pageSize || 10);
  const [total, setTotal] = useState(0);

  // Dialog state - use individual internal state for these
  const [internalDialogOpen, setInternalDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');

  // Use external dialog state if provided, otherwise use internal state
  const isDialogOpen =
    externalDialogOpen !== undefined ? externalDialogOpen : internalDialogOpen;
  const handleDialogClose = () => {
    if (onExternalDialogClose) {
      onExternalDialogClose();
    } else {
      setInternalDialogOpen(false);
    }
  };
  const [selectedItem, setSelectedItem] = useState<T | null>(null);

  // Action menu state
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(
    null
  );
  const [actionMenuItem, setActionMenuItem] = useState<T | null>(null);

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      // Convert 0-indexed page (MUI TablePagination) to 1-indexed page (backend API)
      const result = await service.list(page + 1, rowsPerPage);
      setItems(result.items);
      setTotal(result.total);
    } catch (error) {
      handleError(error, {
        source: 'CrudDataTable.loadData',
        operation: `load ${config.entityNamePlural.toLowerCase()}`,
        additionalData: { entityType: config.entityName },
      });
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, service, config.entityNamePlural, config.entityName]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // CRUD operations
  const handleCreate = () => {
    setDialogMode('create');
    setSelectedItem(null);
    if (externalDialogOpen !== undefined) {
      // External control - parent should handle the dialog opening
      return;
    } else {
      setInternalDialogOpen(true);
    }
  };

  // Expose methods to parent component via ref
  useImperativeHandle(ref, () => ({
    handleCreate,
    handleRefresh: loadData,
  }));

  const handleEdit = (item: T) => {
    setDialogMode('edit');
    setSelectedItem(item);
    setInternalDialogOpen(true);
  };

  const handleDelete = async (item: T) => {
    if (!service.delete) return;

    if (
      window.confirm(
        `Are you sure you want to delete this ${config.entityName.toLowerCase()}?`
      )
    ) {
      try {
        await service.delete(getItemId(item));
        toastService.success(`${config.entityName} deleted successfully`);
        await loadData();
      } catch (error) {
        handleError(error, {
          source: 'CrudDataTable.handleDelete',
          operation: `delete ${config.entityName.toLowerCase()}`,
          additionalData: {
            entityType: config.entityName,
            itemId: item ? getItemId(item) : undefined,
          },
        });
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
      handleDialogClose();
      await loadData();
    } catch (error) {
      handleError(error, {
        source: 'CrudDataTable.handleSave',
        operation: `${dialogMode} ${config.entityName.toLowerCase()}`,
        additionalData: {
          entityType: config.entityName,
          dialogMode,
          itemId: selectedItem ? getItemId(selectedItem) : undefined,
        },
      });
    }
  };

  // Action menu handlers
  const handleActionMenuOpen = (
    event: React.MouseEvent<HTMLElement>,
    item: T
  ) => {
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
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box sx={{ width: '100%' }}>
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
                {(config.enableEdit ||
                  config.enableDelete ||
                  config.actions) && (
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
                items.map((item) => (
                  <TableRow key={getItemId(item)} hover>
                    {config.columns.map((column) => (
                      <TableCell key={String(column.id)}>
                        {column.render
                          ? column.render(
                              (item as Record<string, unknown>)[
                                String(column.id)
                              ],
                              item
                            )
                          : String(
                              (item as Record<string, unknown>)[
                                String(column.id)
                              ] || ''
                            )}
                      </TableCell>
                    ))}
                    {(config.enableEdit ||
                      config.enableDelete ||
                      config.actions) && (
                      <TableCell>
                        <Tooltip title="Actions">
                          <IconButton
                            size="small"
                            onClick={(e) => handleActionMenuOpen(e, item)}
                          >
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
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
        {config.enableEdit && service.update && FormComponent && (
          <MenuItem
            onClick={() => {
              if (actionMenuItem) {
                handleEdit(actionMenuItem);
              }
              handleActionMenuClose();
            }}
          >
            <ListItemIcon>
              <EditIcon />
            </ListItemIcon>
            Edit {config.entityName}
          </MenuItem>
        )}
        {config.enableDelete && service.delete && (
          <MenuItem
            onClick={() => {
              if (actionMenuItem) {
                handleDelete(actionMenuItem);
              }
              handleActionMenuClose();
            }}
          >
            <ListItemIcon>
              <DeleteIcon />
            </ListItemIcon>
            Delete {config.entityName}
          </MenuItem>
        )}
        {(config.enableEdit || config.enableDelete) &&
          config.actions &&
          config.actions.length > 0 && <Divider />}
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
          open={isDialogOpen}
          mode={dialogMode}
          initialData={selectedItem as TUpdate}
          onClose={handleDialogClose}
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

export const CrudDataTable = forwardRef(CrudDataTableInner) as <
  T,
  TCreate,
  TUpdate,
>(
  props: CrudDataTableProps<T, TCreate, TUpdate> & {
    ref?: React.Ref<CrudDataTableRef>;
  }
) => React.ReactElement;

export default CrudDataTable;
