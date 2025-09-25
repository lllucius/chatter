import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '../utils/mui';
import {
  AddIcon,
  RefreshIcon,
} from '../utils/icons';
import PageLayout from '../components/PageLayout';
import WorkflowTemplatesTab from '../components/workflow-management/WorkflowTemplatesTab';
import { useWorkflowData } from '../hooks/useWorkflowData';
import { useFormGeneric } from '../hooks/useFormGeneric';
import { toastService } from '../services/toast-service';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  workflow: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface WorkflowFormData extends Record<string, unknown> {
  name: string;
  description: string;
  category: string;
}

const WorkflowTemplatesPage: React.FC = () => {
  const {
    loading,
    templates: templateResponses,
    selectedTemplate,
    setSelectedTemplate,
    loadTemplates,
    createTemplate,
    executeTemplate,
    deleteTemplate,
  } = useWorkflowData();

  // Convert WorkflowTemplateResponse to WorkflowTemplate format expected by the tab
  const templates: WorkflowTemplate[] = templateResponses.map(template => ({
    id: template.id || '',
    name: template.name || 'Untitled',
    description: template.description || '',
    category: template.category || 'general',
    workflow: template.workflow || {},
    created_at: template.created_at || new Date().toISOString(),
    updated_at: template.updated_at || new Date().toISOString(),
  }));

  // UI state
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [executionInput, setExecutionInput] = useState('');

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
          workflow: {}, // Would come from workflow editor
        } as any;
        await createTemplate(templateData);
        toastService.success('Template created successfully');
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

  const handleEditTemplate = (template: WorkflowTemplate) => {
    // Navigate to builder with template
    window.location.href = `/workflows/builder?template=${template.id}`;
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
      // Navigate to executions tab
      window.location.href = '/workflows/executions';
    } catch {
      // Error handling is done in the hook
    }
  };

  const handleRefresh = () => {
    loadTemplates();
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
          // Navigate to builder to create new template
          window.location.href = '/workflows/builder';
        }}
      >
        Create Template
      </Button>
    </>
  );

  return (
    <PageLayout title="Workflow Templates" toolbar={toolbar}>
      <WorkflowTemplatesTab
        templates={templates}
        loading={loading}
        onExecuteTemplate={handleExecuteTemplate}
        onEditTemplate={handleEditTemplate}
        onDeleteTemplate={handleDeleteTemplate}
      />

      {/* Execute Workflow Dialog */}
      <Dialog
        open={executeDialogOpen}
        onClose={() => setExecuteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Execute Workflow</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Input Data (JSON)"
            value={executionInput}
            onChange={(e) => setExecutionInput(e.target.value)}
            placeholder='{\n  "message": "Hello, world!",\n  "options": {\n    "temperature": 0.7\n  }\n}'
            sx={{ fontFamily: 'monospace', mt: 2 }}
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
    </PageLayout>
  );
};

export default WorkflowTemplatesPage;