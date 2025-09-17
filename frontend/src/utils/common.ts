/**
 * Common utility functions used across the frontend
 */

/**
 * Format file size in bytes to human readable format
 * @param bytes - Size in bytes
 * @returns Formatted string like "1.5 MB"
 */
export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Format a number with locale-specific thousands separators
 * @param value - Number to format
 * @returns Formatted string like "1,234"
 */
export const formatNumber = (value: number): string => {
  return value.toLocaleString();
};

/**
 * Truncate text to a specified length with ellipsis
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis if needed
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
};

/**
 * Get color for status values
 * @param status - Status string
 * @returns MUI color name
 */
export const getStatusColor = (
  status: string
):
  | 'default'
  | 'primary'
  | 'secondary'
  | 'error'
  | 'info'
  | 'success'
  | 'warning' => {
  switch (status.toLowerCase()) {
    case 'processed':
    case 'success':
    case 'completed':
    case 'active':
    case 'enabled':
      return 'success';
    case 'processing':
    case 'pending':
    case 'warning':
      return 'warning';
    case 'failed':
    case 'error':
    case 'inactive':
    case 'disabled':
      return 'error';
    case 'primary':
      return 'primary';
    case 'secondary':
      return 'secondary';
    case 'info':
      return 'info';
    default:
      return 'default';
  }
};

/**
 * Safely parse JSON with fallback
 * @param jsonString - JSON string to parse
 * @param fallback - Fallback value if parsing fails
 * @returns Parsed object or fallback
 */
export const safeJsonParse = <T>(jsonString: string, fallback: T): T => {
  try {
    return JSON.parse(jsonString);
  } catch {
    return fallback;
  }
};

/**
 * Debounce function execution
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 * @returns Debounced function
 */
export const debounce = <T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Generate a random ID
 * @param length - Length of the ID
 * @returns Random string ID
 */
export const generateId = (length: number = 8): string => {
  return Math.random()
    .toString(36)
    .substring(2, 2 + length);
};
