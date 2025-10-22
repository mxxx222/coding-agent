# Coding Agent

An intelligent coding assistant that helps developers build, refactor, and test code with AI-powered suggestions and automated workflows.

## Features

- 🤖 **AI-Powered Code Generation**: Generate code, tests, and documentation
- 🔧 **Smart Refactoring**: Get intelligent refactoring suggestions
- 🧪 **Automated Testing**: Generate and run tests automatically
- 🔗 **Integration Support**: Works with popular frameworks and services
- 📊 **Cost Tracking**: Monitor AI usage and costs
- 🎯 **Guided Development**: Step-by-step project building

## Architecture

```
coding-agent/
├── cli/                 # Command-line interface
├── vscode-extension/    # VS Code extension
├── server/             # Python backend server
├── web-ui/             # Next.js web interface
├── database/           # Database schemas and migrations
├── recipes/            # Pre-built project templates
└── policies/           # Security and safety policies
```

## Quick Start

### CLI Usage

```bash
# Install globally
npm install -g @coding-agent/cli

# Initialize a new project
coding-agent init my-project

# Get refactoring suggestions
coding-agent suggest-refactor src/

# Generate tests
coding-agent generate-test src/components/

# Integrate with services
coding-agent integrate supabase stripe
```

### VS Code Extension

1. Install the "Coding Agent" extension from the VS Code marketplace
2. Open any project and use `Ctrl+Shift+P` to access commands
3. Use the guided development features

### Web Interface

```bash
# Start the development server
cd web-ui
npm install
npm run dev
```

## Development

### Prerequisites

- Node.js 18+
- Python 3.9+
- Docker
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/coding-agent.git
cd coding-agent

# Run setup script
./scripts/setup.sh

# Start development environment
./scripts/dev.sh
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Recipes and Templates](docs/RECIPES.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.
