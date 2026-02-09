"""
Tests for Attachment API

Tests file upload, download, and management functionality.
"""

import io
import os
import pytest
from pathlib import Path
from PIL import Image
from fastapi import status
from httpx import AsyncClient

from app.core.config import get_settings

settings = get_settings()


@pytest.fixture
def test_image_file():
    """Create a test image file in memory."""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def test_text_file():
    """Create a test text file in memory."""
    content = b"This is a test document for attachment testing."
    return io.BytesIO(content)


@pytest.fixture
def test_pdf_file():
    """Create a simple test PDF file in memory."""
    # Simple PDF content (minimal valid PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000317 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF"""
    return io.BytesIO(pdf_content)


@pytest.mark.asyncio
async def test_upload_image_attachment(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file
):
    """Test uploading an image attachment."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    files = {
        "file": ("test_image.jpg", test_image_file, "image/jpeg")
    }
    
    response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert "attachment" in data
    assert data["attachment"]["filename"] == "test_image.jpg"
    assert data["attachment"]["mime_type"] == "image/jpeg"
    assert data["attachment"]["is_image"] is True
    assert data["attachment"]["width"] == 100
    assert data["attachment"]["height"] == 100
    assert data["is_duplicate"] is False
    assert data["message"] == "File uploaded successfully"


@pytest.mark.asyncio
async def test_upload_duplicate_file(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file
):
    """Test uploading the same file twice (deduplication)."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload first time
    test_image_file.seek(0)
    files1 = {
        "file": ("test_image.jpg", test_image_file, "image/jpeg")
    }
    
    response1 = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files1
    )
    
    assert response1.status_code == status.HTTP_201_CREATED
    data1 = response1.json()
    assert data1["is_duplicate"] is False
    
    # Upload second time (same content)
    test_image_file.seek(0)
    files2 = {
        "file": ("test_image_copy.jpg", test_image_file, "image/jpeg")
    }
    
    response2 = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files2
    )
    
    assert response2.status_code == status.HTTP_201_CREATED
    data2 = response2.json()
    assert data2["is_duplicate"] is True
    assert data2["duplicate_of"] == data1["attachment"]["id"]


@pytest.mark.asyncio
async def test_upload_text_file(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_text_file
):
    """Test uploading a text document."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    files = {
        "file": ("test_document.txt", test_text_file, "text/plain")
    }
    
    response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["attachment"]["filename"] == "test_document.txt"
    assert data["attachment"]["mime_type"] == "text/plain"
    assert data["attachment"]["is_document"] is True


@pytest.mark.asyncio
async def test_upload_pdf_file(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_pdf_file
):
    """Test uploading a PDF document."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    files = {
        "file": ("test_document.pdf", test_pdf_file, "application/pdf")
    }
    
    response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["attachment"]["filename"] == "test_document.pdf"
    assert data["attachment"]["mime_type"] == "application/pdf"
    assert data["attachment"]["is_document"] is True


