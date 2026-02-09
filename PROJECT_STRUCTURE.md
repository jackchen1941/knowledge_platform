# 📁 Project Structure / 项目结构

## 🏗️ Overview / 概览

This document provides a comprehensive overview of the Knowledge Management Platform project structure.

```
knowledge-management-platform/
├── 📁 .github/                    # GitHub configuration
│   ├── 📁 ISSUE_TEMPLATE/         # Issue templates
│   ├── 📁 workflows/              # CI/CD workflows
│   └── 📄 pull_request_template.md
├── 📁 backend/                    # Backend application
│   ├── 📁 alembic/               # Database migrations
│   ├── 📁 app/                   # Main application code
│   │   ├── 📁 api/               # API endpoints
│   │   ├── 📁 core/              # Core functionality
│   │   ├── 📁 models/            # Database models
│   │   ├── 📁 schemas/           # Pydantic schemas
│   │   └── 📁 services/          # Business logic
│   ├── 📁 tests/                 # Test files
│   ├── 📄 Dockerfile             # Docker configuration
│   ├── 📄 requirements.txt       # Python dependencies
│   └── 📄 pyproject.toml         # Python project config
├── 📁 frontend/                   # Frontend application
│   ├── 📁 public/                # Static files
│   ├── 📁 src/                   # Source code
│   │   ├── 📁 components/        # React components
│   │   ├── 📁 pages/             # Page components
│   │   ├── 📁 services/          # API services
│   │   ├── 📁 store/             # Redux store
│   │   └── 📁 types/             # TypeScript types
│   ├── 📄 Dockerfile             # Docker configuration
│   ├── 📄 package.json           # Node.js dependencies
│   └── 📄 tsconfig.json          # TypeScript config
├── 📁 deployment/                 # Deployment configurations
│   ├── 📁 docker-compose/        # Docker Compose files
│   ├── 📁 kubernetes/            # Kubernetes manifests
│   ├── 📁 helm-chart/            # Helm chart
│   └── 📁 scripts/               # Deployment scripts
├── 📁 docs/                      # Documentation
│   ├── 📁 implementation/        # Technical implementation docs
│   ├── 📁 progress/              # Project progress reports
│   ├── 📄 README.md              # Documentation index
│   └── 📄 PROJECT_COMPLETE_DOCUMENTATION.md
├── 📄 run_tests.py               # Test runner script
├── 📁 tests/                     # Test suites
│   ├── 📁 integration/           # Integration tests
│   │   ├── test_all_features.py  # Complete feature tests
│   │   ├── test_auth_complete.py # Complete auth tests
│   │   ├── test_knowledge_complete.py # Knowledge tests
│   │   └── test_simple.py        # Simple integration tests
│   ├── 📁 security/              # Security tests
│   │   └── test_security_comprehensive.py # Security test suite
│   ├── 📁 system/                # System tests
│   │   ├── test_system.py        # System functionality tests
│   │   ├── optimize_and_finalize.py # Performance optimization
│   │   └── validate_database.py  # Database validation
│   ├── 📁 features/              # Feature tests
│   │   ├── test_auth.py          # Authentication tests
│   │   ├── test_websocket.py     # WebSocket tests
│   │   ├── test_sync_feature.py  # Sync functionality tests
│   │   └── ... (other feature tests)
│   └── 📄 README.md              # Test documentation
├── 📄 README.md                  # Main project documentation
├── 📄 README_QUICKSTART.md       # Quick start guide
├── 📄 DEPLOYMENT_GUIDE.md        # Deployment guide
├── 📄 CHANGELOG.md               # Version history
├── 📄 LICENSE                    # MIT License
├── 📄 .gitignore                 # Git ignore rules
├── 📄 quick-start.sh             # Unix/Linux quick start
├── 📄 quick-start.bat            # Windows quick start
└── 📄 docker-compose.yml         # Main Docker Compose
```

