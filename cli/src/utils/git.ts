import { execSync } from 'child_process';
import fs from 'fs-extra';
import path from 'path';

export interface GitInfo {
  isRepo: boolean;
  branch?: string;
  remote?: string;
  hasUncommittedChanges: boolean;
  lastCommit?: string;
}

export class GitManager {
  static isGitRepository(dir: string): boolean {
    try {
      execSync('git rev-parse --git-dir', { 
        cwd: dir, 
        stdio: 'ignore' 
      });
      return true;
    } catch {
      return false;
    }
  }

  static getGitInfo(dir: string): GitInfo {
    const isRepo = this.isGitRepository(dir);
    
    if (!isRepo) {
      return {
        isRepo: false,
        hasUncommittedChanges: false
      };
    }

    try {
      const branch = execSync('git branch --show-current', { 
        cwd: dir, 
        encoding: 'utf8' 
      }).trim();

      const remote = execSync('git remote get-url origin', { 
        cwd: dir, 
        encoding: 'utf8' 
      }).trim();

      const hasUncommittedChanges = execSync('git status --porcelain', { 
        cwd: dir, 
        encoding: 'utf8' 
      }).length > 0;

      const lastCommit = execSync('git rev-parse HEAD', { 
        cwd: dir, 
        encoding: 'utf8' 
      }).trim();

      return {
        isRepo: true,
        branch,
        remote,
        hasUncommittedChanges,
        lastCommit
      };
    } catch (error) {
      return {
        isRepo: true,
        hasUncommittedChanges: false
      };
    }
  }

  static async initRepository(dir: string): Promise<void> {
    try {
      execSync('git init', { cwd: dir, stdio: 'inherit' });
    } catch (error) {
      throw new Error(`Failed to initialize git repository: ${error}`);
    }
  }

  static async addAndCommit(dir: string, message: string): Promise<void> {
    try {
      execSync('git add .', { cwd: dir, stdio: 'inherit' });
      execSync(`git commit -m "${message}"`, { cwd: dir, stdio: 'inherit' });
    } catch (error) {
      throw new Error(`Failed to commit changes: ${error}`);
    }
  }

  static async createBranch(dir: string, branchName: string): Promise<void> {
    try {
      execSync(`git checkout -b ${branchName}`, { cwd: dir, stdio: 'inherit' });
    } catch (error) {
      throw new Error(`Failed to create branch: ${error}`);
    }
  }

  static async stashChanges(dir: string): Promise<void> {
    try {
      execSync('git stash push -m "Coding Agent: Stashed changes"', { 
        cwd: dir, 
        stdio: 'inherit' 
      });
    } catch (error) {
      throw new Error(`Failed to stash changes: ${error}`);
    }
  }

  static async popStash(dir: string): Promise<void> {
    try {
      execSync('git stash pop', { cwd: dir, stdio: 'inherit' });
    } catch (error) {
      throw new Error(`Failed to pop stash: ${error}`);
    }
  }

  static async getDiff(dir: string, filePath?: string): Promise<string> {
    try {
      const command = filePath ? `git diff ${filePath}` : 'git diff';
      return execSync(command, { cwd: dir, encoding: 'utf8' });
    } catch (error) {
      throw new Error(`Failed to get diff: ${error}`);
    }
  }

  static async getFileHistory(dir: string, filePath: string, limit: number = 10): Promise<string[]> {
    try {
      const command = `git log --oneline -n ${limit} -- ${filePath}`;
      const output = execSync(command, { cwd: dir, encoding: 'utf8' });
      return output.trim().split('\n').filter(line => line.length > 0);
    } catch (error) {
      return [];
    }
  }

  static async createGitignore(dir: string, patterns: string[]): Promise<void> {
    const gitignorePath = path.join(dir, '.gitignore');
    const existingContent = await fs.pathExists(gitignorePath) 
      ? await fs.readFile(gitignorePath, 'utf8') 
      : '';

    const newPatterns = patterns.filter(pattern => 
      !existingContent.includes(pattern)
    );

    if (newPatterns.length > 0) {
      const content = existingContent + 
        (existingContent ? '\n' : '') + 
        '# Coding Agent\n' + 
        newPatterns.join('\n') + '\n';
      
      await fs.writeFile(gitignorePath, content);
    }
  }
}
