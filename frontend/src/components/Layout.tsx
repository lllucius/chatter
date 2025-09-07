import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Box, Drawer, useTheme, useMediaQuery } from '@mui/material';
import { RightSidebarProvider, useRightSidebar } from './RightSidebarContext';
import DrawerContent from './layout/DrawerContent';
import RightSidebar from './layout/RightSidebar';
import { navSections } from '../config/navigation';

// Layout constants
const DRAWER_WIDTH = 240;
const COLLAPSED_DRAWER_WIDTH = 64;
const RIGHT_DRAWER_WIDTH = 300;
const RIGHT_COLLAPSED_DRAWER_WIDTH = 64;

const LayoutFrame: React.FC = () => {
  // State management
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>(() => {
    const initial: { [key: string]: boolean } = {};
    navSections.forEach(section => {
      initial[section.title] = section.defaultExpanded ?? false;
    });
    return initial;
  });

  // Hooks
  const location = useLocation();
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

  // Computed values
  const currentDrawerWidth = sidebarCollapsed ? COLLAPSED_DRAWER_WIDTH : DRAWER_WIDTH;
  const isRightVisible = !!panelContent;
  const effectiveRightWidth = isRightVisible
    ? (rightCollapsed ? RIGHT_COLLAPSED_DRAWER_WIDTH : RIGHT_DRAWER_WIDTH)
    : 0;

  // Effects
  useEffect(() => {
    if (!location.pathname.startsWith('/chat')) {
      clearPanelContent();
    }
    // Blur active element and dispatch escape event
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
  }, [location.pathname, clearPanelContent]);

  // Event handlers
  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);
  const handleSidebarToggle = () => setSidebarCollapsed(!sidebarCollapsed);
  const handleSectionToggle = (sectionTitle: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionTitle]: !prev[sectionTitle]
    }));
  };
  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => setAnchorEl(event.currentTarget);
  const handleProfileMenuClose = () => setAnchorEl(null);

  // Common drawer content props
  const drawerContentProps = {
    collapsed: sidebarCollapsed,
    onToggleCollapse: handleSidebarToggle,
    expandedSections,
    onSectionToggle: handleSectionToggle,
    anchorEl,
    onProfileMenuOpen: handleProfileMenuOpen,
    onProfileMenuClose: handleProfileMenuClose,
  };

  return (
    <Box sx={{ display: 'flex', height: '100dvh', overflow: 'hidden' }}>
      {/* LEFT SIDEBAR */}
      <Box component="nav" sx={{ width: { sm: currentDrawerWidth }, flexShrink: { sm: 0 } }}>
        {/* Mobile Drawer */}
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
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
            }}
          >
            <DrawerContent
              {...drawerContentProps}
              showCollapseButton={false}
              showMenuButton={true}
              onMenuToggle={handleDrawerToggle}
              isMobile={true}
              onMobileNavigate={handleDrawerToggle}
              navigationStyle={{ height: 'calc(100vh - 128px)' }}
            />
          </Drawer>
        )}

        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: currentDrawerWidth,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
            },
          }}
        >
          <DrawerContent
            {...drawerContentProps}
            navigationStyle={{ height: 'calc(100vh - 64px)' }}
          />
        </Drawer>
      </Box>

      {/* MAIN CONTENT */}
      <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Mobile Menu Button */}
        {isMobile && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 1 }}>
            {/* Add mobile menu button here if needed */}
          </Box>
        )}
        
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          <Outlet />
        </Box>
      </Box>

      {/* RIGHT SIDEBAR */}
      <Box component="nav" sx={{ width: { sm: effectiveRightWidth }, flexShrink: { sm: 0 } }}>
        {/* Mobile Right Drawer */}
        {isMobile && isRightVisible && (
          <Drawer
            variant="temporary"
            anchor="right"
            open={rightOpen}
            onClose={() => setRightOpen(false)}
            hideBackdrop
            ModalProps={{
              keepMounted: false,
              disableEnforceFocus: true,
              disableAutoFocus: true,
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: RIGHT_DRAWER_WIDTH },
            }}
          >
            <RightSidebar
              collapsed={rightCollapsed}
              onToggleCollapse={() => setRightCollapsed(!rightCollapsed)}
              title={title}
            >
              {panelContent}
            </RightSidebar>
          </Drawer>
        )}

        {/* Desktop Right Drawer */}
        <Drawer
          variant="persistent"
          anchor="right"
          open={isRightVisible}
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: effectiveRightWidth,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflow: 'hidden',
              pointerEvents: 'auto',
            },
          }}
        >
          <RightSidebar
            collapsed={rightCollapsed}
            onToggleCollapse={() => setRightCollapsed(!rightCollapsed)}
            title={title}
          >
            {panelContent}
          </RightSidebar>
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