import React, { useState, useEffect, useCallback } from 'react';
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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Paper,
  LinearProgress,
  Tooltip,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  PlayArrow as StartIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  CheckCircle as CompleteIcon,
  Analytics as MetricsIcon,
  Assessment as PerformanceIcon,
  Lightbulb as RecommendationsIcon,
  MoreVert as MoreVertIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { toastService } from '../services/toast-service';
import {
  ABTestResponse,
  ABTestCreateRequest,
  ABTestUpdateRequest,
  ABTestListResponse,
  ABTestMetricsResponse,
  ABTestResultsResponse,
  TestStatus,
  TestType,
  VariantAllocation,
} from '../sdk';

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
      id={`ab-testing-tabpanel-${index}`}
      aria-labelledby={`ab-testing-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
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
  const [testRecommendations, setTestRecommendations] = useState<any>(null);
  const [testPerformance, setTestPerformance] = useState<any>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_type: 'prompt' as TestType,
    variants: [
      { name: 'Control', allocation: 50 },
      { name: 'Variant A', allocation: 50 }
    ],
    minimum_sample_size: 1000,
    confidence_level: 0.95,
    primary_metric: {
      name: 'response_quality',
      improvement_threshold: 0.05,
    },
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
      const response = await chatterSDK.abTesting.listAbTestsApiV1AbTestsGet({});
      const data = response.data;
      setTests(data.tests || []);
    } catch (err: any) {
      toastService.error(err, 'Failed to load AB tests');
    } finally {
      setLoading(false);
    }
  };

  const loadTestDetails = async (test: ABTestResponse) => {
    try {
      const [metricsResponse, resultsResponse, recommendationsResponse, performanceResponse] = 
        await Promise.allSettled([
          chatterSDK.abTesting.getAbTestMetricsApiV1AbTestsTestIdMetricsGet({ testId: test.id }),
          chatterSDK.abTesting.getAbTestResultsApiV1AbTestsTestIdResultsGet({ testId: test.id }),
          chatterSDK.abTesting.getAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGet({ testId: test.id }),
          chatterSDK.abTesting.getAbTestPerformanceApiV1AbTestsTestIdPerformanceGet({ testId: test.id }),
        ]);

      setTestMetrics(metricsResponse.status === 'fulfilled' ? metricsResponse.value.data : null);
      setTestResults(resultsResponse.status === 'fulfilled' ? resultsResponse.value.data : null);
      setTestRecommendations(recommendationsResponse.status === 'fulfilled' ? recommendationsResponse.value.data : null);
      setTestPerformance(performanceResponse.status === 'fulfilled' ? performanceResponse.value.data : null);
    } catch (err: any) {
      console.error('Failed to load test details:', err);
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
          allocation: v.allocation * 100, // Convert from decimal to percentage
        })),
        minimum_sample_size: test.minimum_sample_size,
        confidence_level: test.confidence_level,
        primary_metric: test.primary_metric,
        duration_days: test.duration_days,
      });
    } else {
      setEditingTest(null);
      setFormData({
        name: '',
        description: '',
        test_type: 'prompt',
        variants: [
          { name: 'Control', allocation: 50 },
          { name: 'Variant A', allocation: 50 }
        ],
        minimum_sample_size: 1000,
        confidence_level: 0.95,
        primary_metric: {
          name: 'response_quality',
          improvement_threshold: 0.05,
        },
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
        variants: formData.variants.map(v => ({
          name: v.name,
          allocation: v.allocation / 100, // Convert percentage to decimal
          configuration: {},
        })),
        minimum_sample_size: formData.minimum_sample_size,
        confidence_level: formData.confidence_level,
        primary_metric: formData.primary_metric,
        duration_days: formData.duration_days,
      };

      if (editingTest) {
        await chatterSDK.abTesting.updateAbTestApiV1AbTestsTestIdPut({
          testId: editingTest.id,
          aBTestUpdateRequest: testData,
        });
        toastService.success('Test updated successfully');
      } else {
        await chatterSDK.abTesting.createAbTestApiV1AbTestsPost({
          aBTestCreateRequest: testData,
        });
        toastService.success('Test created successfully');
      }

      handleCloseDialog();
      await loadTests();
    } catch (err: any) {
      toastService.error(err, 'Failed to save test');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (test: ABTestResponse) => {
    if (!window.confirm('Are you sure you want to delete this test?')) {
      return;
    }

    try {
      await chatterSDK.abTesting.deleteAbTestApiV1AbTestsTestIdDelete({ testId: test.id });
      toastService.success('Test deleted successfully');
      await loadTests();
    } catch (err: any) {
      toastService.error(err, 'Failed to delete test');
    }
  };

  const handleTestAction = async (test: ABTestResponse, action: 'start' | 'pause' | 'end' | 'complete') => {
    try {
      let response;
      switch (action) {
        case 'start':
          response = await chatterSDK.abTesting.startAbTestApiV1AbTestsTestIdStartPost({ testId: test.id });
          break;
        case 'pause':
          response = await chatterSDK.abTesting.pauseAbTestApiV1AbTestsTestIdPausePost({ testId: test.id });
          break;
        case 'end':
          response = await chatterSDK.abTesting.endAbTestApiV1AbTestsTestIdEndPost({ testId: test.id });
          break;
        case 'complete':
          response = await chatterSDK.abTesting.completeAbTestApiV1AbTestsTestIdCompletePost({ testId: test.id });
          break;
      }
      toastService.success(response.data.message);
      await loadTests();
      handleCloseActionMenu();
    } catch (err: any) {
      toastService.error(err, `Failed to ${action} test`);
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
      case 'draft': return 'default';
      case 'running': return 'primary';
      case 'paused': return 'warning';
      case 'completed': return 'success';
      case 'stopped': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: TestStatus) => {
    switch (status) {
      case 'running': return <TrendingUpIcon />;
      case 'paused': return <PauseIcon />;
      case 'completed': return <CompleteIcon />;
      case 'stopped': return <StopIcon />;
      default: return <TrendingFlatIcon />;
    }
  };

  const canStart = (test: ABTestResponse) => test.status === 'draft' || test.status === 'paused';
  const canPause = (test: ABTestResponse) => test.status === 'running';
  const canEnd = (test: ABTestResponse) => test.status === 'running' || test.status === 'paused';
  const canComplete = (test: ABTestResponse) => test.status === 'running' || test.status === 'paused';

  const renderTestDialog = () => (
    <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
      <DialogTitle>{editingTest ? 'Edit AB Test' : 'Create AB Test'}</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Test Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
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
            <Grid item xs={12}>
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
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Test Variants</Typography>
              {formData.variants.map((variant, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
                  <TextField
                    label="Variant Name"
                    value={variant.name}
                    onChange={(e) => {
                      const newVariants = [...formData.variants];
                      newVariants[index].name = e.target.value;
                      setFormData({ ...formData, variants: newVariants });
                    }}
                    sx={{ flex: 1 }}
                  />
                  <TextField
                    label="Traffic %"
                    type="number"
                    value={variant.allocation}
                    onChange={(e) => {
                      const newVariants = [...formData.variants];
                      newVariants[index].allocation = Math.max(0, Math.min(100, parseInt(e.target.value) || 0));
                      setFormData({ ...formData, variants: newVariants });
                    }}
                    inputProps={{ min: 0, max: 100 }}
                    sx={{ width: 120 }}
                  />
                  {formData.variants.length > 2 && (
                    <IconButton onClick={() => removeVariant(index)} color="error">
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Box>
              ))}
              <Button onClick={addVariant} startIcon={<AddIcon />} variant="outlined">
                Add Variant
              </Button>
            </Grid>

            {/* Test Configuration */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Minimum Sample Size"
                type="number"
                value={formData.minimum_sample_size}
                onChange={(e) => setFormData({ ...formData, minimum_sample_size: parseInt(e.target.value) || 1000 })}
                inputProps={{ min: 100 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Duration (Days)"
                type="number"
                value={formData.duration_days}
                onChange={(e) => setFormData({ ...formData, duration_days: parseInt(e.target.value) || 14 })}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Confidence Level"
                type="number"
                value={formData.confidence_level}
                onChange={(e) => setFormData({ ...formData, confidence_level: parseFloat(e.target.value) || 0.95 })}
                inputProps={{ min: 0.8, max: 0.99, step: 0.01 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Primary Metric"
                value={formData.primary_metric.name}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  primary_metric: { ...formData.primary_metric, name: e.target.value }
                })}
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
        
        <TabPanel value={activeTab} index={0}>
          {selectedTest && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Test Details</Typography>
                  <Typography><strong>Type:</strong> {selectedTest.test_type}</Typography>
                  <Typography><strong>Status:</strong> {selectedTest.status}</Typography>
                  <Typography><strong>Duration:</strong> {selectedTest.duration_days} days</Typography>
                  <Typography><strong>Sample Size:</strong> {selectedTest.minimum_sample_size.toLocaleString()}</Typography>
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
                        <Chip label={`${(variant.allocation * 100).toFixed(1)}%`} size="small" />
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={variant.allocation * 100} 
                        sx={{ mt: 1, height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Paper>
              </Grid>
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {testMetrics ? (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>Test Metrics</Typography>
                <Paper sx={{ p: 2 }}>
                  <pre>{JSON.stringify(testMetrics, null, 2)}</pre>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">No metrics data available for this test.</Alert>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {testResults ? (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>Test Results</Typography>
                <Paper sx={{ p: 2 }}>
                  <pre>{JSON.stringify(testResults, null, 2)}</pre>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">No results data available for this test.</Alert>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          {testPerformance ? (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>Performance Data</Typography>
                <Paper sx={{ p: 2 }}>
                  <pre>{JSON.stringify(testPerformance, null, 2)}</pre>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">No performance data available for this test.</Alert>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
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

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">A/B Testing</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button onClick={loadTests} startIcon={<RefreshIcon />}>
            Refresh
          </Button>
          <Button variant="contained" onClick={() => handleOpenDialog()} startIcon={<AddIcon />}>
            Create Test
          </Button>
        </Box>
      </Box>

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
                    <TableCell>{test.minimum_sample_size.toLocaleString()}</TableCell>
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
    </Box>
  );
};

export default ABTestingPage;