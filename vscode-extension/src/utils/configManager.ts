import * as vscode from 'vscode';

export class ConfigManager {
    private config: vscode.WorkspaceConfiguration;

    constructor() {
        this.config = vscode.workspace.getConfiguration('coding-agent');
    }

    getApiKey(): string | undefined {
        return this.config.get('apiKey') || process.env.OPENAI_API_KEY;
    }

    getServerUrl(): string {
        return this.config.get('serverUrl', 'http://localhost:8000');
    }

    getAutoSuggest(): boolean {
        return this.config.get('autoSuggest', false);
    }

    getMaxSuggestions(): number {
        return this.config.get('maxSuggestions', 3);
    }

    getLanguage(): string {
        return this.config.get('language', 'auto');
    }

    async setApiKey(apiKey: string): Promise<void> {
        await this.config.update('apiKey', apiKey, vscode.ConfigurationTarget.Global);
    }

    async setServerUrl(serverUrl: string): Promise<void> {
        await this.config.update('serverUrl', serverUrl, vscode.ConfigurationTarget.Workspace);
    }

    async setAutoSuggest(enabled: boolean): Promise<void> {
        await this.config.update('autoSuggest', enabled, vscode.ConfigurationTarget.Global);
    }

    async setMaxSuggestions(maxSuggestions: number): Promise<void> {
        await this.config.update('maxSuggestions', maxSuggestions, vscode.ConfigurationTarget.Global);
    }

    async setLanguage(language: string): Promise<void> {
        await this.config.update('language', language, vscode.ConfigurationTarget.Global);
    }

    // Check if configuration is complete
    isConfigured(): boolean {
        return !!this.getApiKey();
    }

    // Get configuration summary
    getConfigSummary(): string {
        const apiKey = this.getApiKey();
        const serverUrl = this.getServerUrl();
        const autoSuggest = this.getAutoSuggest();
        
        return `API Key: ${apiKey ? '✓ Set' : '✗ Not set'}\nServer URL: ${serverUrl}\nAuto-suggest: ${autoSuggest ? 'Enabled' : 'Disabled'}`;
    }
}
