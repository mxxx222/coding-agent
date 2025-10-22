import { Command } from 'commander';
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { logger } from '../utils/logger';
import { configManager } from '../utils/config';
import axios from 'axios';

interface RefactorOptions {
  language?: string;
  output?: string;
  dryRun?: boolean;
}

export async function suggestRefactorCommand(
  codePath: string,
  options: RefactorOptions = {}
): Promise<void> {
  try {
    logger.step('Analyzing code for refactoring opportunities');

    // Check if path exists
    if (!await fs.pathExists(codePath)) {
      logger.error(`Path does not exist: ${codePath}`);
      process.exit(1);
    }

    // Read code files
    const codeFiles = await getCodeFiles(codePath);
    if (codeFiles.length === 0) {
      logger.warn('No code files found in the specified path');
      return;
    }

    logger.info(`Found ${codeFiles.length} code files to analyze`);

    // Analyze each file
    const spinner = ora('Analyzing code...').start();
    const suggestions: RefactorSuggestion[] = [];

    for (const file of codeFiles) {
      try {
        const fileSuggestions = await analyzeFile(file, options.language);
        suggestions.push(...fileSuggestions);
      } catch (error) {
        logger.warn(`Failed to analyze ${file.path}: ${error}`);
      }
    }

    spinner.succeed(`Analysis complete - found ${suggestions.length} suggestions`);

    if (suggestions.length === 0) {
      logger.success('No refactoring suggestions found. Your code looks good!');
      return;
    }

    // Display suggestions
    displaySuggestions(suggestions);

    // Apply suggestions if not dry run
    if (!options.dryRun) {
      const shouldApply = await confirmApplication();
      if (shouldApply) {
        await applySuggestions(suggestions, options.output);
      }
    }

  } catch (error) {
    logger.error('Failed to analyze code:', error);
    process.exit(1);
  }
}

interface RefactorSuggestion {
  file: string;
  line: number;
  type: 'performance' | 'readability' | 'maintainability' | 'security' | 'best-practice';
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  currentCode: string;
  suggestedCode: string;
  reasoning: string;
}

async function getCodeFiles(path: string): Promise<Array<{ path: string; content: string }>> {
  const files: Array<{ path: string; content: string }> = [];
  
  const stat = await fs.stat(path);
  
  if (stat.isFile()) {
    const content = await fs.readFile(path, 'utf8');
    files.push({ path, content });
  } else if (stat.isDirectory()) {
    const entries = await fs.readdir(path, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path + '/' + entry.name;
      
      if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
        const subFiles = await getCodeFiles(fullPath);
        files.push(...subFiles);
      } else if (entry.isFile() && isCodeFile(entry.name)) {
        const content = await fs.readFile(fullPath, 'utf8');
        files.push({ path: fullPath, content });
      }
    }
  }
  
  return files;
}

function isCodeFile(filename: string): boolean {
  const extensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.java', '.go', '.rs', '.cpp', '.c', '.cs', '.php', '.rb', '.swift', '.kt'];
  return extensions.some(ext => filename.endsWith(ext));
}

