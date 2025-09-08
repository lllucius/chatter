import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tab,
  Tabs,
  Button,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Paper,
  Divider,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Stack,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  AccountTree as WorkflowIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon,
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  Code as CodeIcon,
  Build as BuildIcon,
  GetApp as ExportIcon,
  Publish as ImportIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Launch as LaunchIcon,
  Visibility as ViewIcon,
  ContentCopy as CopyIcon,
  Tune as TuneIcon,
} from '@mui/icons-material';
import { chatterClient } from '../sdk/client';
import { toastService } from '../services/toast-service';
import { WorkflowTemplateInfo, AvailableToolsResponse, ChatRequest } from '../sdk';
import WorkflowEditor from '../components/workflow/WorkflowEditor';
import PageLayout from '../components/PageLayout';

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
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
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

interface WorkflowExecution {
  id: string;
  templateName?: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: Date;
  endTime?: Date;
  result?: any;
  error?: string;
  progress?: number;
}

const WorkflowManagementPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<Record<string, WorkflowTemplateInfo>>({});
  const [availableTools, setAvailableTools] = useState<AvailableToolsResponse | null>(null);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [builderDialogOpen, setBuilderDialogOpen] = useState(false);
  const [executionInput, setExecutionInput] = useState('');
  const [customWorkflow, setCustomWorkflow] = useState({
    name: '',
    description: '',
    type: 'sequential' as 'sequential' | 'parallel' | 'conditional',
    steps: [] as any[],
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const loadWorkflowTemplates = useCallback(async () => {
    try {
      setLoading(true);
      const response = await chatterClient.chat.getWorkflowTemplatesApiV1ChatTemplatesGet();
      if (response.templates) {
        setTemplates(response.templates);
      }
    } catch (error: any) {
      console.error('Failed to load workflow templates:', error);
      toastService.error('Failed to load workflow templates');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAvailableTools = useCallback(async () => {
    try {
      const response = await chatterClient.chat.getAvailableToolsApiV1ChatToolsAvailableGet();
      setAvailableTools(response.data);
    } catch (error: any) {
      console.error('Failed to load available tools:', error);
      toastService.error('Failed to load available tools');
    }
  }, []);

  useEffect(() => {
    loadWorkflowTemplates();
    loadAvailableTools();
  }, [loadWorkflowTemplates, loadAvailableTools]);

  const executeWorkflow = async (templateName: string, input: string) => {
    const executionId = `exec_${Date.now()}`;
    const execution: WorkflowExecution = {
      id: executionId,
      templateName,
      status: 'running',
      startTime: new Date(),
      progress: 0,
    };

    setExecutions(prev => [execution, ...prev]);

    try {
      const chatRequest: ChatRequest = {
        message: input,
        stream: false,
        conversation_id: undefined,
        workflow: 'full' as any,
      };

      const response = await chatterClient.chat.chatWithTemplateApiV1ChatTemplateTemplateNamePost(
        templateName,
        { chatRequest }
      );

      // Update execution with result
      setExecutions(prev => prev.map(exec => 
        exec.id === executionId 
          ? { ...exec, status: 'completed', endTime: new Date(), result: response.data, progress: 100 }
          : exec
      ));

      toastService.success(`Workflow "${templateName}" executed successfully`);
    } catch (error: any) {
      console.error('Workflow execution failed:', error);
      setExecutions(prev => prev.map(exec => 
        exec.id === executionId 
          ? { ...exec, status: 'failed', endTime: new Date(), error: error.message, progress: 100 }
          : exec
      ));
      toastService.error(`Workflow execution failed: ${error.message}`);
    }
  };

  const handleExecuteTemplate = (templateName: string) => {
    setSelectedTemplate(templateName);
    setExecuteDialogOpen(true);
  };

  const handleExecuteConfirm = () => {
    if (selectedTemplate && executionInput.trim()) {
      executeWorkflow(selectedTemplate, executionInput);
      setExecuteDialogOpen(false);
      setExecutionInput('');
      setSelectedTemplate(null);
    }
  };

  const renderTemplatesTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          Workflow Templates
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadWorkflowTemplates}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {Object.entries(templates).map(([name, template]) => (
            <Grid item xs={12} md={6} lg={4} key={name}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <WorkflowIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6" component="h2">
                      {template.name || name}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {template.description || 'No description available'}
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={template.workflow_type || 'Unknown'} 
                      size="small" 
                      color="primary" 
                      sx={{ mr: 1 }}
                    />
                    {template.category && (
                      <Chip 
                        label={template.category} 
                        size="small" 
                        variant="outlined" 
                      />
                    )}
                  </Box>

                  {template.required_tools && template.required_tools.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Required Tools:
                      </Typography>
                      <Box sx={{ mt: 0.5 }}>
                        {template.required_tools.map((tool, index) => (
                          <Chip 
                            key={index}
                            label={tool} 
                            size="small" 
                            variant="outlined" 
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {template.parameters && Object.keys(template.parameters).length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Parameters: {Object.keys(template.parameters).length}
                      </Typography>
                    </Box>
                  )}
                </CardContent>

                <CardContent sx={{ pt: 0 }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<PlayIcon />}
                      onClick={() => handleExecuteTemplate(name)}
                      fullWidth
                    >
                      Execute
                    </Button>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Copy Template">
                      <IconButton size="small">
                        <CopyIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {Object.keys(templates).length === 0 && !loading && (
        <Alert severity="info" sx={{ mt: 2 }}>
          No workflow templates found. Templates allow you to create reusable workflow configurations.
        </Alert>
      )}
    </Box>
  );

  const renderBuilderTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          Workflow Builder
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setBuilderDialogOpen(true)}
        >
          Create Workflow
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <BuildIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Sequential Workflow
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Execute steps one after another, with each step receiving the output of the previous step.
              </Typography>
              <Button variant="outlined" size="small">
                Create Sequential
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Parallel Workflow
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Execute multiple steps simultaneously, combining their results at the end.
              </Typography>
              <Button variant="outlined" size="small">
                Create Parallel
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TuneIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Conditional Workflow
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Execute different steps based on conditions and decision points.
              </Typography>
              <Button variant="outlined" size="small">
                Create Conditional
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Available Tools
        </Typography>
        {availableTools ? (
          <Grid container spacing={2}>
            {availableTools.tools?.map((tool, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      {tool.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {tool.description || 'No description available'}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip 
                        label={tool.server || 'Unknown'} 
                        size="small" 
                        variant="outlined" 
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Alert severity="info">
            Loading available tools...
          </Alert>
        )}
      </Box>
    </Box>
  );

  const getStatusIcon = (status: WorkflowExecution['status']) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon color="success" />;
      case 'failed': return <ErrorIcon color="error" />;
      case 'running': return <CircularProgress size={20} />;
      case 'cancelled': return <WarningIcon color="warning" />;
      default: return <InfoIcon />;
    }
  };

  const getStatusColor = (status: WorkflowExecution['status']) => {
    switch (status) {
      case 'completed': return 'success' as const;
      case 'failed': return 'error' as const;
      case 'running': return 'info' as const;
      case 'cancelled': return 'warning' as const;
      default: return 'default' as const;
    }
  };

  const renderExecutionTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          Workflow Executions
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => {/* Refresh executions */}}
        >
          Refresh
        </Button>
      </Box>

      {executions.length === 0 ? (
        <Alert severity="info">
          No workflow executions yet. Execute a workflow template to see results here.
        </Alert>
      ) : (
        <List>
          {executions.map((execution) => (
            <React.Fragment key={execution.id}>
              <ListItem>
                <ListItemIcon>
                  {getStatusIcon(execution.status)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {execution.templateName || 'Custom Workflow'}
                      </Typography>
                      <Chip 
                        label={execution.status} 
                        size="small" 
                        color={getStatusColor(execution.status)}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Started: {execution.startTime.toLocaleString()}
                      </Typography>
                      {execution.endTime && (
                        <Typography variant="body2" color="text.secondary">
                          Duration: {Math.round((execution.endTime.getTime() - execution.startTime.getTime()) / 1000)}s
                        </Typography>
                      )}
                      {execution.error && (
                        <Typography variant="body2" color="error">
                          Error: {execution.error}
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton size="small">
                    <ViewIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              {execution.status === 'running' && execution.progress !== undefined && (
                <Box sx={{ px: 2, pb: 1 }}>
                  <LinearProgress variant="determinate" value={execution.progress} />
                </Box>
              )}
              <Divider />
            </React.Fragment>
          ))}
        </List>
      )}
    </Box>
  );

  const renderAnalyticsTab = () => (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        Workflow Analytics
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Executions
              </Typography>
              <Typography variant="h4">
                {executions.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h4">
                {executions.length > 0 
                  ? Math.round((executions.filter(e => e.status === 'completed').length / executions.length) * 100)
                  : 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Running
              </Typography>
              <Typography variant="h4">
                {executions.filter(e => e.status === 'running').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Failed
              </Typography>
              <Typography variant="h4">
                {executions.filter(e => e.status === 'failed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Alert severity="info" sx={{ mt: 2 }}>
        Analytics features are coming soon. This will include detailed performance metrics, 
        cost analysis, and workflow optimization insights.
      </Alert>
    </Box>
  );

  return (
    <PageLayout title="Workflow Management">
      {/* Breadcrumbs */}
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link underline="hover" color="inherit" href="/dashboard">
            Dashboard
          </Link>
          <Typography color="text.primary">Workflow Management</Typography>
        </Breadcrumbs>
        
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="workflow management tabs">
          <Tab label="Templates" icon={<WorkflowIcon />} />
          <Tab label="Builder" icon={<BuildIcon />} />
          <Tab label="Executions" icon={<SpeedIcon />} />
          <Tab label="Analytics" icon={<AnalyticsIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <TabPanel value={tabValue} index={0}>
          {renderTemplatesTab()}
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          {renderBuilderTab()}
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          {renderExecutionTab()}
        </TabPanel>
        <TabPanel value={tabValue} index={3}>
          {renderAnalyticsTab()}
        </TabPanel>
      </Box>

      {/* Execute Template Dialog */}
      <Dialog 
        open={executeDialogOpen} 
        onClose={() => setExecuteDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Execute Workflow Template: {selectedTemplate}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Input Message"
            multiline
            rows={4}
            fullWidth
            variant="outlined"
            value={executionInput}
            onChange={(e) => setExecutionInput(e.target.value)}
            placeholder="Enter your message or prompt for the workflow..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleExecuteConfirm} 
            variant="contained"
            disabled={!executionInput.trim()}
          >
            Execute
          </Button>
        </DialogActions>
      </Dialog>

      {/* Builder Dialog */}
      <Dialog 
        open={builderDialogOpen} 
        onClose={() => setBuilderDialogOpen(false)}
        maxWidth="xl"
        fullWidth
        PaperProps={{
          sx: { height: '90vh' }
        }}
      >
        <DialogTitle>
          Visual Workflow Builder
        </DialogTitle>
        <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <WorkflowEditor 
            onSave={(workflow) => {
              try {
                // Save workflow to localStorage for persistence
                const savedWorkflows = JSON.parse(localStorage.getItem('customWorkflows') || '[]');
                const existingIndex = savedWorkflows.findIndex((w: any) => w.metadata.name === workflow.metadata.name);
                
                if (existingIndex >= 0) {
                  savedWorkflows[existingIndex] = workflow;
                } else {
                  savedWorkflows.push(workflow);
                }
                
                localStorage.setItem('customWorkflows', JSON.stringify(savedWorkflows));
                
                // Update local state to reflect the saved workflow  
                setCustomWorkflow({
                  name: workflow.metadata.name,
                  description: workflow.metadata.description,
                  type: 'sequential', // Map from workflow structure
                  steps: workflow.nodes.filter(node => node.type !== 'start').map(node => ({
                    id: node.id,
                    type: node.type,
                    config: node.data.config || {},
                  }))
                });
                
                toastService.success('Workflow saved successfully');
                setBuilderDialogOpen(false);
              } catch (error) {
                console.error('Error saving workflow:', error);
                toastService.error('Failed to save workflow');
              }
            }}
            onWorkflowChange={(workflow) => {
              // Update the current workflow state as user makes changes
              setCustomWorkflow({
                name: workflow.metadata.name,
                description: workflow.metadata.description,
                type: 'sequential',
                steps: workflow.nodes.filter(node => node.type !== 'start').map(node => ({
                  id: node.id,
                  type: node.type,
                  config: node.data.config || {},
                }))
              });
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBuilderDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default WorkflowManagementPage;