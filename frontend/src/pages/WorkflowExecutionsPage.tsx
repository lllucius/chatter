import React from 'react';
import { Button } from '../utils/mui';
import { RefreshIcon } from '../utils/icons';
import PageLayout from '../components/PageLayout';
import WorkflowExecutionsTab from '../components/workflow-management/WorkflowExecutionsTab';
import { useWorkflowData } from '../hooks/useWorkflowData';

interface WorkflowExecution {
  id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
}

const WorkflowExecutionsPage: React.FC = () => {
  const {
    loading,
    executions: executionResponses,
    loadExecutions,
  } = useWorkflowData();

  // Convert WorkflowExecutionResponse to WorkflowExecution format expected by the tab
  const executions: WorkflowExecution[] = executionResponses.map(execution => ({
    id: execution.id || '',
    workflow_name: execution.workflow_name || 'Unknown',
    status: execution.status || 'unknown',
    started_at: execution.started_at || new Date().toISOString(),
    completed_at: execution.completed_at || undefined,
    input: execution.input || {},
    output: execution.output || undefined,
    error: execution.error || undefined,
  }));

  const handleRefresh = () => {
    loadExecutions();
  };

  // Toolbar
  const toolbar = (
    <>
      <Button
        variant="outlined"
        startIcon={<RefreshIcon />}
        onClick={handleRefresh}
        disabled={loading}
      >
        Refresh
      </Button>
    </>
  );

  return (
    <PageLayout title="Workflow Executions" toolbar={toolbar}>
      <WorkflowExecutionsTab executions={executions} loading={loading} />
    </PageLayout>
  );
};

export default WorkflowExecutionsPage;