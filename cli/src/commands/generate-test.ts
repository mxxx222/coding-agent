import { Command } from 'commander';
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { logger } from '../utils/logger';
import { configManager } from '../utils/config';
import axios from 'axios';

interface TestOptions {
  framework?: string;
  output?: string;
  coverage?: boolean;
}

export async function generateTestCommand(
  codePath: string,
  options: TestOptions = {}
): Promise<void> {
  try {
    logger.step('Generating tests for your code');

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

    logger.info(`Found ${codeFiles.length} code files to test`);

    // Generate tests for each file
    const spinner = ora('Generating tests...').start();
    const testResults: TestResult[] = [];

    for (const file of codeFiles) {
      try {
        const tests = await generateTestsForFile(file, options.framework);
        testResults.push(...tests);
      } catch (error) {
        logger.warn(`Failed to generate tests for ${file.path}: ${error}`);
      }
    }

    spinner.succeed(`Generated ${testResults.length} test files`);

    if (testResults.length === 0) {
      logger.warn('No tests could be generated for the provided files');
      return;
    }

    // Write test files
    await writeTestFiles(testResults, options.output);

    // Generate coverage report if requested
    if (options.coverage) {
      await generateCoverageReport(testResults);
    }

    logger.success('Test generation complete!');
    logger.info(`\nGenerated ${testResults.length} test files`);
    logger.info('Run your tests with: npm test (or your preferred test runner)');

  } catch (error) {
    logger.error('Failed to generate tests:', error);
    process.exit(1);
  }
}

