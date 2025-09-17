/**
 * SSE Monitor Demo
 *
 * This file demonstrates how the SSE Monitor component would work with real SSE events.
 * It shows the expected behavior and data flow when the backend is available.
 */

// Example SSE events that would be captured by the monitor
const sampleSSEEvents = [
  {
    id: '01JQKY0D8Z6M1N2P3Q4R5S6T7U',
    type: 'chat.message_chunk',
    data: {
      message_id: '01JQKY0D8Z6M1N2P3Q4R5S6T7V',
      content: 'Hello, how can I help you today?',
      chunk_index: 0,
      is_final: false,
    },
    timestamp: '2024-01-15T10:30:45.123Z',
    user_id: '01JQKY0D8Z6M1N2P3Q4R5S6T7W',
    metadata: {
      priority: 'normal',
      category: 'streaming',
      correlation_id: '01JQKY0D8Z6M1N2P3Q4R5S6T7X',
    },
  },
  {
    id: '01JQKY0D8Z6M1N2P3Q4R5S6T7Y',
    type: 'workflow.started',
    data: {
      workflow_id: '01JQKY0D8Z6M1N2P3Q4R5S6T7Z',
      workflow_name: 'Document Processing Pipeline',
      started_at: '2024-01-15T10:30:50.456Z',
    },
    timestamp: '2024-01-15T10:30:50.456Z',
    user_id: '01JQKY0D8Z6M1N2P3Q4R5S6T7W',
    metadata: {
      priority: 'high',
      category: 'workflow',
      source_system: 'workflow-engine',
    },
  },
  {
    id: '01JQKY0D8Z6M1N2P3Q4R5S6T80',
    type: 'system.alert',
    data: {
      message: 'High memory usage detected',
      severity: 'warning',
      details: {
        memory_usage: '85%',
        threshold: '80%',
        recommendation: 'Consider scaling up resources',
      },
    },
    timestamp: '2024-01-15T10:31:15.789Z',
    metadata: {
      priority: 'critical',
      category: 'monitoring',
      source_system: 'monitoring-service',
    },
  },
  {
    id: '01JQKY0D8Z6M1N2P3Q4R5S6T81',
    type: 'document.processing_completed',
    data: {
      document_id: '01JQKY0D8Z6M1N2P3Q4R5S6T82',
      result: {
        chunks_created: 15,
        text_length: 5420,
        processing_time: 2.34,
      },
      completed_at: '2024-01-15T10:31:30.012Z',
    },
    timestamp: '2024-01-15T10:31:30.012Z',
    user_id: '01JQKY0D8Z6M1N2P3Q4R5S6T7W',
    metadata: {
      priority: 'normal',
      category: 'realtime',
      source_system: 'document-processor',
    },
  },
];

/**
 * How the SSE Monitor would work:
 *
 * 1. User navigates to /sse-monitor
 * 2. Component renders with all controls
 * 3. User clicks "Start Monitoring"
 * 4. Component calls manager.addEventListener('*', handleSSEEvent)
 * 5. Real SSE events arrive from backend
 * 6. Events are displayed in real-time with:
 *    - Event type badge (colored by category)
 *    - Timestamp (HH:mm:ss.SSS format)
 *    - Event ID and User ID
 *    - Data summary or full JSON (if raw view enabled)
 * 7. User can filter by event type
 * 8. Console logging captures events for debugging
 * 9. Export functionality saves filtered events to JSON
 *
 * Event Processing Flow:
 * - SSE stream -> SSEEventManager -> Event Listener -> Monitor Display
 * - Each event shows with appropriate color coding
 * - Auto-scroll keeps newest events visible
 * - Statistics update in real-time
 */

/**
 * Console output when logging is enabled:
 *
 * 🔴 SSE Event: chat.message_chunk
 *   📅 Timestamp: 10:30:45.123
 *   📋 Event: {id: "01JQKY...", type: "chat.message_chunk", ...}
 *   🔗 Event ID: 01JQKY0D8Z6M1N2P3Q4R5S6T7U
 *   👤 User ID: 01JQKY0D8Z6M1N2P3Q4R5S6T7W
 *
 * 🔴 SSE Event: workflow.started
 *   📅 Timestamp: 10:30:50.456
 *   📋 Event: {id: "01JQKY...", type: "workflow.started", ...}
 *   🔗 Event ID: 01JQKY0D8Z6M1N2P3Q4R5S6T7Y
 *   👤 User ID: 01JQKY0D8Z6M1N2P3Q4R5S6T7W
 */

/**
 * Filter options would include:
 * - All Events (default)
 * - chat.message_chunk
 * - workflow.started
 * - system.alert
 * - document.processing_completed
 * - (any other event types that arrive)
 */

/**
 * Export format (JSON):
 * [
 *   {
 *     "id": "msg-1642247445123-0",
 *     "timestamp": "2024-01-15T10:30:45.123Z",
 *     "event": { ... full event object ... },
 *     "rawData": "{\n  \"id\": \"01JQKY...\",\n  \"type\": \"chat.message_chunk\",\n  ...\n}"
 *   },
 *   ...
 * ]
 */

export { sampleSSEEvents };
