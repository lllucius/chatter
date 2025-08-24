import React, { useState, useContext } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Chat as ChatIcon,
  Description as DocumentIcon,
  AccountBox as ProfileIcon,
  TextSnippet as PromptIcon,
  SmartToy as AgentIcon,
  BarChart as AnalyticsIcon,
  HealthAndSafety as HealthIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';
import { chatterSDK } from '../services/chatter-sdk';
import { ThemeContext } from '../App';

const drawerWidth = 240;
const collapsedDrawerWidth = 64;

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactElement;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { label: 'Chat', path: '/chat', icon: <ChatIcon /> },
  { label: 'Conversations', path: '/conversations', icon: <AnalyticsIcon /> },
  { label: 'Documents', path: '/documents', icon: <DocumentIcon /> },
  { label: 'Profiles', path: '/profiles', icon: <ProfileIcon /> },
  { label: 'Prompts', path: '/prompts', icon: <PromptIcon /> },
  { label: 'Agents', path: '/agents', icon: <AgentIcon /> },
  { label: 'Administration', path: '/administration', icon: <AdminIcon /> },
  { label: 'Health', path: '/health', icon: <HealthIcon /> },
];

const Layout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { darkMode, toggleDarkMode } = useContext(ThemeContext);

  const currentDrawerWidth = sidebarCollapsed ? collapsedDrawerWidth : drawerWidth;

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    chatterSDK.logout();
    navigate('/login');
    handleProfileMenuClose();
  };

  const drawer = (
    <div>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {!sidebarCollapsed && (
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
            Chatter
          </Typography>
        )}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {!sidebarCollapsed && (
            <>
              <Tooltip title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}>
                <IconButton onClick={toggleDarkMode} size="small">
                  {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
                </IconButton>
              </Tooltip>
              <IconButton size="small" sx={{ mr: 1 }}>
                <Badge badgeContent={4} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
              <IconButton
                size="small"
                aria-label="account of current user"
                aria-controls="profile-menu"
                aria-haspopup="true"
                onClick={handleProfileMenuOpen}
              >
                <Avatar sx={{ width: 24, height: 24 }}>U</Avatar>
              </IconButton>
            </>
          )}
          <IconButton onClick={handleSidebarToggle} sx={{ display: { xs: 'none', sm: 'block' } }}>
            {sidebarCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        </Box>
      </Toolbar>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                minHeight: 48,
                justifyContent: sidebarCollapsed ? 'center' : 'initial',
                px: 2.5,
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: sidebarCollapsed ? 'auto' : 3,
                  justifyContent: 'center',
                }}
              >
                <Tooltip title={sidebarCollapsed ? item.label : ''} placement="right">
                  {item.icon}
                </Tooltip>
              </ListItemIcon>
              {!sidebarCollapsed && <ListItemText primary={item.label} />}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      {/* Profile Menu */}
      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleProfileMenuClose}>
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
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      
      <Box
        component="nav"
        sx={{ width: { sm: currentDrawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          <Box>
            <Toolbar sx={{ justifyContent: 'space-between' }}>
              <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
                Chatter
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Tooltip title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}>
                  <IconButton onClick={toggleDarkMode} size="small">
                    {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
                  </IconButton>
                </Tooltip>
                <IconButton size="small" sx={{ mr: 1 }}>
                  <Badge badgeContent={4} color="error">
                    <NotificationsIcon />
                  </Badge>
                </IconButton>
                <IconButton
                  size="small"
                  aria-label="account of current user"
                  onClick={handleProfileMenuOpen}
                >
                  <Avatar sx={{ width: 24, height: 24 }}>U</Avatar>
                </IconButton>
                <IconButton onClick={handleDrawerToggle}>
                  <MenuIcon />
                </IconButton>
              </Box>
            </Toolbar>
            <Divider />
            <List>
              {navItems.map((item) => (
                <ListItem key={item.path} disablePadding>
                  <ListItemButton
                    selected={location.pathname === item.path}
                    onClick={() => {
                      navigate(item.path);
                      handleDrawerToggle();
                    }}
                    sx={{
                      minHeight: 48,
                      px: 2.5,
                    }}
                  >
                    <ListItemIcon sx={{ mr: 3 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
            
            {/* Profile Menu */}
            <Menu
              id="profile-menu"
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleProfileMenuClose}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
            >
              <MenuItem onClick={handleProfileMenuClose}>
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
          </Box>
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: currentDrawerWidth,
              transition: (theme) => theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflowX: 'hidden',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${currentDrawerWidth}px)` },
          transition: (theme) => theme.transitions.create(['width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;