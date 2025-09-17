import React, { memo } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Box,
  Alert,
} from '../../utils/mui';
import { PlayIcon, DeleteIcon, EditIcon } from '../../utils/icons';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  workflow: any;
  created_at: string;
  updated_at: string;
}

interface WorkflowTemplatesTabProps {
  templates: WorkflowTemplate[];
  loading: boolean;
  onExecuteTemplate: (templateId: string) => void;
  onEditTemplate: (template: WorkflowTemplate) => void;
  onDeleteTemplate: (templateId: string) => void;
}

const WorkflowTemplatesTab: React.FC<WorkflowTemplatesTabProps> = memo(
  ({
    templates,
    loading,
    onExecuteTemplate,
    onEditTemplate,
    onDeleteTemplate,
  }) => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <Typography>Loading templates...</Typography>
        </Box>
      );
    }

    if (templates.length === 0) {
      return (
        <Alert severity="info">
          No workflow templates found. Create your first template to get
          started.
        </Alert>
      );
    }

    return (
      <Grid container spacing={3}>
        {templates.map((template) => (
          <Grid key={template.id} size={{ xs: 12, md: 6, lg: 4 }}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    mb: 1,
                  }}
                >
                  <Typography variant="h6" component="h3">
                    {template.name}
                  </Typography>
                  <Chip label={template.category} size="small" />
                </Box>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  {template.description}
                </Typography>

                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ mb: 2, display: 'block' }}
                >
                  Created: {new Date(template.created_at).toLocaleDateString()}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<PlayIcon />}
                    onClick={() => onExecuteTemplate(template.id)}
                  >
                    Execute
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<EditIcon />}
                    onClick={() => onEditTemplate(template)}
                  >
                    Edit
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={() => onDeleteTemplate(template.id)}
                  >
                    Delete
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }
);

WorkflowTemplatesTab.displayName = 'WorkflowTemplatesTab';

export default WorkflowTemplatesTab;
