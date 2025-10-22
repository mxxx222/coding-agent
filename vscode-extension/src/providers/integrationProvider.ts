import * as vscode from 'vscode';
import { ConfigManager } from '../utils/configManager';
import { ApiClient } from '../utils/apiClient';

export class IntegrationProvider {
    constructor(
        private context: vscode.ExtensionContext,
        private configManager: ConfigManager,
        private apiClient: ApiClient
    ) {}

    async showIntegrationPanel(): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'codingAgentIntegrations',
            'Coding Agent - Integrations',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this.getIntegrationHtml();

        // Handle messages from webview
        panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'setupIntegration':
                        await this.setupIntegration(message.service, message.config);
                        break;
                    case 'getIntegrations':
                        await this.getIntegrations();
                        break;
                }
            },
            undefined,
            this.context.subscriptions
        );
    }

    private async setupIntegration(service: string, config: any): Promise<void> {
        try {
            const response = await this.apiClient.setupIntegration(service, config);
            
            if (response.success) {
                vscode.window.showInformationMessage(`${service} integration setup successfully!`);
            } else {
                vscode.window.showErrorMessage(`Failed to setup ${service}: ${response.error}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error setting up ${service}: ${error}`);
        }
    }

    private async getIntegrations(): Promise<void> {
        try {
            const response = await this.apiClient.getIntegrations();
            
            if (response.success) {
                // Send integrations data to webview
                // This would be handled by the webview communication
            } else {
                vscode.window.showErrorMessage(`Failed to get integrations: ${response.error}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error getting integrations: ${error}`);
        }
    }

    private getIntegrationHtml(): string {
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coding Agent - Integrations</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
        }
        .integration-card {
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            background-color: var(--vscode-panel-background);
        }
        .integration-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .integration-title {
            font-size: 18px;
            font-weight: bold;
            color: var(--vscode-foreground);
        }
        .integration-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-enabled {
            background-color: var(--vscode-testing-iconPassed);
            color: white;
        }
        .status-disabled {
            background-color: var(--vscode-testing-iconFailed);
            color: white;
        }
        .integration-description {
            color: var(--vscode-descriptionForeground);
            margin-bottom: 12px;
        }
        .integration-actions {
            display: flex;
            gap: 8px;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-primary {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        .btn-secondary {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        .btn:hover {
            opacity: 0.8;
        }
        .config-section {
            margin-top: 12px;
            padding: 12px;
            background-color: var(--vscode-input-background);
            border-radius: 4px;
            display: none;
        }
        .config-section.show {
            display: block;
        }
        .form-group {
            margin-bottom: 12px;
        }
        .form-label {
            display: block;
            margin-bottom: 4px;
            font-weight: bold;
        }
        .form-input {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
        }
    </style>
</head>
<body>
    <h1>Service Integrations</h1>
    <p>Connect your project with external services to enhance functionality.</p>
    
    <div class="integration-card">
        <div class="integration-header">
            <div class="integration-title">Supabase</div>
            <div class="integration-status status-disabled">Not Connected</div>
        </div>
        <div class="integration-description">
            Backend-as-a-Service with database, authentication, and real-time features.
        </div>
        <div class="integration-actions">
            <button class="btn btn-primary" onclick="setupIntegration('supabase')">Setup</button>
            <button class="btn btn-secondary" onclick="toggleConfig('supabase')">Configure</button>
        </div>
        <div id="supabase-config" class="config-section">
            <div class="form-group">
                <label class="form-label">Supabase URL</label>
                <input type="text" class="form-input" placeholder="https://your-project.supabase.co" id="supabase-url">
            </div>
            <div class="form-group">
                <label class="form-label">Anon Key</label>
                <input type="password" class="form-input" placeholder="your-anon-key" id="supabase-key">
            </div>
        </div>
    </div>

    <div class="integration-card">
        <div class="integration-header">
            <div class="integration-title">Stripe</div>
            <div class="integration-status status-disabled">Not Connected</div>
        </div>
        <div class="integration-description">
            Payment processing and subscription management.
        </div>
        <div class="integration-actions">
            <button class="btn btn-primary" onclick="setupIntegration('stripe')">Setup</button>
            <button class="btn btn-secondary" onclick="toggleConfig('stripe')">Configure</button>
        </div>
        <div id="stripe-config" class="config-section">
            <div class="form-group">
                <label class="form-label">Secret Key</label>
                <input type="password" class="form-input" placeholder="sk_test_..." id="stripe-secret">
            </div>
            <div class="form-group">
                <label class="form-label">Publishable Key</label>
                <input type="text" class="form-input" placeholder="pk_test_..." id="stripe-publishable">
            </div>
        </div>
    </div>

    <div class="integration-card">
        <div class="integration-header">
            <div class="integration-title">Auth0</div>
            <div class="integration-status status-disabled">Not Connected</div>
        </div>
        <div class="integration-description">
            Authentication and user management.
        </div>
        <div class="integration-actions">
            <button class="btn btn-primary" onclick="setupIntegration('auth0')">Setup</button>
            <button class="btn btn-secondary" onclick="toggleConfig('auth0')">Configure</button>
        </div>
        <div id="auth0-config" class="config-section">
            <div class="form-group">
                <label class="form-label">Domain</label>
                <input type="text" class="form-input" placeholder="your-domain.auth0.com" id="auth0-domain">
            </div>
            <div class="form-group">
                <label class="form-label">Client ID</label>
                <input type="text" class="form-input" placeholder="your-client-id" id="auth0-client-id">
            </div>
            <div class="form-group">
                <label class="form-label">Client Secret</label>
                <input type="password" class="form-input" placeholder="your-client-secret" id="auth0-client-secret">
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function setupIntegration(service) {
            const config = getConfigForService(service);
            vscode.postMessage({
                command: 'setupIntegration',
                service: service,
                config: config
            });
        }

        function toggleConfig(service) {
            const configSection = document.getElementById(service + '-config');
            configSection.classList.toggle('show');
        }

        function getConfigForService(service) {
            const config = {};
            
            if (service === 'supabase') {
                config.url = document.getElementById('supabase-url').value;
                config.anonKey = document.getElementById('supabase-key').value;
            } else if (service === 'stripe') {
                config.secretKey = document.getElementById('stripe-secret').value;
                config.publishableKey = document.getElementById('stripe-publishable').value;
            } else if (service === 'auth0') {
                config.domain = document.getElementById('auth0-domain').value;
                config.clientId = document.getElementById('auth0-client-id').value;
                config.clientSecret = document.getElementById('auth0-client-secret').value;
            }
            
            return config;
        }

        // Load existing configurations
        vscode.postMessage({
            command: 'getIntegrations'
        });
    </script>
</body>
</html>`;
    }
}
