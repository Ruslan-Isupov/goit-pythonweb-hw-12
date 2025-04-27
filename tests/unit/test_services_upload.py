import pytest
from unittest.mock import AsyncMock
from src.services.upload import UploadService, CloudinaryUploadService


@pytest.mark.asyncio
async def test_send_email(monkeypatch):
    # Setup
    mock_upload_file = AsyncMock()
    monkeypatch.setattr(
        "src.services.upload.CloudinaryUploadService.upload_file", mock_upload_file
    )

    # Call method
    upload_service = UploadService(CloudinaryUploadService())
    await upload_service.upload_file(file="file", username="username")

    # Assertions
    mock_upload_file.assert_called_once_with("file", "username")
