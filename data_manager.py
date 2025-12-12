"""Data management functions for games and votes."""
import json
from datetime import datetime
from pathlib import Path
from config import DATA_DIR, GAMES_FILE, VOTES_FILE


def get_next_game_id(games):
    """Get the next available game ID."""
    if not games:
        return 1
    existing_ids = [game.get("id", 0) for game in games.values() if game.get("id")]
    if not existing_ids:
        # If no IDs exist, assign starting from 1
        return 1
    return max(existing_ids) + 1


def load_games():
    """Load games from JSON file."""
    if GAMES_FILE.exists():
        with open(GAMES_FILE, 'r', encoding='utf-8') as f:
            games = json.load(f)
            # Ensure all games have IDs (backward compatibility)
            needs_save = False
            for game_key, game_data in games.items():
                if "id" not in game_data or not game_data.get("id"):
                    # Assign ID to games without one
                    game_data["id"] = get_next_game_id(games)
                    needs_save = True
            if needs_save:
                save_games(games)
            return games
    return {}


def save_games(games):
    """Save games to JSON file."""
    with open(GAMES_FILE, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)


def load_votes():
    """Load votes from JSON file."""
    if VOTES_FILE.exists():
        with open(VOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_votes(votes):
    """Save votes to JSON file."""
    with open(VOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(votes, f, indent=2, ensure_ascii=False)


def save_old_votes():
    """Save current votes to a dated backup file."""
    votes = load_votes()
    if not votes:
        return None
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    old_votes_file = DATA_DIR / f"votes.old.{date_str}.json"
    
    with open(old_votes_file, 'w', encoding='utf-8') as f:
        json.dump(votes, f, indent=2, ensure_ascii=False)
    
    return str(old_votes_file)


def get_latest_old_votes():
    """Get the most recent old votes file."""
    old_files = list(DATA_DIR.glob("votes.old.*.json"))
    if not old_files:
        return None
    
    # Sort by filename (which includes date) and get the latest
    latest_file = sorted(old_files, reverse=True)[0]
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def clear_votes(save_backup=True):
    """Clear all votes (used when starting a new voting period)."""
    if save_backup:
        save_old_votes()
    save_votes({})

