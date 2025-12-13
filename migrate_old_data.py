"""Script to migrate old game and vote data to new format."""
import json
from pathlib import Path
from data_manager import save_games, save_votes, get_next_game_id

# Server ID
GUILD_ID = 454184083136839680

# User mapping: Discord username -> old data column name
USER_MAPPING = {
    "nada_impetuoso": "Adrien",
    "torlister": "Renzo",
    "servietsky4778": "Jean",
    "jesuisjamaissurdidi": "Pierre-Louis"
}

# Reverse mapping for parsing
COLUMN_TO_USER = {v: k for k, v in USER_MAPPING.items()}


def parse_rating(value):
    """Parse rating value from old format.
    - Empty string or None -> 0
    - -1 -> 1 (don't want to play, but still a vote)
    - 500000 -> 5 (special case for Rematch)
    - Otherwise return as int
    """
    if not value or value == "":
        return 0
    try:
        val = int(value)
        if val == -1:
            return 1  # Don't want to play = 1 star
        if val == 500000:
            return 5  # Special case
        if val < 0:
            return 0
        if val > 5:
            return 5
        return val
    except (ValueError, TypeError):
        return 0


def migrate_data():
    """Migrate old data from text file to new JSON format."""
    old_file = Path("data/old_games_and votes.txt")
    
    if not old_file.exists():
        print(f"[ERROR] File not found: {old_file}")
        return
    
    print(f"[INFO] Reading old data from {old_file}...")
    
    # Read and parse the file
    games = {}
    votes_data = {}
    
    with open(old_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        print("[ERROR] File is empty!")
        return
    
    # Parse header
    header = lines[0].strip().split('\t')
    print(f"[INFO] Header: {header}")
    
    # Find column indices
    game_col = 0
    user_columns = {}
    for i, col in enumerate(header):
        if col == "Jeux":
            game_col = i
        elif col in COLUMN_TO_USER:
            user_columns[col] = i
    
    print(f"[INFO] Game column: {game_col}")
    print(f"[INFO] User columns: {user_columns}")
    
    # Parse each game row
    game_id = 1
    for line_num, line in enumerate(lines[1:], start=2):
        parts = line.strip().split('\t')
        if not parts or not parts[0]:
            continue
        
        game_name = parts[game_col].strip()
        if not game_name:
            continue
        
        # Create game entry
        game_key = game_name.lower()
        games[game_key] = {
            "id": game_id,
            "name": game_name,
            "min_players": 1,  # Default, can be updated later
            "max_players": 10,  # Default, can be updated later
            "emoji": "🎮"
        }
        game_id += 1
        
        # Parse votes for each user
        for old_name, col_idx in user_columns.items():
            discord_username = COLUMN_TO_USER[old_name]
            
            # Initialize user in votes if not exists
            if discord_username not in votes_data:
                votes_data[discord_username] = {
                    "username": discord_username,
                    "votes": {},
                    "unavailable": False,
                    "language": "en"
                }
            
            # Get rating
            if col_idx < len(parts):
                rating = parse_rating(parts[col_idx])
                if rating > 0:  # Only store non-zero votes
                    votes_data[discord_username]["votes"][game_key] = rating
    
    print(f"\n[SUCCESS] Parsed {len(games)} games")
    print(f"[SUCCESS] Parsed votes for {len(votes_data)} users")
    
    # Save games
    print(f"\n[INFO] Saving games to data/guilds/{GUILD_ID}/games.json...")
    save_games(games, GUILD_ID)
    print(f"[SUCCESS] Saved {len(games)} games")
    
    # Save votes
    print(f"\n[INFO] Saving votes to data/guilds/{GUILD_ID}/votes.json...")
    save_votes(votes_data, GUILD_ID)
    print(f"[SUCCESS] Saved votes for {len(votes_data)} users")
    
    # Print summary
    print("\n[SUMMARY]")
    print(f"   Games: {len(games)}")
    for username, user_data in votes_data.items():
        vote_count = len([v for v in user_data["votes"].values() if v > 0])
        print(f"   {username}: {vote_count} games voted")
    
    print("\n[SUCCESS] Migration complete!")


if __name__ == "__main__":
    migrate_data()