## 🔧 Backend Structure / 后端结构

### 📁 app/ - Main Application
```
app/
├── 📁 api/v1/                    # API version 1
│   ├── 📄 api.py                 # Main API router
│   └── 📁 endpoints/             # API endpoints
│       ├── 📄 auth.py            # Authentication
│       ├── 📄 knowledge.py       # Knowledge management
│       ├── 📄 search.py          # Search functionality
│       ├── 📄 categories.py      # Categories & tags
│       ├── 📄 sync.py            # Multi-device sync
│       ├── 📄 notifications.py   # Notifications
│       ├── 📄 websocket.py       # WebSocket
│       ├── 📄 attachments.py     # File attachments
│       ├── 📄 analytics.py       # Analytics
│       └── 📄 import_export.py   # Import/Export
├── 📁 core/                      # Core functionality
│   ├── 📄 config.py              # Configuration
│   ├── 📄 database.py            # Database setup
│   ├── 📄 security.py            # Security features
│   ├── 📄 websocket.py           # WebSocket manager
│   └── 📄 middleware.py          # Middleware
├── 📁 models/                    # SQLAlchemy models
│   ├── 📄 user.py                # User model
│   ├── 📄 knowledge.py           # Knowledge model
│   ├── 📄 category.py            # Category model
│   ├── 📄 tag.py                 # Tag model
│   ├── 📄 sync.py                # Sync models
│   ├── 📄 notification.py        # Notification model
│   └── 📄 attachment.py          # Attachment model
├── 📁 schemas/                   # Pydantic schemas
│   ├── 📄 auth.py                # Auth schemas
│   ├── 📄 knowledge.py           # Knowledge schemas
│   ├── 📄 search.py              # Search schemas
│   └── 📄 ...                    # Other schemas
└── 📁 services/                  # Business logic
    ├── 📄 auth.py                # Auth service
    ├── 📄 knowledge.py           # Knowledge service
    ├── 📄 search.py              # Search service
    ├── 📄 sync.py                # Sync service
    ├── 📄 notification.py        # Notification service
    └── 📁 adapters/              # Import adapters
        ├── 📄 base.py            # Base adapter
        ├── 📄 notion_adapter.py  # Notion import
        ├── 📄 markdown_adapter.py # Markdown import
        └── 📄 ...                # Other adapters
```

### 🧪 Testing Structure
```
tests/
├── 📄 conftest.py                # Test configuration
├── 📄 test_auth.py               # Auth tests
├── 📄 test_knowledge.py          # Knowledge tests
├── 📄 test_search.py             # Search tests
└── 📄 ...                        # Other test files
```

## 🎨 Frontend Structure / 前端结构

### 📁 src/ - Source Code
```
src/
├── 📁 components/                # Reusable components
│   ├── 📁 layout/                # Layout components
│   ├── 📁 common/                # Common components
│   └── 📁 forms/                 # Form components
├── 📁 pages/                     # Page components
│   ├── 📁 auth/                  # Authentication pages
│   ├── 📁 knowledge/             # Knowledge pages
│   ├── 📁 search/                # Search pages
│   ├── 📁 categories/            # Category pages
│   ├── 📁 tags/                  # Tag pages
│   ├── 📁 sync/                  # Sync pages
│   ├── 📁 notifications/         # Notification pages
│   ├── 📁 analytics/             # Analytics pages
│   ├── 📁 settings/              # Settings pages
│   └── 📁 websocket/             # WebSocket test pages
├── 📁 services/                  # API services
│   └── 📄 api.ts                 # Main API client
├── 📁 store/                     # Redux store
│   ├── 📄 index.ts               # Store configuration
│   └── 📁 slices/                # Redux slices
│       ├── 📄 authSlice.ts       # Auth state
│       ├── 📄 knowledgeSlice.ts  # Knowledge state
│       └── 📄 uiSlice.ts         # UI state
├── 📁 hooks/                     # Custom hooks
│   ├── 📄 redux.ts               # Redux hooks
│   └── 📄 useWebSocket.ts        # WebSocket hook
├── 📁 types/                     # TypeScript types
│   └── 📄 auth.ts                # Auth types
├── 📁 styles/                    # CSS styles
│   └── 📄 index.css              # Main styles
├── 📄 App.tsx                    # Main App component
└── 📄 index.tsx                  # Entry point
```

