import React, { useRef } from 'react';
import {
  Typography,
  Box,
  Button,
  Chip,
} from '../utils/mui';
import { RefreshIcon, PlayArrowIcon, InfoIcon } from '../utils/icons';
import PageLayout from '../components/PageLayout';
import CrudDataTable, {
  CrudConfig,
  CrudService,
  CrudColumn,
  CrudDataTableRef,
} from '../components/CrudDataTable';
import {
  createDateRenderer,
} from '../components/CrudRenderers';
import { getSDK } from '../services/auth-service';
import { WorkflowExecutionResponse } from 'chatter-sdk';

const WorkflowExecutionsPage: React.FC = () => {
  const crudTableRef = useRef<CrudDataTableRef>(null);

  // Handle execution details
  const handleViewDetails = (execution: WorkflowExecutionResponse) => {
    console.log('View execution details:', execution);
    // This would open a details dialog or navigate to a details page
  };

  // Status chip renderer
  const renderStatus = (status: unknown) => {
    const statusStr = String(status).toLowerCase();
    let color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
    
    switch (statusStr) {
      case 'completed':
        color = 'success';
        break;
      case 'failed':
        color = 'error';
        break;
      case 'running':
        color = 'primary';
        break;
      case 'pending':
        color = 'warning';
        break;
      default:
        color = 'default';
    }
    
    return (
      <Chip
        label={String(status)}
        color={color}
        size="small"
        variant="outlined"
      />
    );
  };

  // Define table columns
  const columns: CrudColumn<WorkflowExecutionResponse>[] = [
    {
      id: 'id',
      label: 'Execution ID',
      width: '150px',
      render: (id: unknown) => (
        <Typography variant="body2" fontFamily="monospace" fontSize="0.75rem">
          {String(id).substring(0, 8)}...
        </Typography>
      ),
    },
    {
      id: 'definition_id',
      label: 'Workflow',
      width: '150px',
      render: (definitionId: unknown) => (
        <Typography variant="body2" fontFamily="monospace" fontSize="0.75rem">
          {String(definitionId).substring(0, 8)}...
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      width: '100px',
      render: renderStatus,
    },
    {
      id: 'duration',
      label: 'Duration',
      width: '80px',
      render: (value: unknown, execution: WorkflowExecutionResponse) => {
        if (!execution.started_at) return '-';
        
        const start = new Date(execution.started_at);
        const end = execution.completed_at ? new Date(execution.completed_at) : new Date();
        const duration = Math.round((end.getTime() - start.getTime()) / 1000);
        
        if (duration < 60) return `${duration}s`;
        if (duration < 3600) return `${Math.round(duration / 60)}m`;
        return `${Math.round(duration / 3600)}h`;
      },
    },
    {
      id: 'input_data',
      label: 'Input',
      render: (inputData: unknown) => {
        try {
          const keys = Object.keys(inputData || {});
          return (
            <Typography variant="body2" color="text.secondary" noWrap>
              {keys.length > 0 ? `${keys.length} parameters` : 'No input'}
            </Typography>
          );
        } catch {
          return (
            <Typography variant="body2" color="text.secondary">
              Invalid input
            </Typography>
          );
        }
      },
    },
    {
      id: 'started_at',
      label: 'Started',
      width: '140px',
      render: createDateRenderer<WorkflowExecutionResponse>('started_at'),
    },
  ];

  // Define CRUD configuration (read-only for executions)
  const config: CrudConfig<WorkflowExecutionResponse> = {
    entityName: 'Execution',
    entityNamePlural: 'Executions',
    columns,
    actions: [
      {
        icon: <InfoIcon />,
        label: 'View Details',
        onClick: handleViewDetails,
      },
    ],
    enableCreate: false,
    enableEdit: false,
    enableDelete: false,
    enableRefresh: true,
    pageSize: 20,
  };

  // Define service methods
  const service: CrudService<WorkflowExecutionResponse, never, never> = {
    list: async (page: number, pageSize: number) => {
      const sdk = await getSDK();
      // Note: This API may require a workflow ID, will need to adjust
      // For now, return empty results
      return {
        items: [],
        total: 0,
      };
    },
    create: async () => {
      throw new Error('Create not supported for executions');
    },
    update: async () => {
      throw new Error('Update not supported for executions');
    },
    delete: async () => {
      throw new Error('Delete not supported for executions');
    },
  };

  // Toolbar content
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={() => crudTableRef.current?.reload?.()}
      >
        Refresh
      </Button>
    </>
  );

  return (
    <PageLayout title="Workflow Executions" toolbar={toolbar}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          View and monitor workflow execution history. Executions are automatically
          created when workflows are run.
        </Typography>
      </Box>
      
      <CrudDataTable
        ref={crudTableRef}
        config={config}
        service={service}
      />
    </PageLayout>
  );
};

export default WorkflowExecutionsPage;