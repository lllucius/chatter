import React from 'react';
import { Code as CodeIcon } from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn } from '../components/CrudDataTable';
import PromptForm from '../components/PromptForm';
import { 
  createCategoryChipRenderer, 
  createTypeChipRenderer,
  createDateRenderer
} from '../components/CrudRenderers';
import { chatterClient } from '../sdk/client';
import { PromptResponse, PromptCreate, PromptUpdate } from '../sdk';

const PromptsPageRefactored: React.FC = () => {
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
      render: (variables: any[]) => (
        variables?.length > 0 ? `${variables.length} variables` : 'None'
      ),
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
        onClick: () => {
          // TODO: Implement view code functionality
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
      const response = await chatterClient.prompts.listPromptsApiV1PromptsGet({
        page: page + 1, // API is 1-based, component is 0-based
        per_page: pageSize,
      });
      return {
        items: response.prompts || [],
        total: response.totalCount || 0,
      };
    },

    create: async (data: PromptCreate) => {
      const response = await chatterClient.prompts.createPromptApiV1PromptsPost({
        promptCreate: data,
      });
      return response;
    },

    update: async (id: string, data: PromptUpdate) => {
      const response = await chatterClient.prompts.updatePromptApiV1PromptsPromptIdPut({
        promptId: id,
        promptUpdate: data,
      });
      return response;
    },

    delete: async (id: string) => {
      await chatterClient.prompts.deletePromptApiV1PromptsPromptIdDelete({
        promptId: id,
      });
    },
  };

  const getItemId = (item: PromptResponse) => item.id;

  return (
    <PageLayout title="Prompts">
      <CrudDataTable
        config={config}
        service={service}
        FormComponent={PromptForm}
        getItemId={getItemId}
      />
    </PageLayout>
  );
};

export default PromptsPageRefactored;