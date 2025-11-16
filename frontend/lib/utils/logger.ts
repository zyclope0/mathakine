/**
 * Utilitaire de logging pour le frontend
 * Remplace console.log/error/warn avec gestion de l'environnement
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

class Logger {
  private isDevelopment: boolean;
  private isProduction: boolean;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.isProduction = process.env.NODE_ENV === 'production';
  }

  private shouldLog(level: LogLevel): boolean {
    // En production, ne logger que les erreurs
    if (this.isProduction) {
      return level === 'error';
    }
    // En développement, logger tout
    return true;
  }

  private formatMessage(level: LogLevel, message: string, ...args: unknown[]): string {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    return `${prefix} ${message}`;
  }

  debug(message: string, ...args: unknown[]): void {
    if (this.shouldLog('debug')) {
      console.debug(this.formatMessage('debug', message), ...args);
    }
  }

  info(message: string, ...args: unknown[]): void {
    if (this.shouldLog('info')) {
      console.info(this.formatMessage('info', message), ...args);
    }
  }

  warn(message: string, ...args: unknown[]): void {
    if (this.shouldLog('warn')) {
      console.warn(this.formatMessage('warn', message), ...args);
    }
  }

  error(message: string, error?: Error | unknown, ...args: unknown[]): void {
    // Toujours logger les erreurs, même en production
    const formattedMessage = this.formatMessage('error', message);
    
    if (error instanceof Error) {
      console.error(formattedMessage, error, ...args);
      // En production, on pourrait envoyer à un service de monitoring ici
      // if (this.isProduction) {
      //   // Envoyer à Sentry, LogRocket, etc.
      // }
    } else {
      console.error(formattedMessage, error, ...args);
    }
  }
}

// Instance singleton
export const logger = new Logger();

// Export par défaut pour compatibilité
export default logger;