async function analyzeFile(file: { path: string; content: string }, language?: string): Promise<RefactorSuggestion[]> {
  const apiKey = configManager.getApiKey();
  const serverUrl = configManager.getServerUrl();

  if (!apiKey) {
    throw new Error('OpenAI API key not found. Please set OPENAI_API_KEY environment variable or run "coding-agent config"');
  }

  try {
    const response = await axios.post(`${serverUrl}/api/analyze/refactor`, {
      code: file.content,
      filePath: file.path,
      language: language || detectLanguage(file.path)
    }, {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data.suggestions || [];
  } catch (error) {
    // Fallback to local analysis if server is not available
    logger.warn('Server not available, using local analysis');
    return await localAnalysis(file);
  }
}

function detectLanguage(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const languageMap: Record<string, string> = {
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.py': 'python',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.cpp': 'cpp',
    '.c': 'c',
    '.cs': 'csharp',
    '.php': 'php',
    '.rb': 'ruby',
    '.swift': 'swift',
    '.kt': 'kotlin'
  };
  
  return languageMap[ext] || 'unknown';
}

async function localAnalysis(file: { path: string; content: string }): Promise<RefactorSuggestion[]> {
  const suggestions: RefactorSuggestion[] = [];
  const lines = file.content.split('\n');
  
  // Simple local analysis patterns
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Check for long lines
    if (line.length > 120) {
      suggestions.push({
        file: file.path,
        line: i + 1,
        type: 'readability',
        severity: 'medium',
        title: 'Long line detected',
        description: 'Consider breaking this long line into multiple lines',
        currentCode: line,
        suggestedCode: line.substring(0, 80) + '\n  ' + line.substring(80),
        reasoning: 'Long lines reduce readability and make code harder to maintain'
      });
    }
    
    // Check for console.log statements
    if (line.includes('console.log') && !line.includes('//')) {
      suggestions.push({
        file: file.path,
        line: i + 1,
        type: 'best-practice',
        severity: 'low',
        title: 'Console.log statement found',
        description: 'Consider removing or replacing with proper logging',
        currentCode: line,
        suggestedCode: line.replace('console.log', '// console.log'),
        reasoning: 'Console.log statements should be removed from production code'
      });
    }
    
    // Check for TODO comments
    if (line.includes('TODO') || line.includes('FIXME')) {
      suggestions.push({
        file: file.path,
        line: i + 1,
        type: 'maintainability',
        severity: 'medium',
        title: 'TODO/FIXME comment found',
        description: 'Address this TODO or FIXME comment',
        currentCode: line,
        suggestedCode: line,
        reasoning: 'TODO and FIXME comments indicate incomplete work that should be addressed'
      });
    }
  }
  
  return suggestions;
}

function displaySuggestions(suggestions: RefactorSuggestion[]): void {
  console.log(chalk.bold('\n🔍 Refactoring Suggestions\n'));
  
  const groupedSuggestions = groupSuggestionsByFile(suggestions);
  
  for (const [file, fileSuggestions] of Object.entries(groupedSuggestions)) {
    console.log(chalk.cyan(`📁 ${file}`));
    
    for (const suggestion of fileSuggestions) {
      const severityColor = getSeverityColor(suggestion.severity);
      const typeIcon = getTypeIcon(suggestion.type);
      
      console.log(`  ${typeIcon} ${severityColor(suggestion.severity.toUpperCase())} Line ${suggestion.line}: ${suggestion.title}`);
      console.log(`     ${chalk.gray(suggestion.description)}`);
      console.log(`     ${chalk.yellow('Current:')} ${chalk.red(suggestion.currentCode.trim())}`);
      console.log(`     ${chalk.green('Suggested:')} ${chalk.green(suggestion.suggestedCode.trim())}`);
      console.log(`     ${chalk.blue('Reasoning:')} ${suggestion.reasoning}`);
      console.log('');
    }
  }
  
  // Summary
  const summary = suggestions.reduce((acc, suggestion) => {
    acc[suggestion.severity] = (acc[suggestion.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  console.log(chalk.bold('📊 Summary:'));
  console.log(`  High: ${summary.high || 0}`);
  console.log(`  Medium: ${summary.medium || 0}`);
  console.log(`  Low: ${summary.low || 0}`);
}

function groupSuggestionsByFile(suggestions: RefactorSuggestion[]): Record<string, RefactorSuggestion[]> {
  return suggestions.reduce((acc, suggestion) => {
    if (!acc[suggestion.file]) {
      acc[suggestion.file] = [];
    }
    acc[suggestion.file].push(suggestion);
    return acc;
  }, {} as Record<string, RefactorSuggestion[]>);
}

function getSeverityColor(severity: string): (text: string) => string {
  switch (severity) {
    case 'high': return chalk.red;
    case 'medium': return chalk.yellow;
    case 'low': return chalk.green;
    default: return chalk.gray;
  }
}

function getTypeIcon(type: string): string {
  switch (type) {
    case 'performance': return '⚡';
    case 'readability': return '📖';
    case 'maintainability': return '🔧';
    case 'security': return '🔒';
    case 'best-practice': return '✅';
    default: return '💡';
  }
}

async function confirmApplication(): Promise<boolean> {
  const inquirer = await import('inquirer');
  
  const answers = await inquirer.default.prompt([
    {
      type: 'confirm',
      name: 'apply',
      message: 'Would you like to apply these suggestions?',
      default: false
    }
  ]);
  
  return answers.apply;
}

async function applySuggestions(suggestions: RefactorSuggestion[], outputDir?: string): Promise<void> {
  const spinner = ora('Applying suggestions...').start();
  
  try {
    const groupedSuggestions = groupSuggestionsByFile(suggestions);
    
    for (const [file, fileSuggestions] of Object.entries(groupedSuggestions)) {
      const content = await fs.readFile(file, 'utf8');
      const lines = content.split('\n');
      
      // Apply suggestions in reverse order to maintain line numbers
      const sortedSuggestions = fileSuggestions.sort((a, b) => b.line - a.line);
      
      for (const suggestion of sortedSuggestions) {
        if (suggestion.suggestedCode !== suggestion.currentCode) {
          lines[suggestion.line - 1] = suggestion.suggestedCode;
        }
      }
      
      const newContent = lines.join('\n');
      const outputPath = outputDir ? path.join(outputDir, path.basename(file)) : file;
      
      await fs.writeFile(outputPath, newContent);
    }
    
    spinner.succeed('Suggestions applied successfully');
    logger.success('Refactoring complete!');
    
  } catch (error) {
    spinner.fail('Failed to apply suggestions');
    throw error;
  }
}
