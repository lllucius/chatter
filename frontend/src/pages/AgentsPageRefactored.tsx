import React from 'react';
import { Chip, Switch } from '@mui/material';
import { SmartToy as BotIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn } from '../components/CrudDataTable';
import { chatterSDK } from '../services/chatter-sdk';
import { AgentResponse, AgentCreateRequest, AgentUpdateRequest } from '../sdk';

const AgentsPageRefactored: React.FC = () => {
  // Define columns
  const columns: CrudColumn<AgentResponse>[] = [
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
      id: 'model',
      label: 'Model',
      width: '150px',
    },
    {
      id: 'is_active',
      label: 'Active',
      width: '100px',
      render: (value) => (
        <Switch
          checked={!!value}
          disabled
          size="small"
        />
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
  const config: CrudConfig<AgentResponse> = {
    entityName: 'Agent',
    entityNamePlural: 'Agents',
    columns,
    actions: [
      {
        icon: <BotIcon />,
        label: 'Test Agent',
        onClick: (agent) => {
          console.log('Test agent:', agent.name);
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
  const service: CrudService<AgentResponse, AgentCreateRequest, AgentUpdateRequest> = {
    list: async (page: number, pageSize: number) => {
      const response = await chatterSDK.agents.listAgentsApiV1AgentsGet({
        page: page + 1,
        per_page: pageSize,
      });
      return {
        items: response.data || [],
        total: response.data?.length || 0, // Adjust based on actual API response
      };
    },

    create: async (data: AgentCreateRequest) => {
      const response = await chatterSDK.agents.createAgentApiV1AgentsPost({
        agentCreateRequest: data,
      });
      return response.data;
    },

    update: async (id: string, data: AgentUpdateRequest) => {
      const response = await chatterSDK.agents.updateAgentApiV1AgentsAgentIdPut({
        agentId: id,
        agentUpdateRequest: data,
      });
      return response.data;
    },

    delete: async (id: string) => {
      await chatterSDK.agents.deleteAgentApiV1AgentsAgentIdDelete({
        agentId: id,
      });
    },
  };

  const getItemId = (item: AgentResponse) => item.id || '';

  return (
    <PageLayout title="AI Agents">
      <CrudDataTable
        config={config}
        service={service}
        getItemId={getItemId}
        // Note: Form component would be created similar to PromptForm
      />
    </PageLayout>
  );
};

export default AgentsPageRefactored;