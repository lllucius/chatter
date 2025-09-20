/**
 * Error fix verification utility
 * Provides tools to verify that the error handling fixes are working correctly
 */

import { errorConfig } from './error-config';
import { errorBatcher, getErrorBatchStats } from './error-batching';
import { globalErrorHandler } from './global-error-handler';

export interface VerificationResult {
  test: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  details?: unknown;
}

/**
 * Verify that Chrome extension errors are being filtered
 */
export function verifyExtensionErrorFiltering(): VerificationResult[] {
  const results: VerificationResult[] = [];
  
  try {
    // Test Chrome extension error patterns
    const chromeExtensionErrors = [
      "Cannot read properties of undefined (reading 'isCheckout')",
      "Unchecked runtime.lastError: A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received",
      "Error handling response: TypeError: Cannot read properties of undefined",
    ];
    
    let filteredCount = 0;
    const originalConsoleDebug = console.debug;
    let debugCalls = 0;
    
    // Mock console.debug to count filtered errors
    console.debug = (...args: unknown[]) => {
      if (args[0] && typeof args[0] === 'string' && args[0].includes('Chrome extension error (filtered)')) {
        debugCalls++;
      }
      originalConsoleDebug(...args);
    };
    
    // Simulate Chrome extension errors
    chromeExtensionErrors.forEach(errorMessage => {
      const errorEvent = new ErrorEvent('error', {
        message: errorMessage,
        filename: 'chrome-extension://test/content-script.js',
        error: new Error(errorMessage),
      });
      
      // Trigger the error handler
      window.dispatchEvent(errorEvent);
    });
    
    // Restore console.debug
    console.debug = originalConsoleDebug;
    
    if (debugCalls === chromeExtensionErrors.length) {
      results.push({
        test: 'Chrome Extension Error Filtering',
        status: 'pass',
        message: `Successfully filtered ${debugCalls} Chrome extension errors`,
      });
    } else {
      results.push({
        test: 'Chrome Extension Error Filtering',
        status: 'fail',
        message: `Expected to filter ${chromeExtensionErrors.length} errors, but filtered ${debugCalls}`,
      });
    }
  } catch (error) {
    results.push({
      test: 'Chrome Extension Error Filtering',
      status: 'fail',
      message: 'Error during verification',
      details: error,
    });
  }
  
  return results;
}

/**
 * Verify that error configuration is working
 */
export function verifyErrorConfiguration(): VerificationResult[] {
  const results: VerificationResult[] = [];
  
  try {
    const config = errorConfig.getConfig();
    
    // Check that configuration exists
    if (!config) {
      results.push({
        test: 'Error Configuration',
        status: 'fail',
        message: 'Error configuration not available',
      });
      return results;
    }
    
    // Verify key configuration properties
    const expectedProperties = [
      'filterExtensionErrors',
      'showAuthenticationErrors',
      'logToConsole',
      'showToastNotifications',
    ];
    
    const missingProperties = expectedProperties.filter(prop => !(prop in config));
    
    if (missingProperties.length === 0) {
      results.push({
        test: 'Error Configuration',
        status: 'pass',
        message: 'Error configuration is properly initialized',
        details: config,
      });
    } else {
      results.push({
        test: 'Error Configuration',
        status: 'fail',
        message: `Missing configuration properties: ${missingProperties.join(', ')}`,
        details: config,
      });
    }
  } catch (error) {
    results.push({
      test: 'Error Configuration',
      status: 'fail',
      message: 'Error accessing configuration',
      details: error,
    });
  }
  
  return results;
}

/**
 * Verify that error batching is working
 */
export function verifyErrorBatching(): VerificationResult[] {
  const results: VerificationResult[] = [];
  
  try {
    // Clear any existing batches
    errorBatcher.clear();
    
    // Add some test errors
    const testErrors = [
      new Error('Network error: Failed to fetch'),
      new Error('Network error: Failed to fetch'), // Duplicate
      new Error('Server error: 500 Internal Server Error'),
    ];
    
    testErrors.forEach((error, index) => {
      errorBatcher.addError(error, `TestSource${index}`);
    });
    
    const stats = getErrorBatchStats();
    
    if (stats.totalBatches > 0) {
      results.push({
        test: 'Error Batching',
        status: 'pass',
        message: `Error batching is working - ${stats.totalBatches} batches with ${stats.totalErrors} total errors`,
        details: stats,
      });
    } else {
      results.push({
        test: 'Error Batching',
        status: 'warning',
        message: 'Error batching may be disabled or not working as expected',
        details: stats,
      });
    }
    
    // Clean up
    errorBatcher.clear();
  } catch (error) {
    results.push({
      test: 'Error Batching',
      status: 'fail',
      message: 'Error during batching verification',
      details: error,
    });
  }
  
  return results;
}

/**
 * Verify that global error handler is initialized
 */
export function verifyGlobalErrorHandler(): VerificationResult[] {
  const results: VerificationResult[] = [];
  
  try {
    const isInitialized = globalErrorHandler.isInitialized();
    
    if (isInitialized) {
      results.push({
        test: 'Global Error Handler',
        status: 'pass',
        message: 'Global error handler is initialized',
      });
    } else {
      results.push({
        test: 'Global Error Handler',
        status: 'warning',
        message: 'Global error handler is not initialized - call initializeGlobalErrorHandling()',
      });
    }
  } catch (error) {
    results.push({
      test: 'Global Error Handler',
      status: 'fail',
      message: 'Error checking global error handler',
      details: error,
    });
  }
  
  return results;
}

/**
 * Run all verification tests
 */
export function runAllVerifications(): VerificationResult[] {
  const allResults: VerificationResult[] = [];
  
  allResults.push(...verifyErrorConfiguration());
  allResults.push(...verifyGlobalErrorHandler());
  allResults.push(...verifyErrorBatching());
  allResults.push(...verifyExtensionErrorFiltering());
  
  return allResults;
}

/**
 * Generate a verification report
 */
export function generateVerificationReport(results: VerificationResult[] = runAllVerifications()): string {
  const passCount = results.filter(r => r.status === 'pass').length;
  const failCount = results.filter(r => r.status === 'fail').length;
  const warningCount = results.filter(r => r.status === 'warning').length;
  
  let report = `## Error Fix Verification Report\n\n`;
  report += `**Summary:** ${passCount} passed, ${failCount} failed, ${warningCount} warnings\n\n`;
  
  results.forEach(result => {
    const emoji = result.status === 'pass' ? '✅' : result.status === 'fail' ? '❌' : '⚠️';
    report += `${emoji} **${result.test}**: ${result.message}\n`;
    if (result.details) {
      report += `   Details: ${JSON.stringify(result.details, null, 2)}\n`;
    }
    report += '\n';
  });
  
  return report;
}

/**
 * Log verification report to console
 */
export function logVerificationReport(): void {
  const results = runAllVerifications();
  const report = generateVerificationReport(results);
  
  // eslint-disable-next-line no-console
  console.log(report);
}

// Convenience function to verify fixes during development
export function verifyErrorFixes(): void {
  if (process.env.NODE_ENV === 'development') {
    logVerificationReport();
  }
}