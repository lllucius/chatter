import { toast, TypeOptions } from 'react-toastify';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastOptions {
  type?: ToastType;
  autoClose?: number | false;
  closeButton?: boolean;
  toastId?: string;
}

interface ToastUpdateOptions {
  type?: ToastType;
  message?: string;
  autoClose?: number | false;
  closeButton?: boolean;
}

// RFC 9457 Problem Detail structure
interface ProblemDetail {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  [key: string]: unknown; // Additional fields
}

// Error response structure from backend
interface ErrorResponse {
  response?: {
    data?: ProblemDetail | unknown;
    status?: number;
  };
  message?: string;
}

class ToastService {
  private toastCount = 0;
  private readonly maxToasts = 3;

  private canShowToast(): boolean {
    return this.toastCount < this.maxToasts;
  }

  private onToastOpen = () => {
    this.toastCount++;
  };

  private onToastClose = () => {
    this.toastCount--;
  };

  /**
   * Normalize options parameter - handle both object and primitive formats
   */
  private normalizeOptions(
    optionsOrPrimitive?: ToastOptions | number | false,
    defaults: Partial<ToastOptions> = {}
  ): ToastOptions {
    if (typeof optionsOrPrimitive === 'object') {
      return { ...defaults, ...optionsOrPrimitive };
    }

    // Handle primitive autoClose value
    if (
      typeof optionsOrPrimitive === 'number' ||
      optionsOrPrimitive === false
    ) {
      return { ...defaults, autoClose: optionsOrPrimitive };
    }

    return defaults as ToastOptions;
  }

  /**
   * Extract meaningful error message from problem detail response
   */
  private extractErrorMessage(
    error: ErrorResponse | string,
    fallback: string
  ): string {
    // If error is already a string, return it
    if (typeof error === 'string') {
      return error;
    }

    // Try to extract problem detail information
    const problemDetail = error?.response?.data as ProblemDetail;

    if (problemDetail && typeof problemDetail === 'object') {
      // Priority order: title + detail, detail only, title only, fallback
      if (problemDetail.title && problemDetail.detail) {
        return `${problemDetail.title}: ${problemDetail.detail}`;
      }

      if (problemDetail.detail) {
        return problemDetail.detail;
      }

      if (problemDetail.title) {
        return problemDetail.title;
      }
    }

    // Fallback to generic message from error or provided fallback
    return error?.message || fallback;
  }

  private showToast(message: string, options: ToastOptions = {}) {
    if (!this.canShowToast()) {
      // If we're at max capacity, dismiss the oldest toast to make room
      toast.dismiss();
    }

    const {
      type = 'info',
      autoClose = 6000,
      closeButton = type === 'error',
      toastId,
    } = options;

    const toastOptions = {
      type: type as TypeOptions,
      autoClose,
      closeButton,
      onOpen: this.onToastOpen,
      onClose: this.onToastClose,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...(toastId && { toastId }),
    };

    return toast(message, toastOptions);
  }

  private showSuccessToast(
    message: string,
    options: Omit<ToastOptions, 'type'>
  ) {
    if (!this.canShowToast()) {
      toast.dismiss();
    }

    const { autoClose = 6000, closeButton = false, toastId } = options;
    const toastOptions = {
      autoClose,
      closeButton,
      onOpen: this.onToastOpen,
      onClose: this.onToastClose,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...(toastId && { toastId }),
    };

    return toast.success(message, toastOptions);
  }

  private showErrorToast(message: string, options: Omit<ToastOptions, 'type'>) {
    if (!this.canShowToast()) {
      toast.dismiss();
    }

    const { autoClose = false, closeButton = true, toastId } = options;
    const toastOptions = {
      autoClose,
      closeButton,
      onOpen: this.onToastOpen,
      onClose: this.onToastClose,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...(toastId && { toastId }),
    };

    return toast.error(message, toastOptions);
  }

  private showInfoToast(message: string, options: Omit<ToastOptions, 'type'>) {
    if (!this.canShowToast()) {
      toast.dismiss();
    }

    const { autoClose = 6000, closeButton = false, toastId } = options;
    const toastOptions = {
      autoClose,
      closeButton,
      onOpen: this.onToastOpen,
      onClose: this.onToastClose,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...(toastId && { toastId }),
    };

    return toast.info(message, toastOptions);
  }

  private showWarningToast(
    message: string,
    options: Omit<ToastOptions, 'type'>
  ) {
    if (!this.canShowToast()) {
      toast.dismiss();
    }

    const { autoClose = 6000, closeButton = false, toastId } = options;
    const toastOptions = {
      autoClose,
      closeButton,
      onOpen: this.onToastOpen,
      onClose: this.onToastClose,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...(toastId && { toastId }),
    };

    return toast.warning(message, toastOptions);
  }

  success(message: string, optionsOrAutoClose?: ToastOptions | number | false) {
    const options = this.normalizeOptions(optionsOrAutoClose, {
      type: 'success',
      autoClose: 6000,
      closeButton: false,
    });
    return this.showToast(message, options);
  }

  error(
    messageOrError: string | ErrorResponse,
    fallbackOrOptions?: string | ToastOptions,
    optionsOrAutoClose?: ToastOptions | number | false
  ) {
    const message =
      typeof messageOrError === 'string'
        ? messageOrError
        : this.extractErrorMessage(
            messageOrError,
            typeof fallbackOrOptions === 'string'
              ? fallbackOrOptions
              : 'An error occurred'
          );

    // Handle overloaded parameters
    const options =
      typeof fallbackOrOptions === 'object'
        ? fallbackOrOptions
        : this.normalizeOptions(optionsOrAutoClose, {
            type: 'error',
            autoClose: false,
            closeButton: true,
          });

    return this.showToast(message, options);
  }

  info(message: string, optionsOrAutoClose?: ToastOptions | number | false) {
    const options = this.normalizeOptions(optionsOrAutoClose, {
      type: 'info',
      autoClose: 6000,
      closeButton: false,
    });
    return this.showToast(message, options);
  }

  warning(
    messageOrError: string | ErrorResponse,
    fallbackOrOptions?: string | ToastOptions,
    optionsOrAutoClose?: ToastOptions | number | false
  ) {
    const message =
      typeof messageOrError === 'string'
        ? messageOrError
        : this.extractErrorMessage(
            messageOrError,
            typeof fallbackOrOptions === 'string'
              ? fallbackOrOptions
              : 'Warning'
          );

    // Handle overloaded parameters
    const options =
      typeof fallbackOrOptions === 'object'
        ? fallbackOrOptions
        : this.normalizeOptions(optionsOrAutoClose, {
            type: 'warning',
            autoClose: 6000,
            closeButton: false,
          });

    return this.showToast(message, options);
  }

  loading(message: string) {
    return this.showToast(message, {
      type: 'info',
      autoClose: false,
      closeButton: false,
    });
  }

  getToastCount(): number {
    return this.toastCount;
  }

  update(toastId: string | number, options: ToastUpdateOptions) {
    const {
      message,
      type = 'info',
      autoClose = 6000,
      closeButton = type === 'error',
    } = options;

    if (message) {
      return toast.update(toastId, {
        render: message,
        type: type as TypeOptions,
        autoClose,
        closeButton,
      });
    }

    return toast.update(toastId, {
      type: type as TypeOptions,
      autoClose,
      closeButton,
    });
  }

  dismiss(toastId?: string | number) {
    toast.dismiss(toastId);
  }

  dismissAll() {
    toast.dismiss();
    this.toastCount = 0;
  }
}

export const toastService = new ToastService();
