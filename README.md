# TatiBot - Game Night Voting Discord Bot

A Discord bot to help organize game nights by allowing friends to vote on games and track availability.

## Features

- 🎮 **Game Management**: Add, remove, and update games with player count requirements and custom emojis
- ⭐ **Interactive Voting System**: Rate games from 1-5 using dropdown menus with live table updates
- 👥 **Availability Tracking**: Mark yourself available/unavailable while preserving your votes
- 📊 **Smart Results**: Shows top 5 compatible games based on votes and player count
- ⏰ **Automatic Reminders**: Sends reminders every Sunday at 8 PM to vote
- 🔄 **Auto Reset**: Automatically resets votes every Wednesday at 11:59 PM with backup
- 💾 **Vote Restoration**: Restore your personal votes from the previous voting period
- 🗂️ **Game IDs**: Easy game management with unique IDs for each game
- 🌐 **Multi-Language Support**: Choose between English and Français (French)
- 🏢 **Per-Server Data**: Each Discord server has its own separate game list and votes
- 📝 **Logging**: Daily log files created at midnight for tracking bot activity
- 🧹 **Auto Cleanup**: Automatically deletes old vote backups (30+ days) and logs (7+ days)

## Setup Instructions

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT (if you want member info)
5. Copy the bot token (you'll need this later)
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot` and `applications.commands`
8. Select bot permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
9. Copy the generated URL and open it in your browser to invite the bot to your server

### 2. Install Dependencies

Make sure you have Python 3.8+ installed, then:

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

Create a `.env` file in the project root:

```
DISCORD_TOKEN=your_bot_token_here
```

Replace `your_bot_token_here` with the token you copied from the Discord Developer Portal.

### 4. Run the Bot

```bash
python bot.py
```

The bot should now be online in your Discord server!

## Commands

### Game Management

- `/addgame <name> [min_players] [max_players] [emoji]` - Add a new game to the list
  - `min_players`: Minimum players (default: 1)
  - `max_players`: Maximum players (default: 10)
  - `emoji`: Custom emoji for the game (default: 🎮)
  - Each game gets a unique ID automatically
  - Example: `/addgame "Among Us" min_players:4 max_players:10 emoji:👻`

- `/removegame <game>` - Remove a game by ID or name
  - You can use the game's ID (number) or its name
  - Example: `/removegame 5` or `/removegame "Among Us"`

- `/listgames` - Show all available games with IDs and player requirements

- `/updategame` - Update a game's properties (interactive menu)
  - Opens a dropdown to select a game
  - Allows updating name, min/max players, and emoji via modal

- `/setgameemoji <game> <emoji>` - Change the emoji for a game
  - Can use game ID or name
  - Example: `/setgameemoji game:5 emoji:🎮`

### Voting

- `/vote` - Open interactive voting interface
  - Shows a live-updating table of all games and your current ratings
  - Use dropdowns to select a game and rate it (1-5 stars)
  - Rating defaults to 5 if not specified
  - Games not voted on = rating 0
  - **Auto-saves** when both game and rating are selected
  - **"Restore Last Votes"** button to restore your previous week's votes
  - Table automatically updates after each vote

- `/myvotes` - View all your current votes in detail
  - Shows games you've voted on and their ratings
  - Shows games you haven't voted on (rating 0)
  - Displays your availability status

- `/unavailable` - Mark yourself as unavailable (keeps your votes)
  - Your votes are preserved and will be restored when you mark yourself available again
  - You won't be counted in results while unavailable

- `/available` - Mark yourself as available again
  - Restores your previous votes automatically
  - You'll be counted in results again

### Results & Utilities

- `/results` - Show voting results and top 5 recommended games
  - Shows compatible games based on number of available players
  - Displays top 5 games sorted by score
  - Lists all voters (people who are available)

- `/clearvotes` - Manually clear all votes (admin recommended)
  - Saves a backup before clearing
  - Use for emergency resets or manual testing

- `/language <lang>` - Set your preferred language
  - Choose between English (en) or Français (fr)
  - All bot messages will appear in your chosen language
  - Example: `/language lang:English`

- `/sync` - Force sync commands to server (admin only)
  - Use this if commands aren't appearing after updates
  - Provides instant command updates without waiting

## How It Works

1. **Add Games**: Use `/addgame` to add games with their player count requirements and optional emoji
2. **Set Language** (optional): Use `/language` to choose your preferred language (English/Français)
3. **Vote**: Each week, players use `/vote` to open an interactive interface where they:
   - See all games in a live-updating table
   - Select games from a dropdown
   - Rate them 1-5 using another dropdown
   - Optionally restore votes from the previous week
4. **Availability**: 
   - Voting automatically marks you as available
   - Use `/unavailable` to mark yourself unavailable (votes are preserved)
   - Use `/available` to mark yourself available again (votes are restored)
5. **Results**: Use `/results` to see the top 5 compatible games based on votes and player count
   - Only counts available players (not marked as unavailable)
6. **Automatic Workflow**:
   - **Sunday 8 PM**: Bot sends reminder to vote
   - **Wednesday 11:59 PM**: Bot automatically resets all votes and saves backup
   - **Daily 2 AM**: Bot cleans up old vote backups (30+ days) and log files (7+ days)

## Project Structure

```
TatiBot/
├── bot.py                 # Main bot entry point
├── config.py              # Configuration and constants
├── data_manager.py        # Data loading/saving functions
├── logger_config.py       # Logging configuration
├── scheduler.py           # Scheduled tasks (reminders, resets, cleanup)
├── translations.py         # Translation strings (English/French)
├── commands/              # Command modules
│   ├── game_commands.py   # Game management commands
│   ├── voting_commands.py # Voting commands
│   └── utility_commands.py # Results, clear, sync, language, help
├── views/                 # Discord UI components
│   ├── voting_view.py     # Interactive voting interface
│   └── game_update.py     # Game update interface
├── data/                  # Data storage
│   └── guilds/            # Per-server data (one folder per server)
│       └── {guild_id}/    # Server-specific data
│           ├── games.json      # Games list for this server
│           ├── votes.json      # Current votes for this server
│           └── votes.old.*.json # Vote backups (auto-created)
└── logs/                  # Log files
    └── bot_YYYY-MM-DD.log # Daily log files (created at midnight)
```

## Data Storage

The bot stores data per-server in the `data/guilds/` directory:
- Each Discord server gets its own folder: `data/guilds/{server_id}/`
- `games.json` - List of all games with IDs, names, player counts, and emojis (per server)
- `votes.json` - Current votes, availability status, and language preferences (per server)
- `votes.old.YYYY-MM-DD.json` - Automatic vote backups when votes are reset (per server)

**Important**: Each server has completely separate game lists and votes. Users on different servers cannot see each other's games or votes.

Log files are stored in the `logs/` directory:
- `bot_YYYY-MM-DD.log` - One log file per day (created at midnight)
- Old log files are automatically deleted after 7 days

## Example Workflow

1. **Setup** (one-time): Admin adds games:
   - `/addgame name:"Among Us" min_players:4 max_players:10 emoji:👻`
   - `/addgame name:"Astroneer" min_players:1 max_players:4 emoji:🚀`

2. **Weekly Voting** (Sunday reminder or anytime):
   - Players use `/vote` to open the interactive interface
   - Select games from dropdown and rate them 1-5
   - Can restore previous week's votes with one click
   - Table updates automatically after each vote

3. **Game Night**: Someone runs `/results`
   - Bot shows: "5 players available"
   - Top 5 compatible games listed by score
   - Recommended game highlighted

4. **Automatic Reset**: Wednesday at 11:59 PM
   - Bot saves current votes to `votes.old.YYYY-MM-DD.json`
   - Clears all votes for new voting period
   - Sends notification to server

5. **Maintenance** (automatic):
   - Daily cleanup of old vote backups (30+ days)
   - Daily cleanup of old log files (7+ days)
   - New log file created every day at midnight

## Troubleshooting

- **Bot not responding**: 
  - Make sure the bot is online and has proper permissions in your server
  - Check console output for errors
  - Review log files in `logs/` directory

- **Commands not showing**:
  - Wait a few minutes after starting the bot for commands to sync
  - Use `/sync` command (admin only) for instant updates
  - If still not working, check that the bot has `applications.commands` scope

- **Sunday reminder not working**:
  - Make sure the bot is running continuously
  - Check logs for scheduler activity
  - Consider using a hosting service for 24/7 uptime

- **Vote table not updating**:
  - Make sure both game and rating are selected in the dropdowns
  - The table should auto-update after vote is saved
  - Try refreshing the `/vote` command

- **Log files not rotating**:
  - Log files are created at midnight each day
  - Ensure the bot is running at midnight for proper rotation
  - Old logs are automatically cleaned after 7 days

## Notes

- **Continuous Running**: The bot needs to be running 24/7 for scheduled tasks (reminders, resets, cleanup) to work
- **Hosting**: Consider hosting on a cloud service (Heroku, Railway, VPS, etc.) for reliable uptime
- **Game IDs**: Games are automatically assigned unique IDs when added - use these for easier management
- **Vote Defaults**: 
  - Default rating is 5 (if not specified when voting)
  - Games not voted on default to rating 0
- **Availability System**:
  - Voting automatically marks you as available
  - Use `/unavailable` to mark yourself unavailable (votes are preserved, not deleted)
  - Use `/available` to mark yourself available again (votes are restored)
  - Unavailable users are not counted in results or player count
- **Language Support**:
  - Each user can set their preferred language with `/language`
  - Available languages: English (en) and Français (fr)
  - All bot messages, placeholders, and options are translated
- **Per-Server Data**:
  - Each Discord server has its own game list and votes
  - Data is stored in `data/guilds/{server_id}/`
  - Servers are completely isolated from each other
- **Backup Files**: Vote backups are automatically created when votes are reset (Wednesdays at 11:59 PM)
- **Log Files**: 
  - One log file per day (created at midnight)
  - Logs older than 7 days are automatically deleted
  - Check `logs/` directory for debugging information

