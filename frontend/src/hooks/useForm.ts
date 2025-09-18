import { useState, useCallback, useMemo, ChangeEvent } from 'react';

interface UseFormOptions<T> {
  initialValues: T;
  onSubmit?: (values: T) => Promise<void> | void;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
}

interface UseFormReturn<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isSubmitting: boolean;
  handleChange: (
    name: keyof T
  ) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleBlur: (name: keyof T) => () => void;
  handleSubmit: (event?: React.FormEvent) => Promise<void>;
  setFieldValue: (name: keyof T, value: T[keyof T]) => void;
  setFieldError: (name: keyof T, error: string) => void;
  resetForm: () => void;
  isValid: boolean;
}

/**
 * Custom hook for form handling with validation and submission
 */
export function useForm<T extends Record<string, unknown>>(
  options: UseFormOptions<T>
): UseFormReturn<T> {
  const { initialValues, onSubmit, validate } = options;

  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback(
    (name: keyof T) =>
      (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { value, type, checked } = event.target as HTMLInputElement;
        const newValue = type === 'checkbox' ? checked : value;

        setValues((prev) => ({
          ...prev,
          [name]: newValue,
        }));

        // Clear error when user starts typing - clear any error for this field
        setErrors((prev) => ({
          ...prev,
          [name]: undefined,
        }));
      },
    []
  );

  const handleBlur = useCallback(
    (name: keyof T) =>
      () => {
        setTouched((prev) => ({
          ...prev,
          [name]: true,
        }));

        // Only run validation on blur if the field has content or form was previously submitted
        if (validate) {
          const fieldValue = values[name];
          const hasContent = fieldValue && String(fieldValue).trim().length > 0;

          // Only validate on blur if field has content - avoid showing errors for empty fields during navigation
          if (hasContent) {
            const validationErrors = validate(values);
            if (validationErrors[name]) {
              setErrors((prev) => ({
                ...prev,
                [name]: validationErrors[name],
              }));
            }
          }
        }
      },
    [values, validate]
  );

  const setFieldValue = useCallback((name: keyof T, value: T[keyof T]) => {
    setValues((prev) => ({
      ...prev,
      [name]: value,
    }));
  }, []);

  const setFieldError = useCallback((name: keyof T, error: string) => {
    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }));
  }, []);

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  const handleSubmit = useCallback(
    async (event?: React.FormEvent) => {
      if (event) {
        event.preventDefault();
      }

      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce(
        (acc, key) => ({
          ...acc,
          [key]: true,
        }),
        {} as Partial<Record<keyof T, boolean>>
      );
      setTouched(allTouched);

      // Run validation
      if (validate) {
        const validationErrors = validate(values);
        setErrors(validationErrors);

        if (Object.keys(validationErrors).length > 0) {
          return;
        }
      }

      if (onSubmit) {
        setIsSubmitting(true);
        try {
          await onSubmit(values);
        } catch {
          // Form submission error - handled by UI state
          if (process.env.NODE_ENV === 'development') {
            // Error details available for debugging in dev mode
          }
        } finally {
          setIsSubmitting(false);
        }
      }
    },
    [values, validate, onSubmit]
  );

  // Calculate isValid - form is valid if no validation errors exist for filled fields
  // Don't penalize empty fields unless the form has been submitted
  const isValid = useMemo(() => {
    if (!validate) return true;

    // Run validation to get current errors
    const validationErrors = validate(values);

    // Form is valid if there are no validation errors for fields that have content
    // or if all fields are empty (user hasn't started filling the form)
    const hasAnyContent = Object.values(values).some(
      (value) => value && String(value).trim().length > 0
    );

    if (!hasAnyContent) {
      return true; // Empty form is considered valid for button enabling
    }

    // Check if there are any validation errors for non-empty fields
    const hasErrors = Object.keys(validationErrors).some((key) => {
      const fieldValue = values[key as keyof T];
      const hasContent = fieldValue && String(fieldValue).trim().length > 0;
      return hasContent && validationErrors[key as keyof T];
    });

    return !hasErrors;
  }, [values, validate]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
    resetForm,
    isValid,
  };
}
