"""Utility commands (results, clear, sync)."""
import discord
from discord import app_commands
import logging
from data_manager import load_votes, load_games, save_old_votes, clear_votes, set_user_language, get_user_language
from translations import get_translation

logger = logging.getLogger(__name__)


def setup_utility_commands(bot: discord.ext.commands.Bot):
    """Register utility commands."""
    
    @bot.tree.command(name="language", description="Set your preferred language (English/Français)")
    @app_commands.describe(lang="Language code: 'en' for English, 'fr' for Français")
    @app_commands.choices(lang=[
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Français", value="fr")
    ])
    async def language(interaction: discord.Interaction, lang: str):
        """Set user's preferred language."""
        if not interaction.guild:
            t = lambda k: get_translation(k, lang="en")
            await interaction.response.send_message(t("error_server_only"), ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        
        if lang not in ["en", "fr"]:
            lang_name = get_user_language(user_id, guild_id)
            t = lambda k: get_translation(k, user_id=user_id, guild_id=guild_id)
            await interaction.response.send_message(
                t("language_invalid").format(options=t("language_options")),
                ephemeral=True
            )
            return
        
        success = set_user_language(user_id, lang, guild_id)
        
        if success:
            lang_names = {"en": "English", "fr": "Français"}
            t = lambda k: get_translation(k, lang=lang)  # Use new language for response
            await interaction.response.send_message(
                t("language_changed").format(lang=lang_names[lang]),
                ephemeral=True
            )
            logger.info(f"Language changed to {lang} for user {interaction.user} (ID: {user_id}) in guild {guild_id}")
        else:
            t = lambda k: get_translation(k, user_id=user_id, guild_id=guild_id)
            await interaction.response.send_message(
                t("language_invalid").format(options=t("language_options")),
                ephemeral=True
            )
    
    @bot.tree.command(name="help", description="Show how to use the bot and all available commands")
    async def help_command(interaction: discord.Interaction):
        """Display help information about the bot and its commands."""
        if not interaction.guild:
            t = lambda k: get_translation(k, lang="en")
            await interaction.response.send_message(t("error_server_only"), ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        
        embed = discord.Embed(
            title=t("help_title"),
            description=t("help_description"),
            color=discord.Color.blue()
        )
        
        # How It Works
        embed.add_field(
            name=t("help_how_it_works"),
            value=t("help_how_it_works_value"),
            inline=False
        )
        
        # Voting Commands
        embed.add_field(
            name=t("help_voting_commands"),
            value=t("help_voting_commands_value"),
            inline=False
        )
        
        # Game Management Commands
        embed.add_field(
            name=t("help_game_management"),
            value=t("help_game_management_value"),
            inline=False
        )
        
        # Results & Utilities
        embed.add_field(
            name=t("help_results_utilities"),
            value=t("help_results_utilities_value"),
            inline=False
        )
        
        # Rating System
        embed.add_field(
            name=t("help_rating_system"),
            value=t("help_rating_system_value"),
            inline=False
        )
        
        # Tips & Notes
        embed.add_field(
            name=t("help_tips"),
            value=t("help_tips_value"),
            inline=False
        )
        
        embed.set_footer(text=t("help_footer"))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Help command used by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
    
    @bot.tree.command(name="results", description="Show voting results and recommended game")
    async def results(interaction: discord.Interaction):
        """Show voting results and the most wanted game based on votes and player count."""
        if not interaction.guild:
            t = lambda k: get_translation(k, lang="en")
            await interaction.response.send_message(t("error_server_only"), ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        votes = load_votes(guild_id)
        games = load_games(guild_id)
        
        if not votes:
            await interaction.response.send_message(
                t("results_no_votes"),
                ephemeral=True
            )
            return
        
        # Count available players (people who voted AND are not marked unavailable)
        available_users = {
            uid: user_data for uid, user_data in votes.items()
            if not user_data.get("unavailable", False)
        }
        available_players = len(available_users)
        
        # Calculate game scores (sum of ratings) - only from available users
        # Games not voted on default to rating 0 per player
        game_scores = {}
        
        for game_key in games.keys():
            game_scores[game_key] = 0
        
        for user_data in available_users.values():
            user_game_votes = user_data.get("votes", {})
            for game_key in games.keys():
                # If user voted for this game, add their rating; otherwise add 0
                rating = user_game_votes.get(game_key, 0)
                game_scores[game_key] += rating
        
        # Filter games by player count compatibility
        compatible_games = {}
        for game_key, score in game_scores.items():
            game = games[game_key]
            if game["min_players"] <= available_players <= game["max_players"]:
                compatible_games[game_key] = score
        
        if not compatible_games:
            embed = discord.Embed(
                title=t("results_title"),
                description=t("results_available_players", count=available_players),
                color=discord.Color.orange()
            )
            embed.add_field(
                name=t("results_no_compatible"),
                value=t("results_no_compatible_desc", count=available_players),
                inline=False
            )
            
            # Show games that don't match
            embed.add_field(
                name="Available Games",
                value="\n".join([
                    f"{games[k].get('emoji', '🎮')} **{games[k]['name']}** - Needs {games[k]['min_players']}-{games[k]['max_players']} players (Score: {game_scores[k]})"
                    for k in sorted(game_scores.keys(), key=lambda x: game_scores[x], reverse=True)
                ]) or "None",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return
        
        # Find the best game
        best_game_key = max(compatible_games.items(), key=lambda x: x[1])[0]
        best_game = games[best_game_key]
        best_score = compatible_games[best_game_key]
        
        # Create results embed
        embed = discord.Embed(
            title=t("results_title"),
            description=t("results_available_players", count=available_players),
            color=discord.Color.gold()
        )
        
        # Show the winner
        best_emoji = best_game.get('emoji', '🎮')
        embed.add_field(
            name=t("results_recommended"),
            value=f"{best_emoji} **{best_game['name']}**\n"
                  f"{t('results_recommended_score', score=best_score)}\n"
                  f"{t('results_recommended_players', min=best_game['min_players'], max=best_game['max_players'])}",
            inline=False
        )
        
        # Show top 5 compatible games sorted by score
        sorted_games = sorted(compatible_games.items(), key=lambda x: x[1], reverse=True)[:5]  # Limit to top 5
        game_list = []
        for game_key, score in sorted_games:
            game = games[game_key]
            game_emoji = game.get('emoji', '🎮')
            marker = "🏆" if game_key == best_game_key else "•"
            game_list.append(
                f"{marker} {game_emoji} **{game['name']}** - {score} points (Players: {game['min_players']}-{game['max_players']})"
            )
        
        total_compatible = len(compatible_games)
        if total_compatible > 5:
            field_name = t("results_top_showing", total=total_compatible)
        else:
            field_name = t("results_all_games")
        
        embed.add_field(
            name=field_name,
            value="\n".join(game_list) if game_list else "None",
            inline=False
        )
        
        # Show who voted (only available users)
        voters = [available_users[uid]["username"] for uid in available_users.keys()]
        embed.add_field(
            name=t("results_voters"),
            value=", ".join(voters) if voters else "None",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="clearvotes", description="Clear all votes (start fresh)")
    async def clearvotes(interaction: discord.Interaction):
        """Clear all votes. Use this to start a new voting period."""
        if not interaction.guild:
            t = lambda k: get_translation(k, lang="en")
            await interaction.response.send_message(t("error_server_only"), ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        
        old_file = save_old_votes(guild_id)
        clear_votes(guild_id, save_backup=False)
        
        logger.info(f"Votes cleared manually by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
        if old_file:
            logger.info(f"Votes backed up to: {old_file}")
        
        message = t("clearvotes_success")
        if old_file:
            message += f"\n{t('clearvotes_backup', file=old_file.split('/')[-1])}"
        
        await interaction.response.send_message(message)
    
    
    @bot.tree.command(name="sync", description="Force sync commands (admin only - for instant updates)")
    async def sync(interaction: discord.Interaction):
        """Force sync commands to this server for instant updates."""
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            guild_id = interaction.guild.id if interaction.guild else None
            user_id = str(interaction.user.id)
            t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw) if guild_id else get_translation(k, lang="en", **kw)
            await interaction.response.send_message(
                t("error_need_admin"),
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Sync to this specific guild for instant update
            guild_id = interaction.guild.id
            user_id = str(interaction.user.id)
            t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
            
            bot.tree.copy_global_to(guild=interaction.guild)
            synced = await bot.tree.sync(guild=interaction.guild)
            
            await interaction.followup.send(
                t("sync_success", count=len(synced)),
                ephemeral=True
            )
        except Exception as e:
            guild_id = interaction.guild.id if interaction.guild else None
            user_id = str(interaction.user.id)
            t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw) if guild_id else get_translation(k, lang="en", **kw)
            await interaction.followup.send(
                t("sync_error", error=str(e)),
                ephemeral=True
            )

