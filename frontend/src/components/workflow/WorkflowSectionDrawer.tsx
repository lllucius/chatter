import React, { useState } from 'react';
import { Node } from '@xyflow/react';
import {
  Box,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography,
  Collapse,
  Drawer,
  Toolbar,
} from '@mui/material';
import {
  Settings as PropertiesIcon,
  Assessment as AnalyticsIcon,
  ExpandLess,
  ExpandMore,
  ChevronLeft,
  ChevronRight,
} from '@mui/icons-material';
import PropertiesPanel from './PropertiesPanel';
import WorkflowAnalytics from './WorkflowAnalytics';
import { WorkflowDefinition, WorkflowNodeData } from './WorkflowEditor';

interface WorkflowSectionDrawerProps {
  open: boolean;
  collapsed: boolean;
  onToggleCollapsed: () => void;
  selectedNode: Node<WorkflowNodeData> | null;
  currentWorkflow: WorkflowDefinition;
  onNodeUpdate: (nodeId: string, data: Partial<WorkflowNodeData>) => void;
  width: number;
  collapsedWidth: number;
}

const WorkflowSectionDrawer: React.FC<WorkflowSectionDrawerProps> = ({
  open,
  collapsed,
  onToggleCollapsed,
  selectedNode,
  currentWorkflow,
  onNodeUpdate,
  width,
  collapsedWidth,
}) => {
  const [propertiesExpanded, setPropertiesExpanded] = useState(true);
  const [analyticsExpanded, setAnalyticsExpanded] = useState(false);

  const currentWidth = collapsed ? collapsedWidth : width;

  const sectionContent = () => {
    if (collapsed) {
      return (
        <Box sx={{ p: 1, display: 'flex', flexDirection: 'column', gap: 1 }}>
          <IconButton
            onClick={() => {
              setPropertiesExpanded(!propertiesExpanded);
              if (collapsed) {
                onToggleCollapsed(); // Expand first, then show section
              }
            }}
            size="small"
            sx={{
              color: selectedNode ? 'primary.main' : 'text.secondary',
            }}
          >
            <PropertiesIcon />
          </IconButton>
          <IconButton
            onClick={() => {
              setAnalyticsExpanded(!analyticsExpanded);
              if (collapsed) {
                onToggleCollapsed(); // Expand first, then show section
              }
            }}
            size="small"
          >
            <AnalyticsIcon />
          </IconButton>
        </Box>
      );
    }

    return (
      <>
        <List disablePadding>
          {/* Properties Section */}
          <ListItem disablePadding>
            <ListItemButton
              onClick={() => setPropertiesExpanded(!propertiesExpanded)}
              sx={{ py: 1 }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <PropertiesIcon color={selectedNode ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText
                primary="Properties"
                primaryTypographyProps={{
                  variant: 'subtitle2',
                  fontWeight: selectedNode ? 'bold' : 'normal',
                }}
              />
              {propertiesExpanded ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>
          <Collapse in={propertiesExpanded} timeout="auto">
            <Box sx={{ px: 1, pb: 1 }}>
              {selectedNode ? (
                <PropertiesPanel
                  selectedNode={selectedNode}
                  onNodeUpdate={onNodeUpdate}
                  onClose={() => {}} // No close action needed in sectioned drawer
                />
              ) : (
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Select a node to view properties
                  </Typography>
                </Box>
              )}
            </Box>
          </Collapse>

          <Divider />

          {/* Analytics Section */}
          <ListItem disablePadding>
            <ListItemButton
              onClick={() => setAnalyticsExpanded(!analyticsExpanded)}
              sx={{ py: 1 }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <AnalyticsIcon />
              </ListItemIcon>
              <ListItemText
                primary="Analytics"
                primaryTypographyProps={{ variant: 'subtitle2' }}
              />
              {analyticsExpanded ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
          </ListItem>
          <Collapse in={analyticsExpanded} timeout="auto">
            <Box sx={{ px: 1, pb: 1 }}>
              <WorkflowAnalytics workflow={currentWorkflow} />
            </Box>
          </Collapse>
        </List>
      </>
    );
  };

  const drawerContent = (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar
        sx={{
          justifyContent: 'space-between',
          borderBottom: '1px solid',
          borderColor: 'divider',
          minHeight: { xs: 56, sm: 64 }, // Match PageLayout
          px: { xs: 2, sm: 3 }, // Match PageLayout
        }}
      >
        {!collapsed && (
          <Typography
            variant="h6"
            sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center' }}
          >
            Workflow Tools
          </Typography>
        )}
        <IconButton
          onClick={onToggleCollapsed}
          size="small"
          aria-label={collapsed ? 'expand panel' : 'collapse panel'}
        >
          {collapsed ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Toolbar>
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>{sectionContent()}</Box>
    </div>
  );

  return (
    <Drawer
      variant="persistent"
      anchor="right"
      open={open}
      sx={{
        '& .MuiDrawer-paper': {
          boxSizing: 'border-box',
          width: currentWidth,
          transition: (theme) =>
            theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          overflow: 'hidden',
          // Ensure the drawer doesn't interfere with toolbar menus
          zIndex: (theme) => theme.zIndex.drawer - 1,
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default WorkflowSectionDrawer;
