import React from 'react';
import { BrewError as BrewErrorType } from './types';

interface BrewErrorProps {
  error: BrewErrorType;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const BrewError: React.FC<BrewErrorProps> = ({ error, onRetry, onDismiss }) => {
  const severityStyles: Record<string, { bg: string; border: string; icon: string }> = {
    info: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'ℹ️' },
    warning: { bg: 'bg-yellow-50', border: 'border-yellow-200', icon: '⚠️' },
    error: { bg: 'bg-red-50', border: 'border-red-200', icon: '❌' },
    critical: { bg: 'bg-purple-50', border: 'border-purple-200', icon: '🚨' },
  };

  const style = severityStyles[error.severity] || severityStyles.error;

  const categoryLabels: Record<string, string> = {
    scale: 'Scale',
    valve: 'Valve',
    timeseries: 'Database',
    brew: 'Brew',
    network: 'Network',
    hardware: 'Hardware',
    configuration: 'Configuration',
  };

  return (
    <div className={`brew-error p-4 rounded-lg border ${style.bg} ${style.border} mb-4`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <span className="text-2xl">{style.icon}</span>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-gray-800">{error.error}</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-gray-200 text-gray-600">
                {categoryLabels[error.category] || error.category}
              </span>
            </div>
            
            {error.recovery_suggestion && (
              <p className="text-sm text-gray-600 mt-1">
                💡 {error.recovery_suggestion}
              </p>
            )}
            
            {error.error_detailed && error.severity === 'critical' && (
              <details className="mt-2">
                <summary className="text-xs cursor-pointer text-gray-500 hover:text-gray-700">
                  Technical Details
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                  {error.error_detailed}
                </pre>
              </details>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {error.retryable && onRetry && (
            <button
              onClick={onRetry}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Retry
            </button>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
            >
              Dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
