# Attachment Management Implementation

## Overview

This document describes the implementation of the attachment upload and management system for the Knowledge Management Platform. The system supports multiple file types, automatic processing, deduplication, and secure file handling.

## Features Implemented

### 1. File Upload and Storage

- **Multi-format Support**: Images (JPEG, PNG, GIF, WebP), Documents (PDF, Word, Text, Markdown), Audio (MP3, WAV), Video (MP4, WebM)
- **File Validation**: MIME type checking, file size limits, filename sanitization
- **Secure Storage**: Organized directory structure by file type
- **Unique Filenames**: UUID-based naming to prevent conflicts

### 2. File Processing

- **Image Processing**:
  - Automatic dimension detection
  - Thumbnail generation (300x300 max)
  - Format conversion for thumbnails (JPEG)
  
- **File Deduplication**:
  - SHA-256 hash calculation
  - Duplicate detection before storage
  - Reference to existing files instead of re-uploading

### 3. API Endpoints

#### Upload Endpoints

- `POST /api/v1/knowledge/{id}/attachments` - Upload single file
- `POST /api/v1/knowledge/{id}/attachments/batch` - Upload multiple files

#### Retrieval Endpoints

- `GET /api/v1/knowledge/{id}/attachments` - List attachments for knowledge item
- `GET /api/v1/attachments` - List all user attachments
- `GET /api/v1/attachments/{id}` - Get attachment metadata
- `GET /api/v1/attachments/{id}/download` - Download attachment file

#### Management Endpoints

- `PUT /api/v1/attachments/{id}` - Update attachment metadata
- `DELETE /api/v1/attachments/{id}` - Delete attachment
- `GET /api/v1/attachments/stats/summary` - Get attachment statistics

### 4. Security Features

- **Authentication**: All endpoints require valid JWT token
- **Authorization**: Users can only access their own attachments or public ones
- **Permission Checks**: Verify ownership before upload/delete operations
- **Filename Sanitization**: Remove dangerous characters and path traversal attempts
- **File Type Validation**: Whitelist of allowed MIME types
- **Size Limits**: Configurable maximum file size (default 50MB)

### 5. Storage Organization

```
uploads/
├── images/          # Image files
├── videos/          # Video files
├── audio/           # Audio files
├── documents/       # Document files
├── others/          # Other file types
├── thumbnails/      # Generated thumbnails
└── temp/           # Temporary upload location
```

## Database Schema

### Attachment Model

```python
class Attachment:
    id: str                    # UUID primary key
    filename: str              # Display filename
    original_filename: str     # Original upload filename
    file_path: str            # Relative path to file
    mime_type: str            # MIME type
    file_size: int            # Size in bytes
    file_hash: str            # SHA-256 hash for deduplication
    width: int                # Image/video width (optional)
    height: int               # Image/video height (optional)
    duration: int             # Audio/video duration in seconds (optional)
    knowledge_item_id: str    # Foreign key to knowledge item
    uploaded_by: str          # Foreign key to user
    is_processed: bool        # Processing status
    is_public: bool           # Public access flag
    uploaded_at: datetime     # Upload timestamp
    processed_at: datetime    # Processing completion timestamp
```

## Configuration

### Environment Variables

```bash
# File Storage
UPLOAD_DIR=./uploads                    # Upload directory path
MAX_FILE_SIZE=52428800                  # Max file size (50MB)

# Allowed file types (comma-separated MIME types)
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,image/webp,application/pdf,text/plain,text/markdown,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,audio/mpeg,audio/wav,video/mp4,video/webm
```

## Usage Examples

### Upload a File

```bash
curl -X POST \
  http://localhost:8000/api/v1/knowledge/{knowledge_item_id}/attachments \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/image.jpg"
```

### Upload Multiple Files

```bash
curl -X POST \
  http://localhost:8000/api/v1/knowledge/{knowledge_item_id}/attachments/batch \
  -H "Authorization: Bearer {token}" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/document.pdf"
```

