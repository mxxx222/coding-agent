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

# Access at http://localhost:3000
# Auto-deploy: http://localhost:3000/auto-deploy
```

### Automated Notion → Vercel Pipeline

```bash
# Setup environment variables
export NOTION_API_KEY="your_notion_token"
export VERCEL_TOKEN="your_vercel_token"

# Start services
cd server && python -m uvicorn api.main:app --reload
cd web-ui && npm run dev

# Use the automation pipeline
# 1. Go to http://localhost:3000/auto-deploy
# 2. Select a Notion idea
# 3. Start the pipeline
# 4. Get your deployed URL!
```

### Devcontainer (Recommended)

```bash
# Open in VS Code with Remote Containers
code .

# VS Code will prompt to reopen in container
# Or use: Command Palette → Reopen in Container

# Everything is pre-configured!
```

## Security

**⚠️ Important**: Never commit secrets to version control!

See [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for:
- Secret management
- Pre-commit hooks
- BFG repo-cleaner
- Security best practices

## Contributing

See [MERGE_GUIDE.md](MERGE_GUIDE.md) for:
- Pull request process
- CI requirements
- Code review guidelines
- Merge checklist

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
