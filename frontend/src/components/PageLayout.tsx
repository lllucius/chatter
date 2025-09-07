import React from 'react';
import { Box, Typography, Toolbar } from '@mui/material';
import CustomScrollbar from './CustomScrollbar';

interface PageLayoutProps {
  title: string;
  toolbar?: React.ReactNode;
  children: React.ReactNode;
  fixedBottom?: React.ReactNode;
  maxWidth?: string | number;
}

const PageLayout: React.FC<PageLayoutProps> = ({ 
  title, 
  toolbar, 
  children, 
  fixedBottom,
  maxWidth = 'none'
}) => {
  return (
    <Box 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        maxWidth,
        margin: '0 auto',
        width: '100%'
      }}
    >
      {/* Fixed Title Bar */}
      <Box
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper',
          position: 'sticky',
          top: 0,
          zIndex: 1,
        }}
      >
        <Toolbar 
          sx={{ 
            justifyContent: 'space-between',
            minHeight: { xs: 56, sm: 64 },
            px: { xs: 2, sm: 3 }
          }}
        >
          <Typography 
            variant="h4" 
            component="h1" 
            sx={{ 
              fontWeight: 'bold',
              fontSize: { xs: '1.5rem', sm: '2rem' }
            }}
          >
            {title}
          </Typography>
          {toolbar && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {toolbar}
            </Box>
          )}
        </Toolbar>
      </Box>

      {/* Scrollable Content Area */}
      <Box 
        sx={{ 
          flex: 1, 
          minHeight: 0, 
          display: 'flex', 
          flexDirection: 'column',
          position: 'relative'
        }}
      >
        <CustomScrollbar style={{ flex: 1 }}>
          <Box sx={{ p: { xs: 2, sm: 3 } }}>
            {children}
          </Box>
        </CustomScrollbar>
      </Box>

      {/* Fixed Bottom Area */}
      {fixedBottom && (
        <Box
          sx={{
            borderTop: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
            position: 'sticky',
            bottom: 0,
            zIndex: 1,
          }}
        >
          {fixedBottom}
        </Box>
      )}
    </Box>
  );
};

export default PageLayout;