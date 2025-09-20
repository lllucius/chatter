import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Switch,
  FormControlLabel,
  TextField,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  Autocomplete,
  Collapse,
  Grid,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useSSE } from '../services/sse-context';
import {
  AnySSEEvent,
  STATIC_EVENT_TYPES,
  STATIC_CATEGORIES,
  STATIC_PRIORITIES,
} from '../services/sse-types';

interface SSEMessageEntry {
  id: string;
  timestamp: Date;
  event: AnySSEEvent;
  rawData: string;
}

interface SSEMonitorFilters {
  eventTypes: string[];
  categories: string[];
  priorities: string[];
  userIds: string[];
  sourceSystems: string[];
}

interface SSEMonitorSettings {
  filters: SSEMonitorFilters;
  consoleLogging: boolean;
  maxMessages: number;
  showRawData: boolean;
  showAdvancedFilters: boolean;
}

const defaultFilters: SSEMonitorFilters = {
  eventTypes: [],
  categories: [],
  priorities: [],
  userIds: [],
  sourceSystems: [],
};

const defaultSettings: SSEMonitorSettings = {
  filters: defaultFilters,
  consoleLogging: false,
  maxMessages: 100,
  showRawData: false,
  showAdvancedFilters: false,
};

const SSEMonitorPage: React.FC = () => {
  const { manager, isConnected } = useSSE();
  const [messages, setMessages] = useState<SSEMessageEntry[]>([]);

  // Load monitoring state from localStorage with persistence
  const [isMonitoring, setIsMonitoring] = useState(() => {
    const savedMonitoring = localStorage.getItem('sse-monitor-active');
    return savedMonitoring === 'true';
  });

  // Load all settings from localStorage with defaults
  const [settings, setSettings] = useState<SSEMonitorSettings>(() => {
    const saved = localStorage.getItem('sse-monitor-settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return { ...defaultSettings, ...parsed };
      } catch {
        // console.warn('Failed to parse saved SSE monitor settings:', error);
      }
    }
    return defaultSettings;
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageCountRef = useRef(0);

  // Persist monitoring state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('sse-monitor-active', isMonitoring.toString());
  }, [isMonitoring]);

  // Persist all settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('sse-monitor-settings', JSON.stringify(settings));
  }, [settings]);

  // Helper function to update settings
  const updateSettings = useCallback((updates: Partial<SSEMonitorSettings>) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  }, []);

  // Helper function to update filters
  const updateFilters = useCallback((updates: Partial<SSEMonitorFilters>) => {
    setSettings((prev) => ({
      ...prev,
      filters: { ...prev.filters, ...updates },
    }));
  }, []);

  // Get filter options - combine static types with dynamic ones from messages
  const filterOptions = React.useMemo(() => {
    const eventTypes = new Set<string>(STATIC_EVENT_TYPES); // Start with all static types
    const categories = new Set<string>(STATIC_CATEGORIES); // Start with static categories
    const priorities = new Set<string>(STATIC_PRIORITIES); // Start with static priorities
    const userIds = new Set<string>();
    const sourceSystems = new Set<string>();

    messages.forEach((msg) => {
      eventTypes.add(msg.event.type); // Add any additional types from actual messages

      if (msg.event.user_id) {
        userIds.add(msg.event.user_id);
      }

      if (msg.event.metadata) {
        if (msg.event.metadata.category) {
          categories.add(String(msg.event.metadata.category));
        }
        if (msg.event.metadata.priority) {
          priorities.add(String(msg.event.metadata.priority));
        }
        if (msg.event.metadata.source_system) {
          sourceSystems.add(String(msg.event.metadata.source_system));
        }
      }
    });

    return {
      eventTypes: Array.from(eventTypes).sort(),
      categories: Array.from(categories).sort(),
      priorities: Array.from(priorities).sort(),
      userIds: Array.from(userIds).sort(),
      sourceSystems: Array.from(sourceSystems).sort(),
    };
  }, [messages]);

  // Filter messages based on all active filters
  const filteredMessages = React.useMemo(() => {
    return messages.filter((msg) => {
      const { filters } = settings;

      // Filter by event types (if any selected)
      if (
        filters.eventTypes.length > 0 &&
        !filters.eventTypes.includes(msg.event.type)
      ) {
        return false;
      }

      // Filter by categories (if any selected)
      if (filters.categories.length > 0) {
        const category = msg.event.metadata?.category;
        if (!category || !filters.categories.includes(String(category))) {
          return false;
        }
      }

      // Filter by priorities (if any selected)
      if (filters.priorities.length > 0) {
        const priority = msg.event.metadata?.priority;
        if (!priority || !filters.priorities.includes(String(priority))) {
          return false;
        }
      }

      // Filter by user IDs (if any selected)
      if (filters.userIds.length > 0) {
        if (
          !msg.event.user_id ||
          !filters.userIds.includes(msg.event.user_id)
        ) {
          return false;
        }
      }

      // Filter by source systems (if any selected)
      if (filters.sourceSystems.length > 0) {
        const sourceSystem = msg.event.metadata?.source_system;
        if (
          !sourceSystem ||
          !filters.sourceSystems.includes(String(sourceSystem))
        ) {
          return false;
        }
      }

      return true;
    });
  }, [messages, settings]);

  // SSE event handler
  const handleSSEEvent = useCallback(
    (event: AnySSEEvent) => {
      const messageEntry: SSEMessageEntry = {
        id: `${Date.now()}-${messageCountRef.current++}`,
        timestamp: new Date(),
        event,
        rawData: JSON.stringify(event, null, 2),
      };

      setMessages((prev) => {
        const newMessages = [messageEntry, ...prev];
        // Keep only the most recent messages based on maxMessages setting
        return newMessages.slice(0, settings.maxMessages);
      });

      // Console logging if enabled
      if (settings.consoleLogging) {
        // eslint-disable-next-line no-console
        console.group(`🔴 SSE Event: ${event.type}`);
        // eslint-disable-next-line no-console
        console.log(
          '📅 Timestamp:',
          format(messageEntry.timestamp, 'HH:mm:ss.SSS')
        );
        // eslint-disable-next-line no-console
        console.log('📋 Event:', event);
        // eslint-disable-next-line no-console
        console.log('🔗 Event ID:', event.id);
        // eslint-disable-next-line no-console
        console.log('👤 User ID:', event.user_id || 'N/A');
        // eslint-disable-next-line no-console
        console.groupEnd();
      }
    },
    [settings.consoleLogging, settings.maxMessages]
  );

  // Start monitoring
  const startMonitoring = useCallback(() => {
    if (!manager) return;

    // console.log('Starting SSE monitoring...');
    setIsMonitoring(true);
    // Listen to all events using wildcard
    manager.addEventListener('*', handleSSEEvent);

    // Connect if not already connected
    if (!isConnected) {
      manager.connect();
    }
  }, [manager, isConnected, handleSSEEvent]);

  // Stop monitoring
  const stopMonitoring = useCallback(() => {
    if (!manager) return;

    // console.log('Stopping SSE monitoring...');
    setIsMonitoring(false);
    manager.removeEventListener('*', handleSSEEvent);
    // Note: We don't disconnect here to allow other parts of the app to use SSE
  }, [manager, handleSSEEvent]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    messageCountRef.current = 0;
  }, []);

  // Clear all filters
  const clearAllFilters = useCallback(() => {
    updateFilters(defaultFilters);
  }, [updateFilters]);

  // Helper function to count active filters
  const getActiveFilterCount = useCallback(() => {
    const { filters } = settings;
    return (
      filters.eventTypes.length +
      filters.categories.length +
      filters.priorities.length +
      filters.userIds.length +
      filters.sourceSystems.length
    );
  }, [settings]);

  // Export messages to JSON
  const exportMessages = useCallback(() => {
    const dataStr = JSON.stringify(filteredMessages, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sse-messages-${format(new Date(), 'yyyy-MM-dd-HH-mm-ss')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [filteredMessages]);

  // Auto-restore monitoring state when SSE manager becomes available
  useEffect(() => {
    if (isMonitoring && manager) {
      if (!isConnected) {
        // If monitoring was active but we're not connected, try to reconnect
        // console.log('Restoring SSE monitoring state and connecting...');
        manager.connect();
        manager.addEventListener('*', handleSSEEvent);
      } else {
        // If monitoring was active and we're connected, just add the listener
        // console.log('Restoring SSE monitoring state...');
        manager.addEventListener('*', handleSSEEvent);
      }
    }
  }, [manager, isConnected, isMonitoring, handleSSEEvent]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && messagesEndRef.current.scrollIntoView) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Cleanup on unmount - but don't stop monitoring if it should persist
  useEffect(() => {
    return () => {
      // Only clean up the listener, don't stop monitoring to preserve state across navigation
      if (manager) {
        manager.removeEventListener('*', handleSSEEvent);
      }
    };
  }, [manager, handleSSEEvent]);

  const getEventTypeColor = (
    type: string
  ):
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'warning'
    | 'info'
    | 'success' => {
    if (type.includes('error') || type.includes('failed')) return 'error';
    if (type.includes('warning') || type.includes('alert')) return 'warning';
    if (type.includes('success') || type.includes('completed'))
      return 'success';
    if (type.includes('progress') || type.includes('processing')) return 'info';
    if (type.includes('chat') || type.includes('message')) return 'primary';
    if (type.includes('system') || type.includes('connection'))
      return 'secondary';
    return 'default';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        SSE Monitor
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Real-time debugging tool for Server-Sent Events. Monitor incoming
        messages, filter by type, and export for analysis.
      </Typography>

      {/* Control Panel */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid>
              <Button
                variant={isMonitoring ? 'outlined' : 'contained'}
                color={isMonitoring ? 'secondary' : 'primary'}
                startIcon={isMonitoring ? <StopIcon /> : <PlayIcon />}
                onClick={isMonitoring ? stopMonitoring : startMonitoring}
                disabled={!manager}
              >
                {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
              </Button>
            </Grid>

            <Grid>
              <Chip
                label={isConnected ? 'Connected' : 'Disconnected'}
                color={isConnected ? 'success' : 'error'}
                variant="outlined"
              />
            </Grid>

            <Grid>
              <TextField
                type="number"
                label="Max Messages"
                value={settings.maxMessages}
                onChange={(e) =>
                  updateSettings({
                    maxMessages: Math.max(
                      1,
                      Math.min(1000, parseInt(e.target.value) || 100)
                    ),
                  })
                }
                size="small"
                sx={{ width: 120 }}
                inputProps={{ min: 1, max: 1000 }}
              />
            </Grid>

            <Grid>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.consoleLogging}
                    onChange={(e) =>
                      updateSettings({ consoleLogging: e.target.checked })
                    }
                  />
                }
                label="Console Logging"
              />
            </Grid>

            <Grid>
              <Tooltip title="Toggle Raw Data View">
                <IconButton
                  onClick={() =>
                    updateSettings({ showRawData: !settings.showRawData })
                  }
                >
                  {settings.showRawData ? (
                    <VisibilityOffIcon />
                  ) : (
                    <VisibilityIcon />
                  )}
                </IconButton>
              </Tooltip>
            </Grid>

            <Grid>
              <Tooltip title="Clear Messages">
                <IconButton onClick={clearMessages}>
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            </Grid>

            <Grid>
              <Tooltip title="Export Messages">
                <span>
                  <IconButton
                    onClick={exportMessages}
                    disabled={filteredMessages.length === 0}
                  >
                    <DownloadIcon />
                  </IconButton>
                </span>
              </Tooltip>
            </Grid>

            <Grid>
              <Button
                variant="outlined"
                size="small"
                onClick={() => manager?.triggerTestEvent()}
                disabled={!manager || !isConnected}
              >
                Test Event
              </Button>
            </Grid>

            <Grid>
              <Button
                variant="outlined"
                startIcon={<FilterIcon />}
                onClick={() =>
                  updateSettings({
                    showAdvancedFilters: !settings.showAdvancedFilters,
                  })
                }
                endIcon={
                  settings.showAdvancedFilters ? (
                    <ExpandLessIcon />
                  ) : (
                    <ExpandMoreIcon />
                  )
                }
                color={getActiveFilterCount() > 0 ? 'primary' : 'inherit'}
              >
                Filters{' '}
                {getActiveFilterCount() > 0 && `(${getActiveFilterCount()})`}
              </Button>
            </Grid>

            {getActiveFilterCount() > 0 && (
              <Grid>
                <Tooltip title="Clear All Filters">
                  <Button
                    variant="text"
                    size="small"
                    onClick={clearAllFilters}
                    sx={{ textTransform: 'none' }}
                  >
                    Clear All
                  </Button>
                </Tooltip>
              </Grid>
            )}
          </Grid>

          {/* Advanced Filters Section */}
          <Collapse in={settings.showAdvancedFilters}>
            <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle1" gutterBottom>
                Filter Options
              </Typography>
              <Grid container spacing={3}>
                {/* Event Types Filter */}
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Autocomplete
                    multiple
                    options={filterOptions.eventTypes}
                    value={settings.filters.eventTypes}
                    onChange={(_, value) =>
                      updateFilters({ eventTypes: value })
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Event Types"
                        placeholder="Select event types..."
                        size="small"
                        fullWidth
                      />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          {...getTagProps({ index })}
                          key={option}
                          size="small"
                        />
                      ))
                    }
                  />
                </Grid>

                {/* Categories Filter */}
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Autocomplete
                    multiple
                    options={filterOptions.categories}
                    value={settings.filters.categories}
                    onChange={(_, value) =>
                      updateFilters({ categories: value })
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Categories"
                        placeholder="Select categories..."
                        size="small"
                        fullWidth
                      />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          {...getTagProps({ index })}
                          key={option}
                          size="small"
                        />
                      ))
                    }
                    disabled={false} // Always enabled, even with no dynamic categories yet
                  />
                </Grid>

                {/* Priorities Filter */}
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Autocomplete
                    multiple
                    options={filterOptions.priorities}
                    value={settings.filters.priorities}
                    onChange={(_, value) =>
                      updateFilters({ priorities: value })
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Priorities"
                        placeholder="Select priorities..."
                        size="small"
                        fullWidth
                      />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          {...getTagProps({ index })}
                          key={option}
                          size="small"
                        />
                      ))
                    }
                    disabled={false} // Always enabled, even with no dynamic priorities yet
                  />
                </Grid>

                {/* User IDs Filter */}
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Autocomplete
                    multiple
                    options={filterOptions.userIds}
                    value={settings.filters.userIds}
                    onChange={(_, value) => updateFilters({ userIds: value })}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="User IDs"
                        placeholder="Select user IDs..."
                        size="small"
                        fullWidth
                      />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          {...getTagProps({ index })}
                          key={option}
                          size="small"
                        />
                      ))
                    }
                    disabled={false} // Always enabled, even with no dynamic user IDs yet
                  />
                </Grid>

                {/* Source Systems Filter */}
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <Autocomplete
                    multiple
                    options={filterOptions.sourceSystems}
                    value={settings.filters.sourceSystems}
                    onChange={(_, value) =>
                      updateFilters({ sourceSystems: value })
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Source Systems"
                        placeholder="Select source systems..."
                        size="small"
                        fullWidth
                      />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          {...getTagProps({ index })}
                          key={option}
                          size="small"
                        />
                      ))
                    }
                    disabled={false} // Always enabled, even with no dynamic source systems yet
                  />
                </Grid>
              </Grid>
            </Box>
          </Collapse>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid size={2.4}>
              <Typography variant="h6">{messages.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Messages
              </Typography>
            </Grid>
            <Grid size={2.4}>
              <Typography variant="h6">{filteredMessages.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Filtered Messages
              </Typography>
            </Grid>
            <Grid size={2.4}>
              <Typography variant="h6">
                {filterOptions.eventTypes.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Event Types
              </Typography>
            </Grid>
            <Grid size={2.4}>
              <Typography variant="h6">{getActiveFilterCount()}</Typography>
              <Typography variant="body2" color="text.secondary">
                Active Filters
              </Typography>
            </Grid>
            <Grid size={2.4}>
              <Typography variant="h6">
                {isMonitoring ? 'Active' : 'Inactive'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monitor Status
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Messages List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Messages{' '}
            {filteredMessages.length > 0 && `(${filteredMessages.length})`}
          </Typography>

          {!isMonitoring && messages.length === 0 && (
            <Alert severity="info" sx={{ my: 2 }}>
              Click &quot;Start Monitoring&quot; to begin capturing SSE messages. Make
              sure you&apos;re connected to the SSE stream.
            </Alert>
          )}

          {filteredMessages.length === 0 && messages.length > 0 && (
            <Alert severity="warning" sx={{ my: 2 }}>
              No messages match the selected filters. Try clearing some filters
              or selecting different criteria.
            </Alert>
          )}

          <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
            <List>
              {filteredMessages.map((message, index) => (
                <React.Fragment key={message.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemText
                      primary={
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            mb: 1,
                          }}
                        >
                          <Chip
                            label={message.event.type}
                            color={getEventTypeColor(message.event.type)}
                            size="small"
                          />
                          <Typography variant="body2" color="text.secondary">
                            {format(message.timestamp, 'HH:mm:ss.SSS')}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            ID: {message.event.id}
                          </Typography>
                          {message.event.user_id && (
                            <Typography variant="body2" color="text.secondary">
                              User: {message.event.user_id}
                            </Typography>
                          )}
                        </Box>
                      }
                      secondary={
                        <Box>
                          {/* Event Data Summary */}
                          <Box sx={{ mb: 1 }}>
                            {typeof message.event.data === 'object'
                              ? `Data: ${Object.keys(message.event.data || {}).join(', ')}`
                              : `Data: ${String(message.event.data).substring(0, 100)}...`}
                          </Box>

                          {/* Raw Data (if enabled) */}
                          {settings.showRawData && (
                            <Paper
                              sx={{ p: 2, mt: 1, backgroundColor: 'grey.50' }}
                            >
                              <Typography
                                variant="body2"
                                component="pre"
                                sx={{
                                  fontSize: '0.75rem',
                                  whiteSpace: 'pre-wrap',
                                }}
                              >
                                {message.rawData}
                              </Typography>
                            </Paper>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < filteredMessages.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
            <div ref={messagesEndRef} />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SSEMonitorPage;
