#!/bin/bash

# OpenClaw FullStack Engineer - Complete Deployment Script
# This script sets up a complete development environment for OpenClaw with full-stack engineering capabilities

set -e

echo "🚀 Starting OpenClaw FullStack Engineer Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root (optional - allow root for deployment)
if [[ $EUID -eq 0 ]]; then
   log_warning "Running as root - deployment will be system-wide"
   DEPLOY_DIR="/opt/openclaw-fullstack-engineer"
else
   DEPLOY_DIR="$HOME/openclaw-fullstack-engineer"
fi

# Check Node.js version
log_info "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [[ $NODE_VERSION -lt 18 ]]; then
    log_error "Node.js version 18 or higher is required. Current version: $(node --version)"
    exit 1
fi

log_success "Node.js $(node --version) is installed"

# Check npm
log_info "Checking npm..."
if ! command -v npm &> /dev/null; then
    log_error "npm is not installed. Please install npm first."
    exit 1
fi

log_success "npm $(npm --version) is installed"

# Create directory structure
log_info "Creating directory structure..."
mkdir -p "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR/workspace"
mkdir -p "$DEPLOY_DIR/skills"
mkdir -p "$DEPLOY_DIR/config"

# Copy configuration files
log_info "Copying configuration files..."
cp IDENTITY.md "$DEPLOY_DIR/"
cp SOUL.md "$DEPLOY_DIR/"
cp USER.md "$DEPLOY_DIR/"
cp TOOLS.md "$DEPLOY_DIR/"
cp AGENTS.md "$DEPLOY_DIR/"
cp BOOTSTRAP.md "$DEPLOY_DIR/"
cp HEARTBEAT.md "$DEPLOY_DIR/"

# Copy skills
log_info "Copying skills..."
cp -r fullstack-dev "$DEPLOY_DIR/skills/"
cp -r conversation-memory "$DEPLOY_DIR/skills/"

