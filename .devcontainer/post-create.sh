#!/bin/bash

# Make script executable
chmod +x .devcontainer/post-create.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_compare() {
    local version1=$1
    local version2=$2
    if [[ "$(printf '%s\n' "$version2" "$version1" | sort -V | head -n1)" = "$version2" ]]; then
        return 0 # version1 >= version2
    else
        return 1 # version1 < version2
    fi
}

print_status "Starting development environment setup..."

# Update system packages
print_status "Updating system packages..."
sudo apt-get update -qq


# Check and install AWS CLI
if command_exists aws; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)
    print_warning "AWS CLI is already installed (version: $AWS_VERSION)"
else
    print_status "AWS CLI will be installed via devcontainer features"
fi

# Install additional tools (check each one)
print_status "Checking and installing additional tools..."

TOOLS_TO_INSTALL=""

if ! command_exists curl; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL curl"
fi

if ! command_exists wget; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL wget"
fi

if ! command_exists unzip; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL unzip"
fi

if ! command_exists jq; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL jq"
fi

if ! command_exists git; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL git"
fi

if [ -n "$TOOLS_TO_INSTALL" ]; then
    print_status "Installing missing tools:$TOOLS_TO_INSTALL"
    sudo apt-get install -y $TOOLS_TO_INSTALL
else
    print_status "All required system tools are already installed"
fi

# Check and install Python dependencies
print_status "Checking Python dependencies..."

PYTHON_PACKAGES=("boto3" "pytest" "requests")
PYTHON_TO_INSTALL=""

for package in "${PYTHON_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        PYTHON_TO_INSTALL="$PYTHON_TO_INSTALL $package"
    else
        print_warning "Python package '$package' is already installed"
    fi
done

if [ -n "$PYTHON_TO_INSTALL" ]; then
    print_status "Installing Python packages:$PYTHON_TO_INSTALL"
    pip3 install --user $PYTHON_TO_INSTALL
else
    print_status "All required Python packages are already installed"
fi

# Check and install Node.js dependencies
print_status "Checking Node.js dependencies..."

NODE_PACKAGES=("aws-sdk" "serverless @google/gemini-cli @anthropic-ai/claude-code @openai/codex")
NODE_TO_INSTALL=""

for package in "${NODE_PACKAGES[@]}"; do
    if ! npm list -g $package >/dev/null 2>&1; then
        NODE_TO_INSTALL="$NODE_TO_INSTALL $package"
    else
        print_warning "Node.js package '$package' is already installed globally"
    fi
done

if [ -n "$NODE_TO_INSTALL" ]; then
    print_status "Installing Node.js packages:$NODE_TO_INSTALL"
    npm install -g $NODE_TO_INSTALL
else
    print_status "All required Node.js packages are already installed"
fi

# Install flyctl
if [ -f "$HOME/.fly/bin/flyctl" ]; then
    print_warning "flyctl is already installed"
else
    print_status "Installing flyctl..."
    curl -L https://fly.io/install.sh | sh
fi

# Add flyctl to PATH if not already added
if ! grep -q "FLYCTL_INSTALL" ~/.bashrc; then
    print_status "Adding flyctl to PATH..."
    echo 'export FLYCTL_INSTALL="$HOME/.fly"' >> ~/.bashrc
    echo 'export PATH="$FLYCTL_INSTALL/bin:$PATH"' >> ~/.bashrc
fi

# Set for current session
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

# Create helper scripts directory
if [ ! -d "~/scripts" ]; then
    print_status "Creating scripts directory..."
    mkdir -p ~/scripts
else
    print_warning "Scripts directory already exists"
fi

# Make all scripts executable
if [ -d "./scripts" ]; then
    print_status "Making scripts executable..."
    chmod +x ./scripts/*.sh
fi

# Final version check and summary
print_status "=== Installation Summary ==="

if command_exists aws; then
    echo "✅ AWS CLI: $(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)"
else
    print_error "❌ AWS CLI: Not installed"
fi

if command_exists node; then
    echo "✅ Node.js: $(node --version)"
else
    print_error "❌ Node.js: Not installed"
fi

if command_exists python3; then
    echo "✅ Python: $(python3 --version | cut -d' ' -f2)"
else
    print_error "❌ Python: Not installed"
fi

if [ -f "$HOME/.fly/bin/flyctl" ]; then
    echo "✅ flyctl: $($HOME/.fly/bin/flyctl version 2>&1 | grep -o 'v[0-9.]*')"
else
    print_error "❌ flyctl: Not installed"
fi

# Install k6 load testing tool
if command_exists k6; then
    print_warning "k6 is already installed ($(k6 version | grep -o 'v[0-9.]*'))"
else
    print_status "Installing k6 load testing tool..."
    curl -L https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz | tar xvz --strip-components 1
    sudo mv k6 /usr/local/bin/k6
    print_status "k6 installed successfully"
fi

if command_exists k6; then
    echo "✅ k6: $(k6 version | grep -o 'v[0-9.]*')"
else
    print_error "❌ k6: Not installed"
fi

print_status "✅ Development environment setup complete!"