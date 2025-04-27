from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

routerUtils = APIRouter(tags=["utils"])


@routerUtils.get("/healthchecker/")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Check a connection to database

    Args:
        db (AsyncSession): An instance of AsyncSession.

    Returns:
        dict(message)
    """

    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to REST API"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
