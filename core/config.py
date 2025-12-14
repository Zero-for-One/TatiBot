"""Configuration constants for the bot."""
from pathlib import Path

# Data directory structure: data/guilds/{guild_id}/
DATA_DIR = Path("data")
GUILDS_DIR = DATA_DIR / "guilds"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
GUILDS_DIR.mkdir(exist_ok=True)


def get_guild_dir(guild_id: int) -> Path:
    """Get the directory for a specific guild."""
    guild_dir = GUILDS_DIR / str(guild_id)
    guild_dir.mkdir(exist_ok=True)
    return guild_dir


def get_shared_games_file() -> Path:
    """Get the shared games file path (centralized for all servers)."""
    return DATA_DIR / "shared_games.json"


def get_games_file(guild_id: int) -> Path:
    """Get the games file path for a specific guild (legacy - for backward compatibility)."""
    return get_guild_dir(guild_id) / "games.json"


def get_votes_file(guild_id: int) -> Path:
    """Get the votes file path for a specific guild."""
    return get_guild_dir(guild_id) / "votes.json"


def get_config_file(guild_id: int) -> Path:
    """Get the server config file path for a specific guild."""
    return get_guild_dir(guild_id) / "config.json"


def get_schedules_file(guild_id: int) -> Path:
    """Get the scheduled game nights file path for a specific guild."""
    return get_guild_dir(guild_id) / "schedules.json"