### Download a File

```bash
curl -X GET \
  http://localhost:8000/api/v1/attachments/{attachment_id}/download \
  -H "Authorization: Bearer {token}" \
  -o downloaded_file.jpg
```

### List Attachments

```bash
# List all attachments for a knowledge item
curl -X GET \
  http://localhost:8000/api/v1/knowledge/{knowledge_item_id}/attachments \
  -H "Authorization: Bearer {token}"

# Filter by type
curl -X GET \
  "http://localhost:8000/api/v1/knowledge/{knowledge_item_id}/attachments?mime_type_filter=image" \
  -H "Authorization: Bearer {token}"
```

### Get Statistics

```bash
curl -X GET \
  "http://localhost:8000/api/v1/attachments/stats/summary?knowledge_item_id={id}" \
  -H "Authorization: Bearer {token}"
```

## Service Layer

### AttachmentService

The `AttachmentService` class provides the business logic for attachment management:

**Key Methods:**

- `upload_file()` - Handle file upload with validation and processing
- `get_attachment()` - Retrieve attachment metadata with permission check
- `get_attachment_file_path()` - Get file system path for download
- `list_attachments()` - List attachments with filtering and pagination
- `update_attachment()` - Update attachment metadata
- `delete_attachment()` - Delete attachment and file
- `get_attachment_stats()` - Calculate attachment statistics

**Internal Methods:**

- `_validate_file()` - Validate file before upload
- `_calculate_file_hash()` - Calculate SHA-256 hash
- `_sanitize_filename()` - Remove unsafe characters
- `_generate_unique_filename()` - Create unique filename
- `_get_image_dimensions()` - Extract image dimensions
- `_generate_thumbnail()` - Create thumbnail for images
- `_check_duplicate()` - Check for duplicate files
- `_verify_knowledge_item_access()` - Verify user permissions

## Error Handling

The system handles various error conditions:

- **ValidationError**: Invalid file type, size exceeded, invalid filename
- **NotFoundError**: Attachment or knowledge item not found
- **PermissionError**: Unauthorized access attempt
- **IOError**: File system errors during upload/download

## Testing

Comprehensive test suite covers:

- Single and batch file uploads
- File type validation
- File size limits
- Duplicate detection
- Image thumbnail generation
- Download functionality
- Permission checks
- Metadata updates
- File deletion
- Statistics calculation

Run tests:

```bash
cd backend
pytest tests/test_attachment_api.py -v
```

## Performance Considerations

1. **File Hashing**: Calculated once during upload for deduplication
2. **Thumbnail Generation**: Performed synchronously but could be moved to background task
3. **Storage**: Files organized by type for better file system performance
4. **Database Queries**: Indexed on knowledge_item_id and uploaded_by for fast lookups

## Future Enhancements

1. **Background Processing**: Move thumbnail generation to Celery tasks
2. **Cloud Storage**: Support for S3/MinIO object storage
3. **Video Processing**: Extract video thumbnails and metadata
4. **Audio Processing**: Extract audio metadata (duration, bitrate)
5. **Image Optimization**: Automatic compression for large images
6. **CDN Integration**: Serve files through CDN for better performance
7. **Virus Scanning**: Integrate antivirus scanning for uploaded files
8. **Quota Management**: Per-user storage quotas
9. **Bulk Operations**: Bulk delete, bulk download (zip)
10. **Version Control**: Keep multiple versions of attachments

## Dependencies

- **Pillow**: Image processing and thumbnail generation
- **python-magic**: MIME type detection (optional, falls back to mimetypes)
- **FastAPI**: Web framework and file upload handling
- **SQLAlchemy**: Database ORM
- **aiofiles**: Async file operations (future enhancement)

## Compliance

The implementation follows security best practices:

- Input validation and sanitization
- Authentication and authorization
- Secure file storage
- No path traversal vulnerabilities
- MIME type validation
- File size limits
- Safe filename handling
