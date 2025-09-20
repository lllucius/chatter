import React, { useRef, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  Chip,
  Button,
} from '../utils/mui';
import { CodeIcon, RefreshIcon, AddIcon } from '../utils/icons';
import PageLayout from '../components/PageLayout';
import { CrudPageHeader } from '../components/PageHeader';
import CrudDataTable, {
  CrudConfig,
  CrudService,
  CrudColumn,
  CrudDataTableRef,
} from '../components/CrudDataTable';
import PromptForm from '../components/PromptForm';
import {
  createCategoryChipRenderer,
  createTypeChipRenderer,
  createDateRenderer,
} from '../components/CrudRenderers';
import { getSDK } from '../services/auth-service';
import { PromptResponse, PromptCreate, PromptUpdate } from 'chatter-sdk';

const PromptsPage: React.FC = () => {
  const crudTableRef = useRef<CrudDataTableRef>(null);

  // State for view code dialog
  const [codeDialogOpen, setCodeDialogOpen] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState<PromptResponse | null>(
    null
  );

  // Handle view code action
  const handleViewCode = (prompt: PromptResponse) => {
    setSelectedPrompt(prompt);
    setCodeDialogOpen(true);
  };
  // Define columns
  const columns: CrudColumn<PromptResponse>[] = [
    {
      id: 'name',
      label: 'Name',
      width: '200px',
    },
    {
      id: 'description',
      label: 'Description',
      width: '300px',
    },
    {
      id: 'category',
      label: 'Category',
      width: '120px',
      render: createCategoryChipRenderer<PromptResponse>('primary', 'outlined'),
    },
    {
      id: 'prompt_type',
      label: 'Type',
      width: '120px',
      render: createTypeChipRenderer<PromptResponse>('secondary', 'outlined'),
    },
    {
      id: 'variables',
      label: 'Variables',
      width: '150px',
      render: (variables: unknown) =>
        (variables as unknown[])?.length > 0
          ? `${(variables as unknown[]).length} variables`
          : 'None',
    },
    {
      id: 'updated_at',
      label: 'Updated',
      width: '140px',
      render: createDateRenderer<PromptResponse>(),
    },
  ];

  // Define CRUD configuration
  const config: CrudConfig<PromptResponse> = {
    entityName: 'Prompt',
    entityNamePlural: 'Prompts',
    columns,
    actions: [
      {
        icon: <CodeIcon />,
        label: 'View Code',
        onClick: (prompt: PromptResponse) => {
          handleViewCode(prompt);
        },
      },
    ],
    enableCreate: true,
    enableEdit: true,
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  // Define service methods
  const service: CrudService<PromptResponse, PromptCreate, PromptUpdate> = {
    list: async (page: number, pageSize: number) => {
      const response = await getSDK().prompts.listPromptsApiV1Prompts({
        limit: pageSize,
        offset: page * pageSize,
      });
      return {
        items: response.prompts || [],
        total: response.total_count || 0,
      };
    },

    create: async (data: PromptCreate) => {
      const response = await getSDK().prompts.createPromptApiV1Prompts(data);
      return response;
    },

    update: async (id: string, data: PromptUpdate) => {
      const response = await getSDK().prompts.updatePromptApiV1PromptsPromptId(
        id,
        data
      );
      return response;
    },

    delete: async (id: string) => {
      await getSDK().prompts.deletePromptApiV1PromptsPromptId(id);
    },
  };

  const getItemId = (item: PromptResponse) => item.id;

  return (
    <PageLayout title="Prompts">
      <CrudPageHeader
        entityName="Prompt"
        onRefresh={() => crudTableRef.current?.handleRefresh()}
        onAdd={() => crudTableRef.current?.handleCreate()}
      />
      <CrudDataTable
        ref={crudTableRef}
        config={config}
        service={service}
        FormComponent={PromptForm}
        getItemId={getItemId}
      />

      {/* View Code Dialog */}
      <Dialog
        open={codeDialogOpen}
        onClose={() => setCodeDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedPrompt && (
            <Box>
              <Typography variant="h6" component="span">
                {selectedPrompt.name}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Chip
                  label={selectedPrompt.prompt_type}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={selectedPrompt.category}
                  size="small"
                  color="secondary"
                />
              </Box>
            </Box>
          )}
        </DialogTitle>
        <DialogContent>
          {selectedPrompt && (
            <Box>
              {selectedPrompt.description && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  {selectedPrompt.description}
                </Typography>
              )}

              <Typography
                variant="subtitle2"
                sx={{ mb: 1, fontWeight: 'bold' }}
              >
                Template Content:
              </Typography>
              <Box
                component="pre"
                sx={{
                  backgroundColor: 'grey.100',
                  padding: 2,
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: '400px',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {selectedPrompt.content}
              </Box>

              {selectedPrompt.variables &&
                selectedPrompt.variables.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography
                      variant="subtitle2"
                      sx={{ mb: 1, fontWeight: 'bold' }}
                    >
                      Template Variables:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selectedPrompt.variables.map((variable, index) => (
                        <Chip
                          key={index}
                          label={`{${variable}}`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

              {selectedPrompt.examples &&
                selectedPrompt.examples.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography
                      variant="subtitle2"
                      sx={{ mb: 1, fontWeight: 'bold' }}
                    >
                      Examples:
                    </Typography>
                    <Box
                      component="pre"
                      sx={{
                        backgroundColor: 'grey.50',
                        padding: 1.5,
                        borderRadius: 1,
                        overflow: 'auto',
                        maxHeight: '200px',
                        fontFamily: 'monospace',
                        fontSize: '0.8rem',
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {JSON.stringify(selectedPrompt.examples, null, 2)}
                    </Box>
                  </Box>
                )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCodeDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default PromptsPage;
