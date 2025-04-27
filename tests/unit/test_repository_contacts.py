import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactsRepository
from src.schemas.contacts import ContactCreateModel, ContactUpdateModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user():
    return User(id=1, username="Mock", email="testuser@example.com", role="admin")


@pytest.fixture
def contacts_repository(mock_session, user):
    return ContactsRepository(mock_session, user)


@pytest.mark.asyncio
async def test_get_all(contacts_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(
            id=1,
            first_name="Den",
            last_name="Boo",
            email="boo@example.com",
            phone="911",
            birthday="1981-04-15",
            user=user,
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contacts_repository.get_all()

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "Den"
    assert contacts[0].last_name == "Boo"
    assert contacts[0].email == "boo@example.com"
    assert contacts[0].phone == "911"
    assert contacts[0].birthday == "1981-04-15"


@pytest.mark.asyncio
async def test_get_contact_by_email(contacts_repository, mock_session, user):
    # Setup mock
    mock_email = "boo@example.com"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        first_name="Den",
        last_name="Boo",
        email=mock_email,
        phone="911",
        birthday="1981-04-15",
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contacts_repository.get_contact_by_email(email=mock_email)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.email == mock_email


@pytest.mark.asyncio
async def test_get_contact_by_id(contacts_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        first_name="Den",
        last_name="Boo",
        email="boo@example.com",
        phone="911",
        birthday="1981-04-15",
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contacts_repository.get_contact_by_id(contact_id=1)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "Den"


@pytest.mark.asyncio
async def test_create(contacts_repository, mock_session):
    # Setup
    contact_data = ContactCreateModel(
        first_name="Den",
        last_name="Boo",
        email="boo@example.com",
        phone="911",
        birthday="1981-04-15",
    )

    # Call method
    result = await contacts_repository.create(body=contact_data)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "Den"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update(contacts_repository, mock_session, user):
    # Setup
    contact_data = ContactUpdateModel(
        first_name="Updated Den", last_name="Boo", email="boo@example.com", phone="911"
    )
    existing_contact = Contact(
        id=1,
        first_name="Den",
        last_name="Boo",
        email="boo@example.com",
        phone="911",
        birthday="1981-04-15",
        user=user,
    )
    mock_result = MagicMock()
    # Mock calling get_contact_by_id
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contacts_repository.update(contact_id=1, body=contact_data)

    # Assertions
    assert result is not None
    assert result.first_name == "Updated Den"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_delete(contacts_repository, mock_session, user):
    # Setup
    existing_tag = Contact(
        id=1,
        first_name="Den To Delete",
        last_name="Boo",
        email="boo@example.com",
        phone="911",
        birthday="1981-04-15",
        user=user,
    )
    mock_result = MagicMock()
    # Mock calling get_contact_by_id
    mock_result.scalar_one_or_none.return_value = existing_tag
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contacts_repository.delete(contact_id=1)

    # Assertions
    assert result is not None
    assert result.first_name == "Den To Delete"
    mock_session.delete.assert_awaited_once_with(existing_tag)
    mock_session.commit.assert_awaited_once()
