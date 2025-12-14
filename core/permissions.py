"""Permission checking utilities."""
import discord
from .data_manager import load_server_config


def can_manage_games(user: discord.Member, guild: discord.Guild) -> bool:
    """Check if a user can manage games (add/remove/update).
    
    Args:
        user: The Discord member to check
        guild: The Discord guild (server)
        
    Returns:
        True if user can manage games, False otherwise
    """
    # Admins can always manage games
    if user.guild_permissions.administrator:
        return True
    
    # Check role-based permissions
    config = load_server_config(guild.id)
    allowed_roles = config.get("game_management_roles", [])
    
    # If no roles configured, only admins can manage
    if not allowed_roles:
        return False
    
    # Check if user has any of the allowed roles
    user_role_ids = [role.id for role in user.roles]
    for role_id in allowed_roles:
        if role_id in user_role_ids:
            return True
    
    return False
