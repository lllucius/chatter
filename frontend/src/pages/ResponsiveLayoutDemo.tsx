import React, { useState } from 'react';
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
  Card,
  CardContent,
  Grid,
  useTheme,
  useMediaQuery,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Tabs,
  Tab,
  AppBar,
  BottomNavigation,
  BottomNavigationAction,
  Paper,
  Button,
  Chip,
} from '@mui/material';
import {
  MenuIcon,
  DashboardIcon,
  ChatIcon,
  DocumentIcon,
  SettingsIcon,
  ProfileIcon,
  SearchIcon,
  ArrowBack,
} from '../utils/icons';
import {
  Home as HomeIcon,
  Close as CloseIcon,
  MoreVert,
  Visibility,
} from '@mui/icons-material';

// Design A: Collapsible sidebar with icon-only mode
const DesignACollapsibleSidebar: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));
  const [sidebarCollapsed, setSidebarCollapsed] = useState(isMobile || isTablet);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  const sidebarWidth = sidebarCollapsed ? 64 : 240;

  const navigationItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { label: 'Chat', icon: <ChatIcon />, path: '/chat' },
    { label: 'Documents', icon: <DocumentIcon />, path: '/documents' },
    { label: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  const sidebarContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }}>
        {!sidebarCollapsed && (
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Chatter
          </Typography>
        )}
        <Box sx={{ flexGrow: 1 }} />
        {!isMobile && (
          <IconButton onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
            <MenuIcon />
          </IconButton>
        )}
      </Toolbar>
      <List sx={{ flex: 1 }}>
        {navigationItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              sx={{
                minHeight: 48,
                px: 2.5,
                justifyContent: sidebarCollapsed ? 'center' : 'initial',
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: sidebarCollapsed ? 0 : 3,
                  justifyContent: 'center',
                }}
              >
                {item.icon}
              </ListItemIcon>
              {!sidebarCollapsed && <ListItemText primary={item.label} />}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Mobile Navigation */}
      {isMobile ? (
        <>
          <Drawer
            variant="temporary"
            open={mobileDrawerOpen}
            onClose={() => setMobileDrawerOpen(false)}
            sx={{
              '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box' },
            }}
          >
            {sidebarContent}
          </Drawer>
          <Box sx={{ position: 'fixed', top: 16, left: 16, zIndex: 1200 }}>
            <IconButton
              onClick={() => setMobileDrawerOpen(true)}
              sx={{ bgcolor: 'background.paper', boxShadow: 2 }}
            >
              <MenuIcon />
            </IconButton>
          </Box>
        </>
      ) : (
        /* Desktop Sidebar */
        <Drawer
          variant="permanent"
          sx={{
            width: sidebarWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: sidebarWidth,
              boxSizing: 'border-box',
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
            },
          }}
        >
          {sidebarContent}
        </Drawer>
      )}

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${isMobile ? 0 : sidebarWidth}px)` },
          ml: { sm: isMobile ? 0 : `${sidebarWidth}px` },
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Box sx={{ mb: 2 }}>
          <Button startIcon={<ArrowBack />} onClick={onBack} sx={{ mb: 2 }}>
            Back to Design Overview
          </Button>
        </Box>
        
        <Typography variant="h4" gutterBottom>
          Design A: Collapsible Sidebar
        </Typography>
        <Typography variant="body1" paragraph>
          Features: Sidebar collapses to icon-only mode on tablets, switches to drawer on mobile.
          Provides smooth transitions and maintains easy access to navigation.
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Chip label={`Current mode: ${isMobile ? 'Mobile Drawer' : sidebarCollapsed ? 'Icon Only' : 'Full Sidebar'}`} 
                color="primary" sx={{ mr: 1 }} />
          <Chip label={`Sidebar width: ${isMobile ? '0' : sidebarWidth}px`} variant="outlined" />
        </Box>
        
        {/* Sample Content Grid */}
        <Grid container spacing={3}>
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={item}>
              <Card>
                <CardContent>
                  <Typography variant="h6">Card {item}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Sample content that adapts to different screen sizes and sidebar states.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
};

// Design B: Tab-based navigation for mobile
const DesignBTabNavigation: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [currentTab, setCurrentTab] = useState(0);

  const tabs = [
    { label: 'Dashboard', icon: <DashboardIcon /> },
    { label: 'Chat', icon: <ChatIcon /> },
    { label: 'Documents', icon: <DocumentIcon /> },
    { label: 'Settings', icon: <SettingsIcon /> },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Top App Bar */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <IconButton color="inherit" onClick={onBack} sx={{ mr: 1 }}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Chatter
          </Typography>
        </Toolbar>
        {isMobile && (
          <Tabs
            value={currentTab}
            onChange={(_, newValue) => setCurrentTab(newValue)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ bgcolor: 'primary.dark' }}
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                icon={tab.icon}
                label={tab.label}
                iconPosition="start"
                sx={{ minWidth: 120 }}
              />
            ))}
          </Tabs>
        )}
      </AppBar>

      <Box sx={{ display: 'flex', flex: 1 }}>
        {/* Desktop Sidebar */}
        {!isMobile && (
          <Drawer
            variant="permanent"
            sx={{
              width: 240,
              flexShrink: 0,
              '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box' },
            }}
          >
            <List>
              {tabs.map((tab, index) => (
                <ListItem key={index} disablePadding>
                  <ListItemButton
                    selected={currentTab === index}
                    onClick={() => setCurrentTab(index)}
                  >
                    <ListItemIcon>{tab.icon}</ListItemIcon>
                    <ListItemText primary={tab.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Drawer>
        )}

        {/* Main Content */}
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Typography variant="h4" gutterBottom>
            Design B: Tab-Based Navigation
          </Typography>
          <Typography variant="body1" paragraph>
            Features: Horizontal scrollable tabs for mobile, traditional sidebar for desktop.
            Maximizes content space by moving navigation to the top on mobile.
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Chip label={`Current tab: ${tabs[currentTab]?.label}`} color="primary" sx={{ mr: 1 }} />
            <Chip label={`Layout: ${isMobile ? 'Mobile Tabs' : 'Desktop Sidebar'}`} variant="outlined" />
          </Box>
          
          {/* Sample Content */}
          <Grid container spacing={2}>
            {[1, 2, 3, 4, 5, 6].map((item) => (
              <Grid item xs={12} sm={6} lg={4} key={item}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{tabs[currentTab]?.label} Item {item}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Content specifically for the {tabs[currentTab]?.label} section.
                      This layout provides maximum content width on mobile devices.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Box>
    </Box>
  );
};

// Design C: Floating Action Panel System
const DesignCFloatingPanels: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [speedDialOpen, setSpeedDialOpen] = useState(false);

  const actions = [
    { icon: <DashboardIcon />, name: 'Dashboard' },
    { icon: <ChatIcon />, name: 'Chat' },
    { icon: <DocumentIcon />, name: 'Documents' },
    { icon: <SettingsIcon />, name: 'Settings' },
  ];

  return (
    <Box sx={{ height: '100vh', position: 'relative' }}>
      {/* Full-width content area */}
      <Box sx={{ p: 3, height: '100%', overflow: 'auto', pt: 10 }}>
        <Typography variant="h4" gutterBottom>
          Design C: Floating Action Panels
        </Typography>
        <Typography variant="body1" paragraph>
          Features: Maximizes content space with floating navigation. Quick access toolbar
          at the top and expandable speed dial for additional actions.
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Chip label="Full-width layout" color="primary" sx={{ mr: 1 }} />
          <Chip label="Floating navigation" variant="outlined" sx={{ mr: 1 }} />
          <Chip label="Space efficient" variant="outlined" />
        </Box>

        {/* Sample Content Grid - More space efficient */}
        <Grid container spacing={2}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((item) => (
            <Grid item xs={12} sm={6} md={4} lg={3} xl={2} key={item}>
              <Card sx={{ height: 200 }}>
                <CardContent>
                  <Typography variant="h6">Item {item}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Full-width layout allows for more efficient use of available space,
                    showing more content without sacrificing usability.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Floating Navigation */}
      <SpeedDial
        ariaLabel="Navigation"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon openIcon={<CloseIcon />} />}
        open={speedDialOpen}
        onOpen={() => setSpeedDialOpen(true)}
        onClose={() => setSpeedDialOpen(false)}
      >
        {actions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={() => setSpeedDialOpen(false)}
          />
        ))}
      </SpeedDial>

      {/* Quick Access Toolbar */}
      <Paper
        elevation={3}
        sx={{
          position: 'fixed',
          top: 16,
          left: 16,
          right: 16,
          p: 1,
          display: 'flex',
          gap: 1,
          alignItems: 'center',
          zIndex: 1100,
        }}
      >
        <IconButton onClick={onBack} size="small">
          <ArrowBack />
        </IconButton>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mr: 2 }}>
          Chatter
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        {!isMobile && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            {actions.map((action, index) => (
              <IconButton key={index} size="small">
                {action.icon}
              </IconButton>
            ))}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

// Design D: Stackable layout with priority-based content ordering
const DesignDStackableLayout: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [bottomNavValue, setBottomNavValue] = useState(0);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Compact Header */}
      <AppBar position="static" elevation={1} sx={{ height: 56 }}>
        <Toolbar variant="dense">
          <IconButton color="inherit" onClick={onBack} sx={{ mr: 1 }}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Chatter
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton color="inherit" size="small">
                <DashboardIcon />
              </IconButton>
              <IconButton color="inherit" size="small">
                <ChatIcon />
              </IconButton>
              <IconButton color="inherit" size="small">
                <DocumentIcon />
              </IconButton>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Stackable Content Areas */}
      <Box sx={{ flex: 1, overflow: 'auto', p: { xs: 1, sm: 2 } }}>
        <Typography variant="h4" gutterBottom>
          Design D: Stackable Priority Layout
        </Typography>
        <Typography variant="body1" paragraph>
          Features: Content stacks vertically with priority-based ordering.
          Secondary content is hidden on mobile to prioritize essential information.
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Chip label="Priority-based" color="primary" sx={{ mr: 1 }} />
          <Chip label="Adaptive hiding" variant="outlined" sx={{ mr: 1 }} />
          <Chip label={`${isMobile ? 'Mobile stack' : 'Desktop grid'}`} variant="outlined" />
        </Box>

        {/* Priority Content Sections */}
        <Grid container spacing={1}>
          {/* High Priority - Always visible */}
          <Grid item xs={12}>
            <Card sx={{ bgcolor: 'primary.light', color: 'primary.contrastText' }}>
              <CardContent>
                <Typography variant="h6">🔥 High Priority Content</Typography>
                <Typography variant="body2">
                  Always visible and gets priority placement on small screens.
                  This content is considered essential for all users.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Medium Priority - Responsive layout */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6">📱 Main Content Area</Typography>
                <Grid container spacing={1}>
                  {[1, 2, 3, 4].map((item) => (
                    <Grid item xs={12} sm={6} lg={3} key={item}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle1">Item {item}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            Responsive content that adapts to available space
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Low Priority - Hidden on small screens */}
          <Grid item xs={12} md={4} sx={{ display: { xs: 'none', md: 'block' } }}>
            <Card>
              <CardContent>
                <Typography variant="h6">👻 Secondary Panel</Typography>
                <Typography variant="body2" color="text.secondary">
                  This panel is hidden on mobile devices to maximize space for primary content.
                  It reappears on larger screens where space allows.
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" display="block">
                    💡 Try resizing your browser to see this panel disappear on smaller screens!
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <BottomNavigation
          value={bottomNavValue}
          onChange={(_, newValue) => setBottomNavValue(newValue)}
          sx={{ borderTop: 1, borderColor: 'divider' }}
        >
          <BottomNavigationAction label="Home" icon={<HomeIcon />} />
          <BottomNavigationAction label="Chat" icon={<ChatIcon />} />
          <BottomNavigationAction label="Search" icon={<SearchIcon />} />
          <BottomNavigationAction label="Profile" icon={<ProfileIcon />} />
        </BottomNavigation>
      )}
    </Box>
  );
};

// Main Demo Page
const ResponsiveLayoutDemo: React.FC = () => {
  const [currentDesign, setCurrentDesign] = useState<string | null>(null);

  const designs = [
    {
      id: 'collapsible',
      title: 'Design A: Collapsible Sidebar',
      description: 'Traditional sidebar that collapses to icons on smaller screens and becomes a drawer on mobile.',
      pros: ['Familiar UX pattern', 'Smooth transitions', 'Icon-only mode saves space'],
      cons: ['Still takes sidebar space', 'Mobile drawer covers content'],
      component: DesignACollapsibleSidebar,
    },
    {
      id: 'tabs',
      title: 'Design B: Tab Navigation',
      description: 'Horizontal tabs for mobile navigation, traditional sidebar for desktop.',
      pros: ['Maximizes content width', 'Clear section separation', 'Mobile-optimized'],
      cons: ['Navigation takes vertical space', 'Tab overflow on small screens'],
      component: DesignBTabNavigation,
    },
    {
      id: 'floating',
      title: 'Design C: Floating Panels',
      description: 'Full-width content with floating navigation and quick access toolbar.',
      pros: ['Maximum content space', 'Modern floating UI', 'Scalable navigation'],
      cons: ['Navigation can be hidden', 'Requires more user interaction'],
      component: DesignCFloatingPanels,
    },
    {
      id: 'stackable',
      title: 'Design D: Priority Stack',
      description: 'Content stacks by priority, hiding secondary content on mobile.',
      pros: ['Content-first approach', 'Intelligent hiding', 'Bottom nav for mobile'],
      cons: ['Some content becomes inaccessible', 'Requires content prioritization'],
      component: DesignDStackableLayout,
    },
  ];

  if (currentDesign) {
    const design = designs.find(d => d.id === currentDesign);
    const Component = design?.component;
    return Component ? <Component onBack={() => setCurrentDesign(null)} /> : null;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
        Responsive Layout Design Options
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph>
        Four different approaches to improve the layout for smaller screens and non-fixed browser windows.
        Click "Preview" to see each design in action.
      </Typography>

      <Grid container spacing={3}>
        {designs.map((design) => (
          <Grid item xs={12} md={6} key={design.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h5" gutterBottom>
                  {design.title}
                </Typography>
                <Typography variant="body1" paragraph>
                  {design.description}
                </Typography>
                
                <Typography variant="h6" color="success.main" gutterBottom>
                  ✅ Advantages:
                </Typography>
                <Box component="ul" sx={{ ml: 2, mb: 2 }}>
                  {design.pros.map((pro, index) => (
                    <Typography component="li" variant="body2" key={index}>
                      {pro}
                    </Typography>
                  ))}
                </Box>

                <Typography variant="h6" color="warning.main" gutterBottom>
                  ⚠️ Trade-offs:
                </Typography>
                <Box component="ul" sx={{ ml: 2 }}>
                  {design.cons.map((con, index) => (
                    <Typography component="li" variant="body2" key={index}>
                      {con}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
              
              <Box sx={{ p: 2, pt: 0 }}>
                <Button
                  variant="contained"
                  startIcon={<Visibility />}
                  onClick={() => setCurrentDesign(design.id)}
                  fullWidth
                >
                  Preview Design
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ mt: 4, p: 3, bgcolor: 'info.light' }}>
        <Typography variant="h6" gutterBottom>
          📱 Testing Instructions
        </Typography>
        <Typography variant="body1">
          To properly evaluate these designs:
          <br />
          1. <strong>Resize your browser window</strong> to different widths (360px, 768px, 1024px, 1440px+)
          <br />
          2. <strong>Use browser dev tools</strong> to simulate mobile devices
          <br />
          3. <strong>Consider your content needs</strong> - which layout works best for your typical use cases?
          <br />
          4. <strong>Test interactions</strong> - try navigating and using features in each design
        </Typography>
      </Paper>
    </Box>
  );
};

export default ResponsiveLayoutDemo;