# 🔄 GitHub Workflow Guide / GitHub 工作流指南

## 📋 Overview / 概览

This guide explains how to set up and use the GitHub repository for the Knowledge Management Platform, including version control workflows, CI/CD pipelines, and release management.

## 🚀 Initial Repository Setup / 初始仓库设置

### 1. Create GitHub Repository / 创建 GitHub 仓库

```bash
# Create a new repository on GitHub
# Repository name: knowledge-management-platform
# Description: Modern enterprise-grade knowledge management platform
# Visibility: Public (or Private based on your needs)
# Initialize with: None (we'll push existing code)
```

### 2. Connect Local Repository / 连接本地仓库

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Complete Knowledge Management Platform v1.0.0

- ✅ Complete backend with FastAPI
- ✅ Complete frontend with React + TypeScript
- ✅ 14 core modules implemented
- ✅ 100% security tests passed
- ✅ Production-ready deployment configurations
- ✅ Comprehensive documentation"

# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/knowledge-management-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Set Up Branch Protection / 设置分支保护

Go to GitHub repository settings and configure:

```yaml
Branch Protection Rules for 'main':
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators
- Allow force pushes: false
- Allow deletions: false
```

## 🌿 Branching Strategy / 分支策略

### Branch Structure / 分支结构

```
main (production)           # 生产分支
├── develop (staging)       # 开发分支
├── feature/feature-name    # 功能分支
├── bugfix/bug-description  # 修复分支
├── hotfix/urgent-fix       # 热修复分支
└── release/v1.1.0          # 发布分支
```

### Branch Naming Convention / 分支命名规范

- **Feature branches**: `feature/add-ai-recommendations`
- **Bug fix branches**: `bugfix/fix-search-pagination`
- **Hotfix branches**: `hotfix/security-patch-jwt`
- **Release branches**: `release/v1.1.0`

### Workflow Process / 工作流程

1. **Feature Development / 功能开发**
   ```bash
   # Create feature branch from develop
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature-name
   
   # Develop and commit changes
   git add .
   git commit -m "feat: add new feature description"
   
   # Push feature branch
   git push origin feature/new-feature-name
   
   # Create Pull Request to develop branch
   ```

2. **Bug Fixes / 错误修复**
   ```bash
   # Create bugfix branch from develop
   git checkout develop
   git pull origin develop
   git checkout -b bugfix/fix-description
   
   # Fix and commit changes
   git add .
   git commit -m "fix: resolve issue description"
   
   # Push and create PR
   git push origin bugfix/fix-description
   ```

3. **Hotfixes / 热修复**
   ```bash
   # Create hotfix branch from main
   git checkout main
   git pull origin main
   git checkout -b hotfix/urgent-fix
   
   # Fix and commit
   git add .
   git commit -m "hotfix: urgent security fix"
   
   # Push and create PR to main
   git push origin hotfix/urgent-fix
   ```

## 🔄 CI/CD Pipeline / CI/CD 流水线

### Pipeline Stages / 流水线阶段

1. **Code Quality Checks / 代码质量检查**
   - Linting (ESLint, Pylint)
   - Type checking (TypeScript, mypy)
   - Code formatting (Prettier, Black)

2. **Testing / 测试**
   - Unit tests (Jest, pytest)
   - Integration tests
   - Security tests
   - Performance tests

3. **Build / 构建**
   - Backend Docker image
   - Frontend Docker image
   - Documentation build

4. **Security Scanning / 安全扫描**
   - Dependency vulnerability scan
   - Container image scan
   - Code security analysis

5. **Deployment / 部署**
   - Staging deployment (develop branch)
   - Production deployment (main branch)

### GitHub Actions Configuration / GitHub Actions 配置

The CI/CD pipeline is configured in `.github/workflows/ci.yml`:

```yaml
# Triggers
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

# Jobs
jobs:
  - test-backend      # Backend testing
  - test-frontend     # Frontend testing
  - docker-build      # Docker image building
  - security-scan     # Security scanning
  - deploy-staging    # Staging deployment
  - deploy-production # Production deployment
```

### Required Secrets / 必需的密钥

Configure these secrets in GitHub repository settings:

```bash
# Docker Hub credentials
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password

# Deployment credentials (if using cloud providers)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Database credentials for testing
TEST_DATABASE_URL=your-test-db-url

# Other service credentials
REDIS_URL=your-redis-url
```

