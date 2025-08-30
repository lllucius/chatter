import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useForm } from '../useForm';

interface TestFormValues {
  username: string;
  password: string;
}

describe('useForm fix for login button disabled issue', () => {
  const mockValidate = (values: TestFormValues) => {
    const errors: Partial<Record<keyof TestFormValues, string>> = {};
    if (!values.username.trim()) {
      errors.username = 'Username is required';
    }
    if (!values.password.trim()) {
      errors.password = 'Password is required';
    }
    return errors;
  };

  it('should keep button enabled when form is empty', () => {
    const { result } = renderHook(() =>
      useForm<TestFormValues>({
        initialValues: { username: '', password: '' },
        validate: mockValidate,
      })
    );

    expect(result.current.isValid).toBe(true);
  });

  it('should not show errors when tabbing from empty username to password', () => {
    const { result } = renderHook(() =>
      useForm<TestFormValues>({
        initialValues: { username: '', password: '' },
        validate: mockValidate,
      })
    );

    // Simulate blur on empty username field (tab away)
    act(() => {
      result.current.handleBlur('username')();
    });

    expect(result.current.errors.username).toBeUndefined();
    expect(result.current.isValid).toBe(true);
  });

  it('should clear errors when user starts typing', () => {
    const { result } = renderHook(() =>
      useForm<TestFormValues>({
        initialValues: { username: '', password: '' },
        validate: mockValidate,
      })
    );

    // Set a field error (simulating failed login)
    act(() => {
      result.current.setFieldError('password', 'Invalid password');
    });

    expect(result.current.errors.password).toBe('Invalid password');
    expect(result.current.isValid).toBe(true); // Should still be valid for empty form

    // Start typing in password field
    act(() => {
      result.current.handleChange('password')({
        target: { value: 'n', type: 'text' },
      } as any);
    });

    expect(result.current.errors.password).toBeUndefined();
    expect(result.current.isValid).toBe(true);
  });

  it('should enable button when form has valid content', () => {
    const { result } = renderHook(() =>
      useForm<TestFormValues>({
        initialValues: { username: '', password: '' },
        validate: mockValidate,
      })
    );

    // Fill out form with valid data
    act(() => {
      result.current.handleChange('username')({
        target: { value: 'testuser', type: 'text' },
      } as any);
    });

    act(() => {
      result.current.handleChange('password')({
        target: { value: 'testpass', type: 'text' },
      } as any);
    });

    expect(result.current.isValid).toBe(true);
  });

  it('should show validation errors only for fields with content on blur', () => {
    const { result } = renderHook(() =>
      useForm<TestFormValues>({
        initialValues: { username: '', password: '' },
        validate: mockValidate,
      })
    );

    // Fill username field with content then clear it
    act(() => {
      result.current.handleChange('username')({
        target: { value: 'test', type: 'text' },
      } as any);
    });

    // Now blur should trigger validation since field has content
    act(() => {
      result.current.handleBlur('username')();
    });

    expect(result.current.errors.username).toBeUndefined(); // Still has content, so no error

    // Clear the field
    act(() => {
      result.current.handleChange('username')({
        target: { value: '', type: 'text' },
      } as any);
    });

    // Blur on empty field should not show error
    act(() => {
      result.current.handleBlur('username')();
    });

    expect(result.current.errors.username).toBeUndefined();
  });
});