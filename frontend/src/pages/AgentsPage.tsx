import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  IconButton,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { chatterSDK } from '../services/chatter-sdk';
import { AgentResponse, AgentUpdateRequest, AgentCreateRequest } from '../sdk';

const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<AgentResponse | null>(null);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    system_prompt: '',
    agent_type: 'conversational',
    status: 'active',
  });

  const agentTypes = [
    'conversational',
    'analytical',
    'creative',
    'technical',
    'research',
    'assistant',
  ];

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await chatterSDK.agents.listAgentsApiV1AgentsGet();
      setAgents(response.data.agents);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (agent?: AgentResponse) => {
    if (agent) {
      setEditingAgent(agent);
      setFormData({
        name: agent.name,
        description: agent.description || '',
        system_prompt: agent.system_prompt || '',
        agent_type: agent.agent_type,
        status: agent.status,
      });
    } else {
      setEditingAgent(null);
      setFormData({
        name: '',
        description: '',
        system_prompt: '',
        agent_type: 'conversational',
        status: 'active',
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      if (editingAgent) {
        const response = await chatterSDK.agents.updateAgentApiV1AgentsAgentIdPut({
          agentId: editingAgent.id,
          agentUpdateRequest: formData as AgentUpdateRequest
        });
        setAgents(prev => prev.map(a => a.id === editingAgent.id ? response.data : a));
      } else {
        const response = await chatterSDK.agents.createAgentApiV1AgentsPost({
          agentCreateRequest: formData as AgentCreateRequest
        });
        setAgents(prev => [response.data, ...prev]);
      }
      setDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save agent');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (agentId: string) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) {
      return;
    }

    try {
      await chatterSDK.agents.deleteAgentApiV1AgentsAgentIdDelete({ agentId });
      setAgents(prev => prev.filter(a => a.id !== agentId));
    } catch (err: any) {
      setError('Failed to delete agent');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          AI Agents Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadAgents}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Agent
          </Button>
        </Box>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {/* Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                {agents.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Agents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                {agents.filter(agent => agent.status === 'active').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Agents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="info.main">
                {new Set(agents.map(agent => agent.agent_type)).size}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Agent Types
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="secondary.main">
                {agents.filter(agent => agent.status !== 'active').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Inactive Agents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Agents Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {agents.map((agent) => (
                <TableRow key={agent.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <BotIcon sx={{ mr: 1, color: agent.status === 'active' ? 'primary.main' : 'grey.400' }} />
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                          {agent.name}
                        </Typography>
                        {agent.description && (
                          <Typography variant="body2" color="text.secondary">
                            {agent.description}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={agent.agent_type}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={agent.status === 'active' ? 'Active' : 'Inactive'}
                      color={agent.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(new Date(agent.created_at), 'MMM dd, yyyy')}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {agent.updated_at ? (
                      <Typography variant="body2">
                        {format(new Date(agent.updated_at), 'MMM dd, yyyy')}
                      </Typography>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(agent)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(agent.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {agents.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                      No agents found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAgent ? 'Edit Agent' : 'Create Agent'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <TextField
                fullWidth
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid
              size={{
                xs: 12,
                sm: 6
              }}>
              <FormControl fullWidth>
                <InputLabel>Agent Type</InputLabel>
                <Select
                  value={formData.agent_type}
                  label="Agent Type"
                  onChange={(e) => setFormData({ ...formData, agent_type: e.target.value })}
                >
                  {agentTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="System Prompt"
                value={formData.system_prompt}
                onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                multiline
                rows={6}
                placeholder="Enter the system prompt that defines the agent's behavior and personality..."
              />
            </Grid>
            <Grid size={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.status === 'active'}
                    onChange={(e) => setFormData({ ...formData, status: e.target.checked ? 'active' : 'inactive' })}
                  />
                }
                label="Agent is active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={!formData.name || !formData.agent_type || saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentsPage;
