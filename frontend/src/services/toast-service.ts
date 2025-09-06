import { toast, TypeOptions } from 'react-toastify';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastOptions {
  type?: ToastType;
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
  [key: string]: any; // Additional fields
}

// Error response structure from backend
interface ErrorResponse {
  response?: {
    data?: ProblemDetail | any;
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
   * Extract meaningful error message from problem detail response
   */
  private extractErrorMessage(error: ErrorResponse | string, fallback: string): string {
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
      closeButton = type === 'error'
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
    };

    return toast(message, toastOptions);
  }

  success(message: string, autoClose: number | false = 6000) {
    return this.showToast(message, { type: 'success', autoClose, closeButton: false });
  }

  error(messageOrError: string | ErrorResponse, fallback?: string, autoClose: number | false = false) {
    const message = typeof messageOrError === 'string' 
      ? messageOrError 
      : this.extractErrorMessage(messageOrError, fallback || 'An error occurred');
    return this.showToast(message, { type: 'error', autoClose, closeButton: true });
  }

  info(message: string, autoClose: number | false = 6000) {
    return this.showToast(message, { type: 'info', autoClose, closeButton: false });
  }

  warning(messageOrError: string | ErrorResponse, fallback?: string, autoClose: number | false = 6000) {
    const message = typeof messageOrError === 'string' 
      ? messageOrError 
      : this.extractErrorMessage(messageOrError, fallback || 'Warning');
    return this.showToast(message, { type: 'warning', autoClose, closeButton: false });
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