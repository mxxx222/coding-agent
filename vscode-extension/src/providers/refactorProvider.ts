import * as vscode from 'vscode';
import { ConfigManager } from '../utils/configManager';
import { ApiClient } from '../utils/apiClient';

export class RefactorProvider {
    constructor(
        private context: vscode.ExtensionContext,
        private configManager: ConfigManager,
        private apiClient: ApiClient
    ) {}

    async suggestRefactor(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor found');
            return;
        }

        const selection = editor.selection;
        const document = editor.document;
        
        // Get selected text or entire document if no selection
        const code = selection.isEmpty 
            ? document.getText() 
            : document.getText(selection);

        if (!code.trim()) {
            vscode.window.showWarningMessage('No code selected to refactor');
            return;
        }

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing code for refactoring opportunities...",
            cancellable: true
        }, async (progress, token) => {
            try {
                const response = await this.apiClient.suggestRefactor(
                    code,
                    document.fileName,
                    this.getLanguageFromDocument(document)
                );

                if (token.isCancellationRequested) {
                    return;
                }

                if (response.success && response.data?.suggestions) {
                    await this.showRefactorSuggestions(response.data.suggestions, editor, selection);
                } else {
                    vscode.window.showErrorMessage(`Failed to get refactoring suggestions: ${response.error}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Error analyzing code: ${error}`);
            }
        });
    }

    private async showRefactorSuggestions(suggestions: any[], editor: vscode.TextEditor, selection: vscode.Selection): Promise<void> {
        if (suggestions.length === 0) {
            vscode.window.showInformationMessage('No refactoring suggestions found. Your code looks good!');
            return;
        }

        // Create quick pick items for suggestions
        const items = suggestions.map((suggestion, index) => ({
            label: `${suggestion.severity?.toUpperCase() || 'MEDIUM'}: ${suggestion.title}`,
            description: suggestion.description,
            detail: suggestion.reasoning,
            suggestion: suggestion
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a refactoring suggestion to apply',
            canPickMany: false
        });

        if (selected) {
            await this.applyRefactorSuggestion(selected.suggestion, editor, selection);
        }
    }

    private async applyRefactorSuggestion(suggestion: any, editor: vscode.TextEditor, selection: vscode.Selection): Promise<void> {
        const { currentCode, suggestedCode, title, description } = suggestion;

        // Show diff preview
        const apply = await vscode.window.showInformationMessage(
            `Apply refactoring: ${title}`,
            'Preview Changes',
            'Apply',
            'Cancel'
        );

        if (apply === 'Cancel') {
            return;
        }

        if (apply === 'Preview Changes') {
            await this.showDiffPreview(currentCode, suggestedCode, title);
            return;
        }

        if (apply === 'Apply') {
            await this.applyChanges(suggestedCode, editor, selection);
        }
    }

    private async showDiffPreview(currentCode: string, suggestedCode: string, title: string): Promise<void> {
        // Create a new document to show the diff
        const doc = await vscode.workspace.openTextDocument({
            content: `// ${title}\n\n// Current Code:\n${currentCode}\n\n// Suggested Code:\n${suggestedCode}`,
            language: 'typescript'
        });

        await vscode.window.showTextDocument(doc);
    }

    private async applyChanges(suggestedCode: string, editor: vscode.TextEditor, selection: vscode.Selection): Promise<void> {
        const edit = new vscode.WorkspaceEdit();
        
        if (selection.isEmpty) {
            // Replace entire document
            edit.replace(editor.document.uri, new vscode.Range(0, 0, editor.document.lineCount, 0), suggestedCode);
        } else {
            // Replace selected text
            edit.replace(editor.document.uri, selection, suggestedCode);
        }

        const applied = await vscode.workspace.applyEdit(edit);
        
        if (applied) {
            vscode.window.showInformationMessage('Refactoring applied successfully!');
        } else {
            vscode.window.showErrorMessage('Failed to apply refactoring');
        }
    }

    private getLanguageFromDocument(document: vscode.TextDocument): string {
        const languageMap: { [key: string]: string } = {
            'typescript': 'typescript',
            'javascript': 'javascript',
            'python': 'python',
            'java': 'java',
            'go': 'go',
            'rust': 'rust',
            'cpp': 'cpp',
            'c': 'c',
            'csharp': 'csharp',
            'php': 'php',
            'ruby': 'ruby',
            'swift': 'swift',
            'kotlin': 'kotlin'
        };

        return languageMap[document.languageId] || 'unknown';
    }
}
