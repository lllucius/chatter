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
  MenuItem,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  Grid,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
  Console as ConsoleIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useSSE } from '../services/sse-context';
import { AnySSEEvent, SSEEventType } from '../services/sse-types';

interface SSEMessageEntry {
  id: string;
  timestamp: Date;
  event: AnySSEEvent;
  rawData: string;
}

const SSEMonitorPage: React.FC = () => {
  const { manager, isConnected } = useSSE();
  const [messages, setMessages] = useState<SSEMessageEntry[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [consoleLogging, setConsoleLogging] = useState(() => {
    // Load console logging setting from localStorage
    const saved = localStorage.getItem('sse-monitor-console-logging');
    return saved ? JSON.parse(saved) : false;
  });
  const [filterType, setFilterType] = useState<string>('all');
  const [maxMessages, setMaxMessages] = useState(100);
  const [showRawData, setShowRawData] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageCountRef = useRef(0);

  // Persist console logging setting to localStorage
  useEffect(() => {
    localStorage.setItem('sse-monitor-console-logging', JSON.stringify(consoleLogging));
  }, [consoleLogging]);

  // Get unique event types from messages for filter dropdown
  const eventTypes = React.useMemo(() => {
    const types = new Set(messages.map(msg => msg.event.type));
    return ['all', ...Array.from(types).sort()];
  }, [messages]);

  // Filter messages based on selected type
  const filteredMessages = React.useMemo(() => {
    if (filterType === 'all') return messages;
    return messages.filter(msg => msg.event.type === filterType);
  }, [messages, filterType]);

  // SSE event handler
  const handleSSEEvent = useCallback((event: AnySSEEvent) => {
    const messageEntry: SSEMessageEntry = {
      id: `${Date.now()}-${messageCountRef.current++}`,
      timestamp: new Date(),
      event,
      rawData: JSON.stringify(event, null, 2),
    };

    setMessages(prev => {
      const newMessages = [messageEntry, ...prev];
      // Keep only the most recent messages based on maxMessages setting
      return newMessages.slice(0, maxMessages);
    });

    // Console logging if enabled
    if (consoleLogging) {
      console.group(`🔴 SSE Event: ${event.type}`);
      console.log('📅 Timestamp:', format(messageEntry.timestamp, 'HH:mm:ss.SSS'));
      console.log('📋 Event:', event);
      console.log('🔗 Event ID:', event.id);
      console.log('👤 User ID:', event.user_id || 'N/A');
      console.groupEnd();
    }
  }, [consoleLogging, maxMessages]);

  // Start monitoring
  const startMonitoring = useCallback(() => {
    if (!manager) return;
    
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
    
    setIsMonitoring(false);
    manager.removeEventListener('*', handleSSEEvent);
  }, [manager, handleSSEEvent]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    messageCountRef.current = 0;
  }, []);

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

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && messagesEndRef.current.scrollIntoView) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isMonitoring) {
        stopMonitoring();
      }
    };
  }, [isMonitoring, stopMonitoring]);

  const getEventTypeColor = (type: string): 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success' => {
    if (type.includes('error') || type.includes('failed')) return 'error';
    if (type.includes('warning') || type.includes('alert')) return 'warning';
    if (type.includes('success') || type.includes('completed')) return 'success';
    if (type.includes('progress') || type.includes('processing')) return 'info';
    if (type.includes('chat') || type.includes('message')) return 'primary';
    if (type.includes('system') || type.includes('connection')) return 'secondary';
    return 'default';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        SSE Monitor
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Real-time debugging tool for Server-Sent Events. Monitor incoming messages, filter by type, and export for analysis.
      </Typography>

      {/* Control Panel */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <Button
                variant={isMonitoring ? "outlined" : "contained"}
                color={isMonitoring ? "secondary" : "primary"}
                startIcon={isMonitoring ? <StopIcon /> : <PlayIcon />}
                onClick={isMonitoring ? stopMonitoring : startMonitoring}
                disabled={!manager}
              >
                {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
              </Button>
            </Grid>
            
            <Grid item>
              <Chip
                label={isConnected ? 'Connected' : 'Disconnected'}
                color={isConnected ? 'success' : 'error'}
                variant="outlined"
              />
            </Grid>

            <Grid item>
              <TextField
                select
                label="Filter by Type"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                size="small"
                sx={{ minWidth: 150 }}
              >
                {eventTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type === 'all' ? 'All Events' : type}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item>
              <TextField
                type="number"
                label="Max Messages"
                value={maxMessages}
                onChange={(e) => setMaxMessages(Math.max(1, Math.min(1000, parseInt(e.target.value) || 100)))}
                size="small"
                sx={{ width: 120 }}
                inputProps={{ min: 1, max: 1000 }}
              />
            </Grid>

            <Grid item>
              <FormControlLabel
                control={
                  <Switch
                    checked={consoleLogging}
                    onChange={(e) => setConsoleLogging(e.target.checked)}
                  />
                }
                label="Console Logging"
              />
            </Grid>

            <Grid item>
              <Tooltip title="Toggle Raw Data View">
                <IconButton onClick={() => setShowRawData(!showRawData)}>
                  {showRawData ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              </Tooltip>
            </Grid>

            <Grid item>
              <Tooltip title="Clear Messages">
                <IconButton onClick={clearMessages}>
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            </Grid>

            <Grid item>
              <Tooltip title="Export Messages">
                <IconButton onClick={exportMessages} disabled={filteredMessages.length === 0}>
                  <DownloadIcon />
                </IconButton>
              </Tooltip>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={3}>
              <Typography variant="h6">{messages.length}</Typography>
              <Typography variant="body2" color="text.secondary">Total Messages</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6">{filteredMessages.length}</Typography>
              <Typography variant="body2" color="text.secondary">Filtered Messages</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6">{eventTypes.length - 1}</Typography>
              <Typography variant="body2" color="text.secondary">Event Types</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6">{isMonitoring ? 'Active' : 'Inactive'}</Typography>
              <Typography variant="body2" color="text.secondary">Monitor Status</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Messages List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Messages {filteredMessages.length > 0 && `(${filteredMessages.length})`}
          </Typography>
          
          {!isMonitoring && messages.length === 0 && (
            <Alert severity="info" sx={{ my: 2 }}>
              Click "Start Monitoring" to begin capturing SSE messages. Make sure you're connected to the SSE stream.
            </Alert>
          )}

          {filteredMessages.length === 0 && messages.length > 0 && (
            <Alert severity="warning" sx={{ my: 2 }}>
              No messages match the selected filter. Try selecting "All Events" or a different event type.
            </Alert>
          )}

          <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
            <List>
              {filteredMessages.map((message, index) => (
                <React.Fragment key={message.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
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
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            {typeof message.event.data === 'object' 
                              ? `Data: ${Object.keys(message.event.data || {}).join(', ')}`
                              : `Data: ${String(message.event.data).substring(0, 100)}...`
                            }
                          </Typography>
                          
                          {/* Raw Data (if enabled) */}
                          {showRawData && (
                            <Paper sx={{ p: 2, mt: 1, backgroundColor: 'grey.50' }}>
                              <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>
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