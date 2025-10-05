import { useState, useEffect, useCallback, useRef } from 'react';
import { getSDK } from '../services/auth-service';
import { useSSE } from '../services/sse-context';
import { useNotifications } from '../components/NotificationSystem';
import { handleError } from '../utils/error-handler';
import {
  BackupResponse,
  PluginResponse,
  JobResponse,
  JobStatsResponse,
  UserResponse,
} from 'chatter-sdk';
import {
  JobStartedEvent,
  JobCompletedEvent,
  JobFailedEvent,
  BackupStartedEvent,
  BackupCompletedEvent,
  BackupFailedEvent,
} from '../services/sse-types';

// Simple cache to prevent rapid API calls
const API_CACHE_DURATION = 5000; // 5 seconds
const apiCallCache = new Map<string, number>();

const isAPICallRecentlyMade = (key: string): boolean => {
  const lastCall = apiCallCache.get(key);
  const now = Date.now();
  return lastCall ? now - lastCall < API_CACHE_DURATION : false;
};

const markAPICallMade = (key: string): void => {
  apiCallCache.set(key, Date.now());
};

// Rate limit backoff tracking
const rateLimitBackoffs = new Map<string, number>();

const getRateLimitDelay = (key: string): number => {
  const currentBackoff = rateLimitBackoffs.get(key) || 1000; // Start with 1 second
  return Math.min(currentBackoff, 30000); // Cap at 30 seconds
};

const incrementRateLimitBackoff = (key: string): void => {
  const currentBackoff = rateLimitBackoffs.get(key) || 1000;
  rateLimitBackoffs.set(key, Math.min(currentBackoff * 2, 30000));
};

const resetRateLimitBackoff = (key: string): void => {
  rateLimitBackoffs.delete(key);
};

const isRateLimitError = (error: unknown): boolean => {
  if (error && typeof error === 'object') {
    const errorResponse = error as { response?: { status?: number } };
    return errorResponse?.response?.status === 429;
  }
  return false;
};

// Utility function to handle API calls with rate limit retry
const callWithRateLimitRetry = async <T>(
  key: string,
  apiCall: () => Promise<T>,
  maxRetries: number = 2
): Promise<T> => {
  let attempts = 0;

  while (attempts <= maxRetries) {
    try {
      const result = await apiCall();
      resetRateLimitBackoff(key);
      return result;
    } catch (error) {
      if (isRateLimitError(error) && attempts < maxRetries) {
        incrementRateLimitBackoff(key);
        const delay = getRateLimitDelay(key);

        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, delay));
        attempts++;
        continue;
      }

      // If it's not a rate limit error or we've exhausted retries, throw the error
      throw error;
    }
  }

  throw new Error('Max retries exceeded');
};

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

