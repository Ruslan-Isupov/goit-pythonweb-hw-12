import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.contacts import ContactCreateModel
from src.services.contacts import ContactsService
from src.repository.contacts import ContactsRepository

from tests.conftest import test_user
from src.utils import HTTPNotFoundException, HTTPConflictRequestException


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contacts_repository():
    mock_contacts_repository = AsyncMock(spec=ContactsRepository)
    return mock_contacts_repository


@pytest.fixture
async def mock_user():
    """
    Fixture of a test user.

    Returns:
        User
    """

    return User(
        id=test_user["id"],
        username=test_user["username"],
        email=test_user["email"],
    )


@pytest.fixture
async def contact_service(mock_session, mock_user, contacts_repository):
    """
    Fixture of an instance of ContactsService.

    Args:
        mock_session (AsyncSession): The database session fixture.
        mock_user (User): an instance of a current user
        contacts_repository (ContactsRepository): The ContactsRepository fixture.

    Returns:
        ContactsService
    """

    contacts_service = ContactsService(mock_session, mock_user)
    contacts_service.repository = contacts_repository
    return contacts_service


@pytest.mark.asyncio
async def test_create_success(contact_service, contacts_repository):
    # Setup
    contacts_repository.create = AsyncMock()
    contacts_repository.get_contact_by_email = AsyncMock(return_value=None)
    contact_data = ContactCreateModel(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="911",
        birthday="1990-01-01",
    )

    # Call method
    await contact_service.create(contact_data)

    # Assertions
    contacts_repository.create.assert_awaited_once_with(contact_data)


@pytest.mark.asyncio
async def test_create_fail(contact_service, mock_user, contacts_repository):
    # Setup
    contacts_repository.create = AsyncMock()
    contacts_repository.get_contact_by_email = AsyncMock(return_value=mock_user)
    contact_data = ContactCreateModel(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="911",
        birthday="1990-01-01",
    )

    # Call method
    with pytest.raises(HTTPConflictRequestException) as ex_nfo:
        await contact_service.create(contact_data)

    # Assertions
    assert ex_nfo.value.status_code == 409
    contacts_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_all(contact_service, contacts_repository):
    # Setup
    contacts_repository.get_all = AsyncMock()
    args = {
        "search": "search",
        "birthdays_within": 7,
        "offset": 1,
        "limit": 10,
    }

    # Call method
    await contact_service.get_all(**args)

    # Assertions
    contacts_repository.get_all.assert_awaited_once_with(**args)


@pytest.mark.asyncio
async def test_get_by_id_success(contact_service, contacts_repository):
    # Setup
    contact_id = 1
    contact_data = {
        "id": contact_id,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "911",
        "birthday": "1990-01-01",
    }
    contacts_repository.get_contact_by_id = AsyncMock(return_value=contact_data)

    # Call method
    contact = await contact_service.get_by_id(contact_id=contact_id)

    # Assertions
    contacts_repository.get_contact_by_id.assert_awaited_once_with(contact_id)
    assert contact["first_name"] == "John"


@pytest.mark.asyncio
async def test_get_by_id_fail(contact_service, contacts_repository):
    # Setup
    contact_id = 1
    contacts_repository.get_contact_by_id = AsyncMock(return_value=None)

    # Call method
    with pytest.raises(HTTPNotFoundException) as ex_nfo:
        await contact_service.get_by_id(contact_id=contact_id)

    # Assertions
    assert ex_nfo.value.status_code == 404
    contacts_repository.get_contact_by_id.assert_awaited_once_with(contact_id)


@pytest.mark.asyncio
async def test_delete_by_id_success(contact_service, contacts_repository):
    # Setup
    contact_id = 1
    contact_data = {
        "id": contact_id,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "911",
        "birthday": "1990-01-01",
    }
    contacts_repository.delete = AsyncMock()
    contacts_repository.get_contact_by_id = AsyncMock(return_value=contact_data)

    # Call method
    await contact_service.delete_by_id(contact_id=contact_id)

    # Assertions
    contacts_repository.get_contact_by_id.assert_awaited_once_with(contact_id)
    contacts_repository.delete.assert_awaited_once_with(contact_id)


@pytest.mark.asyncio
async def test_delete_by_id_fail(contact_service, contacts_repository):
    # Setup
    contact_id = 1
    contacts_repository.delete = AsyncMock()
    contacts_repository.get_contact_by_id = AsyncMock(return_value=None)

    # Call method
    with pytest.raises(HTTPNotFoundException) as ex_nfo:
        await contact_service.delete_by_id(contact_id=contact_id)

    # Assertions
    assert ex_nfo.value.status_code == 404
    contacts_repository.get_contact_by_id.assert_awaited_once_with(contact_id)
    contacts_repository.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_by_id_success(contact_service, contacts_repository):
    # Setup
    contact_id = 1
    existing_contact = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "911",
        "birthday": "1990-01-01",
    }
    contact_data = {
        "first_name": "New Fisrt name",
    }
    contacts_repository.update = AsyncMock()
    contacts_repository.get_contact_by_id = AsyncMock(return_value=existing_contact)

    # Call method
    await contact_service.update_by_id(contact_id=contact_id, body=contact_data)

    # Assertions
    contacts_repository.get_contact_by_id.assert_awaited_once_with(contact_id)
    contacts_repository.update.assert_awaited_once_with(contact_id, contact_data)


@pytest.mark.asyncio
async def test_update_by_id_fail(contact_service, contacts_repository):
    # Setup
    contact_id = 1
    contact_data = {
        "first_name": "New Fisrt name",
    }
    contacts_repository.update = AsyncMock()
    contacts_repository.get_contact_by_id = AsyncMock(return_value=None)

    # Call method
    with pytest.raises(HTTPNotFoundException) as ex_nfo:
        await contact_service.update_by_id(contact_id=contact_id, body=contact_data)

    # Assertions
    assert ex_nfo.value.status_code == 404
    contacts_repository.get_contact_by_id.assert_awaited_once_with(contact_id)
    contacts_repository.update.assert_not_awaited()
