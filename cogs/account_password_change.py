"""Extension module for AccountPasswordChange Cog."""
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import UserBuilder, DiscordBuilder
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    UsernameIncorrect,
    UnmatchingPasswords
)
from core import BaseCog
from core.crypto import check_password

class AccountPasswordChange(BaseCog):
    """Cog handling updating credentials."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="account_password_change",
        description="Update user credentials."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_bind_credentials.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_password_change(
        self,
        interaction: discord.Interaction,
        old_password: str,
        new_password: str
    ):
        """Update user credentials."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                # Get discord user bind.
                discord_user = await self.discord_builder.select_discord_user(
                    session,
                    str(interaction.user.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        'No account registered for this discord user.'
                    )

                # Get user info.
                user = await self.user_builder.select_user_by_id(
                    session,
                    discord_user.user_id
                )

                if await check_password(old_password, user.password) is False:
                    raise UnmatchingPasswords(
                        'Passwords do not match.'
                    )
                
                #TODO: Password generation. Research password constraints.

                # Commit
                await session.commit()

            except (
                DiscordNotRegistered,
                UsernameIncorrect,
                UnmatchingPasswords
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Password Change Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            except (
                CoroutineFailed
            ) as e:
                logging.error("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Password Change Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            except Exception as e:
                logging.error("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Password Change Failed",
                        description="Unhandled exception.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            finally:
                # Close Session
                await session.close()

    @account_password_change.error
    async def on_account_password_change_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.account_bind_credentials.enabled:
        await client.add_cog(AccountPasswordChange(client))
