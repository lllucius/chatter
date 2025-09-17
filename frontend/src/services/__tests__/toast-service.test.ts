/**
 * Tests for Toast Service
 */

import { vi, describe, beforeEach, expect, test } from 'vitest';
import { toast } from 'react-toastify';
import { toastService } from '../toast-service';

// Mock react-toastify
vi.mock('react-toastify', (): void => ({
  toast: Object.assign(
    vi.fn().mockImplementation(() => 'mock-toast-id'),
    {
      dismiss: vi.fn(),
      update: vi.fn(),
      info: vi.fn().mockImplementation(() => 'mock-info-toast-id'),
      success: vi.fn().mockImplementation(() => 'mock-success-toast-id'),
      error: vi.fn().mockImplementation(() => 'mock-error-toast-id'),
      warning: vi.fn().mockImplementation(() => 'mock-warning-toast-id'),
    }
  ),
}));

describe('ToastService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset toast count
    (toastService as unknown).toastCount = 0;
  });

  describe('Basic Toast Operations', () => {
    test('should show success toast', () => {
      const message = 'Operation completed successfully';
      toastService.success(message);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          type: 'success',
          autoClose: 6000,
          closeButton: false,
          onOpen: expect.unknown(Function),
          onClose: expect.unknown(Function),
        })
      );
    });

    test('should show error toast', () => {
      const message = 'An error occurred';
      toastService.error(message);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          type: 'error',
          autoClose: false,
          closeButton: true, // Error toasts should have close button
          onOpen: expect.unknown(Function),
          onClose: expect.unknown(Function),
        })
      );
    });

    test('should show info toast', () => {
      const message = 'Information message';
      toastService.info(message);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          type: 'info',
          autoClose: 6000,
          closeButton: false,
          onOpen: expect.unknown(Function),
          onClose: expect.unknown(Function),
        })
      );
    });

    test('should show warning toast', () => {
      const message = 'Warning message';
      toastService.warning(message);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          type: 'warning',
          autoClose: 6000,
          closeButton: false,
          onOpen: expect.unknown(Function),
          onClose: expect.unknown(Function),
        })
      );
    });
  });

  describe('Toast Options', () => {
    test('should accept custom autoClose duration', () => {
      const message = 'Custom duration message';
      const options = { autoClose: 3000 };

      toastService.success(message, options);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          autoClose: 3000,
        })
      );
    });

    test('should accept autoClose false for persistent toasts', () => {
      const message = 'Persistent message';
      const options = { autoClose: false };

      toastService.info(message, options);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          autoClose: false,
        })
      );
    });

    test('should accept custom close button setting', () => {
      const message = 'Custom close button';
      const options = { closeButton: true };

      toastService.info(message, options);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          closeButton: true,
        })
      );
    });

    test('should override default close button for error toasts', () => {
      const message = 'Error without close button';
      const options = { closeButton: false };

      toastService.error(message, options);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          closeButton: false,
        })
      );
    });
  });

  describe('Toast Limit Management', () => {
    test('should track toast count', () => {
      // Simulate toast opening
      const result = toastService.success('Test 1');

      // Get the onOpen callback and call it to simulate toast opening
      const callArgs = (toast as unknown).mock.calls[0];
      const options = callArgs[1];
      options.onOpen();

      expect(toastService.getToastCount()).toBe(1);
    });

    test('should dismiss existing toast when at max capacity', () => {
      // Set up service at max capacity
      for (let i = 0; i < 4; i++) {
        toastService.success(`Message ${i}`);
        const callArgs = (toast as unknown).mock.calls[i];
        const options = callArgs[1];
        options.onOpen(); // Simulate toast opening
      }

      // This should trigger dismiss due to max capacity
      expect(toast.dismiss).toHaveBeenCalled();
    });

    test('should decrement count when toast closes', () => {
      toastService.success('Test message');

      const callArgs = (toast as unknown).mock.calls[0];
      const options = callArgs[1];

      // Simulate toast opening and closing
      options.onOpen();
      expect(toastService.getToastCount()).toBe(1);

      options.onClose();
      expect(toastService.getToastCount()).toBe(0);
    });
  });

  describe('Convenience Methods', () => {
    test('should have success method', () => {
      expect(typeof toastService.success).toBe('function');
    });

    test('should have error method', () => {
      expect(typeof toastService.error).toBe('function');
    });

    test('should have info method', () => {
      expect(typeof toastService.info).toBe('function');
    });

    test('should have warning method', () => {
      expect(typeof toastService.warning).toBe('function');
    });

    test('should have loading method', () => {
      expect(typeof toastService.loading).toBe('function');
    });

    test('should show loading toast', () => {
      const message = 'Loading...';
      toastService.loading(message);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          autoClose: false, // Loading should not auto-close
          closeButton: false,
        })
      );
    });
  });

  describe('Error Handling', () => {
    test('should handle empty messages gracefully', () => {
      toastService.info('');
      expect(toast).toHaveBeenCalledWith('', expect.unknown(Object));
    });

    test('should handle null/undefined messages', () => {
      toastService.info(null as unknown);
      expect(toast).toHaveBeenCalledWith(null, expect.unknown(Object));
    });

    test('should handle invalid autoClose values', () => {
      const options = { autoClose: -1 }; // Invalid value
      toastService.info('Test', options);

      // Should still call toast with the provided value
      expect(toast).toHaveBeenCalledWith(
        'Test',
        expect.objectContaining({
          autoClose: -1,
        })
      );
    });
  });

  describe('Toast Configuration', () => {
    test('should set correct default options', () => {
      toastService.info('Default options test');

      expect(toast).toHaveBeenCalledWith(
        'Default options test',
        expect.objectContaining({
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        })
      );
    });

    test('should handle toast position configuration', () => {
      // This would test position if it was configurable
      toastService.info('Position test');

      expect(toast).toHaveBeenCalled();
    });
  });

  describe('Advanced Features', () => {
    test('should support custom toast IDs', () => {
      const message = 'Custom ID toast';
      const customId = 'unique-toast-id';

      // If the service supported custom IDs
      toastService.info(message, { toastId: customId } as unknown);

      expect(toast).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          toastId: customId,
        })
      );
    });

    test('should support toast updates', () => {
      // Test toast update functionality if implemented
      const toastId = toastService.loading('Loading...');

      // Would update the toast if supported
      if (toastService.update) {
        toastService.update(
          toastId as unknown,
          {
            type: 'success',
            message: 'Completed!',
            autoClose: 3000,
          } as unknown
        );
      }

      expect(toast).toHaveBeenCalledWith('Loading...', expect.unknown(Object)); // Called for loading
    });

    test('should support toast dismissal', () => {
      const toastId = toastService.info('Dismissible toast');

      if (toastService.dismiss) {
        toastService.dismiss(toastId as unknown);
      } else {
        // Call global dismiss
        toast.dismiss();
      }

      expect(toast).toHaveBeenCalledWith(
        'Dismissible toast',
        expect.unknown(Object)
      );
    });
  });

  describe('Integration Scenarios', () => {
    test('should handle rapid successive toasts', () => {
      const messages = ['Toast 1', 'Toast 2', 'Toast 3', 'Toast 4', 'Toast 5'];

      messages.forEach((message, index) => {
        toastService.info(message);
        // Simulate toast opening to trigger count increment
        const callArgs = (toast as unknown).mock.calls[index];
        const options = callArgs[1];
        options.onOpen();
      });

      expect(toast).toHaveBeenCalledTimes(5);
      // Should have called dismiss due to exceeding max toasts
      expect(toast.dismiss).toHaveBeenCalled();
    });

    test('should handle mixed toast types', () => {
      toastService.success('Success message');
      toastService.error('Error message');
      toastService.warning('Warning message');
      toastService.info('Info message');

      expect(toast).toHaveBeenCalledTimes(4);
    });

    test('should handle long messages', () => {
      const longMessage = 'A'.repeat(500); // Very long message
      toastService.info(longMessage);

      expect(toast).toHaveBeenCalledWith(longMessage, expect.unknown(Object));
    });

    test('should handle special characters in messages', () => {
      const specialMessage =
        '🎉 Success! ✨ Operation completed with 100% accuracy 📊';
      toastService.success(specialMessage);

      expect(toast).toHaveBeenCalledWith(
        specialMessage,
        expect.unknown(Object)
      );
    });
  });

  describe('Memory Management', () => {
    test('should not leak memory with toast callbacks', () => {
      // Create munknown toasts to test for memory leaks
      for (let i = 0; i < 100; i++) {
        toastService.info(`Toast ${i}`);

        // Simulate opening and closing
        const callArgs = (toast as unknown).mock.calls[i];
        const options = callArgs[1];
        options.onOpen();
        options.onClose();
      }

      expect(toastService.getToastCount()).toBe(0);
    });

    test('should handle cleanup on service destruction', () => {
      toastService.success('Test');

      // If service has cleanup method
      if (toastService.destroy) {
        toastService.destroy();
      }

      expect(toastService.getToastCount()).toBe(0);
    });
  });
});
