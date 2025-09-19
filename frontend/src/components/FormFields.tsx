import React from 'react';
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  FormControlLabel,
  Switch,
  Box,
} from '../utils/mui';

/**
 * Common form field components to reduce repetitive form patterns
 */

export interface BaseFieldProps {
  label: string;
  value: unknown;
  onChange: (value: unknown) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  fullWidth?: boolean;
}

export interface TextFieldProps extends BaseFieldProps {
  type?: 'text' | 'number' | 'email' | 'password' | 'url';
  multiline?: boolean;
  rows?: number;
  placeholder?: string;
  helperText?: string;
  inputProps?: Record<string, unknown>;
}

export interface SelectFieldProps extends BaseFieldProps {
  options: Array<{
    value: string | number;
    label: string;
    disabled?: boolean;
  }>;
  emptyLabel?: string;
}

export interface SliderFieldProps
  extends Omit<BaseFieldProps, 'value' | 'onChange'> {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  marks?: Array<{ value: number; label: string }>;
  displayValue?: boolean;
  formatLabel?: (value: number) => string;
}

export interface SwitchFieldProps extends BaseFieldProps {
  helperText?: string;
}

/**
 * Enhanced TextField with consistent styling and error handling
 */
export const FormTextField: React.FC<TextFieldProps> = ({
  label,
  value,
  onChange,
  error,
  disabled = false,
  required = false,
  fullWidth = true,
  type = 'text',
  multiline = false,
  rows,
  placeholder,
  helperText,
  inputProps,
}) => {
  return (
    <TextField
      fullWidth={fullWidth}
      label={label}
      type={type}
      value={value || ''}
      onChange={(e) => {
        const newValue =
          type === 'number'
            ? e.target.value
              ? parseFloat(e.target.value)
              : ''
            : e.target.value;
        onChange(newValue);
      }}
      error={!!error}
      helperText={error || helperText}
      disabled={disabled}
      required={required}
      multiline={multiline}
      rows={rows}
      placeholder={placeholder}
      inputProps={inputProps}
    />
  );
};

/**
 * Enhanced Select field with consistent styling
 */
export const FormSelectField: React.FC<SelectFieldProps> = ({
  label,
  value,
  onChange,
  options,
  error,
  disabled = false,
  required = false,
  fullWidth = true,
  emptyLabel = 'Select...',
}) => {
  return (
    <FormControl
      fullWidth={fullWidth}
      error={!!error}
      disabled={disabled}
      required={required}
    >
      <InputLabel>{label}</InputLabel>
      <Select
        value={value || ''}
        label={label}
        onChange={(e) => onChange(e.target.value)}
      >
        {emptyLabel && (
          <MenuItem value="">
            <em>{emptyLabel}</em>
          </MenuItem>
        )}
        {options.map((option) => (
          <MenuItem
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </MenuItem>
        ))}
      </Select>
      {error && (
        <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.75 }}>
          {error}
        </Typography>
      )}
    </FormControl>
  );
};

/**
 * Enhanced Slider field with value display
 */
export const FormSliderField: React.FC<SliderFieldProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 0.1,
  marks,
  error,
  disabled = false,
  displayValue = true,
  formatLabel,
}) => {
  const displayText = formatLabel ? formatLabel(value) : value;

  return (
    <Box>
      <Typography gutterBottom>
        {label}
        {displayValue && `: ${displayText}`}
      </Typography>
      <Slider
        value={value || min}
        onChange={(_, newValue) => onChange(newValue)}
        min={min}
        max={max}
        step={step}
        marks={marks}
        disabled={disabled}
      />
      {error && (
        <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
          {error}
        </Typography>
      )}
    </Box>
  );
};

/**
 * Enhanced Switch field
 */
export const FormSwitchField: React.FC<SwitchFieldProps> = ({
  label,
  value,
  onChange,
  error,
  disabled = false,
  helperText,
}) => {
  return (
    <Box>
      <FormControlLabel
        control={
          <Switch
            checked={!!value}
            onChange={(e) => onChange(e.target.checked)}
            disabled={disabled}
          />
        }
        label={label}
      />
      {(error || helperText) && (
        <Typography
          variant="caption"
          color={error ? 'error' : 'text.secondary'}
          sx={{ display: 'block', mt: 0.5, ml: 1.75 }}
        >
          {error || helperText}
        </Typography>
      )}
    </Box>
  );
};

/**
 * Preset field configurations for common use cases
 */
export const CommonFieldPresets = {
  name: {
    label: 'Name',
    required: true,
    placeholder: 'Enter name',
  },
  description: {
    label: 'Description',
    multiline: true,
    rows: 3,
    placeholder: 'Enter description (optional)',
  },
  email: {
    label: 'Email',
    type: 'email' as const,
    required: true,
    placeholder: 'Enter email address',
  },
  url: {
    label: 'URL',
    type: 'url' as const,
    placeholder: 'https://...',
  },
  temperature: {
    label: 'Temperature',
    min: 0,
    max: 2,
    step: 0.1,
    marks: [
      { value: 0, label: '0 (Deterministic)' },
      { value: 1, label: '1 (Balanced)' },
      { value: 2, label: '2 (Creative)' },
    ],
    formatLabel: (value: number) =>
      `${value} (${
        value < 0.3 ? 'Deterministic' : value < 1.3 ? 'Balanced' : 'Creative'
      })`,
  },
  maxTokens: {
    label: 'Max Tokens',
    type: 'number' as const,
    inputProps: { min: 1, max: 32000 },
  },
};