export const useAdministrationData = () => {
  const { isConnected, on } = useSSE();
  const { showNotification } = useNotifications();

  // State management
  const [backups, setBackups] = useState<BackupResponse[]>([]);
  const [plugins, setPlugins] = useState<PluginResponse[]>([]);
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [jobStats, setJobStats] = useState<JobStatsResponse | null>(null);
  const [dataLoading, setDataLoading] = useState(false);
  
  // Users from backend API
  const [users, setUsers] = useState<UserResponse[]>([]);

  const [lastJobStates, setLastJobStates] = useState<Map<string, string>>(
    new Map()
  );

  // Use refs to store the latest values without causing re-renders
  const lastJobStatesRef = useRef(lastJobStates);
  const showNotificationRef = useRef(showNotification);

  // Update refs when values change
  useEffect(() => {
    lastJobStatesRef.current = lastJobStates;
  }, [lastJobStates]);

  useEffect(() => {
    showNotificationRef.current = showNotification;
  }, [showNotification]);

  // Data loading functions
  const loadBackups = useCallback(async () => {
    if (isAPICallRecentlyMade('loadBackups')) {
      return; // Skip if called recently
    }
    markAPICallMade('loadBackups');

    try {
      const response = await callWithRateLimitRetry('loadBackups', () =>
        getSDK().dataManagement.listBackupsApiV1DataBackups()
      );
      setBackups(response?.backups || []);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadBackups',
        operation: 'load backups',
      });
    }
  }, []);

  const loadPlugins = useCallback(async () => {
    if (isAPICallRecentlyMade('loadPlugins')) {
      return; // Skip if called recently
    }
    markAPICallMade('loadPlugins');

    try {
      const response = await callWithRateLimitRetry('loadPlugins', () =>
        getSDK().plugins.listPluginsApiV1Plugins()
      );
      setPlugins(response?.plugins || []);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadPlugins',
        operation: 'load plugins',
      });
    }
  }, []);

  const loadJobs = useCallback(async () => {
    if (isAPICallRecentlyMade('loadJobs')) {
      return; // Skip if called recently
    }
    markAPICallMade('loadJobs');

    try {
      setDataLoading(true);
      const response = await callWithRateLimitRetry('loadJobs', () =>
        getSDK().jobs.listJobsApiV1Jobs({
          limit: 100,
          offset: 0,
        })
      );
      const newJobs = response.jobs || [];
      newJobs.forEach((job) => {
        const previousState = lastJobStatesRef.current.get(job.id);
        if (previousState && previousState !== job.status) {
          showNotificationRef.current({
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
      const newStates = new Map(lastJobStatesRef.current);
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
  }, []); // Remove dependencies to prevent loop

  const loadJobStats = useCallback(async () => {
    if (isAPICallRecentlyMade('loadJobStats')) {
      return; // Skip if called recently
    }
    markAPICallMade('loadJobStats');

    try {
      const response = await callWithRateLimitRetry('loadJobStats', () =>
        getSDK().jobs.getJobStatsApiV1JobsStatsOverview()
      );
      setJobStats(response);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadJobStats',
        operation: 'load job stats',
      });
    }
  }, []);

  const loadUsers = useCallback(async () => {
    if (isAPICallRecentlyMade('loadUsers')) {
      return; // Skip if called recently
    }
    markAPICallMade('loadUsers');

    try {
      const response = await callWithRateLimitRetry('loadUsers', () =>
        getSDK().auth.listUsersApiV1AuthUsers({
          page: 1,
          pageSize: 100,
        })
      );
      setUsers(response?.users || []);
    } catch (error) {
      handleError(error, {
        source: 'useAdministrationData.loadUsers',
        operation: 'load users',
      });
    }
  }, []);

  // SSE Event handlers
  useEffect(() => {
    if (!isConnected) return;

    const unsubscribeJobStarted = on('job.started', (event) => {
      const jobEvent = event as JobStartedEvent;
      const jobData = jobEvent.data as JobSSEEventData;
      showNotificationRef.current({
        title: 'Job Started',
        message: `Job "${jobData.job_name || jobData.job_id}" has started`,
        type: 'info',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobCompleted = on('job.completed', (event) => {
      const jobEvent = event as JobCompletedEvent;
      const jobData = jobEvent.data as JobSSEEventData;
      showNotificationRef.current({
        title: 'Job Completed',
        message: `Job "${jobData.job_name || jobData.job_id}" completed successfully`,
        type: 'success',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeJobFailed = on('job.failed', (event) => {
      const jobEvent = event as JobFailedEvent;
      const jobData = jobEvent.data as JobSSEEventData;
      showNotificationRef.current({
        title: 'Job Failed',
        message: `Job "${jobData.job_name || jobData.job_id}" failed: ${jobData.error}`,
        type: 'error',
        category: 'system',
      });
      loadJobs();
      loadJobStats();
    });

    const unsubscribeBackupStarted = on('backup.started', (event) => {
      const backupEvent = event as BackupStartedEvent;
      const backupData = backupEvent.data as BackupSSEEventData;
      showNotificationRef.current({
        title: 'Backup Started',
        message: `Backup "${backupData.backup_id}" has started`,
        type: 'info',
        category: 'system',
      });
      loadBackups();
    });

    const unsubscribeBackupCompleted = on('backup.completed', (event) => {
      const backupEvent = event as BackupCompletedEvent;
      const backupData = backupEvent.data as BackupSSEEventData;
      showNotificationRef.current({
        title: 'Backup Completed',
        message: `Backup "${backupData.backup_id}" completed successfully`,
        type: 'success',
        category: 'system',
      });
      loadBackups();
    });

    const unsubscribeBackupFailed = on('backup.failed', (event) => {
      const backupEvent = event as BackupFailedEvent;
      const backupData = backupEvent.data as BackupSSEEventData;
      showNotificationRef.current({
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
  }, [isConnected, on, loadJobs, loadJobStats, loadBackups]);

  // Load initial data only once
  useEffect(() => {
    loadBackups();
    loadPlugins();
    loadJobs();
    loadJobStats();
    loadUsers();
  }, [loadBackups, loadPlugins, loadJobs, loadJobStats, loadUsers]); // Include dependencies

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
    loadUsers,
  };
};
