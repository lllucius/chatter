import React, { useRef, useState } from 'react';
import { 
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert
} from '../utils/mui';
import { 
  AgentIcon,
  RefreshIcon,
  AddIcon,
  SendIcon
} from '../utils/icons';
import PageLayout from '../components/PageLayout';
import { CrudPageHeader } from '../components/PageHeader';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudDataTableRef } from '../components/CrudDataTable';
import { 
  createNameWithDescriptionRenderer, 
  createBooleanSwitchRenderer,
  createDateRenderer 
} from '../components/CrudRenderers';
import AgentForm from '../components/AgentForm';
import { getSDK } from "../services/auth-service";
import { AgentResponse, AgentCreateRequest, AgentUpdateRequest, AgentInteractRequest, AgentInteractResponse } from 'chatter-sdk';

const AgentsPage: React.FC = () => {
  const crudTableRef = useRef<CrudDataTableRef>(null);

  // State for test agent dialog
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentResponse | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [testResponse, setTestResponse] = useState<AgentInteractResponse | null>(null);
  const [testing, setTesting] = useState(false);
  const [testError, setTestError] = useState<string | null>(null);

  // Handle test agent action
  const handleTestAgent = (agent: AgentResponse) => {
    setSelectedAgent(agent);
    setTestMessage('');
    setTestResponse(null);
    setTestError(null);
    setTestDialogOpen(true);
  };

  // Handle sending test message
  const handleSendTestMessage = async () => {
    if (!selectedAgent || !testMessage.trim()) return;

    setTesting(true);
    setTestError(null);
    setTestResponse(null);

    try {
      // Generate a test conversation ID
      const conversationId = `test-${Date.now()}`;
      
      const request: AgentInteractRequest = {
        message: testMessage.trim(),
        conversation_id: conversationId,
        context: {
          test: true,
          source: 'agent_test_page'
        }
      };

      const response = await getSDK().agents.interactWithAgentApiV1AgentsAgentIdInteract(
        selectedAgent.id,
        request
      );
      
      setTestResponse(response.data);
    } catch (error: unknown) {
      setTestError(error.message || 'Failed to test agent');
    } finally {
      setTesting(false);
    }
  };
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
        icon: <AgentIcon />,
        label: 'Test Agent',
        onClick: (agent: AgentResponse) => {
          handleTestAgent(agent);
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
        pagination: {
          limit: pageSize,
          offset: page * pageSize,
        },
      });
      return {
        items: response.agents || [],
        total: response.total || 0,
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
      await getSDK().agents.deleteAgentApiV1AgentsAgentId(id);
    },
  };

  const getItemId = (item: AgentResponse) => item.id || '';

  return (
    <PageLayout title="AI Agents">
      <CrudPageHeader
        entityName="Agent"
        onRefresh={() => crudTableRef.current?.handleRefresh()}
        onAdd={() => crudTableRef.current?.handleCreate()}
      />
      <CrudDataTable
        ref={crudTableRef}
        config={config}
        service={service}
        getItemId={getItemId}
        FormComponent={AgentForm}
      />
      
      {/* Test Agent Dialog */}
      <Dialog 
        open={testDialogOpen} 
        onClose={() => setTestDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          {selectedAgent && (
            <Box>
              <Typography variant="h6" component="span">
                Test Agent: {selectedAgent.name}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Chip 
                  label={selectedAgent.type} 
                  size="small" 
                  sx={{ mr: 1 }}
                />
                <Chip 
                  label={selectedAgent.status} 
                  size="small" 
                  color={selectedAgent.status === 'active' ? 'success' : 'default'}
                />
                <Chip 
                  label={selectedAgent.primary_llm} 
                  size="small" 
                  color="info"
                  sx={{ ml: 1 }}
                />
              </Box>
            </Box>
          )}
        </DialogTitle>
        <DialogContent>
          {selectedAgent && (
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {selectedAgent.description}
              </Typography>
              
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Test Message"
                placeholder="Enter a message to test the agent..."
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                sx={{ mb: 2 }}
                disabled={testing}
              />
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                <Button
                  variant="contained"
                  startIcon={testing ? <CircularProgress size={16} /> : <SendIcon />}
                  onClick={handleSendTestMessage}
                  disabled={!testMessage.trim() || testing}
                >
                  {testing ? 'Testing...' : 'Send Test Message'}
                </Button>
              </Box>
              
              {testError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {testError}
                </Alert>
              )}
              
              {testResponse && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                    Agent Response:
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: 'grey.100',
                      padding: 2,
                      borderRadius: 1,
                      mb: 2
                    }}
                  >
                    <Typography variant="body2">
                      {testResponse.response}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                    <Chip 
                      label={`Confidence: ${(testResponse.confidence_score * 100).toFixed(1)}%`}
                      size="small"
                      color="info"
                    />
                    <Chip 
                      label={`Response time: ${testResponse.response_time.toFixed(2)}s`}
                      size="small"
                      color="secondary"
                    />
                    {testResponse.tools_used.length > 0 && (
                      <Chip 
                        label={`Tools: ${testResponse.tools_used.join(', ')}`}
                        size="small"
                        color="primary"
                      />
                    )}
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default AgentsPage;
