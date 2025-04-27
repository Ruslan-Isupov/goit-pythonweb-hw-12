from fastapi import APIRouter, Depends, File, UploadFile, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db

from src.schemas.users import User
from src.services.auth import get_current_user, get_current_user_admin
from src.services.users import UserService
from src.services.upload import UploadService, CloudinaryUploadService

routerUsers = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@routerUsers.get(
    "/me", response_model=User, description="Limitted by 10 requests per 1 minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Return a curent user. Limitted request by 10 requests per 1 minute

    Args:
        request (Request): An instance of Request.
        user (User): a current user

    Returns:
        User
    """
    return user


@routerUsers.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a user avatar. Only a user with admin role can update

    Args:
        file (UploadFile): An instance of UploadFile.
        user (User): a current user
        db (AsyncSession): An instance of AsyncSession.

    Returns:
        User
    """

    upload_service = UploadService(CloudinaryUploadService())
    avatar_url = upload_service.upload_file(file, user.username)
    user_service = UserService(db)

    return await user_service.update_avatar_url(user.email, avatar_url)
