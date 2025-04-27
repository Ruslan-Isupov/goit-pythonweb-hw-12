import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils import HTTPNotFoundException

from src.database.models import UserRole, User
from src.schemas.users import UserCreate
from src.services.users import UserService
from src.repository.users import UserRepository


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository():
    mock_user_repository = AsyncMock(spec=UserRepository)
    return mock_user_repository


@pytest.fixture
async def user_service(mock_session, user_repository):
    """
    Fixture of an instance of UserService.

    Args:
        mock_session (AsyncSession): The database session fixture.
        user_repository (UserRepository): The UserRepository fixture.

    Returns:
        UserService
    """

    service = UserService(mock_session)
    service.repository = user_repository
    return service


@pytest.mark.asyncio
async def test_create_success(monkeypatch, user_service, user_repository):
    # Setup
    avatar_url = "https://evatar.url"
    mock_get_image = Mock(return_value=avatar_url)
    monkeypatch.setattr("src.services.users.Gravatar.get_image", mock_get_image)
    user_repository.create_user = AsyncMock()
    body = UserCreate(
        username="john",
        email="john.doe@example.com",
        password="password",
        role=UserRole.USER,
    )

    # Call method
    await user_service.create_user(body=body)

    # Assertions
    user_repository.create_user.assert_awaited_once_with(body, avatar_url)


@pytest.mark.asyncio
async def test_get_user_by_id_success(user_service, user_repository):
    # Setup
    user_id = 1
    user_model = {
        "id": user_id,
        "username": "john",
        "email": "john.doe@example.com",
        "password": "password",
        "role": "user",
    }
    user_repository.get_user_by_id = AsyncMock(return_value=user_model)

    # Call method
    user = await user_service.get_user_by_id(user_id=user_id)

    # Assertions
    user_repository.get_user_by_id.assert_awaited_once_with(user_id)
    assert user["username"] == "john"


@pytest.mark.asyncio
async def test_get_user_by_id_fail(user_service, user_repository):
    # Setup
    user_id = 1
    user_repository.get_user_by_id = AsyncMock(return_value=None)

    # Call method
    with pytest.raises(HTTPNotFoundException) as ex_nfo:
        await user_service.get_user_by_id(user_id=user_id)

    # Assertions
    assert ex_nfo.value.status_code == 404
    user_repository.get_user_by_id.assert_awaited_once_with(user_id)
