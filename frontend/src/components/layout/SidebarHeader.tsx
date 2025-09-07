import React, { useContext } from 'react';
import {
  Toolbar,
  Typography,
  Box,
  IconButton,
  Avatar,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ThemeContext } from '../../App';
import { chatterSDK } from '../../services/chatter-sdk';

interface SidebarHeaderProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  showCollapseButton?: boolean;
  showMenuButton?: boolean;
  onMenuToggle?: () => void;
  anchorEl: HTMLElement | null;
  onProfileMenuOpen: (event: React.MouseEvent<HTMLElement>) => void;
  onProfileMenuClose: () => void;
}

const SidebarHeader: React.FC<SidebarHeaderProps> = ({
  collapsed,
  onToggleCollapse,
  showCollapseButton = true,
  showMenuButton = false,
  onMenuToggle,
  anchorEl,
  onProfileMenuOpen,
  onProfileMenuClose,
}) => {
  const { darkMode, toggleDarkMode } = useContext(ThemeContext);
  const navigate = useNavigate();

  const handleSettingsClick = () => {
    navigate('/settings');
    onProfileMenuClose();
  };

  const handleLogout = () => {
    chatterSDK.logout();
    navigate('/login');
    onProfileMenuClose();
  };

  return (
    <>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {!collapsed && (
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
            Chatter
          </Typography>
        )}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {!collapsed && (
            <>
              <Tooltip title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}>
                <IconButton onClick={toggleDarkMode} size="small">
                  {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
                </IconButton>
              </Tooltip>
              <IconButton
                size="small"
                aria-label="account of current user"
                aria-controls="profile-menu"
                aria-haspopup="true"
                onClick={onProfileMenuOpen}
              >
                <Avatar sx={{ width: 24, height: 24 }}>U</Avatar>
              </IconButton>
            </>
          )}
          {showCollapseButton && (
            <IconButton onClick={onToggleCollapse} sx={{ display: { xs: 'none', sm: 'block' } }}>
              {collapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
            </IconButton>
          )}
          {showMenuButton && (
            <IconButton onClick={onMenuToggle}>
              <MenuIcon />
            </IconButton>
          )}
        </Box>
      </Toolbar>

      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={onProfileMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem onClick={handleSettingsClick}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
    </>
  );
};

export default SidebarHeader;