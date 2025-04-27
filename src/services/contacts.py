from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactsRepository
from src.schemas.users import User
from src.schemas.contacts import ContactCreateModel, ContactUpdateModel
from src.utils import HTTPNotFoundException, HTTPConflictRequestException


class ContactsService:
    repository: ContactsRepository
    current_user: User

    def __init__(self, db: AsyncSession, user: User):
        self.repository = ContactsRepository(db, user)
        self.current_user = user

    async def get_all(
        self,
        search: str | None = None,
        birthdays_within: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ):
        """
        Return all contacts

        Args:
            search (str, Optional): Search query for email, first name and last name.
            birthdays_within (int, Optional): Number of days within future birthdays.
            offset (int, Optional): The number of Contacts to skip.
            limit (int, Optional): The maximum number of Contacts to return.

        Returns:
            List[Contact]
        """

        return await self.repository.get_all(
            search=search,
            birthdays_within=birthdays_within,
            offset=offset,
            limit=limit,
        )

    async def get_by_id(self, contact_id: int):
        """
        Return a contact by ID

        Args:
            contact_id (int): Contact ID

        Returns:
            Contact
        """

        contact = await self.repository.get_contact_by_id(contact_id)

        if contact is None:
            raise HTTPNotFoundException("Contact not found")

        return contact

    async def create(self, body: ContactCreateModel):
        """
        Create a contact

        Args:
            body (ContactCreateModel): instanse of ContactCreateModel.

        Returns:
            Contact
        """

        contact = await self.repository.get_contact_by_email(body.email)

        if contact:
            raise HTTPConflictRequestException(
                "Contact already exists with the same email"
            )

        return await self.repository.create(body)

    async def update_by_id(self, contact_id: int, body: ContactUpdateModel):
        """
        Update a contact by ID

        Args:
            contact_id (int): Contact ID.
            body (ContactUpdateModel): instance of ContactUpdateModel

        Returns:
            Contact
        """

        contact = await self.repository.get_contact_by_id(contact_id)

        if not contact:
            raise HTTPNotFoundException("Contact not found")

        return await self.repository.update(contact_id, body)

    async def delete_by_id(self, contact_id: int):
        """
        Delete a contact by ID

        Args:
            contact_id (int): Contact ID.

        Returns:
            Contact
        """

        contact = await self.repository.get_contact_by_id(contact_id)

        if contact is None:
            raise HTTPNotFoundException("Contact Not found")

        return await self.repository.delete(contact_id)
