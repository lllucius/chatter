import React, { useState, useContext, useEffect } from 'react';
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
  Collapse,
  ListSubheader,
} from '@mui/material';
import CustomScrollbar from './CustomScrollbar';
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
  Storage as ModelsIcon,
  Build as ToolsIcon,
  AccountTree as WorkflowIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import { chatterSDK } from '../services/chatter-sdk';
import { ThemeContext } from '../App';
import { RightSidebarProvider, useRightSidebar } from './RightSidebarContext';

const drawerWidth = 240;
const collapsedDrawerWidth = 64;

const rightDrawerWidth = 300;
const rightCollapsedDrawerWidth = 64;

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactElement;
}

interface NavSection {
  title: string;
  items: NavItem[];
  defaultExpanded?: boolean;
}

const navSections: NavSection[] = [
  {
    title: 'Core',
    defaultExpanded: true,
    items: [
      { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
      { label: 'Chat', path: '/chat', icon: <ChatIcon /> },
    ]
  },
  {
    title: 'Content Management', 
    defaultExpanded: true,
    items: [
      { label: 'Conversations', path: '/conversations', icon: <AnalyticsIcon /> },
      { label: 'Documents', path: '/documents', icon: <DocumentIcon /> },
      { label: 'Profiles', path: '/profiles', icon: <ProfileIcon /> },
      { label: 'Prompts', path: '/prompts', icon: <PromptIcon /> },
    ]
  },
  {
    title: 'AI & Models',
    defaultExpanded: true,
    items: [
      { label: 'Models', path: '/models', icon: <ModelsIcon /> },
      { label: 'Agents', path: '/agents', icon: <AgentIcon /> },
      { label: 'Tools', path: '/tools', icon: <ToolsIcon /> },
      { label: 'Workflows', path: '/workflows', icon: <WorkflowIcon /> },
    ]
  },
  {
    title: 'System',
    defaultExpanded: false,
    items: [
      { label: 'Administration', path: '/administration', icon: <AdminIcon /> },
      { label: 'Health', path: '/health', icon: <HealthIcon /> },
    ]
  }
];

const LayoutFrame: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedSections, setExpandedSections] = useState<{[key: string]: boolean}>(() => {
    // Initialize expanded state based on defaultExpanded property
    const initial: {[key: string]: boolean} = {};
    navSections.forEach(section => {
      initial[section.title] = section.defaultExpanded ?? false;
    });
    return initial;
  });
  const navigate = useNavigate();
  const location = useLocation();
  const { darkMode, toggleDarkMode } = useContext(ThemeContext);

  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('sm'));
  const isMobile = !isDesktop;

  const {
    panelContent,
    title,
    open: rightOpen,
    setOpen: setRightOpen,
    collapsed: rightCollapsed,
    setCollapsed: setRightCollapsed,
    clearPanelContent,
  } = useRightSidebar();

  const currentDrawerWidth = sidebarCollapsed ? collapsedDrawerWidth : drawerWidth;
  const isRightVisible = rightOpen && !!panelContent;
  const effectiveRightWidth = isRightVisible
    ? (rightCollapsed ? rightCollapsedDrawerWidth : rightDrawerWidth)
    : 0;

  useEffect(() => {
    if (!location.pathname.startsWith('/chat')) {
      // Only clear the panel content when leaving chat, but preserve open state
      clearPanelContent();
    }
    (document.activeElement as HTMLElement | null)?.blur?.();
    const escapeEvent = new KeyboardEvent('keydown', {
      key: 'Escape',
      code: 'Escape',
      keyCode: 27,
      which: 27,
      bubbles: true,
      cancelable: true
    });
    document.dispatchEvent(escapeEvent);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleSectionToggle = (sectionTitle: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionTitle]: !prev[sectionTitle]
    }));
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

  const renderNavigation = (isMobile: boolean = false) => (
    <CustomScrollbar style={{ height: isMobile ? 'calc(100vh - 128px)' : 'calc(100vh - 64px)' }}>
      <List sx={{ pt: 0 }}>
        {navSections.map((section) => (
          <React.Fragment key={section.title}>
            {/* Section Header */}
            {!sidebarCollapsed && (
              <ListSubheader
                component="div"
                sx={{
                  py: 1,
                  px: 2.5,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'text.secondary',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  lineHeight: 1.5,
                  bgcolor: 'transparent',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'action.hover',
                  }
                }}
                onClick={() => handleSectionToggle(section.title)}
              >
                {section.title}
                {section.items.length > 0 && (
                  expandedSections[section.title] ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />
                )}
              </ListSubheader>
            )}
            
            {/* Section Items */}
            <Collapse in={sidebarCollapsed || expandedSections[section.title]} timeout="auto" unmountOnExit>
              {section.items.map((item) => (
                <ListItem key={item.path} disablePadding>
                  <ListItemButton
                    selected={location.pathname === item.path}
                    onClick={() => {
                      navigate(item.path);
                      if (isMobile) {
                        handleDrawerToggle();
                      }
                    }}
                    sx={{
                      minHeight: 48,
                      justifyContent: sidebarCollapsed ? 'center' : 'initial',
                      px: sidebarCollapsed ? 2.5 : 3.5,
                      ml: sidebarCollapsed ? 0 : 1,
                      mr: sidebarCollapsed ? 0 : 1,
                      borderRadius: sidebarCollapsed ? 0 : 1,
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 0,
                        mr: sidebarCollapsed ? 'auto' : 2,
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
            </Collapse>
            
            {/* Add divider between sections, except for the last one */}
            {!sidebarCollapsed && navSections.indexOf(section) < navSections.length - 1 && (
              <Divider sx={{ my: 1, mx: 2 }} />
            )}
          </React.Fragment>
        ))}
      </List>
    </CustomScrollbar>
  );

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
      {renderNavigation()}

      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
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

  const rightDrawerContent = (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ justifyContent: 'space-between', borderBottom: '1px solid', borderColor: 'divider' }}>
        {!rightCollapsed && (
          <Typography variant="h6" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
            <SettingsIcon sx={{ mr: 1 }} />
            {title || 'Panel'}
          </Typography>
        )}
        <IconButton
          onClick={() => setRightCollapsed(!rightCollapsed)}
          size="small"
          sx={{ display: { xs: 'none', sm: 'inline-flex' } }}
          aria-label={rightCollapsed ? 'expand panel' : 'collapse panel'}
        >
          {rightCollapsed ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Toolbar>
      <CustomScrollbar style={{ flexGrow: 1 }}>
        <Box sx={{ p: rightCollapsed ? 1 : 2 }}>
          {panelContent ?? (
            <Typography variant="body2" color="text.secondary">
              No panel content
            </Typography>
          )}
        </Box>
      </CustomScrollbar>
    </div>
  );

  return (
    <Box sx={{ display: 'flex', height: '100dvh', overflow: 'hidden' }}>
      {/* LEFT NAV */}
      <Box component="nav" sx={{ width: { sm: currentDrawerWidth }, flexShrink: { sm: 0 } }}>
        {/* Mobile Left Drawer - mount only on mobile */}
        {isMobile && (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            hideBackdrop
            ModalProps={{
              keepMounted: false,
              disableEnforceFocus: true,
              disableAutoFocus: true,
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
                  <IconButton size="small" aria-label="account of current user" onClick={handleProfileMenuOpen}>
                    <Avatar sx={{ width: 24, height: 24 }}>U</Avatar>
                  </IconButton>
                  <IconButton onClick={handleDrawerToggle}>
                    <MenuIcon />
                  </IconButton>
                </Box>
              </Toolbar>
              <Divider />
              <CustomScrollbar style={{ height: 'calc(100vh - 128px)' }}>
                {renderNavigation(true)}
              </CustomScrollbar>

              {/* Profile Menu (mobile left) */}
              <Menu
                id="profile-menu"
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleProfileMenuClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
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
        )}

        {/* Desktop Left Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: currentDrawerWidth,
              transition: (theme) =>
                theme.transitions.create('width', {
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

      {/* MAIN CONTENT (scrolls instead of window) */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${currentDrawerWidth + effectiveRightWidth}px)` },
          minWidth: 0,
          minHeight: 0,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          transition: (theme) =>
            theme.transitions.create(['width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
        }}
      >
        <CustomScrollbar>
          <Outlet />
        </CustomScrollbar>
      </Box>

      {/* RIGHT NAV */}
      <Box component="nav" sx={{ width: { sm: effectiveRightWidth }, flexShrink: { sm: 0 } }}>
        {/* Mobile Right Drawer - mount/open only on mobile */}
        {isMobile && (
          <Drawer
            variant="temporary"
            anchor="right"
            open={isRightVisible}
            onClose={() => setRightOpen(false)}
            hideBackdrop
            ModalProps={{
              keepMounted: false,
              disableEnforceFocus: true,
              disableAutoFocus: true,
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: rightDrawerWidth },
            }}
          >
            {rightDrawerContent}
          </Drawer>
        )}

        {/* Desktop Right Drawer - use persistent (no modal/backdrop) */}
        <Drawer
          variant="persistent"
          anchor="right"
          open={isRightVisible}
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: effectiveRightWidth,
              transition: (theme) =>
                theme.transitions.create('width', {
                  easing: theme.transitions.easing.sharp,
                  duration: theme.transitions.duration.enteringScreen,
                }),
              overflowX: 'hidden',
              pointerEvents: 'auto',
            },
          }}
        >
          {rightDrawerContent}
        </Drawer>
      </Box>
    </Box>
  );
};

const Layout: React.FC = () => {
  return (
    <RightSidebarProvider>
      <LayoutFrame />
    </RightSidebarProvider>
  );
};

export default Layout;