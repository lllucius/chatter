import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import { CrudFormProps } from './CrudDataTable';

// Define the RemoteServer interface based on the original code
interface RemoteServer {
  id: string;
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

interface RemoteServerFormProps extends CrudFormProps<RemoteServerCreate, RemoteServerUpdate> {}

const RemoteServerForm: React.FC<RemoteServerFormProps> = ({
  open,
  mode,
  initialData,
  onClose,
  onSubmit,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    base_url: '',
    transport_type: 'http' as 'http' | 'sse',
    oauth_enabled: false,
    oauth_client_id: '',
    oauth_client_secret: '',
    oauth_token_url: '',
    oauth_scope: '',
    headers: '{}',
    timeout: 30,
    auto_start: true,
  });

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && initialData) {
        setFormData({
          name: (initialData as any).name || '',
          display_name: initialData.display_name || '',
          description: initialData.description || '',
          base_url: (initialData as any).base_url || '',
          transport_type: (initialData as any).transport_type || 'http',
          oauth_enabled: Boolean((initialData as any).oauth_config),
          oauth_client_id: (initialData as any).oauth_config?.client_id || '',
          oauth_client_secret: (initialData as any).oauth_config?.client_secret || '',
          oauth_token_url: (initialData as any).oauth_config?.token_url || '',
          oauth_scope: (initialData as any).oauth_config?.scope || '',
          headers: (initialData as any).headers ? JSON.stringify((initialData as any).headers) : '{}',
          timeout: initialData.timeout || 30,
          auto_start: initialData.auto_start !== undefined ? initialData.auto_start : true,
        });
      } else {
        setFormData({
          name: '',
          display_name: '',
          description: '',
          base_url: '',
          transport_type: 'http',
          oauth_enabled: false,
          oauth_client_id: '',
          oauth_client_secret: '',
          oauth_token_url: '',
          oauth_scope: '',
          headers: '{}',
          timeout: 30,
          auto_start: true,
        });
      }
    }
  }, [open, mode, initialData]);

  const handleSubmit = async () => {
    try {
      setSaving(true);
      
      const submitData = {
        name: formData.name,
        display_name: formData.display_name,
        description: formData.description,
        base_url: formData.base_url,
        transport_type: formData.transport_type,
        oauth_config: formData.oauth_enabled ? {
          client_id: formData.oauth_client_id,
          client_secret: formData.oauth_client_secret,
          token_url: formData.oauth_token_url,
          scope: formData.oauth_scope || undefined,
        } : undefined,
        headers: formData.headers ? JSON.parse(formData.headers) : undefined,
        timeout: formData.timeout,
        auto_start: formData.auto_start,
      };

      if (mode === 'edit') {
        // For edit mode, remove fields that can't be updated
        const { name, base_url, transport_type, ...updateData } = submitData;
        await onSubmit(updateData);
      } else {
        await onSubmit(submitData);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {mode === 'edit' ? 'Edit Server Configuration' : 'Add Remote MCP Server'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            {mode === 'create' && (
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Server Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  helperText="Internal identifier for the server"
                />
              </Grid>
            )}
            
            <Grid size={12}>
              <TextField
                fullWidth
                label="Display Name"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                required
                helperText="Human-readable name shown in the UI"
              />
            </Grid>
            
            <Grid size={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={2}
                helperText="Optional description of the server's purpose"
              />
            </Grid>

            {/* Connection Settings - only for new servers */}
            {mode === 'create' && (
              <>
                <Grid size={12}>
                  <TextField
                    fullWidth
                    label="Base URL"
                    value={formData.base_url}
                    onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                    placeholder="https://api.example.com"
                    required
                    helperText="The base URL for the MCP server"
                  />
                </Grid>
                
                <Grid size={12}>
                  <FormControl fullWidth>
                    <InputLabel>Transport Type</InputLabel>
                    <Select
                      value={formData.transport_type}
                      onChange={(e) => setFormData({ ...formData, transport_type: e.target.value as 'http' | 'sse' })}
                      label="Transport Type"
                    >
                      <MenuItem value="http">HTTP</MenuItem>
                      <MenuItem value="sse">Server-Sent Events</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}

            {/* Server Configuration */}
            <Grid size={12}>
              <TextField
                fullWidth
                label="Timeout (seconds)"
                type="number"
                value={formData.timeout}
                onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) || 30 })}
                inputProps={{ min: 5, max: 300 }}
                helperText="Request timeout in seconds (5-300)"
              />
            </Grid>
            
            <Grid size={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.auto_start}
                    onChange={(e) => setFormData({ ...formData, auto_start: e.target.checked })}
                  />
                }
                label="Auto-connect on startup"
              />
            </Grid>

            {/* OAuth Authentication */}
            <Grid size={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">OAuth Authentication</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.oauth_enabled}
                          onChange={(e) => setFormData({ ...formData, oauth_enabled: e.target.checked })}
                        />
                      }
                      label="Enable OAuth 2.0 Authentication"
                    />
                    
                    {formData.oauth_enabled && (
                      <>
                        <TextField
                          fullWidth
                          label="Client ID"
                          value={formData.oauth_client_id}
                          onChange={(e) => setFormData({ ...formData, oauth_client_id: e.target.value })}
                          helperText="OAuth client identifier"
                        />
                        
                        <TextField
                          fullWidth
                          label="Client Secret"
                          type="password"
                          value={formData.oauth_client_secret}
                          onChange={(e) => setFormData({ ...formData, oauth_client_secret: e.target.value })}
                          helperText="OAuth client secret"
                        />
                        
                        <TextField
                          fullWidth
                          label="Token URL"
                          value={formData.oauth_token_url}
                          onChange={(e) => setFormData({ ...formData, oauth_token_url: e.target.value })}
                          placeholder="https://oauth.example.com/token"
                          helperText="OAuth token endpoint URL"
                        />
                        
                        <TextField
                          fullWidth
                          label="Scope (optional)"
                          value={formData.oauth_scope}
                          onChange={(e) => setFormData({ ...formData, oauth_scope: e.target.value })}
                          placeholder="read write"
                          helperText="OAuth scope(s)"
                        />
                      </>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Custom Headers */}
            <Grid size={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Custom Headers</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TextField
                    fullWidth
                    label="Custom Headers (JSON)"
                    value={formData.headers}
                    onChange={(e) => setFormData({ ...formData, headers: e.target.value })}
                    placeholder='{"Authorization": "Bearer token", "X-API-Key": "your-key"}'
                    multiline
                    rows={3}
                    helperText="Additional HTTP headers as JSON object"
                  />
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={saving}>Cancel</Button>
        <Button 
          onClick={handleSubmit}
          variant="contained" 
          disabled={saving || (mode === 'create' && (!formData.name || !formData.base_url)) || (mode === 'edit' && !formData.display_name)}
        >
          {saving ? 'Saving...' : mode === 'edit' ? 'Update Server' : 'Create Server'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RemoteServerForm;