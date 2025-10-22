import * as vscode from 'vscode';
import { ConfigManager } from '../utils/configManager';
import { ApiClient } from '../utils/apiClient';

export class CodingAgentProvider implements vscode.TreeDataProvider<CodingAgentItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<CodingAgentItem | undefined | null | void> = new vscode.EventEmitter<CodingAgentItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<CodingAgentItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(
        private context: vscode.ExtensionContext,
        private configManager: ConfigManager,
        private apiClient: ApiClient
    ) {}

    getTreeItem(element: CodingAgentItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: CodingAgentItem): Thenable<CodingAgentItem[]> {
        if (!element) {
            return Promise.resolve(this.getRootItems());
        }
        return Promise.resolve([]);
    }

    private getRootItems(): CodingAgentItem[] {
        const items: CodingAgentItem[] = [];

        // Configuration status
        const isConfigured = this.configManager.isConfigured();
        items.push(new CodingAgentItem(
            isConfigured ? '✓ Configured' : '✗ Not Configured',
            isConfigured ? vscode.TreeItemCollapsibleState.None : vscode.TreeItemCollapsibleState.None,
            'config',
            isConfigured ? 'Coding Agent is properly configured' : 'Click to configure Coding Agent'
        ));

        // Server status
        items.push(new CodingAgentItem(
            'Server Status',
            vscode.TreeItemCollapsibleState.None,
            'server',
            'Check server connection'
        ));

        // Recent suggestions
        items.push(new CodingAgentItem(
            'Recent Suggestions',
            vscode.TreeItemCollapsibleState.Collapsed,
            'suggestions',
            'View recent AI suggestions'
        ));

        // Integrations
        items.push(new CodingAgentItem(
            'Integrations',
            vscode.TreeItemCollapsibleState.Collapsed,
            'integrations',
            'Manage service integrations'
        ));

        return items;
    }

    async initialize(): Promise<void> {
        const isConfigured = this.configManager.isConfigured();
        
        if (!isConfigured) {
            const apiKey = await vscode.window.showInputBox({
                prompt: 'Enter your OpenAI API key',
                placeHolder: 'sk-...',
                password: true
            });

            if (apiKey) {
                await this.configManager.setApiKey(apiKey);
                vscode.window.showInformationMessage('API key saved successfully!');
            } else {
                vscode.window.showWarningMessage('API key is required to use Coding Agent');
                return;
            }
        }

        // Check server connection
        const healthResponse = await this.apiClient.getHealth();
        if (healthResponse.success) {
            vscode.window.showInformationMessage('Coding Agent is ready!');
        } else {
            vscode.window.showWarningMessage('Coding Agent server is not available. Some features may not work.');
        }

        this.refresh();
    }

    async autoSuggest(document: vscode.TextDocument): Promise<void> {
        if (!this.configManager.getAutoSuggest()) {
            return;
        }

        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document !== document) {
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            return;
        }

        const selectedText = document.getText(selection);
        if (selectedText.length < 10) {
            return;
        }

        try {
            const response = await this.apiClient.analyzeCode(selectedText);
            if (response.success && response.data?.suggestions) {
                this.showSuggestions(response.data.suggestions);
            }
        } catch (error) {
            // Silently fail for auto-suggestions
            console.log('Auto-suggestion failed:', error);
        }
    }

    private showSuggestions(suggestions: any[]): void {
        const maxSuggestions = this.configManager.getMaxSuggestions();
        const limitedSuggestions = suggestions.slice(0, maxSuggestions);

        const items = limitedSuggestions.map((suggestion, index) => ({
            label: `Suggestion ${index + 1}`,
            description: suggestion.title,
            detail: suggestion.description
        }));

        vscode.window.showQuickPick(items, {
            placeHolder: 'Select a suggestion to apply',
            canPickMany: false
        }).then(selected => {
            if (selected) {
                // Apply suggestion logic here
                vscode.window.showInformationMessage(`Applied: ${selected.description}`);
            }
        });
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
}

export class CodingAgentItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly command?: string,
        public readonly tooltip?: string
    ) {
        super(label, collapsibleState);
        this.tooltip = tooltip;
        this.command = command;
    }

    iconPath = {
        light: '',
        dark: ''
    };

    contextValue = 'codingAgentItem';
}
