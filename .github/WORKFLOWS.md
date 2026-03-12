# GitHub Workflows Documentation

This directory contains GitHub Actions workflows for the PCM project, implementing comprehensive CI/CD pipelines and automation.

## Workflows Overview

### 1. Backend CI (`backend-ci.yml`)
- **Triggers**: Push/PR to main/develop branches (backend changes)
- **Features**:
  - Multi-Python version testing (3.9, 3.10, 3.11)
  - PostgreSQL and Redis services
  - Code linting (flake8), formatting (black), type checking (mypy)
  - Test coverage reporting
  - Security scanning (safety, bandit, semgrep)
  - Docker image building and pushing

### 2. Frontend CI (`frontend-ci.yml`)
- **Triggers**: Push/PR to main/develop branches (frontend changes)
- **Features**:
  - Multi-Node.js version testing (18.x, 20.x)
  - ESLint, Prettier, TypeScript checking
  - Unit and component testing
  - E2E testing with Playwright
  - Accessibility testing
  - Docker image building and pushing

### 3. Integration Tests (`integration-tests.yml`)
- **Triggers**: Push/PR, daily schedule
- **Features**:
  - Full-stack integration testing
  - Mock Proxmox API with WireMock
  - Backend and frontend health checks
  - API integration testing
  - Full-stack E2E testing

### 4. Security Scan (`security-scan.yml`)
- **Triggers**: Push/PR, daily schedule
- **Features**:
  - Dependency vulnerability scanning
  - Code security analysis (Bandit, Semgrep)
  - Container vulnerability scanning (Trivy)
  - Secrets detection (TruffleHog)
  - CodeQL analysis
  - Security reporting and notifications

### 5. Performance Monitoring (`performance-monitoring.yml`)
- **Triggers**: Push/PR to main, weekly schedule
- **Features**:
  - Backend API performance testing (Locust)
  - Memory profiling
  - Database performance analysis
  - Frontend performance testing (Lighthouse)
  - Core Web Vitals measurement
  - Performance regression detection

### 6. Code Quality (`code-quality.yml`)
- **Triggers**: Push/PR to main/develop
- **Features**:
  - Python code quality (Black, isort, flake8, mypy, pylint)
  - Complexity analysis (radon, xenon)
  - JavaScript/TypeScript quality (ESLint, Prettier)
  - SonarCloud integration
  - Quality reporting and PR comments

### 7. Deploy (`deploy.yml`)
- **Triggers**: Push to main, tags, manual dispatch
- **Features**:
  - Container image building and publishing
  - Staging environment deployment
  - Production environment deployment
  - Smoke testing
  - GitHub releases
  - Slack notifications

## Required Secrets

Configure these secrets in your GitHub repository:

### Docker Registry
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password

### Kubernetes Deployment
- `KUBE_CONFIG_STAGING`: Base64 encoded kubeconfig for staging
- `KUBE_CONFIG_PRODUCTION`: Base64 encoded kubeconfig for production

### Code Quality
- `SONAR_TOKEN`: SonarCloud authentication token

### Notifications
- `SLACK_WEBHOOK`: Slack webhook URL for notifications

## Dependabot Configuration

The `dependabot.yml` file configures automatic dependency updates:
- Python dependencies (weekly, Mondays)
- Node.js dependencies (weekly, Mondays)
- GitHub Actions (weekly, Mondays)
- Docker base images (weekly, Tuesdays)

## Best Practices Implemented

1. **Multi-stage Docker builds** for optimized images
2. **Parallel job execution** for faster CI/CD
3. **Comprehensive testing** (unit, integration, E2E, property-based)
4. **Security-first approach** with multiple scanning tools
5. **Performance monitoring** and regression detection
6. **Code quality gates** with automated reporting
7. **Automated dependency management**
8. **Environment-specific deployments**
9. **Proper secret management**
10. **Comprehensive logging and artifact collection**