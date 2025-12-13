"""Data management functions for games and votes."""
import json
from datetime import datetime
from pathlib import Path
from config import get_games_file, get_votes_file, get_guild_dir, get_config_file, get_schedules_file


def get_next_game_id(games):
    """Get the next available game ID."""
    if not games:
        return 1
    existing_ids = [game.get("id", 0) for game in games.values() if game.get("id")]
    if not existing_ids:
        # If no IDs exist, assign starting from 1
        return 1
    return max(existing_ids) + 1


def load_games(guild_id: int):
    """Load games from JSON file for a specific guild.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        Dictionary of games
    """
    games_file = get_games_file(guild_id)
    if games_file.exists():
        with open(games_file, 'r', encoding='utf-8') as f:
            games = json.load(f)
            # Ensure all games have IDs (backward compatibility)
            needs_save = False
            for game_key, game_data in games.items():
                if "id" not in game_data or not game_data.get("id"):
                    # Assign ID to games without one
                    game_data["id"] = get_next_game_id(games)
                    needs_save = True
            if needs_save:
                save_games(games, guild_id)
            return games
    return {}


def save_games(games, guild_id: int):
    """Save games to JSON file for a specific guild.
    
    Args:
        games: Dictionary of games to save
        guild_id: The Discord guild (server) ID
    """
    games_file = get_games_file(guild_id)
    with open(games_file, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)


