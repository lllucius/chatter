import React from 'react';
import { Chip, Typography, Box, Switch } from '@mui/material';
import { format } from 'date-fns';
import { CrudColumn } from './CrudDataTable';

/**
 * Common renderers for CRUD table columns to reduce code duplication
 */

export const createStatusChipRenderer = <T,>(
  colorMapping?: { [key: string]: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }
): CrudColumn<T>['render'] => {
  return (value: string) => {
    const defaultColorMapping: { [key: string]: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' } = {
      enabled: 'success',
      active: 'success',
      success: 'success',
      error: 'error',
      failed: 'error',
      disabled: 'default',
      inactive: 'default',
      pending: 'warning',
      ...colorMapping
    };
    
    return (
      <Chip 
        label={value}
        color={defaultColorMapping[value?.toLowerCase()] || 'default'}
        size="small"
      />
    );
  };
};

export const createCategoryChipRenderer = <T,>(
  color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'primary',
  variant: 'filled' | 'outlined' = 'outlined'
): CrudColumn<T>['render'] => {
  return (value: string) => (
    <Chip 
      label={value} 
      size="small" 
      color={color}
      variant={variant}
    />
  );
};

export const createTypeChipRenderer = <T,>(
  color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'secondary',
  variant: 'filled' | 'outlined' = 'outlined'
): CrudColumn<T>['render'] => {
  return (value: string) => (
    <Chip 
      label={value?.replace(/[_-]/g, ' ')}
      size="small" 
      color={color}
      variant={variant}
    />
  );
};

export const createDateRenderer = <T,>(
  dateFormat: string = 'MMM dd, yyyy'
): CrudColumn<T>['render'] => {
  return (value: string | Date) => {
    if (!value) return '';
    try {
      const date = typeof value === 'string' ? new Date(value) : value;
      return format(date, dateFormat);
    } catch {
      return '';
    }
  };
};

export const createNameWithDescriptionRenderer = <T extends { name?: string; display_name?: string; description?: string }>(
): CrudColumn<T>['render'] => {
  return (value: any, item: T) => (
    <Box>
      <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
        {value || item.display_name || item.name}
      </Typography>
      {item.description && (
        <Typography variant="body2" color="text.secondary">
          {item.description}
        </Typography>
      )}
    </Box>
  );
};

export const createBooleanSwitchRenderer = <T,>(
  disabled: boolean = true
): CrudColumn<T>['render'] => {
  return (value: boolean) => (
    <Switch
      checked={!!value}
      disabled={disabled}
      size="small"
    />
  );
};

export const createMonospaceTextRenderer = <T,>(): CrudColumn<T>['render'] => {
  return (value: string) => (
    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
      {value || '—'}
    </Typography>
  );
};

export const createCountRenderer = <T,>(
  singular: string,
  plural: string,
  unknownText: string = 'Unknown'
): CrudColumn<T>['render'] => {
  return (value: number | undefined) => (
    <Typography variant="body2">
      {value !== undefined 
        ? `${value} ${value === 1 ? singular : plural}` 
        : unknownText
      }
    </Typography>
  );
};

export const createPerformanceRenderer = <T,>(
  unit: string = 'ms',
  precision: number = 0
): CrudColumn<T>['render'] => {
  return (value: number) => (
    <Typography variant="body2">
      {value ? `${value.toFixed(precision)}${unit}` : 'N/A'}
    </Typography>
  );
};

export const createUsageStatsRenderer = <T extends { total_errors?: number }>(
): CrudColumn<T>['render'] => {
  return (value: number, item: T) => (
    <Box>
      <Typography variant="body2">
        Calls: {value}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Errors: {item.total_errors || 0}
      </Typography>
    </Box>
  );
};

export const createConditionalChipRenderer = <T,>(
  condition: (value: any, item: T) => boolean,
  label: string,
  color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'primary',
  variant: 'filled' | 'outlined' = 'outlined'
): CrudColumn<T>['render'] => {
  return (value: any, item: T) => 
    condition(value, item) ? (
      <Chip 
        label={label}
        color={color}
        variant={variant}
        size="small"
      />
    ) : null;
};