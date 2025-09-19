import React, { memo } from 'react';
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Menu,
  MenuItem,
} from '../../utils/mui';
import { UsersIcon, MoreIcon, SettingsIcon } from '../../utils/icons';

interface User {
  id: string;
  email: string;
  role: string;
  lastLogin: string;
  status: string;
  name: string;
  isActive: boolean;
}

interface UsersTabProps {
  users: User[];
  loading: boolean;
  onAddUser: () => void;
  onEditUser: (user: User) => void;
  actionAnchorEl: HTMLElement | null;
  actionUser: User | null;
  onOpenUserActions: (e: React.MouseEvent<HTMLElement>, user: User) => void;
  onCloseActions: () => void;
}

const UsersTab: React.FC<UsersTabProps> = memo(
  ({
    users,
    loading,
    onAddUser,
    onEditUser,
    actionAnchorEl,
    actionUser,
    onOpenUserActions,
    onCloseActions,
  }) => {
    return (
      <Box>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            startIcon={<UsersIcon />}
            onClick={onAddUser}
            disabled={loading}
          >
            Add User
          </Button>
        </Box>

        <List>
          {users.map((user) => (
            <ListItem key={user.id}>
              <ListItemIcon>
                <UsersIcon />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box
                    component="span"
                    sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                  >
                    <Typography component="span" variant="subtitle1">
                      {user.name}
                    </Typography>
                    <Chip
                      size="small"
                      label={user.role}
                      color={
                        user.role === 'Administrator' ? 'primary' : 'default'
                      }
                    />
                  </Box>
                }
                secondary={
                  <Box component="span" sx={{ display: 'block', mt: 1 }}>
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.secondary"
                      sx={{ display: 'block' }}
                    >
                      {user.email}
                    </Typography>
                    <Box
                      component="span"
                      sx={{ display: 'flex', gap: 1, mt: 0.5 }}
                    >
                      <Chip
                        size="small"
                        label={user.status}
                        color={user.isActive ? 'success' : 'default'}
                      />
                      <Typography
                        component="span"
                        variant="caption"
                        color="text.secondary"
                      >
                        Last login: {user.lastLogin}
                      </Typography>
                    </Box>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={(e) => onOpenUserActions(e, user)}
                >
                  <MoreIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        {/* User Actions Menu */}
        <Menu
          anchorEl={actionAnchorEl}
          open={Boolean(actionAnchorEl)}
          onClose={onCloseActions}
        >
          <MenuItem
            onClick={() => {
              if (actionUser) onEditUser(actionUser);
              onCloseActions();
            }}
          >
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            User Settings
          </MenuItem>
        </Menu>
      </Box>
    );
  }
);

UsersTab.displayName = 'UsersTab';

export default UsersTab;
