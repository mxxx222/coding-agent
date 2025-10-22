import { Command } from 'commander';
import inquirer from 'inquirer';
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { logger } from '../utils/logger';
import { configManager } from '../utils/config';
import { GitManager } from '../utils/git';

interface InitOptions {
  template?: string;
  framework?: string;
  skipInstall?: boolean;
}

export async function initCommand(
  projectName?: string,
  options: InitOptions = {}
): Promise<void> {
  try {
    logger.step('Initializing new project with Coding Agent');

    // Get project name if not provided
    if (!projectName) {
      const answers = await inquirer.prompt([
        {
          type: 'input',
          name: 'projectName',
          message: 'What is the name of your project?',
          validate: (input: string) => {
            if (!input.trim()) {
              return 'Project name is required';
            }
            if (!/^[a-zA-Z0-9-_]+$/.test(input)) {
              return 'Project name can only contain letters, numbers, hyphens, and underscores';
            }
            return true;
          }
        }
      ]);
      projectName = answers.projectName;
    }

    const projectPath = path.resolve(projectName);

    // Check if directory already exists
    if (await fs.pathExists(projectPath)) {
      const answers = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'overwrite',
          message: `Directory ${projectName} already exists. Do you want to overwrite it?`,
          default: false
        }
      ]);

      if (!answers.overwrite) {
        logger.info('Project initialization cancelled');
        return;
      }

      await fs.remove(projectPath);
    }

    // Create project directory
    await fs.ensureDir(projectPath);

    // Get framework if not provided
    let framework = options.framework;
    if (!framework) {
      const answers = await inquirer.prompt([
        {
          type: 'list',
          name: 'framework',
          message: 'Which framework would you like to use?',
          choices: [
            { name: 'Next.js (React)', value: 'nextjs' },
            { name: 'FastAPI (Python)', value: 'fastapi' },
            { name: 'Express.js (Node.js)', value: 'express' },
            { name: 'Django (Python)', value: 'django' },
            { name: 'Vue.js', value: 'vue' },
            { name: 'Svelte', value: 'svelte' },
            { name: 'Vanilla JavaScript', value: 'vanilla' }
          ]
        }
      ]);
      framework = answers.framework;
    }

    // Get template if not provided
    let template = options.template;
    if (!template) {
      const answers = await inquirer.prompt([
        {
          type: 'list',
          name: 'template',
          message: 'Which template would you like to use?',
          choices: [
            { name: 'Basic Starter', value: 'basic' },
            { name: 'Full-Stack App (Next.js + Supabase + Stripe)', value: 'fullstack' },
            { name: 'API Server (FastAPI + PostgreSQL)', value: 'api' },
            { name: 'ML Pipeline (Python + Prefect)', value: 'ml' },
            { name: 'E-commerce Store', value: 'ecommerce' }
          ]
        }
      ]);
      template = answers.template;
    }

    // Initialize project based on template
    const spinner = ora('Setting up project structure...').start();
    
    try {
      await setupProject(projectPath, framework, template);
      spinner.succeed('Project structure created');

      // Initialize git repository
      if (!GitManager.isGitRepository(projectPath)) {
        spinner.start('Initializing git repository...');
        await GitManager.initRepository(projectPath);
        await GitManager.createGitignore(projectPath, [
          'node_modules/',
          '.env',
          '.env.local',
          'dist/',
          'build/',
          '*.log'
        ]);
        spinner.succeed('Git repository initialized');
      }

      // Install dependencies if not skipped
      if (!options.skipInstall) {
        spinner.start('Installing dependencies...');
        await installDependencies(projectPath, framework);
        spinner.succeed('Dependencies installed');
      }

      // Create initial commit
      await GitManager.addAndCommit(projectPath, 'Initial commit: Project setup with Coding Agent');

      logger.success(`Project "${projectName}" created successfully!`);
      logger.info(`\nNext steps:`);
      logger.info(`  cd ${projectName}`);
      if (!options.skipInstall) {
        logger.info(`  npm run dev  # or yarn dev`);
      } else {
        logger.info(`  npm install  # or yarn install`);
        logger.info(`  npm run dev  # or yarn dev`);
      }
      logger.info(`\nUse "coding-agent suggest-refactor" to get AI-powered refactoring suggestions`);
      logger.info(`Use "coding-agent generate-test" to generate tests for your code`);

    } catch (error) {
      spinner.fail('Failed to setup project');
      throw error;
    }

  } catch (error) {
    logger.error('Failed to initialize project:', error);
    process.exit(1);
  }
}

