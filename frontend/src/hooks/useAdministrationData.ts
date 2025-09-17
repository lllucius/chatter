import { useState, useEffect, useCallback } from 'react';
import { getSDK } from '../services/auth-service';
import { useSSE } from '../services/sse-context';
import { useNotifications } from '../components/NotificationSystem';
import { handleError } from '../utils/error-handler';
import {
  BackupResponse,
  BackupListResponse,
  PluginResponse,
  PluginListResponse,
  JobResponse,
  JobListResponse,
  JobStatsResponse,
} from 'chatter-sdk';

// SSE Event interfaces for type safety
interface JobSSEEventData {
  job_id: string;
  job_name?: string;
  error?: string;
}

interface BackupSSEEventData {
  backup_id: string;
  backup_name?: string;
  error?: string;
}

interface PluginSSEEventData {
  plugin_id: string;
  plugin_name?: string;
  error?: string;
}

interface SSEEvent {
  data: JobSSEEventData | BackupSSEEventData | PluginSSEEventData;
}

interface User {
  id: string;
  email: string;
  role: string;
  lastLogin: string;
  status: string;
  name: string;
  isActive: boolean;
}

export const useAdministrationData = () => {
  const { isConnected, on } = useSSE();
  const { showNotification } = useNotifications();

  // State management
  const [backups, setBackups] = useState<BackupResponse[]>([]);
  const [plugins, setPlugins] = useState<PluginResponse[]>([]);
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [jobStats, setJobStats] = useState<JobStatsResponse | null>(null);
  const [dataLoading, setDataLoading] = useState(false);

  // Mock user data - in real app this would come from API
  const [users] = useState<User[]>([
    {
      id: 'admin@chatter.ai',
      email: 'admin@chatter.ai',
      role: 'Administrator',
      lastLogin: '2 hours ago',
      status: 'Active',
      name: 'Admin User',
      isActive: true,
    },
    {
      id: 'user@example.com',
      email: 'user@example.com',
      role: 'User',
      lastLogin: '1 day ago',
      status: 'Active',
      name: 'Regular User',
      isActive: true,
    },
  ]);

  const [lastJobStates, setLastJobStates] = useState<Map<string, string>>(
    new Map()
  );

  // Data loading functions
  const loadBackups = useCallback(async () => {
    try {
      const response =
        await getSDK().dataManagement.listBackupsApiV1DataBackups();
      setBackups(response?.backups || []);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadBackups',
        operation: 'load backups',
      });
    }
  }, []);

  const loadPlugins = useCallback(async () => {
    try {
      const response = await getSDK().plugins.listPluginsApiV1Plugins();
      setPlugins(response?.plugins || []);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadPlugins',
        operation: 'load plugins',
      });
    }
  }, []);

  const loadJobs = useCallback(async () => {
    try {
      setDataLoading(true);
      const response = await getSDK().jobs.listJobsApiV1Jobs(
        {},
        {
          limit: 100,
          offset: 0,
        }
      );
      const newJobs = response.jobs || [];
      newJobs.forEach((job) => {
        const previousState = lastJobStates.get(job.id);
        if (previousState && previousState !== job.status) {
          showNotification({
            title: 'Job Status Update',
            message: `Job "${job.name || job.id.substring(0, 8)}" changed from ${previousState} to ${job.status}`,
            type:
              job.status === 'completed'
                ? 'success'
                : job.status === 'failed'
                  ? 'error'
                  : 'info',
            category: 'system',
          });
        }
      });

      // Update last known states
      const newStates = new Map(lastJobStates);
      newJobs.forEach((job) => {
        newStates.set(job.id, job.status);
      });
      setLastJobStates(newStates);
      setJobs(newJobs);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadJobs',
        operation: 'load jobs',
      });
    } finally {
      setDataLoading(false);
    }
  }, [lastJobStates, showNotification]);

  const loadJobStats = useCallback(async () => {
    try {
      const response = await getSDK().jobs.getJobStatsApiV1JobsStats();
      setJobStats(response);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadJobStats',
        operation: 'load job stats',
      });
    }
  }, []);

  // SSE Event handlers
  useEffect(() => {
    if (!isConnected) return;

    const unsubscribeJobStarted = on('job.started', (event: SSEEvent) => {
      const jobData = event.data as JobSSEEventData;
      showNotification({
        title: 'Job Started',
        message: `Job "${jobData.job_name || jobData.job_id}" has started`,
        type: 'info',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobCompleted = on('job.completed', (event: SSEEvent) => {
      const jobData = event.data as JobSSEEventData;
      showNotification({
        title: 'Job Completed',
        message: `Job "${jobData.job_name || jobData.job_id}" completed successfully`,
        type: 'success',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobFailed = on('job.failed', (event: SSEEvent) => {
      const jobData = event.data as JobSSEEventData;
      showNotification({
        title: 'Job Failed',
        message: `Job "${jobData.job_name || jobData.job_id}" failed: ${jobData.error}`,
        type: 'error',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeBackupStarted = on('backup.started', (event: SSEEvent) => {
      const backupData = event.data as BackupSSEEventData;
      showNotification({
        title: 'Backup Started',
        message: `Backup "${backupData.backup_id}" has started`,
        type: 'info',
        category: 'system',
      });
      loadBackups();
    });

    const unsubscribeBackupCompleted = on(
      'backup.completed',
      (event: SSEEvent) => {
        const backupData = event.data as BackupSSEEventData;
        showNotification({
          title: 'Backup Completed',
          message: `Backup "${backupData.backup_id}" completed successfully`,
          type: 'success',
          category: 'system',
        });
        loadBackups();
      }
    );

    const unsubscribeBackupFailed = on('backup.failed', (event: SSEEvent) => {
      const backupData = event.data as BackupSSEEventData;
      showNotification({
        title: 'Backup Failed',
        message: `Backup "${backupData.backup_id}" failed: ${backupData.error}`,
        type: 'error',
        category: 'system',
      });
      loadBackups();
    });

    return () => {
      unsubscribeJobStarted();
      unsubscribeJobCompleted();
      unsubscribeJobFailed();
      unsubscribeBackupStarted();
      unsubscribeBackupCompleted();
      unsubscribeBackupFailed();
    };
  }, [isConnected, on, showNotification, loadJobs, loadJobStats, loadBackups]);

  // Load initial data
  useEffect(() => {
    loadBackups();
    loadPlugins();
    loadJobs();
    loadJobStats();
  }, [loadBackups, loadPlugins, loadJobs, loadJobStats]);

  return {
    // Data
    backups,
    plugins,
    jobs,
    jobStats,
    users,
    dataLoading,

    // Actions
    loadBackups,
    loadPlugins,
    loadJobs,
    loadJobStats,
  };
};