def load_votes(guild_id: int):
    """Load votes from JSON file for a specific guild.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        Dictionary of votes
    """
    votes_file = get_votes_file(guild_id)
    if votes_file.exists():
        with open(votes_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_votes(votes, guild_id: int):
    """Save votes to JSON file for a specific guild.
    
    Args:
        votes: Dictionary of votes to save
        guild_id: The Discord guild (server) ID
    """
    votes_file = get_votes_file(guild_id)
    with open(votes_file, 'w', encoding='utf-8') as f:
        json.dump(votes, f, indent=2, ensure_ascii=False)


def save_old_votes(guild_id: int):
    """Save current votes to a dated backup file for a specific guild.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        Path to the backup file, or None if no votes to save
    """
    votes = load_votes(guild_id)
    if not votes:
        return None
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    guild_dir = get_guild_dir(guild_id)
    old_votes_file = guild_dir / f"votes.old.{date_str}.json"
    
    with open(old_votes_file, 'w', encoding='utf-8') as f:
        json.dump(votes, f, indent=2, ensure_ascii=False)
    
    return str(old_votes_file)


def find_user_votes_in_old_files(user_id: str, guild_id: int):
    """Search through all old vote files to find user's votes, starting from most recent.
    
    Args:
        user_id: The user's ID as a string
        guild_id: The Discord guild (server) ID
        
    Returns:
        Tuple of (votes_dict, filename) if found, (None, None) otherwise
    """
    guild_dir = get_guild_dir(guild_id)
    old_files = list(guild_dir.glob("votes.old.*.json"))
    if not old_files:
        return None, None
    
    # Sort by filename (which includes date) - newest first
    sorted_files = sorted(old_files, reverse=True)
    
    # Search through each file from newest to oldest
    for old_file in sorted_files:
        try:
            with open(old_file, 'r', encoding='utf-8') as f:
                old_votes = json.load(f)
                
            # Check if this user has votes in this file
            if user_id in old_votes:
                user_data = old_votes[user_id]
                user_votes = user_data.get("votes", {})
                # Only return if they actually have votes
                if user_votes:
                    return old_votes, str(old_file)
        except (json.JSONDecodeError, IOError) as e:
            # Skip corrupted or unreadable files
            continue
    
    # No votes found in any old file
    return None, None


def clear_votes(guild_id: int, save_backup=True):
    """Clear all votes for a specific guild (used when starting a new voting period).
    
    Args:
        guild_id: The Discord guild (server) ID
        save_backup: Whether to save a backup before clearing
    """
    if save_backup:
        save_old_votes(guild_id)
    save_votes({}, guild_id)


def get_user_language(user_id: str, guild_id: int) -> str:
    """Get user's preferred language from votes data for a specific guild.
    
    Args:
        user_id: The user's ID as a string
        guild_id: The Discord guild (server) ID
        
    Returns:
        Language code ('en' or 'fr'), defaults to 'en'
    """
    votes = load_votes(guild_id)
    user_data = votes.get(str(user_id), {})
    return user_data.get("language", "en")


def set_user_language(user_id: str, lang: str, guild_id: int) -> bool:
    """Set user's preferred language in votes data for a specific guild.
    
    Args:
        user_id: The user's ID as a string
        lang: Language code ('en' or 'fr')
        guild_id: The Discord guild (server) ID
        
    Returns:
        True if language is valid and set, False otherwise
    """
    if lang not in ["en", "fr"]:
        return False
    
    votes = load_votes(guild_id)
    user_id_str = str(user_id)
    
    if user_id_str not in votes:
        votes[user_id_str] = {
            "username": "",
            "votes": {},
            "language": lang
        }
    else:
        votes[user_id_str]["language"] = lang
    
    save_votes(votes, guild_id)
    return True


def load_server_config(guild_id: int):
    """Load server configuration from JSON file for a specific guild.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        Dictionary with server configuration (reminder_day, reminder_hour, reminder_minute, etc.)
    """
    config_file = get_config_file(guild_id)
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Ensure game_management_roles exists (backward compatibility)
            if "game_management_roles" not in config:
                config["game_management_roles"] = []
            return config
    # Default configuration
    return {
        "reminder_day": "sun",  # Sunday
        "reminder_hour": 20,     # 8 PM
        "reminder_minute": 0,
        "game_night_day": None,  # None means no recurring game night
        "game_night_hour": None,
        "game_night_minute": None,
        "game_management_roles": []  # Empty list means only admins can manage games
    }


def save_server_config(config: dict, guild_id: int):
    """Save server configuration to JSON file for a specific guild.
    
    Args:
        config: Dictionary with server configuration
        guild_id: The Discord guild (server) ID
    """
    config_file = get_config_file(guild_id)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_schedules(guild_id: int):
    """Load scheduled game nights from JSON file for a specific guild.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        List of scheduled game nights (each with id, datetime, description, etc.)
    """
    schedules_file = get_schedules_file(guild_id)
    if schedules_file.exists():
        with open(schedules_file, 'r', encoding='utf-8') as f:
            schedules = json.load(f)
            # Ensure it's a list
            if isinstance(schedules, list):
                return schedules
            return []
    return []


def save_schedules(schedules: list, guild_id: int):
    """Save scheduled game nights to JSON file for a specific guild.
    
    Args:
        schedules: List of scheduled game nights
        guild_id: The Discord guild (server) ID
    """
    schedules_file = get_schedules_file(guild_id)
    with open(schedules_file, 'w', encoding='utf-8') as f:
        json.dump(schedules, f, indent=2, ensure_ascii=False)


def add_schedule(guild_id: int, schedule_datetime: datetime, description: str = None):
    """Add a new scheduled game night.
    
    Args:
        guild_id: The Discord guild (server) ID
        schedule_datetime: datetime object for when the game night is scheduled
        description: Optional description for the game night
        
    Returns:
        The ID of the newly created schedule
    """
    schedules = load_schedules(guild_id)
    
    # Generate ID (use timestamp as ID for uniqueness)
    schedule_id = int(schedule_datetime.timestamp())
    
    new_schedule = {
        "id": schedule_id,
        "datetime": schedule_datetime.isoformat(),
        "description": description or "",
        "created_at": datetime.now().isoformat()
    }
    
    schedules.append(new_schedule)
    # Sort by datetime
    schedules.sort(key=lambda x: x["datetime"])
    save_schedules(schedules, guild_id)
    
    return schedule_id


def remove_schedule(guild_id: int, schedule_id: int):
    """Remove a scheduled game night by ID.
    
    Args:
        guild_id: The Discord guild (server) ID
        schedule_id: The ID of the schedule to remove
        
    Returns:
        True if schedule was found and removed, False otherwise
    """
    schedules = load_schedules(guild_id)
    original_count = len(schedules)
    schedules = [s for s in schedules if s.get("id") != schedule_id]
    
    if len(schedules) < original_count:
        save_schedules(schedules, guild_id)
        return True
    return False

