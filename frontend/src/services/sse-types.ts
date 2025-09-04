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