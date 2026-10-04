import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  title?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, message: '' };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      message: error?.message || 'An unexpected error occurred while rendering this section.',
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Consulting in a Box render error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, message: '' });
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <section className="flex min-h-[60vh] items-center justify-center py-12">
        <div className="w-full max-w-lg rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-sm dark:border-rose-900 dark:bg-slate-900">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-50 dark:bg-rose-950/40">
            <AlertTriangle className="h-6 w-6 text-rose-600" />
          </div>
          <h2 className="mt-5 text-lg font-bold text-slate-900 dark:text-white">
            {this.props.title || 'This section could not be displayed'}
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
            Something went wrong while rendering this page. Your workspace data is still safe.
          </p>
          <button
            type="button"
            onClick={this.handleRetry}
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100"
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </button>
          {import.meta.env.DEV && (
            <p className="mt-4 break-words text-left text-[11px] text-slate-400">
              {this.state.message}
            </p>
          )}
        </div>
      </section>
    );
  }
}
