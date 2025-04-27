from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize a UserRepository.

        Args:
            session: An AsyncSession object connected to the database.
        """

        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a User by an ID.

        Args:
            user_id (int): An ID to search for a user.

        Returns:
            A User or None.
        """

        user = await self.db.execute(select(User).filter(User.id == user_id))
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a User by a username.

        Args:
            username (str): A username to search for a user.

        Returns:
            A User or None.
        """

        user = await self.db.execute(select(User).filter(User.username == username))
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a User by an email address.

        Args:
            email (str): An email address to search for a user.

        Returns:
            A User or None.
        """

        user = await self.db.execute(select(User).filter(User.email == email))
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: Optional[str] = None) -> User:
        """
        Add a new User.

        Args:
            body (obj): An instance of UserCreate class.
            avatar (str, optional): A url to an avatar

        Returns:
            A User.
        """

        new_user = User(**body.model_dump(exclude_unset=True), avatar=avatar)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_avatar_url(self, email: str, url: str) -> User | None:
        """
        Update an avatar url of a User.

        Args:
            email (str): A email address to search for a user.
            url (str): A url to an avatar

        Returns:
            A User or None.
        """

        user = await self.get_user_by_email(email)

        if user:
            setattr(user, "avatar", url)
            await self.db.commit()
            await self.db.refresh(user)
            return user

    async def verify_email(self, email: str) -> None:
        """
        Verify a User by an email address.

        Args:
            email (str): A email address to search for a user.

        Returns:
            None
        """

        user = await self.get_user_by_email(email)

        if user:
            setattr(user, "confirmed", True)
            await self.db.commit()

    async def update_user(self, user: User, body: UserUpdate) -> User:
        """
        Update passed user with provided data.

        Args:
            user (obj): The instance of User.
            body (UserUpdate): the instance of UserUpdate

        Returns:
            User
        """
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
