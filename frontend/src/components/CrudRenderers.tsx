import React from 'react';
import { Chip, Typography, Box, Switch } from '@mui/material';
import { format } from 'date-fns';
import { CrudColumn } from './CrudDataTable';
import { getStatusColor } from '../utils/common';

/**
 * Common renderers for CRUD table columns to reduce code duplication
 */

export const createStatusChipRenderer = <T,>(colorMapping?: {
  [key: string]:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning';
}): CrudColumn<T>['render'] => {
  const StatusChipRenderer = (value: string) => {
    const color = colorMapping?.[value?.toLowerCase()] || getStatusColor(value);

    return <Chip label={value} color={color} size="small" />;
  };
  StatusChipRenderer.displayName = 'StatusChipRenderer';
  return StatusChipRenderer;
};

export const createCategoryChipRenderer = <T,>(
  color:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning' = 'primary',
  variant: 'filled' | 'outlined' = 'outlined'
): CrudColumn<T>['render'] => {
  const CategoryChipRenderer = (value: string) => (
    <Chip label={value} size="small" color={color} variant={variant} />
  );
  CategoryChipRenderer.displayName = 'CategoryChipRenderer';
  return CategoryChipRenderer;
};

export const createTypeChipRenderer = <T,>(
  color:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning' = 'secondary',
  variant: 'filled' | 'outlined' = 'outlined'
): CrudColumn<T>['render'] => {
  const TypeChipRenderer = (value: string): JSX.Element => (
    <Chip
      label={value?.replace(/[_-]/g, ' ')}
      size="small"
      color={color}
      variant={variant}
    />
  );
  TypeChipRenderer.displayName = 'TypeChipRenderer';
  return TypeChipRenderer;
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

export const createNameWithDescriptionRenderer = <
  T extends { name?: string; display_name?: string; description?: string },
>(): CrudColumn<T>['render'] => {
  return (value: unknown, item: T): JSX.Element => (
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
  return (value: boolean): JSX.Element => (
    <Switch checked={!!value} disabled={disabled} size="small" />
  );
};

export const createMonospaceTextRenderer = <T,>(): CrudColumn<T>['render'] => {
  return (value: string): JSX.Element => (
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
  return (value: number | undefined): JSX.Element => (
    <Typography variant="body2">
      {value !== undefined
        ? `${value} ${value === 1 ? singular : plural}`
        : unknownText}
    </Typography>
  );
};

export const createPerformanceRenderer = <T,>(
  unit: string = 'ms',
  precision: number = 0
): CrudColumn<T>['render'] => {
  return (value: number): JSX.Element => (
    <Typography variant="body2">
      {value ? `${value.toFixed(precision)}${unit}` : 'N/A'}
    </Typography>
  );
};

export const createUsageStatsRenderer = <
  T extends { total_errors?: number },
>(): CrudColumn<T>['render'] => {
  return (value: number, item: T): JSX.Element => (
    <Box>
      <Typography variant="body2">Calls: {value}</Typography>
      <Typography variant="body2" color="text.secondary">
        Errors: {item.total_errors || 0}
      </Typography>
    </Box>
  );
};

export const createConditionalChipRenderer = <T,>(
  condition: (value: unknown, item: T) => boolean,
  label: string,
  color:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning' = 'primary',
  variant: 'filled' | 'outlined' = 'outlined'
): CrudColumn<T>['render'] => {
  return (value: unknown, item: T) =>
    condition(value, item) ? (
      <Chip label={label} color={color} variant={variant} size="small" />
    ) : null;
};
