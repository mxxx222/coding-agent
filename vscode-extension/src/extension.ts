import * as vscode from 'vscode';
import { CodingAgentProvider } from './providers/codingAgentProvider';
import { RefactorProvider } from './providers/refactorProvider';
import { TestProvider } from './providers/testProvider';
import { IntegrationProvider } from './providers/integrationProvider';
import { CodeExplainer } from './providers/codeExplainer';
import { CodeOptimizer } from './providers/codeOptimizer';
import { ConfigManager } from './utils/configManager';
import { ApiClient } from './utils/apiClient';

export function activate(context: vscode.ExtensionContext) {
    console.log('Coding Agent extension is now active!');

    // Initialize configuration manager
    const configManager = new ConfigManager();
    
    // Initialize API client
    const apiClient = new ApiClient(configManager);

    // Initialize providers
    const codingAgentProvider = new CodingAgentProvider(context, configManager, apiClient);
    const refactorProvider = new RefactorProvider(context, configManager, apiClient);
    const testProvider = new TestProvider(context, configManager, apiClient);
    const integrationProvider = new IntegrationProvider(context, configManager, apiClient);
    const codeExplainer = new CodeExplainer(context, configManager, apiClient);
    const codeOptimizer = new CodeOptimizer(context, configManager, apiClient);

    // Register commands
    const commands = [
        vscode.commands.registerCommand('coding-agent.initialize', () => {
            codingAgentProvider.initialize();
        }),
        vscode.commands.registerCommand('coding-agent.suggestRefactor', () => {
            refactorProvider.suggestRefactor();
        }),
        vscode.commands.registerCommand('coding-agent.generateTest', () => {
            testProvider.generateTest();
        }),
        vscode.commands.registerCommand('coding-agent.integrate', () => {
            integrationProvider.showIntegrationPanel();
        }),
        vscode.commands.registerCommand('coding-agent.explainCode', () => {
            codeExplainer.explainCode();
        }),
        vscode.commands.registerCommand('coding-agent.optimizeCode', () => {
            codeOptimizer.optimizeCode();
        })
    ];

    // Register tree data provider
    const treeDataProvider = new CodingAgentProvider(context, configManager, apiClient);
    vscode.window.createTreeView('coding-agent-view', { treeDataProvider });

    // Register status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(robot) Coding Agent";
    statusBarItem.command = 'coding-agent.initialize';
    statusBarItem.show();

    // Register text document change listener for auto-suggestions
    const autoSuggestEnabled = vscode.workspace.getConfiguration('coding-agent').get('autoSuggest', false);
    if (autoSuggestEnabled) {
        const disposable = vscode.workspace.onDidChangeTextDocument((event) => {
            if (event.contentChanges.length > 0) {
                // Debounce auto-suggestions
                setTimeout(() => {
                    codingAgentProvider.autoSuggest(event.document);
                }, 1000);
            }
        });
        context.subscriptions.push(disposable);
    }

    // Add all disposables
    context.subscriptions.push(...commands, statusBarItem);

    // Show welcome message
    vscode.window.showInformationMessage('Coding Agent is ready! Use Ctrl+Shift+P to access commands.');
}

export function deactivate() {
    console.log('Coding Agent extension is now deactivated');
}
