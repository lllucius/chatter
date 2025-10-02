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
  const StatusChipRenderer = (value: unknown, _item: T) => {
    const valueStr = String(value || '');
    const color =
      colorMapping?.[valueStr?.toLowerCase()] || getStatusColor(valueStr);

    return <Chip label={valueStr} color={color} size="small" />;
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
  const CategoryChipRenderer = (value: unknown, _item: T) => (
    <Chip
      label={String(value || '')}
      size="small"
      color={color}
      variant={variant}
    />
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
  const TypeChipRenderer = (value: unknown, _item: T): React.ReactElement => {
    const valueStr = String(value || '');
    return (
      <Chip
        label={valueStr?.replace(/[_-]/g, ' ')}
        size="small"
        color={color}
        variant={variant}
      />
    );
  };
  TypeChipRenderer.displayName = 'TypeChipRenderer';
  return TypeChipRenderer;
};

export const createDateRenderer = <T,>(
  dateFormat: string = 'MMM dd, yyyy'
): CrudColumn<T>['render'] => {
  return (value: unknown, _item: T) => {
    if (!value) return '';
    try {
      const date =
        typeof value === 'string'
          ? new Date(value)
          : value instanceof Date
            ? value
            : new Date(String(value));
      return format(date, dateFormat);
    } catch {
      return '';
    }
  };
};

export const createNameWithDescriptionRenderer = <
  T extends { name?: string; display_name?: string; description?: string | null },
>(): CrudColumn<T>['render'] => {
  return (value: unknown, item: T): React.ReactElement => {
    const displayText = String(value || item.display_name || item.name || '');
    return (
      <Box>
        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
          {displayText}
        </Typography>
        {item.description && (
          <Typography variant="body2" color="text.secondary">
            {item.description}
          </Typography>
        )}
      </Box>
    );
  };
};

export const createBooleanSwitchRenderer = <T,>(
  disabled: boolean = true
): CrudColumn<T>['render'] => {
  return (value: unknown, _item: T): React.ReactElement => (
    <Switch checked={!!value} disabled={disabled} size="small" />
  );
};

export const createMonospaceTextRenderer = <T,>(): CrudColumn<T>['render'] => {
  return (value: unknown, _item: T): React.ReactElement => (
    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
      {String(value || '') || '—'}
    </Typography>
  );
};

export const createCountRenderer = <T,>(
  singular: string,
  plural: string,
  unknownText: string = 'Unknown'
): CrudColumn<T>['render'] => {
  return (value: unknown, _item: T): React.ReactElement => {
    const numValue =
      typeof value === 'number'
        ? value
        : value !== undefined && value !== null
          ? Number(value)
          : undefined;
    return (
      <Typography variant="body2">
        {numValue !== undefined && !isNaN(numValue)
          ? `${numValue} ${numValue === 1 ? singular : plural}`
          : unknownText}
      </Typography>
    );
  };
};

export const createPerformanceRenderer = <T,>(
  unit: string = 'ms',
  precision: number = 0
): CrudColumn<T>['render'] => {
  return (value: unknown, _item: T): React.ReactElement => {
    const numValue =
      typeof value === 'number'
        ? value
        : value !== undefined && value !== null
          ? Number(value)
          : NaN;
    return (
      <Typography variant="body2">
        {!isNaN(numValue) ? `${numValue.toFixed(precision)}${unit}` : 'N/A'}
      </Typography>
    );
  };
};

export const createUsageStatsRenderer = <
  T extends { total_errors?: number },
>(): CrudColumn<T>['render'] => {
  return (value: unknown, item: T): React.ReactElement => {
    const numValue =
      typeof value === 'number'
        ? value
        : value !== undefined && value !== null
          ? Number(value)
          : 0;
    return (
      <Box>
        <Typography variant="body2">
          Calls: {!isNaN(numValue) ? numValue : 0}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Errors: {item.total_errors || 0}
        </Typography>
      </Box>
    );
  };
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
