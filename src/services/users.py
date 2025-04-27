from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.database.models import User
from src.schemas.users import UserCreate, UserUpdate
from src.utils import HTTPNotFoundException


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a user with avatar from Gravatar by email address

        Args:
            body (int): instance of UserCreate

        Returns:
            User
        """

        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Return a user by its ID

        Args:
            user_id (int): a user ID

        Returns:
            User
        """

        user = await self.repository.get_user_by_id(user_id)

        if not user:
            raise HTTPNotFoundException("User Not found")

        return user

    async def get_user_by_username(self, username: str):
        """
        Return a user by username

        Args:
            username (str): username

        Returns:
            User
        """

        user = await self.repository.get_user_by_username(username)
        return user

    async def get_user_by_email(self, email: str):
        """
        Update a user by email address

        Args:
            email (str): email address

        Returns:
            User
        """

        user = await self.repository.get_user_by_email(email)
        return user

    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar by email address

        Args:
            email (str): email address
            url (str): url of avatar

        Returns:
            User
        """

        user = await self.get_user_by_email(email)

        if not user:
            raise HTTPNotFoundException("User Not found")

        return await self.repository.update_avatar_url(email, url)

    async def verify_email(self, email: str):
        """
        Verify a user by email address

        Args:
            email (str): email address

        Returns:
            None
        """

        await self.repository.verify_email(email)

    async def update_user(self, user: User, body: UserUpdate):
        return await self.repository.update_user(user, body)
