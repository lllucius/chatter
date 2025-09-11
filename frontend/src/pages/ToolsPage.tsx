import React, { useState, useRef } from 'react';
import { Box, Tabs, Tab, Chip, Button } from '@mui/material';
import { 
  Refresh as RefreshIcon, 
  Add as AddIcon,
  Storage as ServersIcon,
  Build as ToolsIcon,
  PowerSettingsNew as ToggleIcon,
} from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudAction, CrudDataTableRef } from '../components/CrudDataTable';
import RemoteServerForm from '../components/RemoteServerForm';
import { 
  createNameWithDescriptionRenderer, 
  createTypeChipRenderer,
  createStatusChipRenderer,
  createCountRenderer,
  createConditionalChipRenderer,
  createUsageStatsRenderer,
  createPerformanceRenderer 
} from '../components/CrudRenderers';
import { getSDK } from "../services/auth-service";
import { toastService } from '../services/toast-service';

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
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

// Define interfaces based on the original ToolsPage
interface RemoteServer {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  base_url: string;
  transport_type: 'http' | 'sse';
  status: 'enabled' | 'disabled' | 'error' | 'starting' | 'stopping';
  oauth_config?: {
    client_id: string;
    client_secret: string;
    token_url: string;
    scope?: string;
  };
  headers?: Record<string, string>;
  timeout: number;
  auto_start: boolean;
  tools_count?: number;
  last_health_check?: string;
  created_at: string;
  updated_at: string;
}

interface Tool {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  server_name: string;
  status: 'enabled' | 'disabled' | 'unavailable' | 'error';
  is_available: boolean;
  total_calls: number;
  total_errors: number;
  avg_response_time_ms?: number;
  last_called?: string;
}

interface RemoteServerCreate {
  name: string;
  display_name: string;
  description?: string;
  base_url: string;
  transport_type: 'http' | 'sse';
  oauth_config?: {
    client_id: string;
    client_secret: string;
    token_url: string;
    scope?: string;
  };
  headers?: Record<string, string>;
  timeout: number;
  auto_start: boolean;
}

interface RemoteServerUpdate {
  display_name?: string;
  description?: string;
  timeout?: number;
  auto_start?: boolean;
  oauth_config?: {
    client_id: string;
    client_secret: string;
    token_url: string;
    scope?: string;
  };
  headers?: Record<string, string>;
}

const ToolsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const serverCrudRef = useRef<CrudDataTableRef>(null);
  const toolCrudRef = useRef<CrudDataTableRef>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Remote Server columns and config
  const serverColumns: CrudColumn<RemoteServer>[] = [
    {
      id: 'display_name',
      label: 'Name',
      render: createNameWithDescriptionRenderer<RemoteServer>(),
    },
    {
      id: 'base_url',
      label: 'URL',
    },
    {
      id: 'transport_type',
      label: 'Transport',
      render: createTypeChipRenderer<RemoteServer>('default', 'outlined'),
    },
    {
      id: 'status',
      label: 'Status',
      render: createStatusChipRenderer<RemoteServer>(),
    },
    {
      id: 'tools_count',
      label: 'Tools',
      render: createCountRenderer<RemoteServer>('tool', 'tools', 'Unknown'),
    },
    {
      id: 'oauth_config',
      label: 'Security',
      render: createConditionalChipRenderer<RemoteServer>(
        (value) => !!value,
        'OAuth',
        'primary',
        'outlined'
      ),
    },
  ];

  const serverActions: CrudAction<RemoteServer>[] = [
    {
      icon: <ToggleIcon />,
      label: 'Toggle Status',
      onClick: async (server) => {
        try {
          if (server.status === 'enabled') {
            await getSDK().toolServers.disableToolServerApiV1ToolserversServersServerIdDisable(server.id);
            toastService.success('Server disabled successfully');
          } else {
            await getSDK().toolServers.enableToolServerApiV1ToolserversServersServerIdEnable(server.id);
            toastService.success('Server enabled successfully');
          }
          // Refresh the data after toggle
          serverCrudRef.current?.handleRefresh();
        } catch {
          toastService.error('Failed to toggle server status');
        }
      },
    },
    {
      icon: <RefreshIcon />,
      label: 'Refresh Tools',
      onClick: async (server) => {
        try {
          await getSDK().toolServers.refreshServerToolsApiV1ToolserversServersServerIdRefreshTools(server.id);
          toastService.success('Server tools refreshed successfully');
          // Refresh the data after refreshing tools
          serverCrudRef.current?.handleRefresh();
        } catch {
          toastService.error('Failed to refresh server tools');
        }
      },
    },
  ];

  const serverConfig: CrudConfig<RemoteServer> = {
    entityName: 'Remote Server',
    entityNamePlural: 'Remote Servers',
    columns: serverColumns,
    actions: serverActions,
    enableCreate: true,
    enableEdit: true,
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  const serverService: CrudService<RemoteServer, RemoteServerCreate, RemoteServerUpdate> = {
    list: async () => {
      const response = await getSDK().toolServers.listToolServersApiV1ToolserversServers({});
      return {
        items: response || [],
        total: response?.length || 0,
      };
    },

    create: async (data: RemoteServerCreate) => {
      const response = await getSDK().toolServers.createToolServerApiV1ToolserversServers({
        toolServerCreate: data,
      });
      return response;
    },

    update: async (id: string, data: RemoteServerUpdate) => {
      const response = await getSDK().toolServers.updateToolServerApiV1ToolserversServersServerId(id, data);
      return response;
    },

    delete: async (id: string) => {
      await getSDK().toolServers.deleteToolServerApiV1ToolserversServersServerId(id);
    },
  };

  // Tool columns and config
  const toolColumns: CrudColumn<Tool>[] = [
    {
      id: 'display_name',
      label: 'Name',
      render: createNameWithDescriptionRenderer<Tool>(),
    },
    {
      id: 'server_name',
      label: 'Server',
    },
    {
      id: 'status',
      label: 'Status',
      render: (value, item) => (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {createStatusChipRenderer<Tool>()(value, item)}
          {!item.is_available && (
            <Chip label="Unavailable" color="warning" size="small" />
          )}
        </Box>
      ),
    },
    {
      id: 'total_calls',
      label: 'Usage',
      render: createUsageStatsRenderer<Tool>(),
    },
    {
      id: 'avg_response_time_ms',
      label: 'Performance',
      render: createPerformanceRenderer<Tool>('ms', 0),
    },
  ];

  const toolActions: CrudAction<Tool>[] = [
    {
      icon: <ToggleIcon />,
      label: 'Toggle Status',
      onClick: async (tool) => {
        try {
          if (tool.status === 'enabled') {
            await getSDK().toolServers.disableToolApiV1ToolserversToolsToolIdDisable(tool.id);
            toastService.success('Tool disabled successfully');
          } else {
            await getSDK().toolServers.enableToolApiV1ToolserversToolsToolIdEnable(tool.id);
            toastService.success('Tool enabled successfully');
          }
          // Refresh the data after toggle
          toolCrudRef.current?.handleRefresh();
        } catch {
          toastService.error('Failed to toggle tool status');
        }
      },
    },
  ];

  const toolConfig: CrudConfig<Tool> = {
    entityName: 'Tool',
    entityNamePlural: 'Tools',
    columns: toolColumns,
    actions: toolActions,
    enableCreate: false, // Tools are managed by servers
    enableEdit: false,
    enableDelete: false,
    enableRefresh: true,
    pageSize: 10,
  };

  const toolService: CrudService<Tool, any, any> = {
    list: async () => {
      const response = await getSDK().toolServers.listAllToolsApiV1ToolserversToolsAll();
      return {
        items: response || [],
        total: response?.length || 0,
      };
    },
  };

  const getServerId = (item: RemoteServer) => item.id || '';
  const getToolId = (item: Tool) => item.id || '';

  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={() => {
          if (activeTab === 0) {
            serverCrudRef.current?.handleRefresh();
          } else {
            toolCrudRef.current?.handleRefresh();
          }
        }}
        size="small"
      >
        Refresh
      </Button>
      {activeTab === 0 && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => serverCrudRef.current?.handleCreate()}
          size="small"
        >
          Add Remote Server
        </Button>
      )}
      {activeTab === 1 && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => toolCrudRef.current?.handleCreate()}
          size="small"
        >
          Add Tool
        </Button>
      )}
    </>
  );

  return (
    <PageLayout title="Tool Server Management" toolbar={toolbar}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab 
            label="Remote Servers" 
            icon={<ServersIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Available Tools" 
            icon={<ToolsIcon />} 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        <CrudDataTable
          ref={serverCrudRef}
          config={serverConfig}
          service={serverService}
          FormComponent={RemoteServerForm}
          getItemId={getServerId}
        />
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <CrudDataTable
          ref={toolCrudRef}
          config={toolConfig}
          service={toolService}
          getItemId={getToolId}
        />
      </TabPanel>
    </PageLayout>
  );
};

export default ToolsPage;
