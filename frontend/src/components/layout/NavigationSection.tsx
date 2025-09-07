import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  ListSubheader,
  Divider,
  Tooltip,
} from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { NavSection } from '../../config/navigation';

interface NavigationSectionProps {
  section: NavSection;
  isExpanded: boolean;
  onToggleExpand: () => void;
  sidebarCollapsed: boolean;
  isMobile?: boolean;
  onMobileNavigate?: () => void;
  isLastSection?: boolean;
}

const NavigationSection: React.FC<NavigationSectionProps> = ({
  section,
  isExpanded,
  onToggleExpand,
  sidebarCollapsed,
  isMobile = false,
  onMobileNavigate,
  isLastSection = false,
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleItemClick = (path: string) => {
    navigate(path);
    if (isMobile && onMobileNavigate) {
      onMobileNavigate();
    }
  };

  return (
    <React.Fragment>
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
          onClick={onToggleExpand}
        >
          {section.title}
          {section.items.length > 0 && (
            isExpanded ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />
          )}
        </ListSubheader>
      )}
      
      {/* Section Items */}
      <Collapse in={sidebarCollapsed || isExpanded} timeout="auto" unmountOnExit>
        {section.items.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleItemClick(item.path)}
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
      
      {/* Divider between sections */}
      {!sidebarCollapsed && !isLastSection && (
        <Divider sx={{ my: 1, mx: 2 }} />
      )}
    </React.Fragment>
  );
};

export default NavigationSection;