import React, { useState } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  TabPanel,
  Chip,
} from '../utils/mui';
import { AddIcon, RefreshIcon, TrendingUpIcon } from '../utils/icons';
import PageLayout from '../components/PageLayout';
import ABTestTable from '../components/abtesting/ABTestTable';
import ABTestOverviewTab from '../components/abtesting/ABTestOverviewTab';
import ABTestAnalytics from '../components/ABTestAnalytics';
import { useABTestingData, TestStatus } from '../hooks/useABTestingData';
import { useFormGeneric } from '../hooks/useFormGeneric';
import { toastService } from '../services/toast-service';
import { format } from 'date-fns';
import {
  ABTestCreateRequest,
  MetricType,
  TestType,
  TestVariant,
  VariantAllocation,
} from 'chatter-sdk';

// Extend ABTestCreateRequest for form data
interface ABTestFormData extends ABTestCreateRequest {
  [key: string]: unknown;
}

const ABTestingPage: React.FC = () => {
  const {
    tests,
    loading,
    saving,
    selectedTest,
    testMetrics,
    testResults,
    testPerformance,
    testRecommendations,
    setSelectedTest,
    loadTests,
    createTest,
    updateTest,
    deleteTest,
    startTest,
    stopTest,
  } = useABTestingData();

  // UI state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [editingTest, setEditingTest] = useState<any>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [menuAnchorEl, setMenuAnchorEl] = useState<HTMLElement | null>(null);
  const [selectedTestForMenu, setSelectedTestForMenu] = useState<any>(null);

  // Form management
  const form = useFormGeneric<ABTestFormData>({
    initialValues: {
      name: '',
      description: '',
      test_type: 'a_b' as TestType,
      allocation_strategy: 'equal' as VariantAllocation,
      variants: [] as TestVariant[],
      metrics: [] as MetricType[],
      hypothesis: '',
      duration_days: 14,
      min_sample_size: 1000,
      confidence_level: 0.95,
      target_audience: {},
    },
    onSubmit: async (values) => {
      try {
        if (editingTest) {
          await updateTest(editingTest.id, values);
          toastService.success('Test updated successfully');
        } else {
          await createTest(values);
          toastService.success('Test created successfully');
        }
        handleCloseDialog();
      } catch (error) {
        // Error handling is done in the hook
      }
    },
  });

  // Event handlers
  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleTestSelect = (test: any) => {
    setSelectedTest(test);
    setDetailDialogOpen(true);
    setActiveTab(0);
  };

  const handleTestEdit = (test: any) => {
    setEditingTest(test);
    form.setValues({
      name: test.name || '',
      description: test.description || '',
      test_type: test.test_type || 'a_b',
      allocation_strategy: test.allocation_strategy || 'equal',
      variants: test.variants || [],
      metrics: test.metrics || [],
      hypothesis: test.hypothesis || '',
      duration_days: test.duration_days || 14,
      min_sample_size: test.min_sample_size || 1000,
      confidence_level: test.confidence_level || 0.95,
      target_audience: test.target_audience || {},
    });
    setDialogOpen(true);
  };

  const handleTestDelete = async (testId: string) => {
    if (window.confirm('Are you sure you want to delete this test?')) {
      await deleteTest(testId);
      toastService.success('Test deleted successfully');
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, test: any) => {
    setMenuAnchorEl(event.currentTarget);
    setSelectedTestForMenu(test);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setSelectedTestForMenu(null);
  };

  const handleOpenDialog = () => {
    setEditingTest(null);
    form.reset();
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingTest(null);
    form.reset();
  };

  const getStatusColor = (status: TestStatus) => {
    switch (status) {
      case 'draft':
        return 'default';
      case 'running':
        return 'success';
      case 'paused':
        return 'warning';
      case 'completed':
        return 'info';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (
    status: TestStatus
  ): React.ReactElement | undefined => {
    switch (status) {
      case 'running':
        return <TrendingUpIcon />;
      default:
        return undefined;
    }
  };

  // Toolbar
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={loadTests}
        disabled={loading}
      >
        Refresh
      </Button>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={handleOpenDialog}
      >
        Create A/B Test
      </Button>
    </>
  );

  return (
    <PageLayout title="A/B Testing" toolbar={toolbar}>
      <Card>
        <Box sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            A/B Testing Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Create, manage, and analyze your A/B tests to optimize user
            experience and conversion rates.
          </Typography>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <Typography>Loading tests...</Typography>
            </Box>
          ) : tests.length === 0 ? (
            <Alert severity="info">
              No A/B tests found. Create your first test to get started.
            </Alert>
          ) : (
            <ABTestTable
              tests={tests}
              page={page}
              rowsPerPage={rowsPerPage}
              onPageChange={handlePageChange}
              onRowsPerPageChange={handleRowsPerPageChange}
              onTestSelect={handleTestSelect}
              onTestEdit={handleTestEdit}
              onTestDelete={handleTestDelete}
              onTestStart={startTest}
              onTestStop={stopTest}
              onMenuOpen={handleMenuOpen}
              menuAnchorEl={menuAnchorEl}
              selectedTestForMenu={selectedTestForMenu}
              onMenuClose={handleMenuClose}
            />
          )}
        </Box>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingTest ? 'Edit A/B Test' : 'Create New A/B Test'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Test Name"
              value={form.values.name}
              onChange={(e) => form.handleChange('name', e.target.value)}
              error={Boolean(form.errors.name)}
              helperText={form.errors.name}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={form.values.description}
              onChange={(e) => form.handleChange('description', e.target.value)}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Test Type</InputLabel>
              <Select
                value={form.values.test_type}
                label="Test Type"
                onChange={(e) => form.handleChange('test_type', e.target.value)}
              >
                <MenuItem value="a_b">A/B Test</MenuItem>
                <MenuItem value="multivariate">Multivariate Test</MenuItem>
                <MenuItem value="split_url">Split URL Test</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Hypothesis"
              multiline
              rows={2}
              value={form.values.hypothesis}
              onChange={(e) => form.handleChange('hypothesis', e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Duration (days)"
              type="number"
              value={form.values.duration_days}
              onChange={(e) =>
                form.handleChange(
                  'duration_days',
                  parseInt(e.target.value) || 0
                )
              }
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Minimum Sample Size"
              type="number"
              value={form.values.min_sample_size}
              onChange={(e) =>
                form.handleChange(
                  'min_sample_size',
                  parseInt(e.target.value) || 0
                )
              }
              sx={{ mb: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={form.handleSubmit}
            variant="contained"
            disabled={saving}
          >
            {saving ? 'Saving...' : editingTest ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Test Details Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{ sx: { height: '90vh' } }}
      >
        <DialogTitle>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography variant="h5">{selectedTest?.name}</Typography>
            <Chip
              label={selectedTest?.status || 'Unknown'}
              color={getStatusColor(selectedTest?.status as TestStatus)}
              icon={getStatusIcon(selectedTest?.status as TestStatus)}
            />
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={activeTab}
              onChange={(_, newValue) => setActiveTab(newValue)}
            >
              <Tab label="Overview" />
              <Tab label="Metrics" />
              <Tab label="Results" />
              <Tab label="Performance" />
              <Tab label="Recommendations" />
            </Tabs>
          </Box>

          <TabPanel value={activeTab} index={0} idPrefix="ab-testing">
            {selectedTest && <ABTestOverviewTab test={selectedTest} />}
          </TabPanel>

          <TabPanel value={activeTab} index={1} idPrefix="ab-testing">
            {selectedTest && (
              <ABTestAnalytics
                testId={selectedTest.id}
                testName={selectedTest.name}
                metrics={testMetrics || undefined}
                results={testResults || undefined}
                recommendations={testRecommendations || undefined}
                performance={testPerformance || undefined}
              />
            )}
          </TabPanel>

          <TabPanel value={activeTab} index={2} idPrefix="ab-testing">
            {selectedTest && (
              <ABTestAnalytics
                testId={selectedTest.id}
                testName={selectedTest.name}
                metrics={testMetrics || undefined}
                results={testResults || undefined}
                recommendations={testRecommendations || undefined}
                performance={testPerformance || undefined}
              />
            )}
          </TabPanel>

          <TabPanel value={activeTab} index={3} idPrefix="ab-testing">
            {testPerformance ? (
              <ABTestAnalytics
                testId={selectedTest?.id || ''}
                testName={selectedTest?.name || ''}
                metrics={testMetrics || undefined}
                results={testResults || undefined}
                recommendations={testRecommendations || undefined}
                performance={testPerformance || undefined}
              />
            ) : (
              <Alert severity="info">
                No performance data available for this test.
              </Alert>
            )}
          </TabPanel>

          <TabPanel value={activeTab} index={4} idPrefix="ab-testing">
            {testRecommendations ? (
              <Typography variant="h6" gutterBottom>
                AI Recommendations
              </Typography>
            ) : (
              <Alert severity="info">
                No recommendations available for this test.
              </Alert>
            )}
          </TabPanel>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default ABTestingPage;
