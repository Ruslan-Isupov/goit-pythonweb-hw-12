import pytest
from sqlalchemy import select

from src.database.models import User, Contact
from src.schemas.contacts import ContactCreateModel
from tests.conftest import TestingSessionLocal, test_user

contact_model = {
    "id": 1,
    "first_name": "Den",
    "last_name": "Boo",
    "email": "boo@example.com",
    "phone": "911",
    "birthday": "1981-04-15",
    "user_id": test_user["id"],
}


@pytest.fixture(autouse=True)
@pytest.mark.asyncio
async def init_contacts():
    async with TestingSessionLocal() as session:
        existing_contact = (
            await session.execute(
                select(Contact).filter(Contact.id == contact_model["id"])
            )
        ).scalar_one_or_none()

        if existing_contact:
            await session.delete(existing_contact)

        session.add(Contact(**contact_model))
        await session.commit()

    yield

    async with TestingSessionLocal() as session:
        existing_contact = (
            await session.execute(
                select(Contact).filter(Contact.id == contact_model["id"])
            )
        ).scalar_one_or_none()

        if existing_contact:
            await session.delete(existing_contact)
            await session.commit()


@pytest.mark.asyncio
async def test_get_contacts(client, get_token):
    # Setup
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Call method
    response = client.get("api/contacts/", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200, response.text
    assert len(data) == 1
    assert data[0]["first_name"] == "Den"
    assert data[0]["last_name"] == "Boo"
    assert "password" not in data[0]


@pytest.mark.asyncio
async def test_get_contact_by_id(client, get_token):
    # Setup
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Call method
    response = client.get(f'api/contacts/{contact_model["id"]}', headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200, response.text
    assert data["first_name"] == "Den"
    assert data["last_name"] == "Boo"
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_contact_success(client, get_token):
    # Setup
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    new_contact = contact_model.copy()
    new_contact["id"] = contact_model["id"] + 1
    new_contact["email"] = "new@example.com"

    # Call method
    response = client.post("api/contacts/", headers=headers, json=new_contact)
    data = response.json()

    # Assertions
    assert response.status_code == 201, response.text
    assert data["first_name"] == new_contact["first_name"]
    assert data["last_name"] == new_contact["last_name"]
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_same_contact_fail(client, get_token):
    # Setup
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    new_contact = contact_model.copy()
    new_contact["id"] = contact_model["id"] + 1

    # Call method
    response = client.post("api/contacts/", headers=headers, json=new_contact)
    data = response.json()

    # Assertions
    assert response.status_code == 409, response.text
    assert "detail" in data


@pytest.mark.asyncio
async def test_delete_contact_by_id(client, get_token):
    # Setup
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Call method
    response = client.delete(f'api/contacts/{contact_model["id"]}', headers=headers)

    # Assertions
    assert response.status_code == 204, response.text
    # Check a contact in database if one was deleted
    async with TestingSessionLocal() as session:
        contact = (
            await session.execute(
                select(Contact).filter(Contact.id == contact_model["id"])
            )
        ).scalar_one_or_none()

        assert contact is None


@pytest.mark.asyncio
async def test_update_contact_by_id_success(client, get_token):
    # Setup
    phone = "111-22-333"
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    contact_data = {"phone": phone}

    # Call method
    response = client.patch(
        f'api/contacts/{contact_model["id"]}', headers=headers, json=contact_data
    )
    data = response.json()

    # Assertions
    assert response.status_code == 200, response.text
    assert data["phone"] == phone


@pytest.mark.asyncio
async def test_update_contact_by_id_fail(client, get_token):
    # Setup
    phone = "111-22-333"
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    contact_data = {"phone": phone}
    not_existing_contact_id = 100000

    # Call method
    response = client.patch(
        f"api/contacts/{not_existing_contact_id}", headers=headers, json=contact_data
    )
    data = response.json()

    # Assertions
    assert response.status_code == 404, response.text
    assert "detail" in data
