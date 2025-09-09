/**
 * DEPRECATED: This file exports compatibility references.
 * Use auth-service.ts and getSDK() function directly instead.
 */

// Re-export ChatterSDK types for compatibility
export * from 'chatter-sdk';

// For any remaining test files or legacy code, provide minimal compatibility
import { authService } from './auth-service';

/**
 * @deprecated Use authService from auth-service.ts instead
 */
export const chatterClient = authService;
