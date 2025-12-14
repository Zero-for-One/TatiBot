"""Common helper functions for commands."""
import discord
from typing import Optional, Callable
from .translations import get_translation
from .permissions import can_manage_games


def require_guild(interaction: discord.Interaction) -> Optional[tuple]:
    """Check if interaction is in a guild. Returns (guild_id, user_id, t) or None."""
    if not interaction.guild:
        t = lambda k: get_translation(k, lang="en")
        return None
    guild_id = interaction.guild.id
    user_id = str(interaction.user.id)
    t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
    return (guild_id, user_id, t)


async def send_guild_only_error(interaction: discord.Interaction):
    """Send error message for guild-only commands."""
    t = lambda k: get_translation(k, lang="en")
    await interaction.response.send_message(t("error_server_only"), ephemeral=True)


async def send_permission_error(interaction: discord.Interaction, guild_id: int, user_id: str):
    """Send error message for permission denied."""
    t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
    await interaction.response.send_message(
        t("error_need_permission"),
        ephemeral=True
    )


async def send_admin_error(interaction: discord.Interaction, guild_id: Optional[int] = None, user_id: Optional[str] = None):
    """Send error message for admin-only commands."""
    if guild_id and user_id:
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
    else:
        t = lambda k: get_translation(k, lang="en")
    await interaction.response.send_message(
        t("error_need_admin"),
        ephemeral=True
    )


def require_game_permission(interaction: discord.Interaction) -> Optional[tuple]:
    """Check if user can manage games. Returns (guild_id, user_id, t) or None."""
    result = require_guild(interaction)
    if result is None:
        return None
    
    guild_id, user_id, t = result
    
    if not can_manage_games(interaction.user, interaction.guild):
        return None
    
    return (guild_id, user_id, t)


def require_admin(interaction: discord.Interaction) -> Optional[tuple]:
    """Check if user is admin. Returns (guild_id, user_id, t) or None."""
    result = require_guild(interaction)
    if result is None:
        return None
    
    guild_id, user_id, t = result
    
    if not interaction.user.guild_permissions.administrator:
        return None
    
    return (guild_id, user_id, t)
