import { useState, useEffect, useCallback } from 'react';

/**
 * Base form hook that consolidates common form patterns used across
 * all form components in the application
 */

export interface BaseFormProps<TCreate, TUpdate> {
  open: boolean;
  mode: 'create' | 'edit';
  initialData?: TUpdate;
  onClose: () => void;
  onSubmit: (data: TCreate | TUpdate) => Promise<void>;
}

export interface UseBaseFormOptions<TData> {
  defaultData: TData;
  resetOnOpen?: boolean;
  resetOnClose?: boolean;
  transformInitialData?: (initialData: unknown) => TData;
}

export interface UseBaseFormReturn<TData> {
  formData: TData;
  setFormData: React.Dispatch<React.SetStateAction<TData>>;
  updateFormData: (updates: Partial<TData>) => void;
  resetForm: () => void;
  isSubmitting: boolean;
  setIsSubmitting: React.Dispatch<React.SetStateAction<boolean>>;
  handleSubmit: (
    onSubmit: (data: TData) => Promise<void>
  ) => () => Promise<void>;
  handleClose: (onClose: () => void) => () => void;
}

export function useBaseForm<TData>(
  options: UseBaseFormOptions<TData>,
  open: boolean,
  mode: 'create' | 'edit',
  initialData?: unknown
): UseBaseFormReturn<TData> {
  const {
    defaultData,
    resetOnOpen = true,
    resetOnClose = true,
    transformInitialData,
  } = options;

  const [formData, setFormData] = useState<TData>(defaultData);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset form data when dialog opens
  useEffect(() => {
    if (open && resetOnOpen) {
      if (mode === 'edit' && initialData) {
        const transformedData = transformInitialData
          ? transformInitialData(initialData)
          : { ...defaultData, ...initialData };
        setFormData(transformedData);
      } else {
        setFormData(defaultData);
      }
    }
  }, [open, mode, initialData, resetOnOpen, defaultData, transformInitialData]);

  const updateFormData = useCallback((updates: Partial<TData>) => {
    setFormData((prev) => ({ ...prev, ...updates }));
  }, []);

  const resetForm = useCallback(() => {
    setFormData(defaultData);
    setIsSubmitting(false);
  }, [defaultData]);

  const handleSubmit = useCallback(
    (onSubmit: (data: TData) => Promise<void>) => {
      return async () => {
        try {
          setIsSubmitting(true);
          await onSubmit(formData);
        } finally {
          setIsSubmitting(false);
        }
      };
    },
    [formData]
  );

  const handleClose = useCallback(
    (onClose: () => void) => {
      return () => {
        if (resetOnClose) {
          resetForm();
        }
        onClose();
      };
    },
    [resetOnClose, resetForm]
  );

  return {
    formData,
    setFormData,
    updateFormData,
    resetForm,
    isSubmitting,
    setIsSubmitting,
    handleSubmit,
    handleClose,
  };
}

/**
 * Common form validation utilities
 */
export interface ValidationRule<T = unknown> {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: T) => string | null;
}

export interface ValidationErrors {
  [key: string]: string;
}

export function validateField(
  value: unknown,
  rules: ValidationRule
): string | null {
  if (
    rules.required &&
    (!value || (typeof value === 'string' && !value.trim()))
  ) {
    return 'This field is required';
  }

  if (value && typeof value === 'string') {
    if (rules.minLength && value.length < rules.minLength) {
      return `Minimum length is ${rules.minLength} characters`;
    }

    if (rules.maxLength && value.length > rules.maxLength) {
      return `Maximum length is ${rules.maxLength} characters`;
    }

    if (rules.pattern && !rules.pattern.test(value)) {
      return 'Invalid format';
    }
  }

  if (rules.custom) {
    return rules.custom(value);
  }

  return null;
}

export function validateForm<T extends Record<string, unknown>>(
  data: T,
  rules: { [K in keyof T]?: ValidationRule }
): ValidationErrors {
  const errors: ValidationErrors = {};

  for (const [field, fieldRules] of Object.entries(rules)) {
    if (fieldRules) {
      const error = validateField(data[field], fieldRules);
      if (error) {
        errors[field] = error;
      }
    }
  }

  return errors;
}

/**
 * Hook for form validation
 */
export function useFormValidation<T extends Record<string, unknown>>(
  data: T,
  rules: { [K in keyof T]?: ValidationRule }
) {
  const [errors, setErrors] = useState<ValidationErrors>({});

  const validate = useCallback(() => {
    const newErrors = validateForm(data, rules);
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [data, rules]);

  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  const setFieldError = useCallback((field: string, error: string) => {
    setErrors((prev) => ({ ...prev, [field]: error }));
  }, []);

  const clearFieldError = useCallback((field: string) => {
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
  }, []);

  return {
    errors,
    validate,
    clearErrors,
    setFieldError,
    clearFieldError,
    hasErrors: Object.keys(errors).length > 0,
  };
}
