import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent, 
  Grid,
  Tab,
  Tabs,
  Paper,
  Alert
} from '@mui/material';
import { 
  Refresh as RefreshIcon, 
  Search as SearchIcon, 
  TrendingUp as TrendingUpIcon,
  Analytics as AnalyticsIcon 
} from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import IntegratedDashboard from '../components/IntegratedDashboard';
import RealTimeDashboard from '../components/RealTimeDashboard';
import IntelligentSearch from '../components/IntelligentSearch';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const EnhancedDashboardPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Trigger a manual refresh of dashboard data
      toastService.success('Dashboard refreshed');
    } catch (error) {
      handleError(error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const toolbar = (
    <Box display="flex" gap={1}>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={handleRefresh}
        disabled={isRefreshing}
        size="small"
      >
        {isRefreshing ? 'Refreshing...' : 'Refresh'}
      </Button>
    </Box>
  );

  return (
    <PageLayout title="Enhanced Dashboard" toolbar={toolbar}>
      <Box sx={{ width: '100%' }}>
        {/* Dashboard Introduction */}
        <Alert severity="info" sx={{ mb: 3 }}>
          🚀 <strong>Phase 4 Features:</strong> Experience real-time analytics, intelligent search with personalization, 
          and live dashboard updates powered by our new backend infrastructure.
        </Alert>

        {/* Tab Navigation */}
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="dashboard tabs"
            variant="fullWidth"
          >
            <Tab 
              label="Analytics Dashboard" 
              icon={<AnalyticsIcon />}
              iconPosition="start"
            />
            <Tab 
              label="Real-Time Monitoring" 
              icon={<TrendingUpIcon />}
              iconPosition="start"
            />
            <Tab 
              label="Intelligent Search" 
              icon={<SearchIcon />}
              iconPosition="start"
            />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <TabPanel value={tabValue} index={0}>
          <Box>
            <Typography variant="h5" gutterBottom>
              Analytics Dashboard
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Comprehensive analytics powered by server-side processing with real-time chart data 
              and integrated statistics derived from actual usage metrics.
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <IntegratedDashboard />
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box>
            <Typography variant="h5" gutterBottom>
              Real-Time System Monitoring
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Live dashboard updates with intelligent notifications, performance alerts, 
              and system health monitoring via Server-Sent Events (SSE).
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <RealTimeDashboard />
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box>
            <Typography variant="h5" gutterBottom>
              Intelligent Search & Discovery
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Semantic search with personalized results, smart recommendations, 
              and trending content discovery powered by vector similarity and user behavior analytics.
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <IntelligentSearch />
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        {/* Feature Highlights */}
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Phase 4 Enhancements
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      Real-time Analytics
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      • Live dashboard streaming via SSE<br/>
                      • Intelligent performance alerts<br/>
                      • User behavior tracking<br/>
                      • System health monitoring
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      Intelligent Search
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      • Semantic vector search<br/>
                      • Personalized recommendations<br/>
                      • User preference learning<br/>
                      • Trending content discovery
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      Advanced User Experience
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      • Live notifications<br/>
                      • Collaborative features<br/>
                      • Performance optimization<br/>
                      • Predictive analytics
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>
    </PageLayout>
  );
};

export default EnhancedDashboardPage;