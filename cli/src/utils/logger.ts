import chalk from 'chalk';

export enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3,
}

class Logger {
  private level: LogLevel = LogLevel.INFO;

  setLevel(level: LogLevel): void {
    this.level = level;
  }

  private shouldLog(level: LogLevel): boolean {
    return level <= this.level;
  }

  private formatMessage(level: string, message: string, ...args: any[]): string {
    const timestamp = new Date().toISOString();
    const formattedArgs = args.length > 0 ? ' ' + args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ') : '';
    
    return `[${timestamp}] ${level}: ${message}${formattedArgs}`;
  }

  error(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      console.error(chalk.red(this.formatMessage('ERROR', message, ...args)));
    }
  }

  warn(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(chalk.yellow(this.formatMessage('WARN', message, ...args)));
    }
  }

  info(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.log(chalk.blue(this.formatMessage('INFO', message, ...args)));
    }
  }

  debug(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.log(chalk.gray(this.formatMessage('DEBUG', message, ...args)));
    }
  }

  success(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.log(chalk.green(this.formatMessage('SUCCESS', message, ...args)));
    }
  }

  // Special methods for CLI
  step(message: string): void {
    console.log(chalk.cyan(`→ ${message}`));
  }

  done(message: string): void {
    console.log(chalk.green(`✓ ${message}`));
  }

  fail(message: string): void {
    console.log(chalk.red(`✗ ${message}`));
  }
}

export const logger = new Logger();