async function setupProject(projectPath: string, framework: string, template: string): Promise<void> {
  // Create basic project structure
  const structure = getProjectStructure(framework, template);
  
  for (const [filePath, content] of Object.entries(structure)) {
    const fullPath = path.join(projectPath, filePath);
    await fs.ensureDir(path.dirname(fullPath));
    await fs.writeFile(fullPath, content);
  }
}

function getProjectStructure(framework: string, template: string): Record<string, string> {
  const baseStructure: Record<string, string> = {
    'README.md': `# ${path.basename(process.cwd())}

A project created with Coding Agent.

## Getting Started

\`\`\`bash
npm install
npm run dev
\`\`\`

## Available Commands

- \`coding-agent suggest-refactor\` - Get AI-powered refactoring suggestions
- \`coding-agent generate-test\` - Generate tests for your code
- \`coding-agent integrate\` - Integrate with external services
`,
    '.gitignore': `# Dependencies
node_modules/
__pycache__/
*.pyc

# Environment
.env
.env.local

# Build outputs
dist/
build/
.next/

# Logs
*.log
`,
    '.coding-agent.json': JSON.stringify({
      project: {
        name: path.basename(process.cwd()),
        framework,
        template,
        created: new Date().toISOString()
      },
      settings: {
        autoFormat: true,
        autoTest: false,
        costTracking: true
      }
    }, null, 2)
  };

  // Add framework-specific files
  switch (framework) {
    case 'nextjs':
      return {
        ...baseStructure,
        'package.json': JSON.stringify({
          name: path.basename(process.cwd()),
          version: '0.1.0',
          private: true,
          scripts: {
            dev: 'next dev',
            build: 'next build',
            start: 'next start',
            lint: 'next lint'
          },
          dependencies: {
            next: '^14.0.0',
            react: '^18.0.0',
            'react-dom': '^18.0.0'
          },
          devDependencies: {
            '@types/node': '^20.0.0',
            '@types/react': '^18.0.0',
            '@types/react-dom': '^18.0.0',
            eslint: '^8.0.0',
            'eslint-config-next': '^14.0.0',
            typescript: '^5.0.0'
          }
        }, null, 2),
        'next.config.js': `/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig`,
        'tsconfig.json': JSON.stringify({
          compilerOptions: {
            target: 'es5',
            lib: ['dom', 'dom.iterable', 'es6'],
            allowJs: true,
            skipLibCheck: true,
            strict: true,
            forceConsistentCasingInFileNames: true,
            noEmit: true,
            esModuleInterop: true,
            module: 'esnext',
            moduleResolution: 'node',
            resolveJsonModule: true,
            isolatedModules: true,
            jsx: 'preserve',
            incremental: true,
            plugins: [{ name: 'next' }],
            paths: {
              '@/*': ['./src/*']
            }
          },
          include: ['next-env.d.ts', '**/*.ts', '**/*.tsx', '.next/types/**/*.ts'],
          exclude: ['node_modules']
        }, null, 2),
        'src/app/layout.tsx': `export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}`,
        'src/app/page.tsx': `export default function Home() {
  return (
    <main>
      <h1>Welcome to your Next.js app!</h1>
      <p>Created with Coding Agent</p>
    </main>
  )
}`
      };

    case 'fastapi':
      return {
        ...baseStructure,
        'requirements.txt': `fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-dotenv==1.0.0`,
        'main.py': `from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}`,
        'Dockerfile': `FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`
      };

    default:
      return baseStructure;
  }
}

async function installDependencies(projectPath: string, framework: string): Promise<void> {
  const { execSync } = await import('child_process');
  
  try {
    if (framework === 'nextjs' || framework === 'express' || framework === 'vue' || framework === 'svelte') {
      execSync('npm install', { cwd: projectPath, stdio: 'inherit' });
    } else if (framework === 'fastapi' || framework === 'django' || framework === 'ml') {
      execSync('pip install -r requirements.txt', { cwd: projectPath, stdio: 'inherit' });
    }
  } catch (error) {
    logger.warn('Failed to install dependencies automatically. Please install them manually.');
  }
}
