import React from 'react';
import PageLayout from '../components/PageLayout';
import IntegratedDashboard from '../components/IntegratedDashboard';
import { Button } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

const NewDashboardPage: React.FC = () => {
  const toolbar = (
    <Button
      variant="outlined"
      startIcon={<RefreshIcon />}
      onClick={() => window.location.reload()}
      size="small"
    >
      Refresh
    </Button>
  );

  return (
    <PageLayout title="Dashboard" toolbar={toolbar}>
      <IntegratedDashboard />
    </PageLayout>
  );
};

export default NewDashboardPage;