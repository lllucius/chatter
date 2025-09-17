import { useState, useCallback } from 'react';

export interface UseFormOptions<T> {
  initialValues: T;
  onSubmit?: (values: T) => Promise<void> | void;
  validate?: (values: T) => Record<string, string>;
}

export const useForm = <T extends Record<string, unknown>>(
  options: UseFormOptions<T>
) => {
  const [values, setValues] = useState<T>(options.initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleChange = useCallback(
    (field: keyof T, value: unknown) => {
      setValues((prev) => ({ ...prev, [field]: value }));
      // Clear error when field is changed
      if (errors[field as string]) {
        setErrors((prev) => ({ ...prev, [field]: undefined }));
      }
    },
    [errors]
  );

  const handleBlur = useCallback(
    (field: keyof T) => {
      setTouched((prev) => ({ ...prev, [field]: true }));

      // Validate single field if validator exists
      if (options.validate) {
        const fieldErrors = options.validate(values);
        if (fieldErrors[field as string]) {
          setErrors((prev) => ({
            ...prev,
            [field]: fieldErrors[field as string],
          }));
        }
      }
    },
    [values, options.validate]
  );

  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      if (e) {
        e.preventDefault();
      }

      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce(
        (acc, key) => {
          acc[key] = true;
          return acc;
        },
        {} as Record<string, boolean>
      );
      setTouched(allTouched);

      // Validate all fields
      if (options.validate) {
        const validationErrors = options.validate(values);
        setErrors(validationErrors);

        // Don't submit if there are errors
        if (Object.keys(validationErrors).length > 0) {
          return;
        }
      }

      if (options.onSubmit) {
        try {
          setIsSubmitting(true);
          await options.onSubmit(values);
        } finally {
          setIsSubmitting(false);
        }
      }
    },
    [values, options]
  );

  const reset = useCallback(() => {
    setValues(options.initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [options.initialValues]);

  const setFieldValue = useCallback(
    (field: keyof T, value: unknown) => {
      handleChange(field, value);
    },
    [handleChange]
  );

  const setFieldError = useCallback((field: keyof T, error: string) => {
    setErrors((prev) => ({ ...prev, [field]: error }));
  }, []);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    setFieldValue,
    setFieldError,
    setValues,
  };
};

// Export alias for backward compatibility
export const useFormGeneric = useForm;
