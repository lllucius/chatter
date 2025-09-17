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

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'advanced' | 'custom';
  workflow: WorkflowDefinition;
  tags: string[];
  createdAt: string;
}

interface TemplateManagerProps {
  open: boolean;
  onClose: () => void;
  onSelectTemplate: (workflow: WorkflowDefinition) => void;
  currentWorkflow?: WorkflowDefinition;
  onSaveAsTemplate?: (
    template: Omit<WorkflowTemplate, 'id' | 'createdAt'>
  ) => void;
}

// Default templates
const defaultTemplates: WorkflowTemplate[] = [
  {
    id: 'basic-chat',
    name: 'Basic Chat',
    description: 'Simple conversational workflow with a single model call',
    category: 'basic',
    tags: ['chat', 'simple'],
    createdAt: new Date().toISOString(),
    workflow: {
      nodes: [
        {
          id: 'start-1',
          type: 'start',
          position: { x: 100, y: 200 },
          data: {
            label: 'Start',
            nodeType: 'start',
            config: { isEntryPoint: true },
          },
        },
        {
          id: 'model-1',
          type: 'model',
          position: { x: 300, y: 200 },
          data: {
            label: 'Chat Model',
            nodeType: 'model',
            config: { temperature: 0.7, maxTokens: 1000, model: 'gpt-4' },
          },
        },
      ],
      edges: [
        {
          id: 'e1',
          source: 'start-1',
          target: 'model-1',
          type: 'custom',
          animated: true,
        },
      ],
      metadata: {
        name: 'Basic Chat',
        description: 'Simple chat workflow',
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    },
  },
  {
    id: 'rag-pipeline',
    name: 'RAG Pipeline',
    description:
      'Retrieval-Augmented Generation with memory and error handling',
    category: 'advanced',
    tags: ['rag', 'retrieval', 'memory', 'error-handling'],
    createdAt: new Date().toISOString(),
    workflow: {
      nodes: [
        {
          id: 'start-1',
          type: 'start',
          position: { x: 100, y: 300 },
          data: {
            label: 'Start',
            nodeType: 'start',
            config: { isEntryPoint: true },
          },
        },
        {
          id: 'memory-1',
          type: 'memory',
          position: { x: 280, y: 300 },
          data: {
            label: 'Memory',
            nodeType: 'memory',
            config: { enabled: true, window: 20 },
          },
        },
        {
          id: 'retrieval-1',
          type: 'retrieval',
          position: { x: 460, y: 300 },
          data: {
            label: 'Retrieval',
            nodeType: 'retrieval',
            config: { collection: 'docs', topK: 5 },
          },
        },
        {
          id: 'model-1',
          type: 'model',
          position: { x: 640, y: 300 },
          data: {
            label: 'RAG Model',
            nodeType: 'model',
            config: { temperature: 0.3, maxTokens: 1500 },
          },
        },
        {
          id: 'error-1',
          type: 'errorHandler',
          position: { x: 460, y: 450 },
          data: {
            label: 'Error Handler',
            nodeType: 'errorHandler',
            config: { retryCount: 2, fallbackAction: 'continue' },
          },
        },
      ],
      edges: [
        {
          id: 'e1',
          source: 'start-1',
          target: 'memory-1',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e2',
          source: 'memory-1',
          target: 'retrieval-1',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e3',
          source: 'retrieval-1',
          target: 'model-1',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e4',
          source: 'retrieval-1',
          target: 'error-1',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e5',
          source: 'error-1',
          target: 'model-1',
          type: 'custom',
          animated: true,
        },
      ],
      metadata: {
        name: 'RAG Pipeline',
        description: 'Advanced RAG workflow with error handling',
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    },
  },
  {
    id: 'loop-processor',
    name: 'Loop Processor',
    description: 'Process data in loops with variables and conditional logic',
    category: 'advanced',
    tags: ['loop', 'variables', 'conditional'],
    createdAt: new Date().toISOString(),
    workflow: {
      nodes: [
        {
          id: 'start-1',
          type: 'start',
          position: { x: 100, y: 200 },
          data: {
            label: 'Start',
            nodeType: 'start',
            config: { isEntryPoint: true },
          },
        },
        {
          id: 'variable-1',
          type: 'variable',
          position: { x: 280, y: 200 },
          data: {
            label: 'Initialize Counter',
            nodeType: 'variable',
            config: { operation: 'set', variableName: 'counter', value: '0' },
          },
        },
        {
          id: 'loop-1',
          type: 'loop',
          position: { x: 460, y: 200 },
          data: {
            label: 'Process Loop',
            nodeType: 'loop',
            config: { maxIterations: 10, condition: 'counter < 10' },
          },
        },
        {
          id: 'model-1',
          type: 'model',
          position: { x: 640, y: 120 },
          data: {
            label: 'Process Item',
            nodeType: 'model',
            config: { temperature: 0.5, maxTokens: 800 },
          },
        },
        {
          id: 'variable-2',
          type: 'variable',
          position: { x: 640, y: 280 },
          data: {
            label: 'Increment Counter',
            nodeType: 'variable',
            config: { operation: 'increment', variableName: 'counter' },
          },
        },
        {
          id: 'conditional-1',
          type: 'conditional',
          position: { x: 820, y: 200 },
          data: {
            label: 'Check Complete',
            nodeType: 'conditional',
            config: { condition: 'counter >= 10' },
          },
        },
      ],
      edges: [
        {
          id: 'e1',
          source: 'start-1',
          target: 'variable-1',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e2',
          source: 'variable-1',
          target: 'loop-1',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e3',
          source: 'loop-1',
          target: 'model-1',
          type: 'custom',
          animated: true,
          sourceHandle: 'continue',
        },
        {
          id: 'e4',
          source: 'model-1',
          target: 'variable-2',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e5',
          source: 'variable-2',
          target: 'conditional-1',
          type: 'custom',
          animated: true,
        },
        {
          id: 'e6',
          source: 'conditional-1',
          target: 'loop-1',
          type: 'custom',
          animated: true,
          targetHandle: 'false',
        },
      ],
      metadata: {
        name: 'Loop Processor',
        description: 'Data processing with loops and variables',
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    },
  },
];

const TemplateManager: React.FC<TemplateManagerProps> = ({
  open,
  onClose,
  onSelectTemplate,
  currentWorkflow,
  onSaveAsTemplate,
}) => {
  const [templates, setTemplates] =
    useState<WorkflowTemplate[]>(defaultTemplates);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [templateTags, setTemplateTags] = useState('');
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
            {templates.map((template): void => (
              <Grid size={{ xs: 12, sm: 6 }} md={4} key={template.id}>
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
                      {template.tags.map((tag, index): void => (
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
