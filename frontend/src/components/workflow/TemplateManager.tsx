import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  MoreVert as MoreIcon,
  Description as TemplateIcon,
} from '@mui/icons-material';
import { WorkflowDefinition } from './WorkflowEditor';
import { useWorkflowTemplates, WorkflowTemplate } from './useWorkflowTemplates';

interface TemplateManagerProps {
  open: boolean;
  onClose: () => void;
  onSelectTemplate: (workflow: WorkflowDefinition) => void;
  currentWorkflow?: WorkflowDefinition;
  onSaveAsTemplate?: (
    template: Omit<WorkflowTemplate, 'id' | 'createdAt'>
  ) => void;
}


const TemplateManager: React.FC<TemplateManagerProps> = ({
  open,
  onClose,
  onSelectTemplate,
  currentWorkflow,
  onSaveAsTemplate,
}) => {
  const {
    templates: defaultTemplates,
    loading: _templatesLoading,
    error: _templatesError,
  } = useWorkflowTemplates();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [templateTags, setTemplateTags] = useState('');

  // Update templates when defaults change
  React.useEffect(() => {
    if (defaultTemplates.length > 0) {
      setTemplates(defaultTemplates);
    }
  }, [defaultTemplates]);
  const [menuAnchor, setMenuAnchor] = useState<{
    element: HTMLElement;
    templateId: string;
  } | null>(null);

  const handleSaveTemplate = () => {
    if (!currentWorkflow || !templateName.trim()) return;

    const newTemplate: WorkflowTemplate = {
      id: `custom-${Date.now()}`,
      name: templateName,
      description: templateDescription,
      category: 'custom',
      tags: templateTags
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean),
      workflow: {
        ...currentWorkflow,
        metadata: {
          ...currentWorkflow.metadata,
          name: templateName,
          description: templateDescription,
        },
      },
      createdAt: new Date().toISOString(),
    };

    setTemplates((prev) => [...prev, newTemplate]);

    if (onSaveAsTemplate) {
      onSaveAsTemplate(newTemplate);
    }

    // Reset form
    setTemplateName('');
    setTemplateDescription('');
    setTemplateTags('');
    setSaveDialogOpen(false);
  };

  const handleDeleteTemplate = (templateId: string) => {
    setTemplates((prev) => prev.filter((t) => t.id !== templateId));
    setMenuAnchor(null);
  };

  const getCategoryColor = (
    category: WorkflowTemplate['category']
  ): 'default' | 'primary' | 'secondary' => {
    switch (category) {
      case 'basic':
        return 'default';
      case 'advanced':
        return 'primary';
      case 'custom':
        return 'secondary';
    }
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TemplateIcon sx={{ mr: 1 }} />
              Workflow Templates
            </Box>
            {currentWorkflow && (
              <Button
                startIcon={<AddIcon />}
                onClick={() => setSaveDialogOpen(true)}
                variant="outlined"
                size="small"
              >
                Save as Template
              </Button>
            )}
          </Box>
        </DialogTitle>

        <DialogContent>
          <Grid container spacing={2}>
            {templates.map((template) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={template.id}>
                <Card>
                  <CardContent>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        mb: 1,
                      }}
                    >
                      <Typography variant="h6" component="h3">
                        {template.name}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) =>
                          setMenuAnchor({
                            element: e.currentTarget,
                            templateId: template.id,
                          })
                        }
                      >
                        <MoreIcon />
                      </IconButton>
                    </Box>

                    <Typography
                      variant="body2"
                      color="textSecondary"
                      sx={{ mb: 2, minHeight: 40 }}
                    >
                      {template.description}
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={template.category}
                        color={getCategoryColor(template.category)}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                      />
                      {template.tags.map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 0.5, mb: 1 }}
                        />
                      ))}
                    </Box>

                    <Typography variant="caption" color="textSecondary">
                      {template.workflow.nodes.length} nodes,{' '}
                      {template.workflow.edges.length} connections
                    </Typography>
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => {
                        onSelectTemplate(template.workflow);
                        onClose();
                      }}
                    >
                      Use Template
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Template Menu */}
      <Menu
        anchorEl={menuAnchor?.element}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
      >
        <MenuItem
          onClick={() => {
            if (menuAnchor) {
              handleDeleteTemplate(menuAnchor.templateId);
            }
          }}
          disabled={
            templates.find((t) => t.id === menuAnchor?.templateId)?.category !==
            'custom'
          }
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Delete Template
        </MenuItem>
      </Menu>

      {/* Save Template Dialog */}
      <Dialog
        open={saveDialogOpen}
        onClose={() => setSaveDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Save as Template</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Template Name"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            sx={{ mb: 2, mt: 1 }}
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={templateDescription}
            onChange={(e) => setTemplateDescription(e.target.value)}
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Tags (comma-separated)"
            value={templateTags}
            onChange={(e) => setTemplateTags(e.target.value)}
            helperText="e.g., chat, advanced, tools"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveTemplate}
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={!templateName.trim()}
          >
            Save Template
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default TemplateManager;
