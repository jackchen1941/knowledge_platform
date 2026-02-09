# Knowledge API Implementation

## Overview

This document describes the implementation of the Knowledge Entry CRUD operations (Task 4.1).

## Components Implemented

### 1. Schemas (`app/schemas/knowledge.py`)

Pydantic models for request/response validation:

- **KnowledgeBase**: Base schema with common fields
- **KnowledgeCreate**: Schema for creating knowledge items
- **KnowledgeUpdate**: Schema for updating knowledge items  
- **KnowledgeDraft**: Schema for saving drafts (auto-save support)
- **KnowledgePublish**: Schema for publishing items
- **KnowledgeResponse**: Full response with all details
- **KnowledgeListItem**: Lighter response for list views
- **KnowledgeListResponse**: Paginated list response
- **KnowledgeFilter**: Filtering and pagination parameters
- **TagResponse**, **CategoryResponse**, **AttachmentResponse**, **VersionResponse**: Related entity responses

### 2. Service Layer (`app/services/knowledge.py`)

Business logic for knowledge management:

#### Core Operations

- **create_knowledge_item()**: Creates a new knowledge item with automatic version creation
  - Calculates word count and reading time
  - Handles tag attachment
  - Creates initial version snapshot
  
- **get_knowledge_item()**: Retrieves a knowledge item with permission checks
  - Increments view count
  - Loads related entities (tags, category, attachments)
  - Enforces visibility rules
  
- **list_knowledge_items()**: Lists knowledge items with filtering and pagination
  - Supports search across title, content, and summary
  - Filters by category, tags, visibility, publish status, source platform
  - Date range filtering
  - Sorting and pagination
  
- **update_knowledge_item()**: Updates a knowledge item
  - Creates version snapshot before updating
  - Recalculates word count and reading time
  - Handles tag updates
  - Permission checks (owner only)
  
- **save_draft()**: Saves draft changes without creating a version
  - Supports auto-save functionality
  - Marks item as unpublished
  - No version created for frequent saves
  
- **publish_knowledge_item()**: Publishes a knowledge item
  - Sets published status and timestamp
  - Creates version for publish action
  
- **delete_knowledge_item()**: Soft deletes a knowledge item
  - Moves to recycle bin
  - 30-day recovery period
  - Permission checks
  
- **restore_knowledge_item()**: Restores a soft-deleted item
  - Checks recovery period (30 days)
  - Creates version for restore action
  - Permission checks
  
- **get_deleted_items()**: Lists items in recycle bin
  - Shows only user's own deleted items
  - Paginated results
  
- **search_knowledge_items()**: Searches knowledge items
  - Full-text search in title, content, summary
  - Respects visibility rules

#### Helper Methods

- **_calculate_word_count()**: Calculates word count from content
- **_calculate_reading_time()**: Estimates reading time (200 words/min)
- **_attach_tags()**: Attaches tags to a knowledge item
- **_update_tags()**: Updates tags with proper usage count management

### 3. API Endpoints (`app/api/v1/endpoints/knowledge.py`)

RESTful API endpoints with authentication:

- **POST /api/v1/knowledge**: Create knowledge item
- **GET /api/v1/knowledge**: List knowledge items (with filtering)
- **GET /api/v1/knowledge/deleted**: Get recycle bin items
- **GET /api/v1/knowledge/search**: Search knowledge items
- **GET /api/v1/knowledge/{id}**: Get single knowledge item
- **PUT /api/v1/knowledge/{id}**: Update knowledge item
- **POST /api/v1/knowledge/{id}/draft**: Save draft (auto-save)
- **POST /api/v1/knowledge/{id}/publish**: Publish knowledge item
- **DELETE /api/v1/knowledge/{id}**: Soft delete knowledge item
- **POST /api/v1/knowledge/{id}/restore**: Restore deleted item

All endpoints:
- Require authentication (JWT token)
- Include proper error handling
- Return appropriate HTTP status codes
- Have comprehensive documentation

### 4. Exception Handling (`app/core/exceptions.py`)

Added **PermissionError** exception for permission-related errors.

## Features Implemented

### ✅ CRUD Operations
- Create knowledge items with automatic version creation
- Read with permission checks and view counting
- Update with automatic versioning
- Delete with soft-delete (30-day recovery)

### ✅ Rich Text Editor Support
- Support for markdown, HTML, and plain text
- Content type validation
- Word count and reading time calculation

### ✅ Auto-Save and Draft Functionality
- Draft endpoint for frequent saves without versioning
- Publish/unpublish workflow
- Draft state management

### ✅ Version Control
- Automatic version creation on create/update/publish/restore
- Version snapshots include title, content, metadata
- Change summaries and change types

### ✅ Permission Control
- Owner-only access for private items
- Visibility levels: private, shared, public
- Permission checks on all operations

### ✅ Advanced Features
- Full-text search
- Tag management with usage counting
- Category organization
- Soft delete with recovery period
- Recycle bin view
- Pagination and filtering
- Sorting options

## Requirements Satisfied

### Requirement 1.1: Knowledge Content Management
- ✅ Rich text editor support with Markdown format
- ✅ Create and edit knowledge entries

### Requirement 1.5: Auto-Save
- ✅ Auto-save functionality via draft endpoint
- ✅ Prevents data loss during editing

## API Usage Examples

### Create Knowledge Item
```bash
POST /api/v1/knowledge
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Knowledge Item",
  "content": "This is the content...",
  "content_type": "markdown",
  "summary": "Brief summary",
  "visibility": "private",
  "is_published": false,
  "tag_ids": ["tag-id-1", "tag-id-2"]
}
```

### List Knowledge Items
```bash
GET /api/v1/knowledge?search=python&page=1&page_size=20&sort_by=updated_at&sort_order=desc
Authorization: Bearer <token>
```

### Save Draft (Auto-Save)
```bash
POST /api/v1/knowledge/{id}/draft
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated title",
  "content": "Updated content..."
}
```

### Publish Knowledge Item
```bash
POST /api/v1/knowledge/{id}/publish
Authorization: Bearer <token>
```

### Delete Knowledge Item
```bash
DELETE /api/v1/knowledge/{id}
Authorization: Bearer <token>
```

### Restore Deleted Item
```bash
POST /api/v1/knowledge/{id}/restore
Authorization: Bearer <token>
```

## Testing

Comprehensive test suite created in `tests/test_knowledge_api.py` covering:
- Create, read, update, delete operations
- Draft saving
- Publishing workflow
- Soft delete and restore
- Recycle bin
- Search functionality
- Permission checks
- List and pagination

## Database Schema

The implementation uses the existing knowledge models:
- **KnowledgeItem**: Main knowledge entry table
- **KnowledgeVersion**: Version history table
- **Tag**: Tags for categorization
- **Category**: Hierarchical categories
- **Attachment**: File attachments

All models support:
- Soft delete with recovery period
- Version control
- Metadata storage
- Relationships and foreign keys

## Security

- JWT authentication required for all endpoints
- Permission checks enforce ownership rules
- Visibility controls (private/shared/public)
- Input validation and sanitization
- SQL injection prevention via ORM

## Performance Considerations

- Eager loading of relationships to avoid N+1 queries
- Pagination for large result sets
- Efficient filtering with database indexes
- Word count and reading time pre-calculated

## Next Steps

The knowledge CRUD API is complete and ready for:
1. Integration testing with frontend
2. Performance testing with large datasets
3. Property-based testing (Task 4.3)
4. Attachment upload implementation (Task 4.2)
5. Version history API endpoints (Task 4.4)
