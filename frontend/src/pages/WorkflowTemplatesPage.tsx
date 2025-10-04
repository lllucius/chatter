import React, { useRef, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  Button,
  TextField,
} from '../utils/mui';
import {
  AddIcon,
  RefreshIcon,
  PlayArrowIcon,
  EditIcon,
  DownloadIcon,
  UploadIcon,
} from '../utils/icons';
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
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importData, setImportData] = useState('');
  const [importName, setImportName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Use the workflow data hook
  const { executeTemplate } = useWorkflowData();

  // Handle template export
  const handleExportTemplate = async (template: WorkflowTemplateResponse) => {
    try {
      const sdk = await getSDK();
      const response =
        await sdk.workflows.exportWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdExport(
          template.id
        );

      // Download as JSON file
      const blob = new Blob([JSON.stringify(response.template, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${template.name.replace(/\s+/g, '_')}_template.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toastService.success('Template exported successfully');
    } catch (error) {
      handleError(error, {
        source: 'WorkflowTemplatesPage.handleExportTemplate',
        operation: 'export template',
      });
    }
  };

  // Handle import from file
  const handleImportFromFile = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      setImportData(text);
      setImportDialogOpen(true);

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      handleError(error, {
        source: 'WorkflowTemplatesPage.handleFileChange',
        operation: 'read import file',
      });
    }
  };

  const handleImportTemplate = async () => {
    try {
      let templateData;
      try {
        templateData = JSON.parse(importData);
      } catch {
        toastService.error('Invalid JSON format');
        return;
      }

      const sdk = await getSDK();
      await sdk.workflows.importWorkflowTemplateApiV1WorkflowsTemplatesImport({
        template: templateData,
        override_name: importName || undefined,
        merge_with_existing: false,
      });

      toastService.success('Template imported successfully');
      setImportDialogOpen(false);
      setImportData('');
      setImportName('');
      crudTableRef.current?.handleRefresh();
    } catch (error) {
      handleError(error, {
        source: 'WorkflowTemplatesPage.handleImportTemplate',
        operation: 'import template',
      });
    }
  };

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
      {
        icon: <DownloadIcon />,
        label: 'Export',
        onClick: handleExportTemplate,
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
        variant="outlined"
        startIcon={<UploadIcon />}
        onClick={handleImportFromFile}
      >
        Import
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
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".json"
        onChange={handleFileChange}
      />
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

      {/* Import Template Dialog */}
      <Dialog
        open={importDialogOpen}
        onClose={() => setImportDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Import Workflow Template</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Override Name (optional)"
            value={importName}
            onChange={(e) => setImportName(e.target.value)}
            sx={{ mb: 2, mt: 1 }}
            helperText="Leave empty to use the template's original name"
          />
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Template Data (JSON):
          </Typography>
          <Box
            component="textarea"
            sx={{
              width: '100%',
              minHeight: '300px',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              p: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              resize: 'vertical',
            }}
            value={importData}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
              setImportData(e.target.value)
            }
            placeholder="Paste template JSON data here..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleImportTemplate} variant="contained">
            Import
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default WorkflowTemplatesPage;
