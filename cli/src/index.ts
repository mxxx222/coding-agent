#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { initCommand } from './commands/init';
import { suggestRefactorCommand } from './commands/suggest-refactor';
import { generateTestCommand } from './commands/generate-test';
import { integrateCommand } from './commands/integrate';
import { logger } from './utils/logger';

const program = new Command();

program
  .name('coding-agent')
  .description('AI-powered coding assistant for development workflows')
  .version('1.0.0');

// Initialize command
program
  .command('init')
  .description('Initialize a new project with Coding Agent')
  .argument('[project-name]', 'Name of the project to create')
  .option('-t, --template <template>', 'Project template to use')
  .option('-f, --framework <framework>', 'Framework to use (nextjs, fastapi, etc.)')
  .option('--skip-install', 'Skip package installation')
  .action(initCommand);

// Refactor command
program
  .command('suggest-refactor')
  .description('Get AI-powered refactoring suggestions for your code')
  .argument('<path>', 'Path to the code to refactor')
  .option('-l, --language <language>', 'Programming language')
  .option('-o, --output <output>', 'Output file for refactored code')
  .option('--dry-run', 'Show suggestions without applying changes')
  .action(suggestRefactorCommand);

// Test generation command
program
  .command('generate-test')
  .description('Generate tests for your code')
  .argument('<path>', 'Path to the code to test')
  .option('-f, --framework <framework>', 'Testing framework (jest, pytest, etc.)')
  .option('-o, --output <output>', 'Output directory for tests')
  .option('--coverage', 'Generate coverage reports')
  .action(generateTestCommand);

// Integration command
program
  .command('integrate')
  .description('Integrate with external services')
  .argument('<services...>', 'Services to integrate (supabase, stripe, etc.)')
  .option('-c, --config <config>', 'Configuration file path')
  .option('--dry-run', 'Show integration plan without applying')
  .action(integrateCommand);

// Global options
program
  .option('-v, --verbose', 'Enable verbose logging')
  .option('--api-key <key>', 'OpenAI API key')
  .option('--server <url>', 'Coding Agent server URL')
  .option('--config <path>', 'Configuration file path');

// Error handling
program.on('command:*', () => {
  logger.error(`Unknown command: ${program.args.join(' ')}`);
  logger.info('Use --help to see available commands');
  process.exit(1);
});

// Global error handler
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Parse command line arguments
program.parse();

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
  console.log(chalk.blue('\n🚀 Welcome to Coding Agent!'));
  console.log(chalk.gray('Use "coding-agent --help" to see all available commands.\n'));
}
