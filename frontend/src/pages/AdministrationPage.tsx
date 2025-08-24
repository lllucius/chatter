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

  const handleChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  const openDialog = (type: 'user' | 'tool' | 'backup' | 'plugin') => {
    setDialogType(type);
    setDialogOpen(true);
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
                <IconButton edge="end">
                  <DownloadIcon />
                </IconButton>
                <IconButton edge="end">
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
                <IconButton edge="end">
                  <DownloadIcon />
                </IconButton>
                <IconButton edge="end">
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
                <IconButton edge="end">
                  <EditIcon />
                </IconButton>
                <IconButton edge="end">
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
                <IconButton edge="end">
                  <EditIcon />
                </IconButton>
                <IconButton edge="end">
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
                <IconButton edge="end">
                  <SettingsIcon />
                </IconButton>
                <IconButton edge="end">
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
                <IconButton edge="end">
                  <SettingsIcon />
                </IconButton>
                <IconButton edge="end">
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
                label="Email"
                margin="normal"
                type="email"
                placeholder="user@example.com"
              />
              <TextField
                fullWidth
                label="Password"
                margin="normal"
                type="password"
              />
              <TextField
                fullWidth
                label="Role"
                margin="normal"
                select
                SelectProps={{ native: true }}
                defaultValue="user"
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
              />
              <TextField
                fullWidth
                label="Server URL"
                margin="normal"
                placeholder="http://localhost:3000"
              />
              <TextField
                fullWidth
                label="Description"
                margin="normal"
                multiline
                rows={3}
                placeholder="Description of the tool server capabilities"
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
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Include user data"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Include documents"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
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
          <Button variant="contained" onClick={() => setDialogOpen(false)}>
            {dialogType === 'backup' ? 'Create' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdministrationPage;