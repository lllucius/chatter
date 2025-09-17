import React from 'react';
import { Box, SxProps, Theme } from '@mui/material';

/**
 * Custom TabPanel component that consolidates the tab panel pattern
 * used across multiple pages in the application
 */

export interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
  idPrefix?: string;
  sx?: SxProps<Theme>;
}

export const TabPanel: React.FC<TabPanelProps> = ({
  children,
  value,
  index,
  idPrefix = 'simple',
  sx,
  ...other
}) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`${idPrefix}-tabpanel-${index}`}
      aria-labelledby={`${idPrefix}-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3, ...sx }}>{children}</Box>}
    </div>
  );
};
