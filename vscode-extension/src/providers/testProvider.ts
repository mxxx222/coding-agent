import * as vscode from 'vscode';
import * as path from 'path';
import { ConfigManager } from '../utils/configManager';
import { ApiClient } from '../utils/apiClient';

export class TestProvider {
    constructor(
        private context: vscode.ExtensionContext,
        private configManager: ConfigManager,
        private apiClient: ApiClient
    ) {}

    async generateTest(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor found');
            return;
        }

        const document = editor.document;
        const code = document.getText();

        if (!code.trim()) {
            vscode.window.showWarningMessage('No code found to generate tests for');
            return;
        }

        // Ask for test framework if not detected
        const framework = await this.detectOrSelectFramework(document);
        if (!framework) {
            return;
        }

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Generating tests...",
            cancellable: true
        }, async (progress, token) => {
            try {
                const response = await this.apiClient.generateTest(
                    code,
                    document.fileName,
                    framework
                );

                if (token.isCancellationRequested) {
                    return;
                }

                if (response.success && response.data?.tests) {
                    await this.createTestFiles(response.data.tests, document);
                } else {
                    vscode.window.showErrorMessage(`Failed to generate tests: ${response.error}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Error generating tests: ${error}`);
            }
        });
    }

    private async detectOrSelectFramework(document: vscode.TextDocument): Promise<string | undefined> {
        const detectedFramework = this.detectFramework(document);
        
        if (detectedFramework) {
            return detectedFramework;
        }

        // Let user select framework
        const frameworks = [
            { label: 'Jest (JavaScript/TypeScript)', value: 'jest' },
            { label: 'Pytest (Python)', value: 'pytest' },
            { label: 'JUnit (Java)', value: 'junit' },
            { label: 'Go Testing', value: 'testing' },
            { label: 'Rust Testing', value: 'cargo-test' },
            { label: 'Mocha (JavaScript)', value: 'mocha' },
            { label: 'Vitest (JavaScript/TypeScript)', value: 'vitest' }
        ];

        const selected = await vscode.window.showQuickPick(frameworks, {
            placeHolder: 'Select a testing framework',
            canPickMany: false
        });

        return selected?.value;
    }

    private detectFramework(document: vscode.TextDocument): string | undefined {
        const fileName = path.basename(document.fileName);
        const language = document.languageId;

        // Check for existing test files
        if (fileName.includes('.test.') || fileName.includes('.spec.')) {
            return 'jest'; // Assume Jest for existing test files
        }

        // Check package.json for test scripts
        if (language === 'typescript' || language === 'javascript') {
            return 'jest'; // Default for JS/TS
        }

        if (language === 'python') {
            return 'pytest';
        }

        if (language === 'java') {
            return 'junit';
        }

        if (language === 'go') {
            return 'testing';
        }

        if (language === 'rust') {
            return 'cargo-test';
        }

        return undefined;
    }

    private async createTestFiles(tests: any[], sourceDocument: vscode.TextDocument): Promise<void> {
        const sourcePath = sourceDocument.fileName;
        const sourceDir = path.dirname(sourcePath);
        const sourceName = path.basename(sourcePath, path.extname(sourcePath));

        for (const test of tests) {
            const testFileName = this.getTestFileName(sourceName, test.framework);
            const testFilePath = path.join(sourceDir, testFileName);

            try {
                // Create test file
                const testDoc = await vscode.workspace.openTextDocument({
                    content: test.content,
                    language: this.getLanguageForFramework(test.framework)
                });

                await vscode.window.showTextDocument(testDoc);
                
                // Save the file
                await testDoc.save();

                vscode.window.showInformationMessage(`Test file created: ${testFileName}`);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to create test file: ${error}`);
            }
        }

        // Show summary
        vscode.window.showInformationMessage(`Generated ${tests.length} test file(s)`);
    }

    private getTestFileName(sourceName: string, framework: string): string {
        switch (framework) {
            case 'jest':
            case 'mocha':
            case 'vitest':
                return `${sourceName}.test.ts`;
            case 'pytest':
                return `test_${sourceName}.py`;
            case 'junit':
                return `${sourceName}Test.java`;
            case 'testing':
                return `${sourceName}_test.go`;
            case 'cargo-test':
                return `${sourceName}_test.rs`;
            default:
                return `${sourceName}.test.ts`;
        }
    }

    private getLanguageForFramework(framework: string): string {
        switch (framework) {
            case 'jest':
            case 'mocha':
            case 'vitest':
                return 'typescript';
            case 'pytest':
                return 'python';
            case 'junit':
                return 'java';
            case 'testing':
                return 'go';
            case 'cargo-test':
                return 'rust';
            default:
                return 'typescript';
        }
    }
}