@pytest.mark.asyncio
async def test_upload_invalid_file_type(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str
):
    """Test uploading an invalid file type."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Create a fake executable file
    fake_exe = io.BytesIO(b"fake executable content")
    files = {
        "file": ("malicious.exe", fake_exe, "application/x-msdownload")
    }
    
    response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_oversized_file(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str
):
    """Test uploading a file that exceeds size limit."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Create a file larger than the limit
    # Note: This test assumes MAX_FILE_SIZE is set reasonably
    large_content = b"x" * (settings.MAX_FILE_SIZE + 1024)
    large_file = io.BytesIO(large_content)
    
    files = {
        "file": ("large_file.txt", large_file, "text/plain")
    }
    
    response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceeds maximum" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_batch_upload_attachments(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file,
    test_text_file
):
    """Test uploading multiple files at once."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    test_image_file.seek(0)
    test_text_file.seek(0)
    
    files = [
        ("files", ("image1.jpg", test_image_file, "image/jpeg")),
        ("files", ("document1.txt", test_text_file, "text/plain"))
    ]
    
    response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments/batch",
        headers=headers,
        files=files
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["total_uploaded"] == 2
    assert len(data["attachments"]) == 2
    assert data["total_size"] > 0


@pytest.mark.asyncio
async def test_get_attachment(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file
):
    """Test retrieving attachment metadata."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload file first
    files = {
        "file": ("test_image.jpg", test_image_file, "image/jpeg")
    }
    
    upload_response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    attachment_id = upload_response.json()["attachment"]["id"]
    
    # Get attachment
    response = await async_client.get(
        f"/api/v1/attachments/{attachment_id}",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == attachment_id
    assert data["filename"] == "test_image.jpg"
    assert data["mime_type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_download_attachment(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_text_file
):
    """Test downloading an attachment file."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload file first
    test_text_file.seek(0)
    original_content = test_text_file.read()
    test_text_file.seek(0)
    
    files = {
        "file": ("test_document.txt", test_text_file, "text/plain")
    }
    
    upload_response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    attachment_id = upload_response.json()["attachment"]["id"]
    
    # Download attachment
    response = await async_client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.content == original_content
    assert "attachment" in response.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_list_knowledge_item_attachments(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file,
    test_text_file
):
    """Test listing attachments for a knowledge item."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload multiple files
    test_image_file.seek(0)
    files1 = {
        "file": ("image1.jpg", test_image_file, "image/jpeg")
    }
    await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files1
    )
    
    test_text_file.seek(0)
    files2 = {
        "file": ("document1.txt", test_text_file, "text/plain")
    }
    await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files2
    )
    
    # List attachments
    response = await async_client.get(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_list_attachments_with_filter(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file,
    test_text_file
):
    """Test listing attachments with MIME type filter."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload files
    test_image_file.seek(0)
    files1 = {
        "file": ("image1.jpg", test_image_file, "image/jpeg")
    }
    await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files1
    )
    
    test_text_file.seek(0)
    files2 = {
        "file": ("document1.txt", test_text_file, "text/plain")
    }
    await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files2
    )
    
    # List only images
    response = await async_client.get(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments?mime_type_filter=image",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Should only return images
    for item in data["items"]:
        assert item["is_image"] is True


@pytest.mark.asyncio
async def test_update_attachment(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file
):
    """Test updating attachment metadata."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload file first
    files = {
        "file": ("test_image.jpg", test_image_file, "image/jpeg")
    }
    
    upload_response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    attachment_id = upload_response.json()["attachment"]["id"]
    
    # Update attachment
    update_data = {
        "filename": "renamed_image.jpg",
        "is_public": True
    }
    
    response = await async_client.put(
        f"/api/v1/attachments/{attachment_id}",
        headers=headers,
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["filename"] == "renamed_image.jpg"
    assert data["is_public"] is True


@pytest.mark.asyncio
async def test_delete_attachment(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file
):
    """Test deleting an attachment."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload file first
    files = {
        "file": ("test_image.jpg", test_image_file, "image/jpeg")
    }
    
    upload_response = await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files
    )
    
    attachment_id = upload_response.json()["attachment"]["id"]
    
    # Delete attachment
    response = await async_client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    get_response = await async_client.get(
        f"/api/v1/attachments/{attachment_id}",
        headers=headers
    )
    
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_attachment_stats(
    async_client: AsyncClient,
    test_user_token: str,
    test_knowledge_item_id: str,
    test_image_file,
    test_text_file
):
    """Test getting attachment statistics."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Upload files
    test_image_file.seek(0)
    files1 = {
        "file": ("image1.jpg", test_image_file, "image/jpeg")
    }
    await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files1
    )
    
    test_text_file.seek(0)
    files2 = {
        "file": ("document1.txt", test_text_file, "text/plain")
    }
    await async_client.post(
        f"/api/v1/knowledge/{test_knowledge_item_id}/attachments",
        headers=headers,
        files=files2
    )
    
    # Get stats
    response = await async_client.get(
        f"/api/v1/attachments/stats/summary?knowledge_item_id={test_knowledge_item_id}",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["total_count"] >= 2
    assert data["total_size"] > 0
    assert "by_type" in data
    assert "by_mime_type" in data


@pytest.mark.asyncio
async def test_unauthorized_access(
    async_client: AsyncClient,
    test_image_file
):
    """Test that unauthorized users cannot upload attachments."""
    files = {
        "file": ("test_image.jpg", test_image_file, "image/jpeg")
    }
    
    response = await async_client.post(
        "/api/v1/knowledge/some-id/attachments",
        files=files
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_upload_to_nonexistent_knowledge_item(
    async_client: AsyncClient,
    test_user_token: str,
    test_image_file
):
    """Test uploading to a non-existent knowledge item."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    files = {
        "file": ("test_image.jpg", test_image_file, "image/jpeg")
    }
    
    response = await async_client.post(
        "/api/v1/knowledge/nonexistent-id/attachments",
        headers=headers,
        files=files
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
