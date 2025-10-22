import fs from 'fs-extra';
import path from 'path';
import os from 'os';

export interface Config {
  apiKey?: string;
  serverUrl?: string;
  defaultLanguage?: string;
  defaultFramework?: string;
  templates?: {
    [key: string]: string;
  };
  integrations?: {
    [key: string]: {
      enabled: boolean;
      config: Record<string, any>;
    };
  };
}

const CONFIG_DIR = path.join(os.homedir(), '.coding-agent');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

export class ConfigManager {
  private config: Config = {};

  constructor() {
    this.loadConfig();
  }

  private async loadConfig(): Promise<void> {
    try {
      if (await fs.pathExists(CONFIG_FILE)) {
        this.config = await fs.readJson(CONFIG_FILE);
      }
    } catch (error) {
      console.warn('Failed to load config file:', error);
    }
  }

  async saveConfig(): Promise<void> {
    try {
      await fs.ensureDir(CONFIG_DIR);
      await fs.writeJson(CONFIG_FILE, this.config, { spaces: 2 });
    } catch (error) {
      throw new Error(`Failed to save config: ${error}`);
    }
  }

  get<K extends keyof Config>(key: K): Config[K] {
    return this.config[key];
  }

  set<K extends keyof Config>(key: K, value: Config[K]): void {
    this.config[key] = value;
  }

  getAll(): Config {
    return { ...this.config };
  }

  async updateConfig(updates: Partial<Config>): Promise<void> {
    this.config = { ...this.config, ...updates };
    await this.saveConfig();
  }

  // Environment variable overrides
  getApiKey(): string | undefined {
    return process.env.OPENAI_API_KEY || this.config.apiKey;
  }

  getServerUrl(): string {
    return process.env.CODING_AGENT_SERVER || this.config.serverUrl || 'http://localhost:8000';
  }

  // Template management
  getTemplatePath(templateName: string): string | undefined {
    return this.config.templates?.[templateName];
  }

  setTemplate(templateName: string, templatePath: string): void {
    if (!this.config.templates) {
      this.config.templates = {};
    }
    this.config.templates[templateName] = templatePath;
  }

  // Integration management
  getIntegrationConfig(integrationName: string): Record<string, any> | undefined {
    return this.config.integrations?.[integrationName]?.config;
  }

  setIntegrationConfig(integrationName: string, config: Record<string, any>): void {
    if (!this.config.integrations) {
      this.config.integrations = {};
    }
    if (!this.config.integrations[integrationName]) {
      this.config.integrations[integrationName] = { enabled: false, config: {} };
    }
    this.config.integrations[integrationName].config = config;
  }

  enableIntegration(integrationName: string): void {
    if (!this.config.integrations) {
      this.config.integrations = {};
    }
    if (!this.config.integrations[integrationName]) {
      this.config.integrations[integrationName] = { enabled: false, config: {} };
    }
    this.config.integrations[integrationName].enabled = true;
  }

  disableIntegration(integrationName: string): void {
    if (this.config.integrations?.[integrationName]) {
      this.config.integrations[integrationName].enabled = false;
    }
  }
}

export const configManager = new ConfigManager();
