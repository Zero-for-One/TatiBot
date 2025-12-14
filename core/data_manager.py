"""Data management functions for games and votes."""
import json
from datetime import datetime
from pathlib import Path
from .config import get_games_file, get_shared_games_file, get_votes_file, get_guild_dir, get_config_file, get_schedules_file
from .config import GUILDS_DIR


def get_next_game_id(games):
    """Get the next available game ID."""
    if not games:
        return 1
    existing_ids = [game.get("id", 0) for game in games.values() if game.get("id")]
    if not existing_ids:
        # If no IDs exist, assign starting from 1
        return 1
    return max(existing_ids) + 1


def load_shared_games() -> dict:
    """Load all shared game definitions (full game data).
    
    Returns:
        Dictionary of all shared games with full definitions
    """
    shared_games_file = get_shared_games_file()
    
    if shared_games_file.exists():
        with open(shared_games_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_server_game_list(guild_id: int) -> list:
    """Load server-specific list of enabled game keys.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        List of game keys (strings) that are enabled on this server
    """
    games_file = get_games_file(guild_id)
    
    if games_file.exists():
        with open(games_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Support both old format (dict) and new format (list of keys)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Legacy format: convert to list of keys
                return list(data.keys())
    return []


def load_games(guild_id: int):
    """Load games for a specific server.
    Combines shared game definitions with server-specific game list.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        Dictionary of games (only games enabled on this server, with full data from shared)
    """
    # Load shared game definitions (all games with full data)
    shared_games = load_shared_games()
    
    # Load server-specific game list (which games are enabled on this server)
    server_game_keys = load_server_game_list(guild_id)
    
    # If server has no game list yet, migrate from legacy format
    if not server_game_keys and shared_games:
        legacy_games_file = get_games_file(guild_id)
        if legacy_games_file.exists():
            try:
                with open(legacy_games_file, 'r', encoding='utf-8') as f:
                    legacy_data = json.load(f)
                    if isinstance(legacy_data, dict):
                        # Migrate: use all keys from legacy file
                        server_game_keys = list(legacy_data.keys())
                        # Save as new format (list of keys)
                        save_server_game_list(server_game_keys, guild_id)
            except Exception:
                pass
    
    # Return only games that are in server's list, with full data from shared
    result = {}
    for game_key in server_game_keys:
        if game_key in shared_games:
            result[game_key] = shared_games[game_key].copy()
        # If game not in shared, it will be missing (could add warning)
    
    return result


def save_shared_games(games: dict):
    """Save shared game definitions (full game data).
    
    Args:
        games: Dictionary of all shared games with full definitions
    """
    shared_games_file = get_shared_games_file()
    with open(shared_games_file, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)


def save_server_game_list(game_keys: list, guild_id: int):
    """Save server-specific list of enabled game keys.
    
    Args:
        game_keys: List of game keys (strings) that are enabled on this server
        guild_id: The Discord guild (server) ID
    """
    games_file = get_games_file(guild_id)
    with open(games_file, 'w', encoding='utf-8') as f:
        json.dump(game_keys, f, indent=2, ensure_ascii=False)


def add_game_to_shared(game_key: str, game_data: dict):
    """Add or update a game in the shared games database.
    
    Args:
        game_key: The game key (lowercase name)
        game_data: Full game data dictionary
    """
    shared_games = load_shared_games()
    shared_games[game_key] = game_data.copy()
    save_shared_games(shared_games)


def add_game_to_server(game_key: str, guild_id: int):
    """Add a game to a server's enabled game list.
    
    Args:
        game_key: The game key (lowercase name)
        guild_id: The Discord guild (server) ID
    """
    server_game_keys = load_server_game_list(guild_id)
    if game_key not in server_game_keys:
        server_game_keys.append(game_key)
        save_server_game_list(server_game_keys, guild_id)


def remove_game_from_server(game_key: str, guild_id: int):
    """Remove a game from a server's enabled game list (but keep in shared).
    
    Args:
        game_key: The game key (lowercase name)
        guild_id: The Discord guild (server) ID
    """
    server_game_keys = load_server_game_list(guild_id)
    if game_key in server_game_keys:
        server_game_keys.remove(game_key)
        save_server_game_list(server_game_keys, guild_id)


def save_games(games, guild_id: int):
    """Save games - updates both shared definitions and server list.
    This is a convenience function for backward compatibility.
    
    Args:
        games: Dictionary of games (for this server)
        guild_id: The Discord guild (server) ID
    """
    # Update shared games with any new/updated definitions
    shared_games = load_shared_games()
    for game_key, game_data in games.items():
        shared_games[game_key] = game_data.copy()
    save_shared_games(shared_games)
    
    # Update server's game list (just the keys)
    server_game_keys = list(games.keys())
    save_server_game_list(server_game_keys, guild_id)


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


def export_guild_data(guild_id: int) -> dict:
    """Export all guild data (shared games, votes, config, schedules) to a dictionary.
    
    Note: Games are now centralized (shared across all servers), but are still included in exports.
    
    Args:
        guild_id: The Discord guild (server) ID
        
    Returns:
        Dictionary containing all guild data
    """
    return {
        "guild_id": guild_id,
        "export_date": datetime.now().isoformat(),
        "shared_games": load_shared_games(),  # Load shared games (all definitions)
        "server_game_list": load_server_game_list(guild_id),  # Load server's game list
        "votes": load_votes(guild_id),
        "config": load_server_config(guild_id),
        "schedules": load_schedules(guild_id)
    }


def import_guild_data(guild_id: int, data: dict, overwrite: bool = False) -> dict:
    """Import guild data from a dictionary.
    
    Note: Games are now centralized (shared across all servers), so importing games affects all servers.
    
    Args:
        guild_id: The Discord guild (server) ID
        data: Dictionary containing data to import (from export_guild_data)
        overwrite: If True, completely replace existing data. If False, merge data.
        
    Returns:
        Dictionary with import results: {"games": count, "votes": count, "config": bool, "schedules": count, "errors": []}
    """
    results = {
        "games": 0,
        "votes": 0,
        "config": False,
        "schedules": 0,
        "errors": []
    }
    
    try:
        # Import games (shared across all servers)
        if "shared_games" in data or "games" in data:
            # Support both old format ("games") and new format ("shared_games")
            games_data = data.get("shared_games") or data.get("games", {})
            shared_games = load_shared_games()
            if overwrite:
                save_shared_games(games_data)
                results["games"] = len(games_data)
            else:
                # Merge: existing games take precedence, add new ones
                merged_games = {**games_data, **shared_games}
                save_shared_games(merged_games)
                results["games"] = len(games_data)
        
        # Import server game list if provided
        if "server_game_list" in data:
            save_server_game_list(data["server_game_list"], guild_id)
        
        # Import votes
        if "votes" in data:
            if overwrite:
                save_votes(data["votes"], guild_id)
                results["votes"] = len(data["votes"])
            else:
                # Merge: existing votes take precedence, add new users
                existing_votes = load_votes(guild_id)
                merged_votes = {**data["votes"], **existing_votes}
                save_votes(merged_votes, guild_id)
                results["votes"] = len(data["votes"])
        
        # Import config
        if "config" in data:
            if overwrite:
                save_server_config(data["config"], guild_id)
                results["config"] = True
            else:
                # Merge: existing config takes precedence, add missing keys
                existing_config = load_server_config(guild_id)
                merged_config = {**data["config"], **existing_config}
                save_server_config(merged_config, guild_id)
                results["config"] = True
        
        # Import schedules
        if "schedules" in data:
            if overwrite:
                save_schedules(data["schedules"], guild_id)
                results["schedules"] = len(data["schedules"])
            else:
                # Merge: combine lists, remove duplicates by ID
                existing_schedules = load_schedules(guild_id)
                existing_ids = {s.get("id") for s in existing_schedules}
                new_schedules = [s for s in data["schedules"] if s.get("id") not in existing_ids]
                merged_schedules = existing_schedules + new_schedules
                # Sort by datetime
                merged_schedules.sort(key=lambda x: x.get("datetime", ""))
                save_schedules(merged_schedules, guild_id)
                results["schedules"] = len(new_schedules)
                
    except Exception as e:
        results["errors"].append(str(e))
    
    return results

