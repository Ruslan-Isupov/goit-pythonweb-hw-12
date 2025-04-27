import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User, UserRole
from src.repository.users import UserRepository
from src.schemas.users import UserCreate, UserUpdate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user():
    return User(id=1, username="Mock", email="testuser@example.com", role="admin")


@pytest.fixture
def admin_user():
    return User(id=1, username="Mock", email="testuser@example.com", role="user")


@pytest.fixture
def repository(mock_session):
    return UserRepository(mock_session)


@pytest.mark.asyncio
async def test_get_user_by_email(repository, mock_session, user):
    # Setup mock
    email = "boo@example.com"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="Den",
        email=email,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await repository.get_user_by_email(email=email)

    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.email == email


@pytest.mark.asyncio
async def test_get_user_by_id(repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="Den",
        email="boo@example.com",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await repository.get_user_by_id(user_id=1)

    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.username == "Den"


@pytest.mark.asyncio
async def test_get_user_by_username(repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="denboo",
        email="boo@example.com",
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await repository.get_user_by_username(username="denboo")

    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.username == "denboo"


@pytest.mark.asyncio
async def test_create(repository, mock_session):
    # Setup
    user_data = UserCreate(
        username="denboo",
        password="111",
        email="boo@example.com",
        role=UserRole.USER,
    )

    # Call method
    result = await repository.create_user(body=user_data, avatar="avatar.url")

    # Assertions
    assert isinstance(result, User)
    assert result.username == "denboo"
    assert result.avatar == "avatar.url"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update(repository, mock_session):
    # Setup
    user_data = UserUpdate(password="111222")
    existing_user = User(
        username="denboo",
        password="111",
        email="boo@example.com",
        role=UserRole.USER,
    )

    # Call method
    result = await repository.update_user(user=existing_user, body=user_data)

    # Assertions
    assert result is not None
    assert result.username == "denboo"
    assert result.password == "111222"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_user)


@pytest.mark.asyncio
async def test_update_avatar(repository, mock_session):
    # Setup
    email = "boo@example.com"
    avatar = "avatar.url"
    existing_user = User(username="denboo", email=email, avatar=None)

    mock_result = MagicMock()
    # Mock calling get_user_by_email
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await repository.update_avatar_url(email=email, url=avatar)

    # Assertions
    assert result is not None
    assert result.username == "denboo"
    assert result.avatar == avatar
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_user)