# Copy workspace files
log_info "Copying workspace files..."
cp -r workspace/* "$DEPLOY_DIR/workspace/" 2>/dev/null || log_warning "Some workspace files may not exist"

# Copy config template
cp config-template.json "$DEPLOY_DIR/config/"

# Create installation script
cat > "$DEPLOY_DIR/install.sh" << 'EOF'
#!/bin/bash

# OpenClaw FullStack Engineer Installation Script

set -e

echo "🚀 Installing OpenClaw FullStack Engineer..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Install OpenClaw globally
echo "📦 Installing OpenClaw..."
npm install -g @openclaw/openclaw

# Create symbolic link for workspace
ln -sf "$DEPLOY_DIR" ~/.openclaw

echo "✅ Installation completed!"
echo "🎯 You can now run: openclaw"
echo "📁 Your workspace is at: $DEPLOY_DIR"
EOF

# Create startup script
cat > "$DEPLOY_DIR/start.sh" << 'EOF'
#!/bin/bash

# OpenClaw FullStack Engineer Startup Script

echo "🚀 Starting OpenClaw FullStack Engineer..."
echo "📁 Workspace: $DEPLOY_DIR"

# Check if OpenClaw is installed
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw is not installed. Please run install.sh first."
    exit 1
fi

# Start OpenClaw
cd "$DEPLOY_DIR"
openclaw
EOF

# Create README
cat > "$DEPLOY_DIR/README.md" << 'EOF'
# OpenClaw FullStack Engineer

A complete deployment package for OpenClaw with specialized full-stack engineering capabilities and advanced conversation memory management.

## 🎯 Features

- **Full-Stack Engineering**: Specialized skills for web development, APIs, databases, and DevOps
- **Advanced Memory Management**: Intelligent conversation memory system for long-term context
- **Professional Identity**: Configured as a FullStack Engineer with best practices
- **Complete Workspace**: Ready-to-use development environment with pre-configured skills

## 🚀 Quick Start

### 1. Installation
\`\`\`bash
cd openclaw-fullstack-engineer
chmod +x install.sh
./install.sh
\`\`\`

### 2. Startup
\`\`\`bash
chmod +x start.sh
./start.sh
\`\`\`

### 3. Usage
\`\`\`bash
openclaw
\`\`\`

## 📁 Directory Structure

\`\`\`
openclaw-fullstack-engineer/
├── README.md                 # This file
├── install.sh               # Installation script
├── start.sh                 # Startup script
├── IDENTITY.md              # AI identity configuration
├── SOUL.md                  # AI behavior and principles
├── USER.md                  # User profile
├── TOOLS.md                 # Local tool configuration
├── AGENTS.md                # Agent workspace configuration
├── BOOTSTRAP.md             # Bootstrap instructions
├── HEARTBEAT.md             # Heartbeat configuration
├── config/                  # Configuration files
│   └── config-template.json
├── skills/                  # Specialized skills
│   ├── fullstack-dev/       # Full-stack development skills
│   └── conversation-memory/ # Memory management skills
└── workspace/               # OpenClaw workspace
\`\`\`

## 🧠 Memory System

The conversation memory system provides:

- **Multi-layer memory**: Short-term, medium-term, and long-term memory
- **Intelligent compression**: Automatic prioritization and compression
- **Context management**: Dynamic context window optimization
- **Conversation continuity**: Maintains coherence across long interactions

## 🛠️ Full-Stack Skills

The full-stack development skills include:

- **Frontend**: React, Vue, Angular, TypeScript, modern CSS
- **Backend**: Node.js, Python, Go, REST APIs, GraphQL
- **Database**: PostgreSQL, MongoDB, Redis, database optimization
- **DevOps**: Docker, CI/CD, cloud deployment, monitoring

## 🔧 Configuration

All configuration files are pre-configured for:

- Professional full-stack development workflow
- Advanced memory management
- Git integration with GitHub
- Best practices and coding standards

## 🚀 Deployment

This package is designed to be deployed on any system with Node.js 18+ and can be easily:

- Copied to different machines
- Shared with team members
- Used as a template for new deployments
- Integrated with existing development workflows

## 📝 Notes

- The system is optimized for long-running development sessions
- Memory system automatically manages context to prevent performance issues
- All skills are designed to work together for comprehensive development support
- Configuration follows professional software development practices

## 🤝 Contributing

If you have suggestions for improvements or find issues, please:

1. Create an issue in the GitHub repository
2. Submit a pull request with your improvements
3. Contact the maintainers for feature requests

---

**Built with ❤️ using OpenClaw**
EOF

# Make scripts executable
chmod +x "$DEPLOY_DIR/install.sh"
chmod +x "$DEPLOY_DIR/start.sh"

# Create deployment summary
cat > "$DEPLOY_DIR/DEPLOYMENT_SUMMARY.md" << 'EOF'
# Deployment Summary

## 🎯 Package Overview
- **Name**: OpenClaw FullStack Engineer
- **Version**: 1.0.0
- **Type**: Complete development environment deployment

## 📦 Included Components

### Core Configuration
- **IDENTITY.md**: AI identity as FullStack Engineer
- **SOUL.md**: Behavior principles and memory capabilities
- **USER.md**: User profile for full-stack developer
- **TOOLS.md**: Tool configuration and preferences
- **AGENTS.md**: Agent workspace configuration

### Specialized Skills
- **fullstack-dev/**: Complete full-stack development toolkit
- **conversation-memory/**: Advanced memory management system

### Automation Scripts
- **install.sh**: Automated installation script
- **start.sh**: Quick startup script

## 🚀 Deployment Steps

1. **Extract Package**: Deploy to desired location
2. **Run Installation**: `./install.sh`
3. **Start System**: `./start.sh`
4. **Begin Development**: `openclaw`

## 🔧 Requirements
- Node.js 18+
- npm (comes with Node.js)
- Git (for GitHub integration)
- 500MB+ free disk space

## 📊 Performance Characteristics
- Memory optimized for long conversations
- Context window automatically managed
- Skills designed for efficient operation
- Professional development workflow optimized

---

This deployment provides a complete, ready-to-use development environment with advanced AI capabilities for full-stack engineering.
EOF

# Create symbolic link for workspace
if [[ $EUID -eq 0 ]]; then
    # For root deployment, create system-wide link
    ln -sf "$DEPLOY_DIR" /root/.openclaw-workspace
else
    # For user deployment, create user link
    ln -sf "$DEPLOY_DIR" ~/.openclaw-workspace
fi

log_success "Deployment package created successfully!"
log_info "Location: $DEPLOY_DIR"
log_info "To install: cd $DEPLOY_DIR && ./install.sh"
log_info "To start: cd $DEPLOY_DIR && ./start.sh"

echo ""
echo "🎉 OpenClaw FullStack Engineer deployment package ready!"
echo "📁 Package location: $DEPLOY_DIR"
echo "🚀 Installation: cd $DEPLOY_DIR && ./install.sh"
echo "🎯 Startup: cd $DEPLOY_DIR && ./start.sh"