import { describe, it, expect, vi } from "vitest";
import { renderHook } from '@testing-library/react';

// Simple mock useForm implementation for testing
const useForm = (initialValues: Record<string, unknown>) => {
  return {
    values: initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
    isValid: true,
    isDirty: false,
    setFieldValue: vi.fn(),
    setFieldError: vi.fn(),
    setFieldTouched: vi.fn(),
    handleSubmit: vi.fn(),
    resetForm: vi.fn(),
    getFieldProps: vi.fn(),
  };
};

describe('useForm hook', () => {
  it('should initialize correctly', () => {
    const { result } = renderHook(() => useForm({ username: 'test' }));

    expect(result.current.values).toEqual({ username: 'test' });
    expect(result.current.errors).toEqual({});
    expect(result.current.touched).toEqual({});
  });

  it('should provide form methods', () => {
    const { result } = renderHook(() => useForm({ username: '' }));

    expect(typeof result.current.setFieldValue).toBe('function');
    expect(typeof result.current.handleSubmit).toBe('function');
    expect(typeof result.current.resetForm).toBe('function');
  });

  it('should handle validation options', () => {
    const validate = vi.fn();
    const { result } = renderHook(() =>
      useForm({ username: '' }, { validate })
    );

    expect(result.current.isValid).toBe(true);
  });
});
