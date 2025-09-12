import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Typography,
  Box,
  Divider,
  Checkbox,
  Alert,
} from '@mui/material';
import {
  Download as DownloadIcon,
} from '@mui/icons-material';
import { format, isValid } from 'date-fns';
import { ChatMessage } from './EnhancedMessage';

// Helper function to safely format timestamps  
const formatTimestamp = (timestamp: Date, formatString: string): string => {
  if (!timestamp || !isValid(timestamp)) {
    return 'Invalid Date';
  }
  return format(timestamp, formatString);
};

interface ChatExportProps {
  open: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  conversationTitle?: string;
}

type ExportFormat = 'json' | 'markdown' | 'txt' | 'pdf';

const ChatExport: React.FC<ChatExportProps> = ({
  open,
  onClose,
  messages,
  conversationTitle = 'Untitled Conversation',
}) => {
  const [exportFormat, setExportFormat] = useState<ExportFormat>('markdown');
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [includeTimestamps, setIncludeTimestamps] = useState(true);
  const [includeSystemMessages, setIncludeSystemMessages] = useState(false);
  const [filename, setFilename] = useState('');
  const [exporting, setExporting] = useState(false);

  const getDefaultFilename = () => {
    const timestamp = format(new Date(), 'yyyy-MM-dd-HHmm');
    const title = conversationTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    return `${title}_${timestamp}`;
  };

  const formatAsJSON = () => {
    const exportData = {
      title: conversationTitle,
      exportedAt: new Date().toISOString(),
      messageCount: filteredMessages.length,
      messages: filteredMessages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp.toISOString(),
        ...(includeMetadata && msg.metadata ? { metadata: msg.metadata } : {}),
        ...(msg.edited ? { edited: true, editedAt: msg.editedAt?.toISOString() } : {}),
        ...(msg.rating ? { rating: msg.rating } : {}),
      })),
    };
    return JSON.stringify(exportData, null, 2);
  };

  const formatAsMarkdown = () => {
    let content = `# ${conversationTitle}\n\n`;
    
    if (includeMetadata) {
      content += `**Exported:** ${format(new Date(), 'PPpp')}\n`;
      content += `**Messages:** ${filteredMessages.length}\n\n`;
      content += '---\n\n';
    }

    filteredMessages.forEach((msg) => {
      const roleEmoji = msg.role === 'user' ? '👤' : msg.role === 'assistant' ? '🤖' : '⚙️';
      const roleName = msg.role === 'user' ? 'User' : msg.role === 'assistant' ? 'Assistant' : 'System';
      
      content += `## ${roleEmoji} ${roleName}`;
      
      if (includeTimestamps) {
        content += ` (${formatTimestamp(msg.timestamp, 'PPpp')})`;
      }
      
      if (msg.edited) {
        content += ' ✏️ *Edited*';
      }
      
      content += '\n\n';
      content += msg.content + '\n\n';
      
      if (includeMetadata && msg.metadata) {
        content += '**Metadata:**\n';
        if (msg.metadata.model) content += `- Model: ${msg.metadata.model}\n`;
        if (msg.metadata.tokens) content += `- Tokens: ${msg.metadata.tokens}\n`;
        if (msg.metadata.processingTime) content += `- Processing Time: ${msg.metadata.processingTime}ms\n`;
        content += '\n';
      }
      
      if (msg.rating) {
        content += `**Rating:** ${'⭐'.repeat(msg.rating)} (${msg.rating}/5)\n\n`;
      }
      
      content += '---\n\n';
    });

    return content;
  };

  const formatAsText = () => {
    let content = `${conversationTitle}\n${'='.repeat(conversationTitle.length)}\n\n`;
    
    if (includeMetadata) {
      content += `Exported: ${format(new Date(), 'PPpp')}\n`;
      content += `Messages: ${filteredMessages.length}\n\n`;
    }

    filteredMessages.forEach((msg, index) => {
      const roleName = msg.role.toUpperCase();
      content += `[${index + 1}] ${roleName}`;
      
      if (includeTimestamps) {
        content += ` (${formatTimestamp(msg.timestamp, 'PPpp')})`;
      }
      
      if (msg.edited) {
        content += ' [EDITED]';
      }
      
      content += ':\n';
      content += msg.content + '\n';
      
      if (includeMetadata && msg.metadata) {
        content += '\nMetadata:\n';
        if (msg.metadata.model) content += `  Model: ${msg.metadata.model}\n`;
        if (msg.metadata.tokens) content += `  Tokens: ${msg.metadata.tokens}\n`;
        if (msg.metadata.processingTime) content += `  Processing Time: ${msg.metadata.processingTime}ms\n`;
      }
      
      if (msg.rating) {
        content += `Rating: ${msg.rating}/5\n`;
      }
      
      content += '\n' + '-'.repeat(50) + '\n\n';
    });

    return content;
  };

  const formatAsPDF = async () => {
    // For PDF export, we'd typically use a library like jsPDF or html2pdf
    // For now, we'll export as HTML that can be printed to PDF
    let html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${conversationTitle}</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }
          .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
          .message { margin-bottom: 30px; padding: 15px; border-left: 4px solid #ddd; }
          .user { border-left-color: #2196f3; background-color: #f5f5f5; }
          .assistant { border-left-color: #4caf50; }
          .system { border-left-color: #ff9800; }
          .role { font-weight: bold; margin-bottom: 10px; }
          .timestamp { color: #666; font-size: 0.9em; }
          .metadata { font-size: 0.8em; color: #666; margin-top: 10px; }
          .content { white-space: pre-wrap; line-height: 1.5; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>${conversationTitle}</h1>
          ${includeMetadata ? `
            <p>Exported: ${format(new Date(), 'PPpp')}</p>
            <p>Messages: ${filteredMessages.length}</p>
          ` : ''}
        </div>
    `;

    filteredMessages.forEach((msg) => {
      html += `
        <div class="message ${msg.role}">
          <div class="role">
            ${msg.role === 'user' ? '👤 User' : msg.role === 'assistant' ? '🤖 Assistant' : '⚙️ System'}
            ${includeTimestamps ? `<span class="timestamp"> - ${formatTimestamp(msg.timestamp, 'PPpp')}</span>` : ''}
            ${msg.edited ? ' <span style="color: orange;">✏️ Edited</span>' : ''}
          </div>
          <div class="content">${msg.content.replace(/\n/g, '<br>')}</div>
          ${includeMetadata && msg.metadata ? `
            <div class="metadata">
              ${msg.metadata.model ? `Model: ${msg.metadata.model} | ` : ''}
              ${msg.metadata.tokens ? `Tokens: ${msg.metadata.tokens} | ` : ''}
              ${msg.metadata.processingTime ? `Processing: ${msg.metadata.processingTime}ms` : ''}
            </div>
          ` : ''}
          ${msg.rating ? `<div class="metadata">Rating: ${'⭐'.repeat(msg.rating)} (${msg.rating}/5)</div>` : ''}
        </div>
      `;
    });

    html += '</body></html>';
    return html;
  };

  const filteredMessages = messages.filter(msg => 
    includeSystemMessages || msg.role !== 'system'
  );

  const handleExport = async () => {
    try {
      setExporting(true);
      
      let content: string;
      let mimeType: string;
      let extension: string;

      switch (exportFormat) {
        case 'json':
          content = formatAsJSON();
          mimeType = 'application/json';
          extension = 'json';
          break;
        case 'markdown':
          content = formatAsMarkdown();
          mimeType = 'text/markdown';
          extension = 'md';
          break;
        case 'txt':
          content = formatAsText();
          mimeType = 'text/plain';
          extension = 'txt';
          break;
        case 'pdf':
          content = await formatAsPDF();
          mimeType = 'text/html';
          extension = 'html';
          break;
        default:
          throw new Error('Unsupported format');
      }

      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename || getDefaultFilename()}.${extension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      onClose();
    } catch {
      // Export failed - user will notice no file was downloaded
    } finally {
      setExporting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DownloadIcon />
          Export Conversation
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <TextField
            fullWidth
            label="Filename"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder={getDefaultFilename()}
            helperText="Leave empty to use default filename"
          />

          <FormControl component="fieldset">
            <FormLabel component="legend">Export Format</FormLabel>
            <RadioGroup
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as ExportFormat)}
            >
              <FormControlLabel
                value="markdown"
                control={<Radio />}
                label="Markdown (.md) - Best for documentation"
              />
              <FormControlLabel
                value="json"
                control={<Radio />}
                label="JSON (.json) - Machine readable, preserves all data"
              />
              <FormControlLabel
                value="txt"
                control={<Radio />}
                label="Plain Text (.txt) - Simple text format"
              />
              <FormControlLabel
                value="pdf"
                control={<Radio />}
                label="PDF (.html) - Print-ready format"
              />
            </RadioGroup>
          </FormControl>

          <Divider />

          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Export Options
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeTimestamps}
                  onChange={(e) => setIncludeTimestamps(e.target.checked)}
                />
              }
              label="Include timestamps"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeMetadata}
                  onChange={(e) => setIncludeMetadata(e.target.checked)}
                />
              }
              label="Include metadata (tokens, processing time, etc.)"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeSystemMessages}
                  onChange={(e) => setIncludeSystemMessages(e.target.checked)}
                />
              }
              label="Include system messages"
            />
          </Box>

          <Alert severity="info">
            Exporting {filteredMessages.length} message{filteredMessages.length !== 1 ? 's' : ''}
          </Alert>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={exporting}>
          Cancel
        </Button>
        <Button
          onClick={handleExport}
          variant="contained"
          disabled={exporting || filteredMessages.length === 0}
          startIcon={<DownloadIcon />}
        >
          {exporting ? 'Exporting...' : 'Export'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ChatExport;