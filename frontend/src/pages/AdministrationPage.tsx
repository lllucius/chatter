import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  Alert,
} from '@mui/material';
import Grid from '@mui/material/GridLegacy';
import {
  ExpandMore as ExpandMoreIcon,
  Backup as BackupIcon,
  Work as JobIcon,
  Extension as PluginIcon,
  People as UsersIcon,
  Build as ToolsIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

const AdministrationPage: React.FC = () => {
  const [expanded, setExpanded] = useState<string | false>('backups');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'user' | 'tool' | 'backup' | 'plugin'>('user');
  
  // Form state
  const [formData, setFormData] = useState({
    userId: '',
    email: '',
    password: '',
    role: 'user',
    serverName: '',
    serverUrl: '',
    description: '',
    backupName: '',
    includeUserData: true,
    includeDocuments: true,
    includeConfigurations: true,
    pluginUrl: '',
  });

  const handleChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  const openDialog = (type: 'user' | 'tool' | 'backup' | 'plugin') => {
    setDialogType(type);
    setDialogOpen(true);
    // Reset form data
    setFormData({
      userId: '',
      email: '',
      password: '',
      role: 'user',
      serverName: '',
      serverUrl: '',
      description: '',
      backupName: '',
      includeUserData: true,
      includeDocuments: true,
      includeConfigurations: true,
      pluginUrl: '',
    });
  };

  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      switch (dialogType) {
        case 'user':
          // TODO: Implement user creation using AuthenticationApi.registerApiV1AuthRegisterPost
          console.log('Creating user:', { 
            username: formData.userId, 
            email: formData.email, 
            password: formData.password 
          });
          alert('User creation functionality will be implemented with API integration');
          break;
        case 'tool':
          // TODO: Implement tool server creation using ToolServersApi.createToolServerApiV1ToolserversServersPost
          console.log('Creating tool server:', { 
            name: formData.serverName, 
            url: formData.serverUrl, 
            description: formData.description 
          });
          alert('Tool server creation functionality will be implemented with API integration');
          break;
        case 'backup':
          // TODO: Implement backup creation using DataManagementApi.createBackupApiV1DataBackupPost
          console.log('Creating backup:', { 
            name: formData.backupName, 
            includeUserData: formData.includeUserData, 
            includeDocuments: formData.includeDocuments, 
            includeConfigurations: formData.includeConfigurations 
          });
          alert('Backup creation functionality will be implemented with API integration');
          break;
        case 'plugin':
          // TODO: Implement plugin installation
          console.log('Installing plugin:', { url: formData.pluginUrl });
          alert('Plugin installation functionality will be implemented with API integration');
          break;
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('An error occurred. Please try again.');
    }
  };

  const handleDeleteAction = (type: string, id: string) => {
    if (window.confirm(`Are you sure you want to delete this ${type}?`)) {
      // TODO: Implement delete functionality based on type
      console.log(`Deleting ${type} with id:`, id);
      alert(`${type} deletion functionality will be implemented with API integration`);
    }
  };

  const handleEditAction = (type: string, id: string) => {
    // TODO: Implement edit functionality based on type
    console.log(`Editing ${type} with id:`, id);
    alert(`${type} editing functionality will be implemented with API integration`);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Administration Dashboard
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Manage system components, users, and configurations from this central dashboard.
      </Alert>

      {/* Backups Section */}
      <Accordion expanded={expanded === 'backups'} onChange={handleChange('backups')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <BackupIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Backups</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Button
                  variant="contained"
                  startIcon={<BackupIcon />}
                  onClick={() => openDialog('backup')}
                  sx={{ mr: 1 }}
                >
                  Create Backup
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                >
                  Restore Backup
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Automatic Backups"
                />
              </Grid>
            </Grid>
          </Box>
          <List>
            <ListItem>
              <ListItemText
                primary="Daily Backup - 2024-01-15"
                secondary="Size: 245 MB | Status: Complete"
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => alert('Download backup functionality will be implemented with API integration')}>
                  <DownloadIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('backup', 'daily-2024-01-15')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Weekly Backup - 2024-01-14"
                secondary="Size: 1.2 GB | Status: Complete"
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => alert('Download backup functionality will be implemented with API integration')}>
                  <DownloadIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('backup', 'weekly-2024-01-14')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Jobs Section */}
      <Accordion expanded={expanded === 'jobs'} onChange={handleChange('jobs')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <JobIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Background Jobs</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <List>
            <ListItem>
              <ListItemText
                primary="Document Processing Queue"
                secondary="Processing 3 documents | Next: document-001.pdf"
              />
              <Chip label="Running" color="success" size="small" />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Index Optimization"
                secondary="Last run: 2 hours ago | Next: In 6 hours"
              />
              <Chip label="Scheduled" color="info" size="small" />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Cleanup Old Conversations"
                secondary="Last run: 1 day ago | Cleaned 45 conversations"
              />
              <Chip label="Completed" color="default" size="small" />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Plugins Section */}
      <Accordion expanded={expanded === 'plugins'} onChange={handleChange('plugins')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <PluginIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Plugins</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('plugin')}
            >
              Install Plugin
            </Button>
          </Box>
          <List>
            <ListItem>
              <ListItemIcon>
                <PluginIcon />
              </ListItemIcon>
              <ListItemText
                primary="RAG Enhanced Search"
                secondary="Version 1.2.0 | Enabled | Enhances document search capabilities"
              />
              <ListItemSecondaryAction>
                <Switch defaultChecked />
                <IconButton edge="end">
                  <SettingsIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <PluginIcon />
              </ListItemIcon>
              <ListItemText
                primary="Advanced Analytics"
                secondary="Version 2.1.3 | Enabled | Provides detailed usage analytics"
              />
              <ListItemSecondaryAction>
                <Switch defaultChecked />
                <IconButton edge="end">
                  <SettingsIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Users Section */}
      <Accordion expanded={expanded === 'users'} onChange={handleChange('users')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <UsersIcon sx={{ mr: 2 }} />
          <Typography variant="h6">User Management</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('user')}
            >
              Add User
            </Button>
          </Box>
          <List>
            <ListItem>
              <ListItemText
                primary="admin@chatter.ai"
                secondary="Role: Administrator | Last login: 2 hours ago | Status: Active"
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleEditAction('user', 'admin@chatter.ai')}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('user', 'admin@chatter.ai')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="user@example.com"
                secondary="Role: User | Last login: 1 day ago | Status: Active"
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleEditAction('user', 'user@example.com')}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('user', 'user@example.com')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Tools Section */}
      <Accordion expanded={expanded === 'tools'} onChange={handleChange('tools')}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <ToolsIcon sx={{ mr: 2 }} />
          <Typography variant="h6">Tool Servers</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('tool')}
            >
              Add Tool Server
            </Button>
          </Box>
          <List>
            <ListItem>
              <ListItemText
                primary="File Operations Server"
                secondary="URL: http://localhost:3000 | Status: Connected | Tools: 8"
              />
              <Chip label="Connected" color="success" size="small" sx={{ mr: 1 }} />
              <ListItemSecondaryAction>
                <IconButton edge="end" sx={{ mr: 1 }} onClick={() => handleEditAction('tool-server', 'file-ops')}>
                  <SettingsIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('tool-server', 'file-ops')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Web Search Server"
                secondary="URL: http://localhost:3001 | Status: Disconnected | Tools: 4"
              />
              <Chip label="Disconnected" color="error" size="small" sx={{ mr: 1 }} />
              <ListItemSecondaryAction>
                <IconButton edge="end" sx={{ mr: 1 }} onClick={() => handleEditAction('tool-server', 'web-search')}>
                  <SettingsIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteAction('tool-server', 'web-search')}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Generic Dialog for Adding/Editing */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'user' && 'Add New User'}
          {dialogType === 'tool' && 'Add Tool Server'}
          {dialogType === 'backup' && 'Create Backup'}
          {dialogType === 'plugin' && 'Install Plugin'}
        </DialogTitle>
        <DialogContent>
          {dialogType === 'user' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="User ID"
                margin="normal"
                placeholder="username"
                helperText="Unique username for the user"
                value={formData.userId}
                onChange={(e) => handleFormChange('userId', e.target.value)}
              />
              <TextField
                fullWidth
                label="Email"
                margin="normal"
                type="email"
                placeholder="user@example.com"
                value={formData.email}
                onChange={(e) => handleFormChange('email', e.target.value)}
              />
              <TextField
                fullWidth
                label="Password"
                margin="normal"
                type="password"
                value={formData.password}
                onChange={(e) => handleFormChange('password', e.target.value)}
              />
              <TextField
                fullWidth
                label="Role"
                margin="normal"
                select
                SelectProps={{ native: true }}
                value={formData.role}
                onChange={(e) => handleFormChange('role', e.target.value)}
              >
                <option value="user">User</option>
                <option value="admin">Administrator</option>
              </TextField>
            </Box>
          )}
          {dialogType === 'tool' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Server Name"
                margin="normal"
                placeholder="My Tool Server"
                value={formData.serverName}
                onChange={(e) => handleFormChange('serverName', e.target.value)}
              />
              <TextField
                fullWidth
                label="Server URL"
                margin="normal"
                placeholder="http://localhost:3000"
                value={formData.serverUrl}
                onChange={(e) => handleFormChange('serverUrl', e.target.value)}
              />
              <TextField
                fullWidth
                label="Description"
                margin="normal"
                multiline
                rows={3}
                placeholder="Description of the tool server capabilities"
                value={formData.description}
                onChange={(e) => handleFormChange('description', e.target.value)}
              />
            </Box>
          )}
          {dialogType === 'backup' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Backup Name"
                margin="normal"
                placeholder="Manual Backup - 2024-01-15"
                value={formData.backupName}
                onChange={(e) => handleFormChange('backupName', e.target.value)}
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={formData.includeUserData}
                    onChange={(e) => handleFormChange('includeUserData', e.target.checked)}
                  />
                }
                label="Include user data"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={formData.includeDocuments}
                    onChange={(e) => handleFormChange('includeDocuments', e.target.checked)}
                  />
                }
                label="Include documents"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={formData.includeConfigurations}
                    onChange={(e) => handleFormChange('includeConfigurations', e.target.checked)}
                  />
                }
                label="Include configurations"
              />
            </Box>
          )}
          {dialogType === 'plugin' && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Plugin URL or File"
                margin="normal"
                placeholder="https://plugins.chatter.ai/awesome-plugin.zip"
                value={formData.pluginUrl}
                onChange={(e) => handleFormChange('pluginUrl', e.target.value)}
              />
              <Typography variant="body2" sx={{ mt: 2, mb: 1 }}>
                Or upload plugin file:
              </Typography>
              <Button variant="outlined" component="label">
                Choose File
                <input type="file" hidden accept=".zip,.tar.gz" />
              </Button>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {dialogType === 'backup' ? 'Create' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdministrationPage;