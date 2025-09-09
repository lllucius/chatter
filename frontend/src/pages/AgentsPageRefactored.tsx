import React, { useRef } from 'react';
import { Button } from '@mui/material';
import { 
  SmartToy as BotIcon,
  Refresh as RefreshIcon,
  Add as AddIcon
} from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudDataTableRef } from '../components/CrudDataTable';
import { 
  createNameWithDescriptionRenderer, 
  createBooleanSwitchRenderer,
  createDateRenderer 
} from '../components/CrudRenderers';
import { getSDK } from "../services/auth-service";
import { AgentResponse, AgentCreateRequest, AgentUpdateRequest } from 'chatter-sdk';

const AgentsPageRefactored: React.FC = () => {
  const crudTableRef = useRef<CrudDataTableRef>(null);
  // Define columns
  const columns: CrudColumn<AgentResponse>[] = [
    {
      id: 'name',
      label: 'Name',
      width: '200px',
      render: createNameWithDescriptionRenderer<AgentResponse>(),
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
      render: createBooleanSwitchRenderer<AgentResponse>(),
    },
    {
      id: 'updated_at',
      label: 'Updated',
      width: '140px',
      render: createDateRenderer<AgentResponse>(),
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
        onClick: () => {
          // TODO: Implement test agent functionality
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
      const response = await getSDK().agents.listAgentsApiV1Agents({
        page: page + 1,
        per_page: pageSize,
      });
      return {
        items: response.data || [],
        total: response.data?.length || 0, // Adjust based on actual API response
      };
    },

    create: async (data: AgentCreateRequest) => {
      const response = await getSDK().agents.createAgentApiV1Agents(data);
      return response.data;
    },

    update: async (id: string, data: AgentUpdateRequest) => {
      const response = await getSDK().agents.updateAgentApiV1AgentsAgentId(
        id,
        data
      );
      return response.data;
    },

    delete: async (id: string) => {
      await getSDK().agents.deleteAgentApiV1AgentsAgentIdDelete({
        agentId: id,
      });
    },
  };

  const getItemId = (item: AgentResponse) => item.id || '';

  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={() => crudTableRef.current?.handleRefresh()}
        size="small"
      >
        Refresh
      </Button>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => crudTableRef.current?.handleCreate()}
        size="small"
      >
        Add Agent
      </Button>
    </>
  );

  return (
    <PageLayout title="AI Agents" toolbar={toolbar}>
      <CrudDataTable
        ref={crudTableRef}
        config={config}
        service={service}
        getItemId={getItemId}
        // Note: Form component would be created similar to PromptForm
      />
    </PageLayout>
  );
};

export default AgentsPageRefactored;
