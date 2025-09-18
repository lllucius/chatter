/**
 * SSE Event Types and Interfaces
 *
 * TypeScript definitions for Server-Sent Events from the Chatter platform
 */

// Base SSE event structure
export interface SSEEvent {
  id: string;
  type: string;
  data: unknown;
  timestamp: string;
  user_id?: string;
  metadata: Record<string, unknown>;
}

// Event categories matching backend unified system
export enum EventCategory {
  REALTIME = 'realtime',
  SECURITY = 'security',
  AUDIT = 'audit',
  MONITORING = 'monitoring',
  STREAMING = 'streaming',
  ANALYTICS = 'analytics',
  WORKFLOW = 'workflow',
}

// Event priorities matching backend
export enum EventPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// SSE Event Type constants for frontend usage
export enum SSEEventType {
  // Chat Events
  CHAT_MESSAGE_CHUNK = 'chat.message_chunk',
  CHAT_MESSAGE_COMPLETE = 'chat.message_complete',

  // Workflow Events
  WORKFLOW_STATUS = 'workflow.status',
  WORKFLOW_STARTED = 'workflow.started',
  WORKFLOW_COMPLETED = 'workflow.completed',
  WORKFLOW_FAILED = 'workflow.failed',

  // Document Events
  DOCUMENT_PROCESSING = 'document.processing_progress',
  DOCUMENT_UPLOADED = 'document.uploaded',
  DOCUMENT_PROCESSING_STARTED = 'document.processing_started',
  DOCUMENT_PROCESSING_COMPLETED = 'document.processing_completed',
  DOCUMENT_PROCESSING_FAILED = 'document.processing_failed',

  // Job Events
  JOB_STARTED = 'job.started',
  JOB_COMPLETED = 'job.completed',
  JOB_FAILED = 'job.failed',
  JOB_PROGRESS = 'job.progress',

  // Backup Events
  BACKUP_STARTED = 'backup.started',
  BACKUP_COMPLETED = 'backup.completed',
  BACKUP_FAILED = 'backup.failed',
  BACKUP_PROGRESS = 'backup.progress',

  // Plugin Events
  PLUGIN_STARTED = 'plugin.started',
  PLUGIN_STOPPED = 'plugin.stopped',
  PLUGIN_ERROR = 'plugin.error',

  // System Events
  SYSTEM_ALERT = 'system.alert',
  SYSTEM_STATUS = 'system.status',
  CONNECTION_ESTABLISHED = 'connection.established',
}

// Enhanced event with unified system metadata
export interface UnifiedSSEEvent extends SSEEvent {
  category?: EventCategory;
  priority?: EventPriority;
  source_system?: string;
  correlation_id?: string;
  session_id?: string;
}

// Backup Events
export interface BackupStartedEvent extends SSEEvent {
  type: 'backup.started';
  data: {
    backup_id: string;
    started_at: string;
  };
}

export interface BackupCompletedEvent extends SSEEvent {
  type: 'backup.completed';
  data: {
    backup_id: string;
    backup_path: string;
    completed_at: string;
  };
}

export interface BackupFailedEvent extends SSEEvent {
  type: 'backup.failed';
  data: {
    backup_id: string;
    error: string;
    failed_at: string;
  };
}

export interface BackupProgressEvent extends SSEEvent {
  type: 'backup.progress';
  data: {
    backup_id: string;
    progress_percent: number;
    current_step: string;
  };
}

// Job Events
export interface JobStartedEvent extends SSEEvent {
  type: 'job.started';
  data: {
    job_id: string;
    job_name: string;
    started_at: string;
  };
}

export interface JobCompletedEvent extends SSEEvent {
  type: 'job.completed';
  data: {
    job_id: string;
    job_name: string;
    result: unknown;
    completed_at: string;
  };
}

export interface JobFailedEvent extends SSEEvent {
  type: 'job.failed';
  data: {
    job_id: string;
    job_name: string;
    error: string;
    failed_at: string;
  };
}

export interface JobProgressEvent extends SSEEvent {
  type: 'job.progress';
  data: {
    job_id: string;
    job_name: string;
    progress_percent: number;
    current_step: string;
  };
}

// Document Events
export interface DocumentUploadedEvent extends SSEEvent {
  type: 'document.uploaded';
  data: {
    document_id: string;
    filename: string;
    uploaded_at: string;
  };
}

export interface DocumentProcessingStartedEvent extends SSEEvent {
  type: 'document.processing_started';
  data: {
    document_id: string;
    started_at: string;
  };
}

export interface DocumentProcessingCompletedEvent extends SSEEvent {
  type: 'document.processing_completed';
  data: {
    document_id: string;
    result: {
      chunks_created: number;
      text_length: number;
      processing_time: number;
    };
    completed_at: string;
  };
}

export interface DocumentProcessingFailedEvent extends SSEEvent {
  type: 'document.processing_failed';
  data: {
    document_id: string;
    error: string;
    failed_at: string;
  };
}

