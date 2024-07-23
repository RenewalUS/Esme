"""Query Builder module for Users related queries."""
from sqlalchemy import select, update
from sqlalchemy.orm import load_only

from data.connector import CONN

from data.mappings.erupe import (
    Users
)
class UserBuilder():
    """Query builder class for Users table."""
    def __init__(self) -> None:
        self.db = CONN

    async def select_id_by_token(self, session, discord_token):
        """Select user_id by discord_token."""
        stmt = select(Users).options(
            load_only(Users.id)
        ).where(Users.discord_token == discord_token)
        user_id = await self.db.select_object(session, stmt)
        if user_id:
            return user_id.id
        return user_id

    async def select_user_by_username(self, session, username: str):
        """Select user id and password hash by username."""
        stmt = select(Users).options(
            load_only(Users.id, Users.password)
        ).where(Users.username == username)
        user = await self.db.select_object(session, stmt)
        return user

    async def select_user_by_id(self, session, user_id: str):
        """Select user id and password hash by user id."""
        stmt = select(Users).options(
            load_only(Users.id, Users.password)
        ).where(Users.id == user_id)
        user = await self.db.select_object(session, stmt)
        return user

    async def clear_user_token(
        self,
        session,
        user_id: int
    ) -> (int | None):
        """Update user by setting discord token to NULL"""
        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(discord_token=None)
        )
        return await self.db.update_objects(session, stmt)

    async def select_user_psn(self, session, psn_id: str):
        """Select user psn_id."""
        stmt = select(Users).options(
            load_only(Users.id, Users.psn_id)
        ).where(Users.psn_id == psn_id)
        rows = await self.db.select_object(session, stmt)
        return rows

    async def update_user_psn(
        self,
        session,
        user_id: int,
        psn_id: str
    ) -> (int | None):
        """Update user psn_id by user_id."""
        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(psn_id=psn_id)
        )
        return await self.db.update_objects(session, stmt)
