import React, { memo } from 'react';
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '../../utils/mui';
import { BackupIcon, DownloadIcon } from '../../utils/icons';
import { BackupResponse } from 'chatter-sdk';

interface BackupsTabProps {
  backups: BackupResponse[];
  loading: boolean;
  onCreateBackup: () => void;
  onDownloadBackup: (backup: BackupResponse) => void;
}

const BackupsTab: React.FC<BackupsTabProps> = memo(({
  backups,
  loading,
  onCreateBackup,
  onDownloadBackup,
}) => {
  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<BackupIcon />}
          onClick={onCreateBackup}
          disabled={loading}
        >
          Create Backup
        </Button>
      </Box>

      <List>
        {backups.map((backup) => (
          <ListItem
            key={backup.id}
            secondaryAction={
              <Button
                size="small"
                startIcon={<DownloadIcon />}
                onClick={() => onDownloadBackup(backup)}
              >
                Download
              </Button>
            }
          >
            <ListItemIcon>
              <BackupIcon />
            </ListItemIcon>
            <ListItemText
              primary={backup.name}
              secondary={
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <Chip
                    size="small"
                    label={backup.status}
                    color={
                      backup.status === 'completed'
                        ? 'success'
                        : backup.status === 'failed'
                          ? 'error'
                          : 'default'
                    }
                  />
                  <Typography variant="caption" color="text.secondary">
                    {new Date(backup.created_at).toLocaleString()}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        ))}
        {backups.length === 0 && (
          <ListItem>
            <ListItemText
              primary="No backups found"
              secondary="Create your first backup to get started"
            />
          </ListItem>
        )}
      </List>
    </Box>
  );
});

BackupsTab.displayName = 'BackupsTab';

export default BackupsTab;