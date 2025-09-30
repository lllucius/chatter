import React, { useRef, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  Button,
} from '../utils/mui';
import { AddIcon, RefreshIcon, PlayArrowIcon, EditIcon } from '../utils/icons';
import { useNavigate } from 'react-router-dom';
import PageLayout from '../components/PageLayout';
import CrudDataTable, {
  CrudConfig,
  CrudService,
  CrudColumn,
  CrudDataTableRef,
} from '../components/CrudDataTable';
import { createCategoryChipRenderer } from '../components/CrudRenderers';
import { getSDK } from '../services/auth-service';
import {
  WorkflowTemplateResponse,
  WorkflowTemplateCreate,
  WorkflowTemplateUpdate,
} from 'chatter-sdk';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';
import { useWorkflowData } from '../hooks/useWorkflowData';

const WorkflowTemplatesPage: React.FC = () => {
  const navigate = useNavigate();
  const crudTableRef = useRef<CrudDataTableRef>(null);
  const [selectedTemplate, setSelectedTemplate] =
    useState<WorkflowTemplateResponse | null>(null);
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [executionInput, setExecutionInput] = useState('');

  // Use the workflow data hook
  const { executeTemplate } = useWorkflowData();

  // Handle template execution
  const handleExecuteTemplate = (template: WorkflowTemplateResponse) => {
    setSelectedTemplate(template);
    setExecuteDialogOpen(true);
    setExecutionInput('');
  };

  const handleEditTemplate = (template: WorkflowTemplateResponse) => {
    // Navigate to builder page with template data
    navigate('/workflows/builder', {
      state: {
        editTemplate: template,
        mode: 'edit',
      },
    });
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

      await executeTemplate(selectedTemplate.id, input);

      toastService.success('Workflow execution started');
      setExecuteDialogOpen(false);
    } catch (error) {
      handleError(error, {
        source: 'WorkflowTemplatesPage.handleExecuteWorkflow',
        operation: 'execute workflow template',
      });
    }
  };

  // Define table columns
  const columns: CrudColumn<WorkflowTemplateResponse>[] = [
    {
      id: 'name',
      label: 'Name',
      width: '200px',
      render: (name: unknown) => (
        <Typography variant="body2" fontWeight="medium">
          {String(name)}
        </Typography>
      ),
    },
    {
      id: 'description',
      label: 'Description',
      render: (description: unknown) => (
        <Typography variant="body2" color="text.secondary" noWrap>
          {String(description || '')}
        </Typography>
      ),
    },
    {
      id: 'category',
      label: 'Category',
      width: '120px',
      render: createCategoryChipRenderer<WorkflowTemplateResponse>(),
    },
    {
      id: 'version',
      label: 'Version',
      width: '100px',
      render: (version: unknown) => (
        <Typography variant="body2" color="text.secondary">
          v{String(version || '1')}
        </Typography>
      ),
    },
  ];

  // Define CRUD configuration
  const config: CrudConfig<WorkflowTemplateResponse> = {
    entityName: 'Template',
    entityNamePlural: 'Templates',
    columns,
    actions: [
      {
        icon: <PlayArrowIcon />,
        label: 'Execute',
        onClick: handleExecuteTemplate,
      },
      {
        icon: <EditIcon />,
        label: 'Edit',
        onClick: handleEditTemplate,
      },
    ],
    enableCreate: true,
    enableEdit: true,
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  // Define service methods
  const service: CrudService<
    WorkflowTemplateResponse,
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate
  > = {
    list: async (_page: number, _pageSize: number) => {
      const sdk = await getSDK();
      const response =
        await sdk.workflows.listWorkflowTemplatesApiV1WorkflowsTemplates();
      return {
        items: response.templates || [],
        total: response.total_count || 0,
      };
    },
    create: async (data: WorkflowTemplateCreate) => {
      const sdk = await getSDK();
      return await sdk.workflows.createWorkflowTemplateApiV1WorkflowsTemplates(
        data
      );
    },
    update: async (_id: string, data: WorkflowTemplateUpdate) => {
      const sdk = await getSDK();
      return await sdk.workflows.updateWorkflowTemplateApiV1WorkflowsTemplatesTemplateId(
        _id,
        data
      );
    },
    delete: async (_id: string) => {
      // Note: Delete method may not be available in API, will need to implement
      throw new Error('Delete not implemented for templates');
    },
  };

  // Toolbar content
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={() => crudTableRef.current?.handleRefresh()}
      >
        Refresh
      </Button>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => {
          // Navigate to builder page to create new template
          navigate('/workflows/builder', {
            state: {
              mode: 'create',
            },
          });
        }}
      >
        Create Template
      </Button>
    </>
  );

  return (
    <PageLayout title="Workflow Templates" toolbar={toolbar}>
      <CrudDataTable
        ref={crudTableRef}
        config={config}
        service={service}
        FormComponent={undefined} // Would need to implement a template form
        getItemId={(item) => item.id}
      />

      {/* Execute Template Dialog */}
      <Dialog
        open={executeDialogOpen}
        onClose={() => setExecuteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Execute Workflow Template</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Template: <strong>{selectedTemplate?.name}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Provide input data for the workflow execution (JSON format):
          </Typography>
          <Box
            component="textarea"
            sx={{
              width: '100%',
              minHeight: '150px',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              p: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              resize: 'vertical',
            }}
            value={executionInput}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
              setExecutionInput(e.target.value)
            }
            placeholder={`{\n  "message": "Hello, world!",\n  "options": {\n    "temperature": 0.7\n  }\n}`}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleExecuteWorkflow} variant="contained">
            Execute
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default WorkflowTemplatesPage;
