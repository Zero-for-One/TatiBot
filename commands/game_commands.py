"""Game management commands."""
import discord
from discord import app_commands
import logging
from data_manager import load_games, save_games
from views.game_update import UpdateGameView
from translations import get_translation

logger = logging.getLogger(__name__)


def setup_game_commands(bot: discord.ext.commands.Bot):
    """Register game management commands."""
    
    @bot.tree.command(name="addgame", description="Add a new game to the list")
    @app_commands.describe(
        name="The name of the game",
        min_players="Minimum number of players required (default: 1)",
        max_players="Maximum number of players supported (default: 10)",
        emoji="Emoji/emote for the game (default: 🎮)"
    )
    async def addgame(interaction: discord.Interaction, name: str, min_players: int = 1, max_players: int = 10, emoji: str = "🎮"):
        """Add a new game to the voting list."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        
        if min_players < 1:
            await interaction.response.send_message(
                t("game_invalid_min"),
                ephemeral=True
            )
            return
        
        if max_players < min_players:
            await interaction.response.send_message(
                t("game_invalid_max"),
                ephemeral=True
            )
            return
        
        games = load_games(guild_id)
        game_key = name.lower()
        
        if game_key in games:
            await interaction.response.send_message(
                t("game_exists", name=name),
                ephemeral=True
            )
            return
        
        from data_manager import get_next_game_id
        
        game_id = get_next_game_id(games)
        games[game_key] = {
            "id": game_id,
            "name": name,
            "min_players": min_players,
            "max_players": max_players,
            "emoji": emoji
        }
        save_games(games, guild_id)
        
        logger.info(f"Game added: '{name}' (Players: {min_players}-{max_players}, Emoji: {emoji}) by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
        
        await interaction.response.send_message(
            t("game_added", emoji=emoji, name=name, min_players=min_players, max_players=max_players)
        )
    
    
    @bot.tree.command(name="removegame", description="Remove a game from the list by ID or name")
    @app_commands.describe(game="The ID (number) or name of the game to remove (e.g., '5' or 'Minecraft')")
    async def removegame(interaction: discord.Interaction, game: str):
        """Remove a game from the voting list by ID or name."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        games = load_games(guild_id)
        
        # Try to find by ID first, then by name
        game_key = None
        game_name = None
        found_by_id = False
        
        # Check if input is a number (ID)
        try:
            game_id = int(game.strip())
            for key, game_data in games.items():
                if game_data.get("id") == game_id:
                    game_key = key
                    game_name = game_data["name"]
                    found_by_id = True
                    break
        except ValueError:
            # Not a number, search by name
            game_key = game.lower().strip()
            if game_key in games:
                game_name = games[game_key]["name"]
        
        if game_key is None or game_key not in games:
            await interaction.response.send_message(
                t("error_game_not_found", game=game),
                ephemeral=True
            )
            return
        
        game_id = games[game_key].get("id", "?")
        del games[game_key]
        save_games(games, guild_id)
        
        logger.info(f"Game removed: '{game_name}' (ID: {game_id}) by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
        
        await interaction.response.send_message(t("game_removed", game_id=game_id, game_name=game_name))
    
    
    @bot.tree.command(name="updategame", description="Update a game's properties using an interactive menu")
    async def updategame(interaction: discord.Interaction):
        """Update properties of an existing game using dropdown and modal."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        games = load_games(guild_id)
        
        if not games:
            await interaction.response.send_message(
                t("error_no_games"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=t("game_update_title"),
            description=t("game_update_description"),
            color=discord.Color.blue()
        )
        
        view = UpdateGameView(games, guild_id, user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    
    @bot.tree.command(name="listgames", description="Show all available games")
    async def listgames(interaction: discord.Interaction):
        """List all available games."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        games = load_games(guild_id)
        
        if not games:
            await interaction.response.send_message(t("error_no_games"))
            return
        
        embed = discord.Embed(
            title=t("game_list_title"),
            color=discord.Color.green()
        )
        
        game_list = []
        for game_data in sorted(games.values(), key=lambda x: (x.get("id", 9999), x["name"])):
            emoji = game_data.get("emoji", "🎮")
            game_id = game_data.get("id", "?")
            game_list.append(
                f"{emoji} **[{game_id}] {game_data['name']}** - Players: {game_data['min_players']}-{game_data['max_players']}"
            )
        
        embed.description = "\n".join(game_list)
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="setgameemoji", description="Change the emoji/emote for a game")
    @app_commands.describe(
        game="The name or ID of the game",
        emoji="The emoji/emote to use for this game"
    )
    async def setgameemoji(interaction: discord.Interaction, game: str, emoji: str):
        """Change the emoji for an existing game."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        games = load_games(guild_id)
        
        # Try to find by ID first, then by name
        game_key = None
        game_name = None
        
        # Check if input is a number (ID)
        try:
            game_id = int(game)
            for key, game_data in games.items():
                if game_data.get("id") == game_id:
                    game_key = key
                    game_name = game_data["name"]
                    break
        except ValueError:
            # Not a number, search by name
            game_key = game.lower()
            if game_key in games:
                game_name = games[game_key]["name"]
        
        if game_key is None or game_key not in games:
            await interaction.response.send_message(
                t("error_game_not_found", game=game),
                ephemeral=True
            )
            return
        
        old_emoji = games[game_key].get("emoji", "🎮")
        games[game_key]["emoji"] = emoji
        save_games(games, guild_id)
        
        logger.info(f"Game emoji changed: '{game_name}' from {old_emoji} to {emoji} by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
        
        # Show list of games instead of confirmation message
        embed = discord.Embed(
            title="🎮 Available Games",
            color=discord.Color.green()
        )
        
        game_list = []
        for game_data in sorted(games.values(), key=lambda x: (x.get("id", 9999), x["name"])):
            emoji_display = game_data.get("emoji", "🎮")
            game_id = game_data.get("id", "?")
            game_list.append(
                f"{emoji_display} **[{game_id}] {game_data['name']}** - Players: {game_data['min_players']}-{game_data['max_players']}"
            )
        
        embed.description = "\n".join(game_list)
        await interaction.response.send_message(embed=embed)

