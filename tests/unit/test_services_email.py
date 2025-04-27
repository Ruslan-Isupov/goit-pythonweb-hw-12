import pytest
from unittest.mock import AsyncMock

from src.services.email import send_email, send_reset_email


@pytest.mark.asyncio
async def test_send_email(monkeypatch):
    # Setup
    mock_send_message = AsyncMock()
    monkeypatch.setattr("src.services.email.FastMail.send_message", mock_send_message)

    # Call method
    await send_email(
        email="email@example.com", username="doon", host="https:/example.com"
    )

    # Assertions
    mock_send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_reset_email(monkeypatch):
    # Setup
    mock_send_message = AsyncMock()
    monkeypatch.setattr("src.services.email.FastMail.send_message", mock_send_message)

    # Call method
    await send_reset_email(
        email="email@example.com", token="token", host="https:/example.com"
    )

    # Assertions
    mock_send_message.assert_awaited_once()
