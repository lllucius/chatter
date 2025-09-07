import React, { useState } from 'react';
import { Box, Tabs, Tab, Typography, Chip, Button } from '@mui/material';
import { 
  Refresh as RefreshIcon, 
  Add as AddIcon,
  Storage as ServersIcon,
  Build as ToolsIcon,
  PowerSettingsNew as ToggleIcon,
} from '@mui/icons-material';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudAction } from '../components/CrudDataTable';
import RemoteServerForm from '../components/RemoteServerForm';
import { chatterSDK } from '../services/chatter-sdk';
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

const ToolsPageRefactored: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Remote Server columns and config
  const serverColumns: CrudColumn<RemoteServer>[] = [
    {
      id: 'display_name',
      label: 'Name',
      render: (value, item) => (
        <Box>
          <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
            {value}
          </Typography>
          {item.description && (
            <Typography variant="body2" color="text.secondary">
              {item.description}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      id: 'base_url',
      label: 'URL',
      render: (value) => (
        <Typography variant="body2">
          {value}
        </Typography>
      ),
    },
    {
      id: 'transport_type',
      label: 'Transport',
      render: (value) => (
        <Chip 
          label={value.toUpperCase()} 
          variant="outlined"
          size="small"
        />
      ),
    },
    {
      id: 'status',
      label: 'Status',
      render: (value) => (
        <Chip 
          label={value} 
          color={value === 'enabled' ? 'success' : value === 'error' ? 'error' : 'default'}
          size="small"
        />
      ),
    },
    {
      id: 'tools_count',
      label: 'Tools',
      render: (value) => (
        <Typography variant="body2">
          {value !== undefined ? `${value} tools` : 'Unknown'}
        </Typography>
      ),
    },
    {
      id: 'oauth_config',
      label: 'Security',
      render: (value) => (
        value ? (
          <Chip 
            label="OAuth" 
            color="primary"
            variant="outlined"
            size="small"
          />
        ) : null
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
            await chatterSDK.disableToolServer(server.id);
            toastService.success('Server disabled successfully');
          } else {
            await chatterSDK.enableToolServer(server.id);
            toastService.success('Server enabled successfully');
          }
        } catch (error) {
          toastService.error('Failed to toggle server status');
        }
      },
    },
    {
      icon: <RefreshIcon />,
      label: 'Refresh Tools',
      onClick: async (server) => {
        try {
          await chatterSDK.refreshServerTools(server.id);
          toastService.success('Server tools refreshed successfully');
        } catch (error) {
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
    list: async (page: number, pageSize: number) => {
      const response = await chatterSDK.getToolServers();
      return {
        items: response.data || [],
        total: response.data?.length || 0,
      };
    },

    create: async (data: RemoteServerCreate) => {
      const response = await chatterSDK.createToolServer(data);
      return response.data;
    },

    update: async (id: string, data: RemoteServerUpdate) => {
      const response = await chatterSDK.updateToolServer(id, data);
      return response.data;
    },

    delete: async (id: string) => {
      await chatterSDK.deleteToolServer(id);
    },
  };

  // Tool columns and config
  const toolColumns: CrudColumn<Tool>[] = [
    {
      id: 'display_name',
      label: 'Name',
      render: (value, item) => (
        <Box>
          <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
            {value || item.name}
          </Typography>
          {item.description && (
            <Typography variant="body2" color="text.secondary">
              {item.description}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      id: 'server_name',
      label: 'Server',
      render: (value) => (
        <Typography variant="body2">
          {value}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      render: (value, item) => (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip 
            label={value} 
            color={value === 'enabled' ? 'success' : value === 'error' ? 'error' : 'default'}
            size="small"
          />
          {!item.is_available && (
            <Chip label="Unavailable" color="warning" size="small" />
          )}
        </Box>
      ),
    },
    {
      id: 'total_calls',
      label: 'Usage',
      render: (value, item) => (
        <Box>
          <Typography variant="body2">
            Calls: {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Errors: {item.total_errors}
          </Typography>
        </Box>
      ),
    },
    {
      id: 'avg_response_time_ms',
      label: 'Performance',
      render: (value) => (
        <Typography variant="body2">
          {value ? `${value.toFixed(0)}ms` : 'N/A'}
        </Typography>
      ),
    },
  ];

  const toolActions: CrudAction<Tool>[] = [
    {
      icon: <ToggleIcon />,
      label: 'Toggle Status',
      onClick: async (tool) => {
        try {
          if (tool.status === 'enabled') {
            await chatterSDK.disableTool(tool.id);
            toastService.success('Tool disabled successfully');
          } else {
            await chatterSDK.enableTool(tool.id);
            toastService.success('Tool enabled successfully');
          }
        } catch (error) {
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
    list: async (page: number, pageSize: number) => {
      const response = await chatterSDK.getAllTools();
      return {
        items: response.data || [],
        total: response.data?.length || 0,
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
          // The CRUD table handles its own refresh
        }}
      >
        Refresh
      </Button>
      {activeTab === 0 && (
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            // The CRUD table handles creation
          }}
        >
          Add Remote Server
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
          config={serverConfig}
          service={serverService}
          FormComponent={RemoteServerForm}
          getItemId={getServerId}
        />
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <CrudDataTable
          config={toolConfig}
          service={toolService}
          getItemId={getToolId}
        />
      </TabPanel>
    </PageLayout>
  );
};

export default ToolsPageRefactored;