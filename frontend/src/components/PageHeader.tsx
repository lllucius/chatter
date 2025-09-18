import React from 'react';
import { Box, Typography, Button, Chip } from '@mui/material';
import { AddIcon, RefreshIcon } from '../utils/icons';

/**
 * Common page header component that consolidates repeated header patterns
 * across CRUD pages
 */

export interface PageHeaderAction {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  variant?: 'text' | 'outlined' | 'contained';
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  disabled?: boolean;
}

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: PageHeaderAction[];
  onRefresh?: () => void;
  onAdd?: () => void;
  refreshLabel?: string;
  addLabel?: string;
  stats?: Array<{
    label: string;
    value: string | number;
    color?:
      | 'default'
      | 'primary'
      | 'secondary'
      | 'error'
      | 'info'
      | 'success'
      | 'warning';
  }>;
  loading?: boolean;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  actions = [],
  onRefresh,
  onAdd,
  refreshLabel = 'Refresh',
  addLabel = 'Add',
  stats = [],
  loading = false,
}) => {
  // Build default actions
  const defaultActions: PageHeaderAction[] = [];

  if (onRefresh) {
    defaultActions.push({
      label: refreshLabel,
      icon: <RefreshIcon />,
      onClick: onRefresh,
      variant: 'outlined',
      disabled: loading,
    });
  }

  if (onAdd) {
    defaultActions.push({
      label: addLabel,
      icon: <AddIcon />,
      onClick: onAdd,
      variant: 'contained',
      color: 'primary',
    });
  }

  const allActions = [...defaultActions, ...actions];

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        mb: 3,
        gap: 2,
        flexWrap: 'wrap',
      }}
    >
      {/* Title and subtitle section */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 'bold' }}
        >
          {title}
        </Typography>

        {subtitle && (
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            {subtitle}
          </Typography>
        )}

        {/* Stats chips */}
        {stats.length > 0 && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {stats.map((stat, index) => (
              <Chip
                key={index}
                label={`${stat.label}: ${stat.value}`}
                color={stat.color || 'default'}
                size="small"
                variant="outlined"
              />
            ))}
          </Box>
        )}
      </Box>

      {/* Actions section */}
      {allActions.length > 0 && (
        <Box
          sx={{
            display: 'flex',
            gap: 1,
            flexWrap: 'wrap',
            alignItems: 'center',
          }}
        >
          {allActions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || 'outlined'}
              color={action.color || 'primary'}
              startIcon={action.icon}
              onClick={action.onClick}
              disabled={action.disabled}
            >
              {action.label}
            </Button>
          ))}
        </Box>
      )}
    </Box>
  );
};

/**
 * Specialized header for CRUD pages with common patterns
 */
export interface CrudPageHeaderProps {
  entityName: string;
  entityNamePlural?: string;
  onRefresh: () => void;
  onAdd: () => void;
  totalCount?: number;
  loading?: boolean;
  additionalActions?: PageHeaderAction[];
}

export const CrudPageHeader: React.FC<CrudPageHeaderProps> = ({
  entityName,
  entityNamePlural,
  onRefresh,
  onAdd,
  totalCount,
  loading,
  additionalActions = [],
}) => {
  const plural = entityNamePlural || `${entityName}s`;

  const stats =
    totalCount !== undefined
      ? [{ label: 'Total', value: totalCount, color: 'primary' as const }]
      : [];

  return (
    <PageHeader
      title={plural}
      onRefresh={onRefresh}
      onAdd={onAdd}
      refreshLabel={`Refresh ${plural}`}
      addLabel={`Add ${entityName}`}
      stats={stats}
      loading={loading}
      actions={additionalActions}
    />
  );
};

export default PageHeader;
