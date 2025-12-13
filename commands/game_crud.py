"""Game CRUD commands (add, remove, update, list)."""
import discord
from discord import app_commands
import logging
from data_manager import load_games
from views.game_update import UpdateGameView, AddGameModal, RemoveGameView
from helpers import require_game_permission, send_guild_only_error, send_permission_error

logger = logging.getLogger(__name__)


def setup_game_crud_commands(bot: discord.ext.commands.Bot):
    """Register game CRUD commands."""
    
    @bot.tree.command(name="addgame", description="Add a new game to the list")
    async def addgame(interaction: discord.Interaction):
        """Add a new game to the voting list using a form."""
        result = require_game_permission(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_permission_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        guild_id, user_id, _ = result
        modal = AddGameModal(guild_id, user_id)
        await interaction.response.send_modal(modal)
    
    
    @bot.tree.command(name="removegame", description="Remove a game from the list using a dropdown")
    async def removegame(interaction: discord.Interaction):
        """Remove a game from the voting list using a dropdown menu."""
        result = require_game_permission(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_permission_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        guild_id, user_id, t = result
        games = load_games(guild_id)
        
        if not games:
            await interaction.response.send_message(t("error_no_games"), ephemeral=True)
            return
        
        embed = discord.Embed(
            title=t("game_remove_title"),
            description=t("game_remove_description"),
            color=discord.Color.red()
        )
        
        view = RemoveGameView(games, guild_id, user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    
    @bot.tree.command(name="updategame", description="Update a game's properties using an interactive menu")
    async def updategame(interaction: discord.Interaction):
        """Update properties of an existing game using dropdown and modal."""
        result = require_game_permission(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_permission_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        guild_id, user_id, t = result
        games = load_games(guild_id)
        
        if not games:
            await interaction.response.send_message(t("error_no_games"), ephemeral=True)
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
        from helpers import require_guild
        
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        games = load_games(guild_id)
        
        if not games:
            await interaction.response.send_message(t("error_no_games"))
            return
        
        embed = discord.Embed(title=t("game_list_title"), color=discord.Color.green())
        
        game_list = []
        for game_data in sorted(games.values(), key=lambda x: (x.get("id", 9999), x["name"])):
            emoji = game_data.get("emoji", "🎮")
            game_id = game_data.get("id", "?")
            line = f"{emoji} **[{game_id}] {game_data['name']}** - Players: {game_data['min_players']}-{game_data['max_players']}"
            store_links = game_data.get("store_links", "")
            if store_links:
                line += f"\n   🔗 {store_links}"
            game_list.append(line)
        
        embed.description = "\n".join(game_list)
        await interaction.response.send_message(embed=embed)