export interface DocumentProcessingProgressEvent extends SSEEvent {
  type: 'document.processing_progress';
  data: {
    document_id: string;
    progress_percent: number;
    current_step: string;
  };
}

// Plugin Events
export interface PluginEvent extends SSEEvent {
  type: 'plugin.started' | 'plugin.stopped' | 'plugin.error';
  data: {
    plugin_id: string;
    plugin_name: string;
    [key: string]: unknown;
  };
}

// System Events
export interface SystemAlertEvent extends SSEEvent {
  type: 'system.alert';
  data: {
    message: string;
    severity: 'info' | 'warning' | 'error';
    details?: unknown;
  };
}

export interface SystemStatusEvent extends SSEEvent {
  type: 'system.status';
  data: {
    status: string;
    details?: unknown;
  };
}

export interface ConnectionEstablishedEvent extends SSEEvent {
  type: 'connection.established';
  data: {
    user_id: string;
    connection_id: string;
    established_at: string;
  };
}

// Chat Events
export interface ChatMessageChunkEvent extends SSEEvent {
  type: 'chat.message_chunk';
  data: {
    message_id: string;
    chunk: string;
    chunk_index: number;
    is_final: boolean;
  };
}

export interface ChatMessageCompleteEvent extends SSEEvent {
  type: 'chat.message_complete';
  data: {
    message_id: string;
    complete_message: string;
    tokens_used: number;
  };
}

// Workflow Events
export interface WorkflowStatusEvent extends SSEEvent {
  type: 'workflow.status';
  data: {
    workflow_id: string;
    status: 'running' | 'completed' | 'failed' | 'paused';
    current_step: string;
    progress_percentage: number;
  };
}

export interface WorkflowStartedEvent extends SSEEvent {
  type: 'workflow.started';
  data: {
    workflow_id: string;
    started_at: string;
    input_data: Record<string, unknown>;
  };
}

export interface WorkflowCompletedEvent extends SSEEvent {
  type: 'workflow.completed';
  data: {
    workflow_id: string;
    completed_at: string;
    output_data: Record<string, unknown>;
    execution_time_ms: number;
  };
}

export interface WorkflowFailedEvent extends SSEEvent {
  type: 'workflow.failed';
  data: {
    workflow_id: string;
    failed_at: string;
    error_message: string;
    error_code?: string;
  };
}

// Union type for all possible events
export type AnySSEEvent =
  | BackupStartedEvent
  | BackupCompletedEvent
  | BackupFailedEvent
  | BackupProgressEvent
  | JobStartedEvent
  | JobCompletedEvent
  | JobFailedEvent
  | JobProgressEvent
  | DocumentUploadedEvent
  | DocumentProcessingStartedEvent
  | DocumentProcessingCompletedEvent
  | DocumentProcessingFailedEvent
  | DocumentProcessingProgressEvent
  | PluginEvent
  | SystemAlertEvent
  | SystemStatusEvent
  | ConnectionEstablishedEvent
  | ChatMessageChunkEvent
  | ChatMessageCompleteEvent
  | WorkflowStatusEvent
  | WorkflowStartedEvent
  | WorkflowCompletedEvent
  | WorkflowFailedEvent;

// Event listener callback type
export type SSEEventListener = (event: AnySSEEvent) => void;

// Event listener map type
export type SSEEventListeners = {
  [K in AnySSEEvent['type']]?: SSEEventListener[];
} & {
  '*'?: SSEEventListener[]; // wildcard listener for all events
};

// Static list of all possible event types for filtering (derived from backend EventType enum)
export const STATIC_EVENT_TYPES = [
  // Backup events
  'backup.started',
  'backup.completed',
  'backup.failed',
  'backup.progress',

  // Job events
  'job.started',
  'job.completed',
  'job.failed',
  'job.progress',

  // Tool server events
  'tool_server.started',
  'tool_server.stopped',
  'tool_server.health_changed',
  'tool_server.error',

  // Document events
  'document.uploaded',
  'document.processing_started',
  'document.processing_completed',
  'document.processing_failed',
  'document.processing_progress',

  // Chat events
  'conversation.started',
  'conversation.ended',
  'message.received',
  'message.sent',
  'chat.message_chunk',
  'chat.message_complete',

  // Workflow events
  'workflow.status',
  'workflow.started',
  'workflow.completed',
  'workflow.failed',

  // User events
  'user.registered',
  'user.updated',
  'user.connected',
  'user.disconnected',
  'user.status_changed',

  // Plugin events
  'plugin.installed',
  'plugin.activated',
  'plugin.deactivated',
  'plugin.error',

  // Agent events
  'agent.created',
  'agent.updated',

  // System events
  'system.alert',
  'system.status',
  'connection.established',
] as const;

// Static filter options for common values
export const STATIC_CATEGORIES = [
  'realtime',
  'security',
  'audit',
  'monitoring',
  'streaming',
  'analytics',
  'workflow',
] as const;

export const STATIC_PRIORITIES = ['low', 'normal', 'high', 'critical'] as const;