interface TestResult {
  sourceFile: string;
  testFile: string;
  content: string;
  framework: string;
  testCount: number;
  coverage?: number;
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

async function generateTestsForFile(file: { path: string; content: string }, framework?: string): Promise<TestResult[]> {
  const apiKey = configManager.getApiKey();
  const serverUrl = configManager.getServerUrl();

  if (!apiKey) {
    throw new Error('OpenAI API key not found. Please set OPENAI_API_KEY environment variable or run "coding-agent config"');
  }

  try {
    const response = await axios.post(`${serverUrl}/api/generate/tests`, {
      code: file.content,
      filePath: file.path,
      framework: framework || detectFramework(file.path)
    }, {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data.tests || [];
  } catch (error) {
    // Fallback to local test generation if server is not available
    logger.warn('Server not available, using local test generation');
    return await localTestGeneration(file, framework);
  }
}

function detectFramework(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  
  if (ext === '.ts' || ext === '.tsx' || ext === '.js' || ext === '.jsx') {
    // Check for framework-specific files
    if (filePath.includes('next.config') || filePath.includes('pages/') || filePath.includes('app/')) {
      return 'jest'; // Next.js typically uses Jest
    }
    if (filePath.includes('cypress/') || filePath.includes('e2e/')) {
      return 'cypress';
    }
    return 'jest';
  } else if (ext === '.py') {
    return 'pytest';
  } else if (ext === '.java') {
    return 'junit';
  } else if (ext === '.go') {
    return 'testing';
  } else if (ext === '.rs') {
    return 'cargo-test';
  }
  
  return 'jest'; // Default to Jest
}

async function localTestGeneration(file: { path: string; content: string }, framework?: string): Promise<TestResult[]> {
  const detectedFramework = framework || detectFramework(file.path);
  const testContent = generateBasicTest(file.content, file.path, detectedFramework);
  
  return [{
    sourceFile: file.path,
    testFile: getTestFilePath(file.path),
    content: testContent,
    framework: detectedFramework,
    testCount: 1
  }];
}

function getTestFilePath(sourcePath: string): string {
  const dir = path.dirname(sourcePath);
  const name = path.basename(sourcePath, path.extname(sourcePath));
  const ext = path.extname(sourcePath);
  
  // Determine test file extension
  let testExt = ext;
  if (ext === '.ts' || ext === '.tsx') {
    testExt = '.test.ts';
  } else if (ext === '.js' || ext === '.jsx') {
    testExt = '.test.js';
  } else if (ext === '.py') {
    testExt = '_test.py';
  } else if (ext === '.java') {
    testExt = 'Test.java';
  }
  
  return path.join(dir, `${name}${testExt}`);
}

function generateBasicTest(code: string, filePath: string, framework: string): string {
  const ext = path.extname(filePath).toLowerCase();
  
  if (ext === '.ts' || ext === '.tsx' || ext === '.js' || ext === '.jsx') {
    return generateJestTest(code, filePath);
  } else if (ext === '.py') {
    return generatePytestTest(code, filePath);
  } else if (ext === '.java') {
    return generateJUnitTest(code, filePath);
  } else if (ext === '.go') {
    return generateGoTest(code, filePath);
  }
  
  return generateGenericTest(code, filePath);
}

function generateJestTest(code: string, filePath: string): string {
  const fileName = path.basename(filePath, path.extname(filePath));
  const importPath = filePath.replace(/\.(ts|tsx|js|jsx)$/, '');
  
  return `import { ${fileName} } from '${importPath}';

describe('${fileName}', () => {
  test('should be defined', () => {
    expect(${fileName}).toBeDefined();
  });

  // Add more tests here
  // TODO: Implement comprehensive test cases
});
`;
}

function generatePytestTest(code: string, filePath: string): string {
  const fileName = path.basename(filePath, '.py');
  
  return `import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ${fileName} import *

class Test${fileName.charAt(0).toUpperCase() + fileName.slice(1)}:
    def test_module_imports(self):
        """Test that the module can be imported without errors."""
        assert True  # Basic import test
    
    # Add more tests here
    # TODO: Implement comprehensive test cases
`;
}

function generateJUnitTest(code: string, filePath: string): string {
  const className = path.basename(filePath, '.java');
  
  return `import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class ${className}Test {
    
    @BeforeEach
    void setUp() {
        // Setup code here
    }
    
    @Test
    void testBasicFunctionality() {
        // Test basic functionality
        assertTrue(true, "Basic test should pass");
    }
    
    // Add more tests here
    // TODO: Implement comprehensive test cases
}
`;
}

function generateGoTest(code: string, filePath: string): string {
  const packageName = path.basename(path.dirname(filePath));
  
  return `package ${packageName}

import (
    "testing"
)

func TestBasic(t *testing.T) {
    // Basic test
    if true != true {
        t.Error("Basic test failed")
    }
}

// Add more tests here
// TODO: Implement comprehensive test cases
`;
}

function generateGenericTest(code: string, filePath: string): string {
  return `// Test file for ${filePath}
// TODO: Implement test cases

// Basic test structure
function testBasic() {
    // Add your tests here
    console.log('Test file created for ${filePath}');
}

// Run tests
testBasic();
`;
}

async function writeTestFiles(testResults: TestResult[], outputDir?: string): Promise<void> {
  const spinner = ora('Writing test files...').start();
  
  try {
    for (const result of testResults) {
      const testPath = outputDir ? path.join(outputDir, path.basename(result.testFile)) : result.testFile;
      
      // Ensure directory exists
      await fs.ensureDir(path.dirname(testPath));
      
      // Write test file
      await fs.writeFile(testPath, result.content);
      
      logger.info(`Created test file: ${testPath}`);
    }
    
    spinner.succeed('Test files written successfully');
    
  } catch (error) {
    spinner.fail('Failed to write test files');
    throw error;
  }
}

async function generateCoverageReport(testResults: TestResult[]): Promise<void> {
  const spinner = ora('Generating coverage report...').start();
  
  try {
    // This would typically run the actual test coverage tools
    // For now, we'll create a basic coverage report structure
    
    const coverageReport = {
      timestamp: new Date().toISOString(),
      summary: {
        totalFiles: testResults.length,
        totalTests: testResults.reduce((sum, result) => sum + result.testCount, 0),
        coverage: testResults.reduce((sum, result) => sum + (result.coverage || 0), 0) / testResults.length
      },
      files: testResults.map(result => ({
        file: result.sourceFile,
        testFile: result.testFile,
        testCount: result.testCount,
        coverage: result.coverage || 0
      }))
    };
    
    await fs.writeFile('coverage-report.json', JSON.stringify(coverageReport, null, 2));
    
    spinner.succeed('Coverage report generated');
    logger.info('Coverage report saved to: coverage-report.json');
    
  } catch (error) {
    spinner.fail('Failed to generate coverage report');
    logger.warn('Coverage report generation failed, but tests were still created');
  }
}
