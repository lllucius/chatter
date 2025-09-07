import React from 'react';
import { List } from '@mui/material';
import CustomScrollbar from '../CustomScrollbar';
import NavigationSection from './NavigationSection';
import { navSections } from '../../config/navigation';

interface NavigationProps {
  sidebarCollapsed: boolean;
  isMobile?: boolean;
  onMobileNavigate?: () => void;
  expandedSections: { [key: string]: boolean };
  onSectionToggle: (sectionTitle: string) => void;
  style?: React.CSSProperties;
}

const Navigation: React.FC<NavigationProps> = ({
  sidebarCollapsed,
  isMobile = false,
  onMobileNavigate,
  expandedSections,
  onSectionToggle,
  style,
}) => {
  return (
    <CustomScrollbar style={style}>
      <List sx={{ pt: 0 }}>
        {navSections.map((section, index) => (
          <NavigationSection
            key={section.title}
            section={section}
            isExpanded={expandedSections[section.title]}
            onToggleExpand={() => onSectionToggle(section.title)}
            sidebarCollapsed={sidebarCollapsed}
            isMobile={isMobile}
            onMobileNavigate={onMobileNavigate}
            isLastSection={index === navSections.length - 1}
          />
        ))}
      </List>
    </CustomScrollbar>
  );
};

export default Navigation;