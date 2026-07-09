export interface ErrorContext {
  [key: string]: any;
}

export interface MonitoringService {
  captureException(error: Error | unknown, context?: ErrorContext): void;
  captureMessage(message: string, context?: ErrorContext): void;
  setUser(userId: string | null): void;
}

/**
 * Default Console Monitor
 * This abstraction allows us to drop in Sentry, Datadog, or OpenTelemetry
 * in the future without changing component or client logic.
 */
class ConsoleMonitor implements MonitoringService {
  captureException(error: Error | unknown, context?: ErrorContext): void {
    console.error("[Monitor] Exception Captured:", error);
    if (context) console.error("[Monitor] Context:", context);
    // TODO: Initialize real provider (e.g., Sentry.captureException)
  }

  captureMessage(message: string, context?: ErrorContext): void {
    console.log(`[Monitor] Message: ${message}`);
    if (context) console.log("[Monitor] Context:", context);
    // TODO: Initialize real provider
  }

  setUser(userId: string | null): void {
    console.log(`[Monitor] User set: ${userId}`);
    // TODO: Initialize real provider
  }
}

export const monitor: MonitoringService = new ConsoleMonitor();
