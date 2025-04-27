from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from src.utils import HTTPConflictRequestException
from tests.conftest import TestingSessionLocal, test_user

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "admin",
}


def test_register_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_register_user_again(client, monkeypatch):
    # Setup
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    # Call method
    response = client.post("api/auth/register", json=user_data)
    data = response.json()

    # Assertions
    assert response.status_code == 409, response.text
    assert data["detail"] == "A user already exists with the same email."


def test_register_user_with_same_username(client, monkeypatch):
    # Setup
    mock_send_email = Mock()
    updated_user_data = user_data.copy()
    updated_user_data["email"] = "updatedemail@gmail.com"
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    # Call method
    response = client.post("api/auth/register", json=updated_user_data)
    data = response.json()

    # Assertions
    assert response.status_code == 409, response.text
    assert data["detail"] == "A user already exists with the same username."


def test_login_user_not_confirmed(client):
    # Call method
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    data = response.json()

    # Assertions
    assert response.status_code == 401, response.text
    assert data["detail"] == "Email address not confirmed."


@pytest.mark.asyncio
async def test_login_user(client):
    # Setup
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            setattr(current_user, "confirmed", True)
            await session.commit()

    # Call method
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    data = response.json()

    # Assertions
    assert response.status_code == 200, response.text
    assert "access_token" in data
    assert "token_type" in data


def test_login_user_wrong_password(client):
    # Call method
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    data = response.json()

    # Assertions
    assert response.status_code == 401, response.text
    assert data["detail"] == "Incorrect login or password."


def test_login_user_wrong_username(client):
    # Call method
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    data = response.json()

    # Assertions
    assert response.status_code == 401, response.text
    assert data["detail"] == "Incorrect login or password."


def test_login_user_validation_error(client):
    # Call method
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    data = response.json()

    # Assertions
    assert response.status_code == 400, response.text
    assert "detail" in data


@pytest.mark.asyncio
async def test_verify_email(client, get_reset_token):
    # Setup
    token = get_reset_token

    # Call method
    response = client.get(f"api/auth/verify_email/{token}")
    data = response.json()

    # Assertions
    assert response.status_code == 200, response.text
    assert "message" in data

    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == test_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        assert current_user.confirmed is True
