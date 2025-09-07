import React from 'react';
import { Chip } from '@mui/material';
import { Code as CodeIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn } from '../components/CrudDataTable';
import PromptForm from '../components/PromptForm';
import { chatterSDK } from '../services/chatter-sdk';
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
      render: (value) => (
        <Chip 
          label={value} 
          size="small" 
          color="primary" 
          variant="outlined" 
        />
      ),
    },
    {
      id: 'prompt_type',
      label: 'Type',
      width: '120px',
      render: (value) => (
        <Chip 
          label={value?.replace('_', ' ')} 
          size="small" 
          color="secondary" 
          variant="outlined" 
        />
      ),
    },
    {
      id: 'variables',
      label: 'Variables',
      width: '150px',
      render: (variables) => (
        variables?.length > 0 ? `${variables.length} variables` : 'None'
      ),
    },
    {
      id: 'updated_at',
      label: 'Updated',
      width: '140px',
      render: (value) => value ? format(new Date(value), 'MMM dd, yyyy') : '',
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
        onClick: (prompt) => {
          // Handle view code action
          console.log('View code for:', prompt.name);
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
      const response = await chatterSDK.prompts.listPromptsApiV1PromptsGet({
        page: page + 1, // API is 1-based, component is 0-based
        per_page: pageSize,
      });
      return {
        items: response.data.prompts || [],
        total: response.data.total || 0,
      };
    },

    create: async (data: PromptCreate) => {
      const response = await chatterSDK.prompts.createPromptApiV1PromptsPost({
        promptCreate: data,
      });
      return response.data;
    },

    update: async (id: string, data: PromptUpdate) => {
      const response = await chatterSDK.prompts.updatePromptApiV1PromptsPromptIdPut({
        promptId: id,
        promptUpdate: data,
      });
      return response.data;
    },

    delete: async (id: string) => {
      await chatterSDK.prompts.deletePromptApiV1PromptsPromptIdDelete({
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