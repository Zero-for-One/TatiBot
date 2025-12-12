"""Configuration constants for the bot."""
from pathlib import Path

# Data file paths
DATA_DIR = Path("data")
GAMES_FILE = DATA_DIR / "games.json"
VOTES_FILE = DATA_DIR / "votes.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

