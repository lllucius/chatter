/**
 * SSE Event Types and Interfaces
 * 
 * TypeScript definitions for Server-Sent Events from the Chatter platform
 */

// Base SSE event structure
export interface SSEEvent {
  id: string;
  type: string;
  data: any;
  timestamp: string;
  user_id?: string;
  metadata: Record<string, any>;
}

// Event categories matching backend unified system
export enum EventCategory {
  REALTIME = 'realtime',
  SECURITY = 'security',
  AUDIT = 'audit',
  MONITORING = 'monitoring',
  STREAMING = 'streaming',
  ANALYTICS = 'analytics',
  WORKFLOW = 'workflow'
}

// Event priorities matching backend
export enum EventPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  CRITICAL = 'critical'
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
  CONNECTION_ESTABLISHED = 'connection.established'
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
    result: any;
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
    [key: string]: any;
  };
}

// System Events
export interface SystemAlertEvent extends SSEEvent {
  type: 'system.alert';
  data: {
    message: string;
    severity: 'info' | 'warning' | 'error';
    details?: any;
  };
}

export interface SystemStatusEvent extends SSEEvent {
  type: 'system.status';
  data: {
    status: string;
    details?: any;
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
  | ConnectionEstablishedEvent;

// Event listener callback type
export type SSEEventListener = (event: AnySSEEvent) => void;

// Event listener map type
export type SSEEventListeners = {
  [K in AnySSEEvent['type']]?: SSEEventListener[];
} & {
  '*'?: SSEEventListener[]; // wildcard listener for all events
};