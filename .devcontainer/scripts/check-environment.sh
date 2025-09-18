#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "✅ ${GREEN}$1${NC}"
}

print_error() {
    echo -e "❌ ${RED}$1${NC}"
}

print_warning() {
    echo -e "⚠️  ${YELLOW}$1${NC}"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_header "Development Environment Status Check"

# Check core tools
echo -e "\n${BLUE}Core Tools:${NC}"
if command_exists sam; then
    print_success "AWS SAM CLI: $(sam --version)"
else
    print_error "AWS SAM CLI: Not installed"
fi

if command_exists aws; then
    print_success "AWS CLI: $(aws --version 2>&1)"
else
    print_error "AWS CLI: Not installed"
fi

if command_exists docker; then
    print_success "Docker: $(docker --version)"
else
    print_error "Docker: Not installed"
fi

if command_exists docker-compose; then
    print_success "Docker Compose: $(docker-compose --version)"
else
    print_error "Docker Compose: Not installed"
fi

# Check language runtimes
echo -e "\n${BLUE}Language Runtimes:${NC}"
if command_exists node; then
    print_success "Node.js: $(node --version)"
    print_success "NPM: $(npm --version)"
else
    print_error "Node.js: Not installed"
fi

if command_exists python3; then
    print_success "Python: $(python3 --version)"
    print_success "Pip: $(pip3 --version)"
else
    print_error "Python: Not installed"
fi

# Check Python packages
echo -e "\n${BLUE}Python Packages:${NC}"
PYTHON_PACKAGES=("boto3" "pytest" "requests")
for package in "${PYTHON_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        VERSION=$(python3 -c "import $package; print($package.__version__)" 2>/dev/null || echo "unknown")
        print_success "$package: $VERSION"
    else
        print_error "$package: Not installed"
    fi
done

# Check Node.js packages
echo -e "\n${BLUE}Node.js Global Packages:${NC}"
NODE_PACKAGES=("aws-sdk" "serverless")
for package in "${NODE_PACKAGES[@]}"; do
    if npm list -g $package >/dev/null 2>&1; then
        VERSION=$(npm list -g $package --depth=0 2>/dev/null | grep $package | cut -d'@' -f2 || echo "unknown")
        print_success "$package: $VERSION"
    else
        print_error "$package: Not installed globally"
    fi
done

# Check Docker services status
echo -e "\n${BLUE}Docker Services Status:${NC}"
if command_exists docker-compose; then
    if [ -f "docker-compose.yml" ]; then
        SERVICES=$(docker-compose ps --services 2>/dev/null || echo "")
        if [ -n "$SERVICES" ]; then
            for service in $SERVICES; do
                STATUS=$(docker-compose ps $service --format "table {{.State}}" 2>/dev/null | tail -n +2)
                if [[ "$STATUS" == *"Up"* ]]; then
                    print_success "Service $service: Running"
                else
                    print_warning "Service $service: $STATUS"
                fi
            done
        else
            print_warning "No Docker services defined or running"
        fi
    else
        print_warning "No docker-compose.yml found"
    fi
fi

echo -e "\n${BLUE}Environment Check Complete!${NC}"