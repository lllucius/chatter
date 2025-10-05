import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  TabPanel,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Alert,
} from '../utils/mui';
import {
  AddIcon,
  RefreshIcon,
  WorkflowIcon,
  BuildIcon,
  SpeedIcon,
} from '../utils/icons';
import PageLayout from '../components/PageLayout';
import WorkflowTemplatesTab, {
  WorkflowTemplate,
} from '../components/workflow-management/WorkflowTemplatesTab';
import WorkflowExecutionsTab, {
  WorkflowExecution,
} from '../components/workflow-management/WorkflowExecutionsTab';
import WorkflowEditor, {
  WorkflowDefinition,
} from '../components/workflow/WorkflowEditor';
import { useWorkflowData } from '../hooks/useWorkflowData';
import { useFormGeneric } from '../hooks/useFormGeneric';
import { toastService } from '../services/toast-service';
import { WorkflowTemplateResponse } from 'chatter-sdk';

interface WorkflowFormData extends Record<string, unknown> {
  name: string;
  description: string;
  category: string;
}

const WorkflowManagementPage: React.FC = () => {
  const {
    loading,
    templates,
    availableTools: _availableTools,
    executions,
    selectedTemplate,
    setSelectedTemplate,
    loadTemplates,
    loadExecutions,
    createTemplate,
    // executeWorkflow,  // Not used
    executeTemplate,
    deleteTemplate,
  } = useWorkflowData();

  // UI state
  const [tabValue, setTabValue] = useState(0);
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [builderDialogOpen, setBuilderDialogOpen] = useState(false);
  const [executionInput, setExecutionInput] = useState('');
  const [editingTemplate, setEditingTemplate] =
    useState<WorkflowTemplateResponse | null>(null);

  // Form for template creation
  const templateForm = useFormGeneric<WorkflowFormData>({
    initialValues: {
      name: '',
      description: '',
      category: 'general',
    },
    onSubmit: async (values) => {
      try {
        // This would create a template with the workflow data
        const templateData = {
          ...values,
          // workflow field doesn't exist in WorkflowTemplateCreate
        } as unknown as WorkflowTemplateResponse;
        await createTemplate(templateData);
        toastService.success('Template created successfully');
        setBuilderDialogOpen(false);
      } catch {
        // Error handling is done in the hook
      }
    },
  });

  // Event handlers
  const handleExecuteTemplate = (templateId: string) => {
    setSelectedTemplate(templateId);
    setExecuteDialogOpen(true);
    setExecutionInput('');
  };

  const handleEditTemplate = (template: WorkflowTemplateResponse) => {
    setEditingTemplate(template);
    templateForm.setValues({
      name: template.name || '',
      description: template.description || '',
      category: template.category || 'general',
    });
    setBuilderDialogOpen(true);
  };

  const handleDeleteTemplate = async (templateId: string) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      await deleteTemplate(templateId);
      toastService.success('Template deleted successfully');
    }
  };

  const handleExecuteWorkflow = async () => {
    if (!selectedTemplate) return;

    try {
      let input;
      try {
        input = executionInput.trim() ? JSON.parse(executionInput) : {};
      } catch {
        toastService.error('Invalid JSON input');
        return;
      }

      await executeTemplate(selectedTemplate, input);
      toastService.success('Workflow execution started');
      setExecuteDialogOpen(false);
      setTabValue(2); // Switch to executions tab
    } catch {
      // Error handling is done in the hook
    }
  };

  const handleRefresh = () => {
    loadTemplates();
    loadExecutions();
  };

  // Toolbar
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={handleRefresh}
        disabled={loading}
      >
        Refresh
      </Button>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => {
          setEditingTemplate(null);
          templateForm.reset();
          setBuilderDialogOpen(true);
        }}
      >
        Create Template
      </Button>
    </>
  );

  return (
    <PageLayout title="Workflow Management" toolbar={toolbar}>
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={(_, newValue) => setTabValue(newValue)}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab
              label="Templates"
              icon={<WorkflowIcon />}
              iconPosition="start"
            />
            <Tab label="Builder" icon={<BuildIcon />} iconPosition="start" />
            <Tab label="Executions" icon={<SpeedIcon />} iconPosition="start" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0} idPrefix="workflow">
          <WorkflowTemplatesTab
            templates={templates as unknown as WorkflowTemplate[]}
            loading={loading}
            onExecuteTemplate={handleExecuteTemplate}
            onEditTemplate={
              handleEditTemplate as unknown as (template: WorkflowTemplate) => void
            }
            onDeleteTemplate={handleDeleteTemplate}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1} idPrefix="workflow">
          <Alert severity="info" sx={{ mb: 2 }}>
            Use the &quot;Create Template&quot; button to open the workflow
            builder in a dialog.
          </Alert>
        </TabPanel>

        <TabPanel value={tabValue} index={2} idPrefix="workflow">
          <WorkflowExecutionsTab
            executions={executions as unknown as WorkflowExecution[]}
            loading={loading}
          />
        </TabPanel>
      </Box>

      {/* Execute Workflow Dialog */}
      <Dialog
        open={executeDialogOpen}
        onClose={() => setExecuteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Execute Workflow</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Provide input data for the workflow execution (JSON format):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Input Data (JSON)"
            value={executionInput}
            onChange={(e) => setExecutionInput(e.target.value)}
            placeholder='{\n  "message": "Hello, world!",\n  "options": {\n    "temperature": 0.7\n  }\n}'
            sx={{ fontFamily: 'monospace' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleExecuteWorkflow}
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Executing...' : 'Execute'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Workflow Builder Dialog */}
      <Dialog
        open={builderDialogOpen}
        onClose={() => setBuilderDialogOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{ sx: { height: '90vh' } }}
      >
        <DialogTitle>
          {editingTemplate
            ? 'Edit Workflow Template'
            : 'Create Workflow Template'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              label="Template Name"
              value={templateForm.values.name}
              onChange={(e) =>
                templateForm.handleChange('name', e.target.value)
              }
              error={Boolean(templateForm.errors.name)}
              helperText={templateForm.errors.name}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Description"
              multiline
              rows={2}
              value={templateForm.values.description}
              onChange={(e) =>
                templateForm.handleChange('description', e.target.value)
              }
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Category"
              value={templateForm.values.category}
              onChange={(e) =>
                templateForm.handleChange('category', e.target.value)
              }
            />
          </Box>

          <Box
            sx={{
              height: '60vh',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
            }}
          >
            <WorkflowEditor
              initialWorkflow={
                editingTemplate
                  ? ((editingTemplate as unknown as WorkflowTemplate)
                      .workflow as unknown as WorkflowDefinition)
                  : undefined
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBuilderDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={templateForm.handleSubmit}
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Saving...' : editingTemplate ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default WorkflowManagementPage;
