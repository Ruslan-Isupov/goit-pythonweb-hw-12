from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
import logging

from src.schemas.users import (
    UserCreate,
    User,
    ResetPasswordRequest,
    ResetPasswordConfirm,
    UserUpdate,
)
from src.schemas.token import Token
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    create_token,
)
from src.services.users import UserService
from src.services.email import send_email, send_reset_email
from src.database.db import get_db
from src.utils import HTTPConflictRequestException, HTTPBadRequestException

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

routerAuth = APIRouter(prefix="/auth", tags=["auth"])


@routerAuth.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new User.

    Args:
        user (UserCreate): instance of UserCreate
        background_tasks (BackgroundTasks): An instance of BackgroundTasks.
        request (Request): An instance of Request.
        db (AsyncSession): An instance of AsyncSession.

    Returns:
        User
    """

    user_service = UserService(db)
    email_user = await user_service.get_user_by_email(user.email)

    if email_user:
        raise HTTPConflictRequestException("A user already exists with the same email.")

    username_user = await user_service.get_user_by_username(user.username)

    if username_user:
        raise HTTPConflictRequestException(
            "A user already exists with the same username."
        )

    user.password = Hash().get_password_hash(user.password)
    new_user = await user_service.create_user(user)

    background_tasks.add_task(
        send_email, str(new_user.email), str(new_user.username), str(request.base_url)
    )

    logger.info(f'Verification email sent for "{new_user.username}".')

    return new_user


@routerAuth.post("/login", response_model=Token)
async def login_user(
    request_form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Log in with a OAuth2PasswordRequestForm from.

    Args:
        request_form (OAuth2PasswordRequestForm): instance of OAuth2PasswordRequestForm with email and password fields
        db (AsyncSession): An instance of AsyncSession.

    Returns:
        dict(access_token and token_type)
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_username(request_form.username)

    if not user or not Hash().verify_password(request_form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email address not confirmed.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = {"sub": user.username}
    access_token = await create_access_token(payload)
    return {"access_token": access_token, "token_type": "bearer"}


@routerAuth.get("/verify_email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify email address by provided email address in a token.

    Args:
        token (str): token
        db (AsyncSession): An instance of AsyncSession.

    Returns:
        dict(message)
    """

    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    if bool(user.confirmed):
        return {"message": "Email already verified"}

    await user_service.verify_email(email)
    logger.info(f"Email address {email} verified.")
    return {"message": "Email verified!"}


@routerAuth.post("/password-reset/")
async def password_reset(
    body: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    token = create_token(payload={"sub": body.email})

    background_tasks.add_task(
        send_reset_email,
        body.email,
        token,
        str(request.base_url),
    )

    logger.info(
        f'Reset password email sent for a user with email address "{body.email}".'
    )
    return {"message": "Reset password email sent"}


@routerAuth.post("/password-reset-confirm/")
async def password_reset_confirm(
    data: ResetPasswordConfirm,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    email = await get_email_from_token(data.token)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPBadRequestException("Invalid or expired token")

    new_password = Hash().get_password_hash(data.password)
    updated_user = await user_service.update_user(
        user, UserUpdate(password=new_password)
    )

    if updated_user:
        logger.info(f'Password updated for a user with email "{email}".')
        return {"message": "Password updated"}