## 🚀 Deployment Structure / 部署结构

### 📁 deployment/ - Deployment Configurations
```
deployment/
├── 📄 docker-compose.auto.yml    # Auto-configured Docker Compose
├── 📄 docker-compose.mysql.yml   # MySQL Docker Compose
├── 📄 docker-compose.sqlite.yml  # SQLite Docker Compose
├── 📄 docker-compose.mongodb.yml # MongoDB Docker Compose
├── 📁 kubernetes/                # Kubernetes manifests
│   ├── 📄 namespace.yaml         # Namespace
│   ├── 📄 configmap.yaml         # Configuration
│   ├── 📄 secrets.yaml           # Secrets
│   ├── 📄 backend-deployment.yaml # Backend deployment
│   ├── 📄 frontend-deployment.yaml # Frontend deployment
│   ├── 📄 mysql-deployment.yaml  # MySQL deployment
│   ├── 📄 redis-deployment.yaml  # Redis deployment
│   └── 📄 ingress.yaml           # Ingress
├── 📁 helm-chart/                # Helm chart
│   ├── 📄 Chart.yaml             # Chart metadata
│   ├── 📄 values.yaml            # Default values
│   └── 📁 templates/             # Kubernetes templates
├── 📁 scripts/                   # Deployment scripts
│   └── 📄 deploy.sh              # Deployment script
└── 📁 windows/                   # Windows deployment
    └── 📄 install.bat            # Windows installer
```

## 📚 Documentation Structure / 文档结构

### 📁 docs/ - Documentation
```
docs/
├── 📄 README.md                  # Documentation index
├── 📄 PROJECT_COMPLETE_DOCUMENTATION.md # Complete docs
├── 📄 development.md             # Development guide
├── 📁 implementation/            # Implementation details
│   ├── 📄 AUTHENTICATION_IMPLEMENTATION.md
│   ├── 📄 KNOWLEDGE_MODELS_IMPLEMENTATION.md
│   ├── 📄 KNOWLEDGE_API_IMPLEMENTATION.md
│   ├── 📄 ATTACHMENT_IMPLEMENTATION.md
│   ├── 📄 TAG_CATEGORY_IMPLEMENTATION.md
│   ├── 📄 SEARCH_IMPLEMENTATION.md
│   ├── 📄 EXPORT_ANALYTICS_IMPLEMENTATION.md
│   ├── 📄 EXTERNAL_IMPORT_IMPLEMENTATION.md
│   ├── 📄 FRONTEND_IMPLEMENTATION.md
│   ├── 📄 WEBSOCKET_IMPLEMENTATION_COMPLETE.md
│   ├── 📄 NOTIFICATION_SYSTEM_COMPLETE.md
│   ├── 📄 SYNC_FEATURE_COMPLETE.md
│   ├── 📄 IMPORT_FEATURE_COMPLETE.md
│   └── 📄 KNOWLEDGE_GRAPH_BACKUP_IMPLEMENTATION.md
└── 📁 progress/                  # Progress reports
    ├── 📄 PROJECT_PROGRESS.md    # Overall progress
    └── 📄 FINAL_PROJECT_COMPLETION_REPORT.md # Final report
```

## 🔧 Configuration Files / 配置文件

### Root Level Configuration
- **📄 .gitignore** - Git ignore rules
- **📄 .env.example** - Environment variables template
- **📄 docker-compose.yml** - Main Docker Compose
- **📄 LICENSE** - MIT License
- **📄 PROJECT_STRUCTURE.md** - This file

