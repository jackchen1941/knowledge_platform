/**
 * Error Handler Utilities
 * 
 * Utilities for handling API errors and formatting error messages
 */

/**
 * Format API error message for display
 * Handles FastAPI validation errors and other error formats
 */
export const formatErrorMessage = (error: any, defaultMessage: string = '操作失败'): string => {
  if (!error?.response?.data?.detail) {
    return defaultMessage;
  }

  const detail = error.response.data.detail;

  // Handle FastAPI validation errors (array format)
  if (Array.isArray(detail)) {
    return detail
      .map((err: any) => {
        const location = err.loc?.slice(1).join('.') || 'unknown';
        return `${location}: ${err.msg}`;
      })
      .join('; ');
  }

  // Handle string error messages
  if (typeof detail === 'string') {
    return detail;
  }

  // Handle object error messages
  if (typeof detail === 'object' && detail.message) {
    return detail.message;
  }

  return defaultMessage;
};

/**
 * Extract validation errors for form fields
 * Returns a map of field names to error messages
 */
export const extractValidationErrors = (error: any): Record<string, string> => {
  const errors: Record<string, string> = {};

  if (!error?.response?.data?.detail || !Array.isArray(error.response.data.detail)) {
    return errors;
  }

  error.response.data.detail.forEach((err: any) => {
    if (err.loc && err.loc.length > 1) {
      const fieldName = err.loc.slice(1).join('.');
      errors[fieldName] = err.msg;
    }
  });

  return errors;
};
