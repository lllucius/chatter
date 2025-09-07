import React from 'react';
import { Box, Divider } from '@mui/material';
import SidebarHeader from './SidebarHeader';
import Navigation from './Navigation';

interface DrawerContentProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  showCollapseButton?: boolean;
  showMenuButton?: boolean;
  onMenuToggle?: () => void;
  isMobile?: boolean;
  onMobileNavigate?: () => void;
  expandedSections: { [key: string]: boolean };
  onSectionToggle: (sectionTitle: string) => void;
  anchorEl: HTMLElement | null;
  onProfileMenuOpen: (event: React.MouseEvent<HTMLElement>) => void;
  onProfileMenuClose: () => void;
  navigationStyle?: React.CSSProperties;
}

const DrawerContent: React.FC<DrawerContentProps> = ({
  collapsed,
  onToggleCollapse,
  showCollapseButton = true,
  showMenuButton = false,
  onMenuToggle,
  isMobile = false,
  onMobileNavigate,
  expandedSections,
  onSectionToggle,
  anchorEl,
  onProfileMenuOpen,
  onProfileMenuClose,
  navigationStyle,
}) => {
  return (
    <Box>
      <SidebarHeader
        collapsed={collapsed}
        onToggleCollapse={onToggleCollapse}
        showCollapseButton={showCollapseButton}
        showMenuButton={showMenuButton}
        onMenuToggle={onMenuToggle}
        anchorEl={anchorEl}
        onProfileMenuOpen={onProfileMenuOpen}
        onProfileMenuClose={onProfileMenuClose}
      />
      <Divider />
      <Navigation
        sidebarCollapsed={collapsed}
        isMobile={isMobile}
        onMobileNavigate={onMobileNavigate}
        expandedSections={expandedSections}
        onSectionToggle={onSectionToggle}
        style={navigationStyle}
      />
    </Box>
  );
};

export default DrawerContent;