### Backend Configuration
- **📄 backend/pyproject.toml** - Python project configuration
- **📄 backend/requirements.txt** - Python dependencies
- **📄 backend/requirements-dev.txt** - Development dependencies
- **📄 backend/alembic.ini** - Database migration configuration
- **📄 backend/.env.example** - Backend environment template

### Frontend Configuration
- **📄 frontend/package.json** - Node.js dependencies
- **📄 frontend/tsconfig.json** - TypeScript configuration
- **📄 frontend/.eslintrc.js** - ESLint configuration
- **📄 frontend/.prettierrc** - Prettier configuration

## 🎯 Key Features by Directory / 目录功能说明

### 🔐 Authentication & Security
- **Location**: `backend/app/api/v1/endpoints/auth.py`, `backend/app/services/auth.py`
- **Features**: JWT authentication, password hashing, security middleware

### 📚 Knowledge Management
- **Location**: `backend/app/api/v1/endpoints/knowledge.py`, `frontend/src/pages/knowledge/`
- **Features**: CRUD operations, version control, Markdown support

### 🔍 Search & Discovery
- **Location**: `backend/app/api/v1/endpoints/search.py`, `frontend/src/pages/search/`
- **Features**: Full-text search, suggestions, filtering

### 🏷️ Categories & Tags
- **Location**: `backend/app/api/v1/endpoints/categories.py`, `frontend/src/pages/categories/`
- **Features**: Hierarchical categories, colored tags

### 🔄 Multi-device Sync
- **Location**: `backend/app/api/v1/endpoints/sync.py`, `frontend/src/pages/sync/`
- **Features**: Device registration, data synchronization, conflict resolution

### 🔔 Notifications
- **Location**: `backend/app/api/v1/endpoints/notifications.py`, `frontend/src/pages/notifications/`
- **Features**: Real-time notifications, templates, preferences

### 🌐 WebSocket Communication
- **Location**: `backend/app/api/v1/endpoints/websocket.py`, `frontend/src/hooks/useWebSocket.ts`
- **Features**: Real-time messaging, room subscriptions, connection management

### 📤 Import/Export
- **Location**: `backend/app/api/v1/endpoints/import_export.py`, `backend/app/services/adapters/`
- **Features**: Multiple format support, batch processing, data conversion

### 🗂️ Attachments
- **Location**: `backend/app/api/v1/endpoints/attachments.py`, `backend/app/services/attachment.py`
- **Features**: File upload/download, security validation, metadata management

### 📊 Analytics
- **Location**: `backend/app/api/v1/endpoints/analytics.py`, `frontend/src/pages/analytics/`
- **Features**: Usage statistics, performance monitoring, data visualization

## 🚀 Quick Navigation / 快速导航

### For New Developers / 新开发者
1. Start with **[README.md](README.md)** for project overview
2. Follow **[README_QUICKSTART.md](README_QUICKSTART.md)** for setup
3. Read **[docs/development.md](docs/development.md)** for development guidelines
4. Browse **[docs/implementation/](docs/implementation/)** for technical details

### For DevOps Engineers / 运维工程师
1. Check **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for deployment options
2. Use **[deployment/](deployment/)** folder for configurations
3. Review **[docs/PROJECT_COMPLETE_DOCUMENTATION.md](docs/PROJECT_COMPLETE_DOCUMENTATION.md)** for technical specs

### For Project Managers / 项目经理
1. Review **[docs/progress/FINAL_PROJECT_COMPLETION_REPORT.md](docs/progress/FINAL_PROJECT_COMPLETION_REPORT.md)** for project status
2. Check **[CHANGELOG.md](CHANGELOG.md)** for version history
3. Browse **[docs/progress/](docs/progress/)** for progress reports

---

**Last Updated**: 2024-02-09  
**Version**: 1.0.0  
**Maintainer**: Knowledge Platform Team