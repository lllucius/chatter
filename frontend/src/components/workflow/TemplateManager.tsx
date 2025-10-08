import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Typography,
  Chip,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
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
}) => {
  const {
    templates: defaultTemplates,
    loading: _templatesLoading,
    error: _templatesError,
  } = useWorkflowTemplates();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);

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
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TemplateIcon sx={{ mr: 1 }} />
            Workflow Templates
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 0 }}>
          <List sx={{ pt: 0 }}>
            {templates.map((template, index) => (
              <React.Fragment key={template.id}>
                {index > 0 && <Divider />}
                <ListItem
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={(e) =>
                        setMenuAnchor({
                          element: e.currentTarget,
                          templateId: template.id,
                        })
                      }
                    >
                      <MoreIcon />
                    </IconButton>
                  }
                  disablePadding
                >
                  <ListItemButton
                    onClick={() => {
                      onSelectTemplate(template.workflow);
                      onClose();
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            flexWrap: 'wrap',
                          }}
                        >
                          <Typography variant="subtitle1" component="span">
                            {template.name}
                          </Typography>
                          <Chip
                            label={template.category}
                            color={getCategoryColor(template.category)}
                            size="small"
                          />
                          {template.tags.map((tag, tagIndex) => (
                            <Chip
                              key={tagIndex}
                              label={tag}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 0.5 }}>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mb: 0.5 }}
                          >
                            {template.description}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {template.workflow.nodes.length} nodes,{' '}
                            {template.workflow.edges.length} connections
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
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
    </>
  );
};

export default TemplateManager;
