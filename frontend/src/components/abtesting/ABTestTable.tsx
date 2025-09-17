import React, { memo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  Paper,
} from '../../utils/mui';
import {
  EditIcon,
  DeleteIcon,
  PlayIcon as StartIcon,
  PauseIcon,
  StopIcon,
  CheckIcon as CompleteIcon,
  MoreIcon as MoreVertIcon,
} from '../../utils/icons';
import { ABTestResponse } from 'chatter-sdk';
import { format } from 'date-fns';

export type TestStatus =
  | 'draft'
  | 'running'
  | 'paused'
  | 'completed'
  | 'cancelled';

interface ABTestTableProps {
  tests: ABTestResponse[];
  page: number;
  rowsPerPage: number;
  onPageChange: (event: unknown, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onTestSelect: (test: ABTestResponse) => void;
  onTestEdit: (test: ABTestResponse) => void;
  onTestDelete: (testId: string) => void;
  onTestStart: (testId: string) => void;
  onTestStop: (testId: string) => void;
  onMenuOpen: (
    event: React.MouseEvent<HTMLElement>,
    test: ABTestResponse
  ) => void;
  menuAnchorEl: HTMLElement | null;
  selectedTestForMenu: ABTestResponse | null;
  onMenuClose: () => void;
}

const ABTestTable: React.FC<ABTestTableProps> = memo(
  ({
    tests,
    page,
    rowsPerPage,
    onPageChange,
    onRowsPerPageChange,
    onTestSelect,
    onTestEdit,
    onTestDelete,
    onTestStart,
    onTestStop,
    onMenuOpen,
    menuAnchorEl,
    selectedTestForMenu,
    onMenuClose,
  }) => {
    const getStatusColor = (status: TestStatus) => {
      switch (status) {
        case 'draft':
          return 'default';
        case 'running':
          return 'success';
        case 'paused':
          return 'warning';
        case 'completed':
          return 'info';
        case 'cancelled':
          return 'error';
        default:
          return 'default';
      }
    };

    const getStatusIcon = (status: TestStatus) => {
      switch (status) {
        case 'running':
          return <StartIcon />;
        case 'paused':
          return <PauseIcon />;
        case 'completed':
          return <CompleteIcon />;
        case 'cancelled':
          return <StopIcon />;
        default:
          return null;
      }
    };

    return (
      <>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Sample Size</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tests
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((test) => (
                  <TableRow
                    key={test.id}
                    hover
                    onClick={() => onTestSelect(test)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <strong>{test.name}</strong>
                      {test.description && (
                        <div
                          style={{
                            fontSize: '0.875rem',
                            color: 'text.secondary',
                          }}
                        >
                          {test.description.length > 50
                            ? `${test.description.substring(0, 50)}...`
                            : test.description}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>{test.test_type}</TableCell>
                    <TableCell>
                      <Chip
                        label={test.status}
                        size="small"
                        color={getStatusColor(test.status as TestStatus)}
                        icon={getStatusIcon(test.status as TestStatus)}
                      />
                    </TableCell>
                    <TableCell>{test.duration_days} days</TableCell>
                    <TableCell>
                      {test.min_sample_size?.toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {test.created_at &&
                        format(new Date(test.created_at), 'MMM dd, yyyy')}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        onClick={(e) => {
                          e.stopPropagation();
                          onMenuOpen(e, test);
                        }}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={tests.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={onPageChange}
          onRowsPerPageChange={onRowsPerPageChange}
        />

        <Menu
          anchorEl={menuAnchorEl}
          open={Boolean(menuAnchorEl)}
          onClose={onMenuClose}
        >
          <MenuItem
            onClick={() => {
              if (selectedTestForMenu) onTestEdit(selectedTestForMenu);
              onMenuClose();
            }}
          >
            <ListItemIcon>
              <EditIcon fontSize="small" />
            </ListItemIcon>
            Edit
          </MenuItem>

          {selectedTestForMenu?.status === 'draft' && (
            <MenuItem
              onClick={() => {
                if (selectedTestForMenu) onTestStart(selectedTestForMenu.id);
                onMenuClose();
              }}
            >
              <ListItemIcon>
                <StartIcon fontSize="small" />
              </ListItemIcon>
              Start Test
            </MenuItem>
          )}

          {selectedTestForMenu?.status === 'running' && (
            <MenuItem
              onClick={() => {
                if (selectedTestForMenu) onTestStop(selectedTestForMenu.id);
                onMenuClose();
              }}
            >
              <ListItemIcon>
                <StopIcon fontSize="small" />
              </ListItemIcon>
              Stop Test
            </MenuItem>
          )}

          <MenuItem
            onClick={() => {
              if (selectedTestForMenu) onTestDelete(selectedTestForMenu.id);
              onMenuClose();
            }}
          >
            <ListItemIcon>
              <DeleteIcon fontSize="small" />
            </ListItemIcon>
            Delete
          </MenuItem>
        </Menu>
      </>
    );
  }
);

ABTestTable.displayName = 'ABTestTable';

export default ABTestTable;