## 📦 Release Management / 发布管理

### Version Numbering / 版本号规则

Following [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process / 发布流程

1. **Prepare Release / 准备发布**
   ```bash
   # Create release branch from develop
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.1.0
   
   # Update version numbers
   # Update CHANGELOG.md
   # Final testing
   
   git add .
   git commit -m "chore: prepare release v1.1.0"
   git push origin release/v1.1.0
   ```

2. **Create Release PR / 创建发布 PR**
   - Create PR from `release/v1.1.0` to `main`
   - Include release notes
   - Get approval from team

3. **Deploy to Production / 部署到生产**
   ```bash
   # Merge to main triggers production deployment
   git checkout main
   git merge release/v1.1.0
   git tag v1.1.0
   git push origin main --tags
   ```

4. **Create GitHub Release / 创建 GitHub 发布**
   - Go to GitHub Releases
   - Create new release with tag `v1.1.0`
   - Add release notes from CHANGELOG.md
   - Attach binaries if needed

5. **Merge Back to Develop / 合并回开发分支**
   ```bash
   git checkout develop
   git merge main
   git push origin develop
   ```

### Release Notes Template / 发布说明模板

```markdown
# Release v1.1.0

## 🎉 New Features
- Added AI-powered knowledge recommendations
- Implemented advanced search filters
- Added mobile responsive design

## 🐛 Bug Fixes
- Fixed search pagination issue
- Resolved WebSocket connection drops
- Fixed category deletion cascade

## 🔒 Security Updates
- Updated JWT token validation
- Enhanced input sanitization
- Fixed XSS vulnerability in comments

## ⚡ Performance Improvements
- Optimized database queries
- Reduced bundle size by 20%
- Improved API response times

## 📚 Documentation
- Updated API documentation
- Added deployment troubleshooting guide
- Improved README with examples

## 🔄 Breaking Changes
- None in this release

## 📊 Statistics
- 15 commits
- 3 contributors
- 5 issues closed
- 2 security fixes
```

## 🤝 Contribution Workflow / 贡献工作流

### For Contributors / 贡献者指南

1. **Fork Repository / Fork 仓库**
   ```bash
   # Fork on GitHub, then clone
   git clone https://github.com/YOUR_USERNAME/knowledge-management-platform.git
   cd knowledge-management-platform
   
   # Add upstream remote
   git remote add upstream https://github.com/ORIGINAL_OWNER/knowledge-management-platform.git
   ```

2. **Create Feature Branch / 创建功能分支**
   ```bash
   # Sync with upstream
   git checkout develop
   git pull upstream develop
   
   # Create feature branch
   git checkout -b feature/your-feature-name
   ```

3. **Develop and Test / 开发和测试**
   ```bash
   # Make changes
   # Run tests locally
   npm test                    # Frontend tests
   python -m pytest tests/    # Backend tests
   
   # Commit changes
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Submit Pull Request / 提交 Pull Request**
   ```bash
   # Push to your fork
   git push origin feature/your-feature-name
   
   # Create PR on GitHub from your fork to upstream/develop
   ```

### Code Review Process / 代码审查流程

1. **Automated Checks / 自动检查**
   - CI/CD pipeline runs automatically
   - All tests must pass
   - Security scans must pass
   - Code coverage requirements met

2. **Manual Review / 人工审查**
   - At least 1 reviewer approval required
   - Code quality and style review
   - Architecture and design review
   - Documentation review

3. **Merge Requirements / 合并要求**
   - All CI checks pass ✅
   - At least 1 approval ✅
   - No merge conflicts ✅
   - Branch up to date ✅

## 🏷️ Issue Management / 问题管理

### Issue Labels / 问题标签

```yaml
Type Labels:
- bug          # Bug reports
- enhancement  # Feature requests
- documentation # Documentation improvements
- question     # Questions and support

Priority Labels:
- priority/low    # Low priority
- priority/medium # Medium priority
- priority/high   # High priority
- priority/urgent # Urgent fixes

Status Labels:
- status/triage      # Needs triage
- status/in-progress # Being worked on
- status/blocked     # Blocked by dependencies
- status/ready       # Ready for work

Component Labels:
- backend    # Backend related
- frontend   # Frontend related
- deployment # Deployment related
- security   # Security related
```

### Issue Templates / 问题模板

Pre-configured templates available:
- **Bug Report**: `.github/ISSUE_TEMPLATE/bug_report.md`
- **Feature Request**: `.github/ISSUE_TEMPLATE/feature_request.md`

## 📊 Project Management / 项目管理

### GitHub Projects / GitHub 项目

Set up GitHub Projects for tracking:

1. **Development Board / 开发看板**
   - Backlog
   - In Progress
   - In Review
   - Done

2. **Release Planning / 发布计划**
   - Next Release
   - Future Releases
   - Ideas

### Milestones / 里程碑

Create milestones for major releases:
- **v1.1.0** - AI Features
- **v1.2.0** - Mobile Support
- **v2.0.0** - Major Architecture Update

## 🔍 Monitoring and Analytics / 监控和分析

### Repository Insights / 仓库洞察

Monitor these metrics:
- **Code frequency** - Commit activity
- **Contributors** - Active contributors
- **Traffic** - Repository views and clones
- **Issues** - Open/closed issue trends
- **Pull requests** - PR merge rates

### Quality Metrics / 质量指标

Track these quality indicators:
- **Test coverage** - Maintain >80%
- **Security alerts** - Address promptly
- **Dependency updates** - Keep dependencies current
- **Performance** - Monitor build times

## 🛠️ Tools and Integrations / 工具和集成

### Recommended Tools / 推荐工具

1. **Development / 开发**
   - VS Code with GitHub extension
   - GitHub Desktop (for GUI users)
   - GitHub CLI (`gh` command)

2. **Project Management / 项目管理**
   - GitHub Projects
   - GitHub Milestones
   - GitHub Issues

3. **Quality Assurance / 质量保证**
   - Codecov for coverage
   - Dependabot for dependencies
   - GitHub Security Advisories

### GitHub CLI Usage / GitHub CLI 使用

```bash
# Install GitHub CLI
# macOS: brew install gh
# Windows: winget install GitHub.cli

# Authenticate
gh auth login

# Common commands
gh repo clone owner/repo
gh pr create --title "Feature: Add new functionality"
gh pr list
gh pr merge 123
gh issue create --title "Bug: Fix search issue"
gh release create v1.1.0
```

## 📚 Best Practices / 最佳实践

### Commit Messages / 提交信息

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: type(scope): description
feat(auth): add OAuth2 integration
fix(search): resolve pagination bug
docs(api): update endpoint documentation
style(frontend): fix linting issues
refactor(backend): optimize database queries
test(auth): add unit tests for login
chore(deps): update dependencies
```

### Pull Request Guidelines / Pull Request 指南

1. **Title**: Clear and descriptive
2. **Description**: Explain what and why
3. **Testing**: Include test results
4. **Screenshots**: For UI changes
5. **Breaking Changes**: Clearly marked
6. **Documentation**: Update if needed

### Security Considerations / 安全考虑

1. **Never commit secrets** - Use GitHub Secrets
2. **Review dependencies** - Check for vulnerabilities
3. **Enable security alerts** - Monitor for issues
4. **Use signed commits** - Verify authenticity
5. **Regular security audits** - Schedule reviews

---

## 🎯 Quick Reference / 快速参考

### Common Commands / 常用命令

```bash
# Setup
git clone https://github.com/owner/knowledge-management-platform.git
cd knowledge-management-platform
git checkout develop

# Feature development
git checkout -b feature/new-feature
# ... make changes ...
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create PR via GitHub CLI
gh pr create --base develop --title "Feature: New functionality"

# Release
git checkout main
git tag v1.1.0
git push origin main --tags
gh release create v1.1.0 --generate-notes
```

### Useful Links / 有用链接

- **Repository**: https://github.com/owner/knowledge-management-platform
- **Issues**: https://github.com/owner/knowledge-management-platform/issues
- **Pull Requests**: https://github.com/owner/knowledge-management-platform/pulls
- **Actions**: https://github.com/owner/knowledge-management-platform/actions
- **Releases**: https://github.com/owner/knowledge-management-platform/releases
- **Wiki**: https://github.com/owner/knowledge-management-platform/wiki

---

**Last Updated**: 2024-02-09  
**Version**: 1.0.0  
**Maintainer**: Knowledge Platform Team