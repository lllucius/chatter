import React from 'react';
import { Box, Toolbar, Typography, IconButton } from '@mui/material';
import { Settings as SettingsIcon, ChevronLeft as ChevronLeftIcon, ChevronRight as ChevronRightIcon } from '@mui/icons-material';
import CustomScrollbar from '../CustomScrollbar';

interface RightSidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  title: string;
  children: React.ReactNode;
}

const RightSidebar: React.FC<RightSidebarProps> = ({
  collapsed,
  onToggleCollapse,
  title,
  children,
}) => {
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ justifyContent: 'space-between', borderBottom: '1px solid', borderColor: 'divider' }}>
        {!collapsed && (
          <Typography variant="h6" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
            <SettingsIcon sx={{ mr: 1 }} />
            {title || 'Panel'}
          </Typography>
        )}
        <IconButton
          onClick={onToggleCollapse}
          size="small"
          sx={{ display: { xs: 'none', sm: 'inline-flex' } }}
          aria-label={collapsed ? 'expand panel' : 'collapse panel'}
        >
          {collapsed ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Toolbar>
      <CustomScrollbar style={{ flexGrow: 1 }}>
        <Box sx={{ p: collapsed ? 1 : 2 }}>
          {children}
        </Box>
      </CustomScrollbar>
    </Box>
  );
};

export default RightSidebar;