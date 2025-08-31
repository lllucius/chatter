import { toast, TypeOptions } from 'react-toastify';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastOptions {
  type?: ToastType;
  autoClose?: number | false;
  closeButton?: boolean;
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

  error(message: string, autoClose: number | false = false) {
    return this.showToast(message, { type: 'error', autoClose, closeButton: true });
  }

  info(message: string, autoClose: number | false = 6000) {
    return this.showToast(message, { type: 'info', autoClose, closeButton: false });
  }

  warning(message: string, autoClose: number | false = 6000) {
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