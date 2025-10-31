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

### Backend API (Development)

```bash
# Navigate to server directory
cd server

# Install dependencies
pip install -r requirements.txt

# Create .env file (see server/.env.example)
cp .env.example .env

# Run the server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# http://localhost:8000/api/docs
```

### Docker (Recommended)

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### CLI Usage (Coming Soon)

```bash
# Install globally
npm install -g @coding-agent/cli

# Initialize a new project
coding-agent init my-project

# Get refactoring suggestions
coding-agent suggest-refactor src/
```

### Web Interface (Coming Soon)

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

- **[Production Guide](PRODUCTION_README.md)** - Complete guide to getting production-ready
- **[Setup Instructions](SETUP.md)** - Detailed setup instructions
- [Architecture Guide](docs/ARCHITECTURE.md) - System architecture
- [API Documentation](docs/API.md) - API reference
- [Recipes and Templates](docs/RECIPES.md) - Project templates
- [Deployment Guide](docs/DEPLOYMENT.md) - Deployment options

## Current Status

✅ **Backend API** - Fully functional with OpenAI integration (mock mode without API key)  
✅ **Database** - PostgreSQL schema and migrations ready  
✅ **Services** - All core services implemented  
⚠️ **CLI Tool** - In development  
⚠️ **VS Code Extension** - In development  
⚠️ **Web UI** - In development

## What's Working Now

- FastAPI backend with full CRUD operations
- Code analysis and quality assessment
- Refactoring suggestions
- Test generation
- Integration services (Supabase, Stripe, etc.)
- JWT authentication
- Cost tracking
- Docker support
- Database migrations

## What's Coming Next

- CLI tool release
- VS Code extension
- Web UI implementation
- Comprehensive test suite
- CI/CD pipeline
- Additional integrations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.
