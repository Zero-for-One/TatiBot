"""Game management commands (add, remove, update, list, configure)."""
import discord
from discord import app_commands
import logging
import re
from core.data_manager import load_games, save_games, load_server_config, save_server_config
from core.helpers import require_game_permission, require_admin, send_guild_only_error, send_permission_error, send_admin_error
from views.game_views import UpdateGameView, AddGameModal, RemoveGameView, GameListPaginationView

logger = logging.getLogger(__name__)


def setup_game_commands(bot: discord.ext.commands.Bot):
    """Register all game management commands."""
    
    # ========== Game CRUD Commands ==========
    
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
        from core.helpers import require_guild
        
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        games = load_games(guild_id)
        
        if not games:
            await interaction.response.send_message(t("error_no_games"))
            return
        
        # Prepare game list as tuples (game_key, game_data) sorted by ID and name
        games_list = sorted(
            [(key, game_data) for key, game_data in games.items()],
            key=lambda x: (x[1].get("id", 9999), x[1]["name"])
        )
        
        # Create pagination view
        view = GameListPaginationView(games_list, guild_id, user_id)
        embed = view.create_embed()
        
        await interaction.response.send_message(embed=embed, view=view)
    
    # ========== Game Configuration Commands ==========
    
    @bot.tree.command(name="setgameemoji", description="Change the emoji/emote for a game")
    @app_commands.describe(
        game="The name or ID of the game",
        emoji="The emoji/emote to use for this game"
    )
    async def setgameemoji(interaction: discord.Interaction, game: str, emoji: str):
        """Change the emoji for an existing game."""
        result = require_game_permission(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_permission_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        guild_id, user_id, t = result
        games = load_games(guild_id)
        
        # Try to find by ID first, then by name
        game_key = None
        game_name = None
        
        try:
            game_id = int(game)
            for key, game_data in games.items():
                if game_data.get("id") == game_id:
                    game_key = key
                    game_name = game_data["name"]
                    break
        except ValueError:
            game_key = game.lower()
            if game_key in games:
                game_name = games[game_key]["name"]
        
        if game_key is None or game_key not in games:
            await interaction.response.send_message(t("error_game_not_found", game=game), ephemeral=True)
            return
        
        old_emoji = games[game_key].get("emoji", "🎮")
        games[game_key]["emoji"] = emoji
        save_games(games, guild_id)
        
        logger.info(f"Game emoji changed: '{game_name}' from {old_emoji} to {emoji} by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
        
        # Show list of games
        embed = discord.Embed(title="🎮 Available Games", color=discord.Color.green())
        game_list = []
        for game_data in sorted(games.values(), key=lambda x: (x.get("id", 9999), x["name"])):
            emoji_display = game_data.get("emoji", "🎮")
            line = f"{emoji_display} **{game_data['name']}** - Players: {game_data['min_players']}-{game_data['max_players']}"
            store_links = game_data.get("store_links", "")
            if store_links:
                line += f"\n   🔗 {store_links}"
            game_list.append(line)
        
        embed.description = "\n".join(game_list)
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="setgameroles", description="Configure which roles can manage games (admin only)")
    @app_commands.describe(
        roles="Roles that can manage games (leave empty to allow only admins)"
    )
    async def setgameroles(interaction: discord.Interaction, roles: str = None):
        """Configure which roles can manage games."""
        result = require_admin(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_admin_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        guild_id, user_id, t = result
        config = load_server_config(guild_id)
        
        if not roles or not roles.strip():
            config["game_management_roles"] = []
            save_server_config(config, guild_id)
            await interaction.response.send_message(t("gameroles_cleared"), ephemeral=True)
            return
        
        # Parse role mentions or IDs
        role_ids = []
        role_names = []
        
        role_mentions = re.findall(r'<@&(\d+)>', roles)
        for role_id_str in role_mentions:
            try:
                role_id = int(role_id_str)
                role = interaction.guild.get_role(role_id)
                if role:
                    role_ids.append(role_id)
                    role_names.append(role.name)
            except ValueError:
                continue
        
        # Also try to find roles by name
        for role_name in roles.split(','):
            role_name = role_name.strip()
            if not role_name:
                continue
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role and role.id not in role_ids:
                role_ids.append(role.id)
                role_names.append(role.name)
        
        if not role_ids:
            await interaction.response.send_message(t("gameroles_invalid"), ephemeral=True)
            return
        
        config["game_management_roles"] = role_ids
        save_server_config(config, guild_id)
        
        logger.info(f"Game management roles updated: {role_names} by {interaction.user} (ID: {user_id}) in guild {guild_id}")
        
        roles_display = ", ".join([f"`{name}`" for name in role_names])
        await interaction.response.send_message(t("gameroles_set", roles=roles_display), ephemeral=True)
