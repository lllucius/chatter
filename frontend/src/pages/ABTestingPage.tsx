import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Menu,
  ListItemIcon,
  Grid,
  Paper,
  LinearProgress,
  Tabs,
  Tab,
  TabPanel,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '../utils/mui';
import {
  EditIcon,
  DeleteIcon,
  AddIcon,
  RefreshIcon,
  PlayIcon as StartIcon,
  PauseIcon,
  StopIcon,
  CheckIcon as CompleteIcon,
  MoreIcon as MoreVertIcon,
  TrendingUpIcon,
} from '../utils/icons';
import { TrendingFlat as TrendingFlatIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import { getSDK } from "../services/auth-service";
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import {
  ABTestResponse,
  ABTestCreateRequest,
  ABTestUpdateRequest,
  ABTestMetricsResponse,
  ABTestResultsResponse,
  TestStatus,
  TestType,
  VariantAllocation,
  MetricType,
} from 'chatter-sdk';
import PageLayout from '../components/PageLayout';
import ABTestAnalytics from '../components/ABTestAnalytics';



interface TestRecommendations {
  recommendations?: string[];
  insights?: string[];
  suggestions?: string[];
  nextSteps?: string[];
  improvements?: string[];
}

interface TestPerformance {
  averageResponseTime: number;
  throughput: number;
  errorRate: number;
  successRate: number;
}

const ABTestingPage: React.FC = () => {
  const [tests, setTests] = useState<ABTestResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [editingTest, setEditingTest] = useState<ABTestResponse | null>(null);
  const [selectedTest, setSelectedTest] = useState<ABTestResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  
  // Additional data states
  const [testMetrics, setTestMetrics] = useState<ABTestMetricsResponse | null>(null);
  const [testResults, setTestResults] = useState<ABTestResultsResponse | null>(null);
  const [testRecommendations, setTestRecommendations] = useState<TestRecommendations | null>(null);
  const [testPerformance, setTestPerformance] = useState<TestPerformance | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_type: TestType.prompt,
    variants: [
      { name: 'Control', allocation: 50 },
      { name: 'Variant A', allocation: 50 }
    ],
    min_sample_size: 1000,
    confidence_level: 0.95,
    duration_days: 14,
  });

  const [actionAnchorEl, setActionAnchorEl] = useState<HTMLElement | null>(null);
  const [actionTest, setActionTest] = useState<ABTestResponse | null>(null);

  const testTypes = [
    { value: 'prompt', label: 'Prompt Testing' },
    { value: 'model', label: 'Model Testing' },
    { value: 'parameter', label: 'Parameter Testing' },
    { value: 'workflow', label: 'Workflow Testing' },
  ];

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    try {
      setLoading(true);
      const response = await getSDK().abTesting.listAbTestsApiV1AbTests(null);
      setTests(response.tests || []);
    } catch (err: unknown) {
      handleError(err, {
        source: 'ABTestingPage.loadTests',
        operation: 'load AB tests'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadTestDetails = async (test: ABTestResponse) => {
    try {
      const [metricsResponse, resultsResponse, recommendationsResponse, performanceResponse] = 
        await Promise.allSettled([
          getSDK().abTesting.getAbTestMetricsApiV1AbTestsTestIdMetrics(test.id),
          getSDK().abTesting.getAbTestResultsApiV1AbTestsTestIdResults(test.id),
          getSDK().abTesting.getAbTestRecommendationsApiV1AbTestsTestIdRecommendations(test.id),
          getSDK().abTesting.getAbTestPerformanceApiV1AbTestsTestIdPerformance(test.id),
        ]);

      setTestMetrics(metricsResponse.status === 'fulfilled' ? metricsResponse.value : null);
      setTestResults(resultsResponse.status === 'fulfilled' ? resultsResponse.value : null);
      setTestRecommendations(recommendationsResponse.status === 'fulfilled' ? recommendationsResponse.value as TestRecommendations : null);
      setTestPerformance(performanceResponse.status === 'fulfilled' ? performanceResponse.value as unknown as TestPerformance : null);
    } catch {
      // Error loading test details - will show in UI appropriately
    }
  };

  const handleOpenDialog = (test?: ABTestResponse) => {
    if (test) {
      setEditingTest(test);
      setFormData({
        name: test.name,
        description: test.description || '',
        test_type: test.test_type,
        variants: test.variants.map(v => ({
          name: v.name,
          allocation: (v.weight || 0) * 100, // Convert from decimal to percentage
        })),
        min_sample_size: test.min_sample_size,
        confidence_level: test.confidence_level,
        duration_days: test.duration_days,
      });
    } else {
      setEditingTest(null);
      setFormData({
        name: '',
        description: '',
        test_type: TestType.prompt,
        variants: [
          { name: 'Control', allocation: 50 },
          { name: 'Variant A', allocation: 50 }
        ],
        min_sample_size: 1000,
        confidence_level: 0.95,
        duration_days: 14,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingTest(null);
  };

  const handleOpenDetailDialog = async (test: ABTestResponse) => {
    setSelectedTest(test);
    setActiveTab(0);
    await loadTestDetails(test);
    setDetailDialogOpen(true);
  };

  const handleCloseDetailDialog = () => {
    setDetailDialogOpen(false);
    setSelectedTest(null);
    setTestMetrics(null);
    setTestResults(null);
    setTestRecommendations(null);
    setTestPerformance(null);
  };

  const handleSave = async () => {
    try {
      setSaving(true);

      const testData: ABTestCreateRequest | ABTestUpdateRequest = {
        name: formData.name,
        description: formData.description,
        test_type: formData.test_type,
        allocation_strategy: VariantAllocation.equal, // Default allocation strategy
        variants: formData.variants.map(v => ({
          name: v.name,
          description: v.name === 'Control' ? 'Control variant for baseline comparison' : `${v.name} test variant`,
          weight: v.allocation / 100, // Convert percentage to decimal
          configuration: {},
        })),
        metrics: [MetricType.user_satisfaction], // Default metrics
        min_sample_size: formData.min_sample_size,
        confidence_level: formData.confidence_level,
        duration_days: formData.duration_days,
      };

      if (editingTest) {
        await getSDK().abTesting.updateAbTestApiV1AbTestsTestId(
          editingTest.id,
          testData
        );
        toastService.success('Test updated successfully');
      } else {
        await getSDK().abTesting.createAbTestApiV1AbTests(testData);
        toastService.success('Test created successfully');
      }

      handleCloseDialog();
      await loadTests();
    } catch (err: unknown) {
      handleError(err, {
        source: 'ABTestingPage.handleSaveTest',
        operation: editingTest ? 'update AB test' : 'create AB test',
        additionalData: { 
          testId: editingTest?.id,
          testName: formData.name 
        }
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (test: ABTestResponse) => {
    if (!window.confirm('Are you sure you want to delete this test?')) {
      return;
    }

    try {
      await getSDK().abTesting.deleteAbTestApiV1AbTestsTestId(test.id);
      toastService.success('Test deleted successfully');
      await loadTests();
    } catch (err: unknown) {
      handleError(err, {
        source: 'ABTestingPage.handleDeleteTest',
        operation: 'delete AB test',
        additionalData: { testId: test.id, testName: test.name }
      });
    }
  };

  const handleTestAction = async (test: ABTestResponse, action: 'start' | 'pause' | 'end' | 'complete') => {
    try {
      let response;
      switch (action) {
        case 'start':
          response = await getSDK().abTesting.startAbTestApiV1AbTestsTestIdStart(test.id);
          break;
        case 'pause':
          response = await getSDK().abTesting.pauseAbTestApiV1AbTestsTestIdPause(test.id);
          break;
        case 'end':
          response = await getSDK().abTesting.endAbTestApiV1AbTestsTestIdEnd(test.id);
          break;
        case 'complete':
          response = await getSDK().abTesting.completeAbTestApiV1AbTestsTestIdComplete(test.id);
          break;
      }
      toastService.success(response.message);
      await loadTests();
      handleCloseActionMenu();
    } catch (err: unknown) {
      handleError(err, {
        source: 'ABTestingPage.handleTestAction',
        operation: `${action} AB test`,
        additionalData: { 
          testId: test.id, 
          testName: test.name,
          action 
        }
      });
    }
  };

  const handleOpenActionMenu = (event: React.MouseEvent<HTMLElement>, test: ABTestResponse) => {
    setActionAnchorEl(event.currentTarget);
    setActionTest(test);
  };

  const handleCloseActionMenu = () => {
    setActionAnchorEl(null);
    setActionTest(null);
  };

  const addVariant = () => {
    const totalAllocation = formData.variants.reduce((sum, v) => sum + v.allocation, 0);
    const newAllocation = Math.max(0, 100 - totalAllocation);
    setFormData({
      ...formData,
      variants: [...formData.variants, { name: `Variant ${String.fromCharCode(65 + formData.variants.length - 1)}`, allocation: newAllocation }]
    });
  };

  const removeVariant = (index: number) => {
    if (formData.variants.length > 2) {
      const newVariants = formData.variants.filter((_, i) => i !== index);
      setFormData({ ...formData, variants: newVariants });
    }
  };

  const getStatusColor = (status: TestStatus): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (status) {
      case TestStatus.draft: return 'default';
      case TestStatus.running: return 'primary';
      case TestStatus.paused: return 'warning';
      case TestStatus.completed: return 'success';
      case TestStatus.cancelled: return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: TestStatus) => {
    switch (status) {
      case TestStatus.running: return <TrendingUpIcon />;
      case TestStatus.paused: return <PauseIcon />;
      case TestStatus.completed: return <CompleteIcon />;
      case TestStatus.cancelled: return <StopIcon />;
      default: return <TrendingFlatIcon />;
    }
  };

  const canStart = (test: ABTestResponse) => test.status === TestStatus.draft || test.status === TestStatus.paused;
  const canPause = (test: ABTestResponse) => test.status === TestStatus.running;
  const canEnd = (test: ABTestResponse) => test.status === TestStatus.running || test.status === TestStatus.paused;
  const canComplete = (test: ABTestResponse) => test.status === TestStatus.running || test.status === TestStatus.paused;

  const renderTestDialog = () => (
    <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
      <DialogTitle>{editingTest ? 'Edit AB Test' : 'Create AB Test'}</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          <Grid container spacing={3}>
            {/* Basic Information Section */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Test Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Test Type</InputLabel>
                <Select
                  value={formData.test_type}
                  onChange={(e) => setFormData({ ...formData, test_type: e.target.value as TestType })}
                  label="Test Type"
                >
                  {testTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Description Section */}
            <Grid size={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            
            {/* Variants Section */}
            <Grid size={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 2 }}>
                Test Variants
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {formData.variants.map((variant, index) => (
                  <Grid container spacing={2} key={index} alignItems="center">
                    <Grid size={{ xs: 12, sm: 8 }}>
                      <TextField
                        fullWidth
                        label="Variant Name"
                        value={variant.name}
                        onChange={(e) => {
                          const newVariants = [...formData.variants];
                          newVariants[index].name = e.target.value;
                          setFormData({ ...formData, variants: newVariants });
                        }}
                      />
                    </Grid>
                    <Grid size={{ xs: 8, sm: 3 }}>
                      <TextField
                        fullWidth
                        label="Traffic %"
                        type="number"
                        value={variant.allocation}
                        onChange={(e) => {
                          const newVariants = [...formData.variants];
                          newVariants[index].allocation = Math.max(0, Math.min(100, parseInt(e.target.value) || 0));
                          setFormData({ ...formData, variants: newVariants });
                        }}
                        inputProps={{ min: 0, max: 100 }}
                      />
                    </Grid>
                    <Grid size={{ xs: 4, sm: 1 }}>
                      {formData.variants.length > 2 && (
                        <IconButton onClick={() => removeVariant(index)} color="error">
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Grid>
                  </Grid>
                ))}
              </Box>
              <Button 
                onClick={addVariant} 
                startIcon={<AddIcon />} 
                variant="outlined" 
                sx={{ mt: 2 }}
              >
                Add Variant
              </Button>
            </Grid>

            {/* Test Configuration Section */}
            <Grid size={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 3, mb: 2 }}>
                Test Configuration
              </Typography>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Minimum Sample Size"
                type="number"
                value={formData.min_sample_size}
                onChange={(e) => setFormData({ ...formData, min_sample_size: parseInt(e.target.value) || 1000 })}
                inputProps={{ min: 100 }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Duration (Days)"
                type="number"
                value={formData.duration_days}
                onChange={(e) => setFormData({ ...formData, duration_days: parseInt(e.target.value) || 14 })}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Confidence Level"
                type="number"
                value={formData.confidence_level}
                onChange={(e) => setFormData({ ...formData, confidence_level: parseFloat(e.target.value) || 0.95 })}
                inputProps={{ min: 0.8, max: 0.99, step: 0.01 }}
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCloseDialog}>Cancel</Button>
        <Button 
          onClick={handleSave} 
          variant="contained"
          disabled={saving || !formData.name.trim()}
        >
          {saving ? <CircularProgress size={20} /> : editingTest ? 'Update Test' : 'Create Test'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderDetailDialog = () => (
    <Dialog 
      open={detailDialogOpen} 
      onClose={handleCloseDetailDialog} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{ sx: { height: '90vh' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label="Overview" />
            <Tab label="Metrics" />
            <Tab label="Results" />
            <Tab label="Performance" />
            <Tab label="Recommendations" />
          </Tabs>
        </Box>
        
        <TabPanel value={activeTab} index={0} idPrefix="ab-testing">
          {selectedTest && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Test Details</Typography>
                  <Typography><strong>Type:</strong> {selectedTest.test_type}</Typography>
                  <Typography><strong>Status:</strong> {selectedTest.status}</Typography>
                  <Typography><strong>Duration:</strong> {selectedTest.duration_days} days</Typography>
                  <Typography><strong>Sample Size:</strong> {selectedTest.min_sample_size.toLocaleString()}</Typography>
                  <Typography><strong>Confidence:</strong> {(selectedTest.confidence_level * 100).toFixed(1)}%</Typography>
                  {selectedTest.created_at && (
                    <Typography><strong>Created:</strong> {format(new Date(selectedTest.created_at), 'MMM dd, yyyy HH:mm')}</Typography>
                  )}
                  {selectedTest.description && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2">Description</Typography>
                      <Typography variant="body2" color="text.secondary">{selectedTest.description}</Typography>
                    </Box>
                  )}
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Test Variants</Typography>
                  {selectedTest.variants.map((variant) => (
                    <Box key={variant.name} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle1">{variant.name}</Typography>
                        <Chip label={`${((variant.weight || 0) * 100).toFixed(1)}%`} size="small" />
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={(variant.weight || 0) * 100} 
                        sx={{ mt: 1, height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Paper>
              </Grid>
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={1} idPrefix="ab-testing">
          {selectedTest && (
            <ABTestAnalytics
              testId={selectedTest.id}
              testName={selectedTest.name}
              metrics={testMetrics}
              results={testResults}
              recommendations={testRecommendations}
              performance={testPerformance}
            />
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={2} idPrefix="ab-testing">
          {selectedTest && (
            <ABTestAnalytics
              testId={selectedTest.id}
              testName={selectedTest.name}
              metrics={testMetrics}
              results={testResults}
              recommendations={testRecommendations}
              performance={testPerformance}
            />
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={3} idPrefix="ab-testing">
          {testPerformance ? (
            <ABTestAnalytics
              testId={selectedTest?.id || ''}
              testName={selectedTest?.name || ''}
              metrics={testMetrics}
              results={testResults}
              recommendations={testRecommendations}
              performance={testPerformance}
            />
          ) : (
            <Alert severity="info">No performance data available for this test.</Alert>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={4} idPrefix="ab-testing">
          {testRecommendations ? (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>AI Recommendations</Typography>
                <Paper sx={{ p: 2 }}>
                  {testRecommendations.recommendations && testRecommendations.recommendations.length > 0 ? (
                    <List>
                      {testRecommendations.recommendations.map((rec: string, index: number) => (
                        <ListItem key={index}>
                          <ListItemText primary={rec} />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography>No recommendations available.</Typography>
                  )}
                  
                  {testRecommendations.insights && testRecommendations.insights.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle1">Insights</Typography>
                      <List>
                        {testRecommendations.insights.map((insight: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemText primary={insight} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">No recommendations available for this test.</Alert>
          )}
        </TabPanel>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCloseDetailDialog}>Close</Button>
      </DialogActions>
    </Dialog>
  );

  const renderActionMenu = () => (
    <Menu
      anchorEl={actionAnchorEl}
      open={Boolean(actionAnchorEl)}
      onClose={handleCloseActionMenu}
    >
      {actionTest && canStart(actionTest) && (
        <MenuItem onClick={() => handleTestAction(actionTest, 'start')}>
          <ListItemIcon><StartIcon fontSize="small" /></ListItemIcon>
          Start Test
        </MenuItem>
      )}
      {actionTest && canPause(actionTest) && (
        <MenuItem onClick={() => handleTestAction(actionTest, 'pause')}>
          <ListItemIcon><PauseIcon fontSize="small" /></ListItemIcon>
          Pause Test
        </MenuItem>
      )}
      {actionTest && canEnd(actionTest) && (
        <MenuItem onClick={() => handleTestAction(actionTest, 'end')}>
          <ListItemIcon><StopIcon fontSize="small" /></ListItemIcon>
          End Test
        </MenuItem>
      )}
      {actionTest && canComplete(actionTest) && (
        <MenuItem onClick={() => handleTestAction(actionTest, 'complete')}>
          <ListItemIcon><CompleteIcon fontSize="small" /></ListItemIcon>
          Complete Test
        </MenuItem>
      )}
      <Divider />
      <MenuItem onClick={() => { handleOpenDialog(actionTest); handleCloseActionMenu(); }}>
        <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
        Edit Test
      </MenuItem>
      <MenuItem onClick={() => { actionTest && handleDelete(actionTest); handleCloseActionMenu(); }} sx={{ color: 'error.main' }}>
        <ListItemIcon><DeleteIcon fontSize="small" /></ListItemIcon>
        Delete Test
      </MenuItem>
    </Menu>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const toolbar = (
    <>
      <Button onClick={loadTests} startIcon={<RefreshIcon />} size="small">
        Refresh
      </Button>
      <Button variant="contained" onClick={() => handleOpenDialog()} startIcon={<AddIcon />} size="small">
        Create Test
      </Button>
    </>
  );

  return (
    <PageLayout title="A/B Testing" toolbar={toolbar}>

      {tests.length === 0 ? (
        <Alert severity="info">
          No AB tests found. Create your first test to get started with experimentation.
        </Alert>
      ) : (
        <Card>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Variants</TableCell>
                  <TableCell>Sample Size</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tests.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((test) => (
                  <TableRow key={test.id} hover>
                    <TableCell>
                      <Box>
                        <Typography 
                          variant="subtitle2" 
                          component="button"
                          onClick={() => handleOpenDetailDialog(test)}
                          sx={{ 
                            cursor: 'pointer', 
                            color: 'primary.main',
                            textDecoration: 'none',
                            border: 'none',
                            background: 'none',
                            '&:hover': { textDecoration: 'underline' }
                          }}
                        >
                          {test.name}
                        </Typography>
                        {test.description && (
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {test.description}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={test.test_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={test.status} 
                        color={getStatusColor(test.status)} 
                        size="small"
                        icon={getStatusIcon(test.status)}
                      />
                    </TableCell>
                    <TableCell>{test.variants.length}</TableCell>
                    <TableCell>{test.min_sample_size.toLocaleString()}</TableCell>
                    <TableCell>
                      {test.created_at ? format(new Date(test.created_at), 'MMM dd, yyyy') : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={(e) => handleOpenActionMenu(e, test)}>
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={tests.length}
            page={page}
            onPageChange={(_, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </Card>
      )}

      {renderTestDialog()}
      {renderDetailDialog()}
      {renderActionMenu()}
    </PageLayout>
  );
};

export default ABTestingPage;
