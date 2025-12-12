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
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
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
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
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
            name="📖 How It Works",
            value="1. **Vote**: Use `/vote` to rate games from 1-5 stars\n"
                  "2. **Availability**: Voting marks you as available for game night\n"
                  "3. **Unavailable**: Use `/unavailable` to mark yourself unavailable (votes preserved)\n"
                  "4. **Available**: Use `/available` to mark yourself available again (votes restored)\n"
                  "5. **Results**: Use `/results` to see the top recommended game\n"
                  "6. **Auto Reset**: Votes reset every Wednesday at 11:59 PM\n"
                  "7. **Reminders**: Bot reminds everyone to vote every Sunday at 8 PM",
            inline=False
        )
        
        # Voting Commands
        embed.add_field(
            name="⭐ Voting Commands",
            value="**`/vote`** - Open interactive voting interface\n"
                  "• Select games from dropdown and rate them 1-5\n"
                  "• Default rating is 5 if not specified\n"
                  "• Games not voted on = rating 0\n"
                  "• Table updates automatically after each vote\n"
                  "• Use 'Restore Last Votes' to restore previous week's votes\n"
                  "• Voting automatically marks you as available\n\n"
                  "**`/myvotes`** - View all your current votes and availability status\n\n"
                  "**`/unavailable`** - Mark yourself unavailable (keeps your votes)\n\n"
                  "**`/available`** - Mark yourself available again (restores your votes)",
            inline=False
        )
        
        # Game Management Commands
        embed.add_field(
            name="🎮 Game Management",
            value="**`/addgame <name> [min_players] [max_players] [emoji]`**\n"
                  "• Add a new game (defaults: min=1, max=10, emoji=🎮)\n"
                  "• Games get unique IDs automatically\n\n"
                  "**`/listgames`** - Show all games with IDs and player counts\n\n"
                  "**`/removegame <ID or name>`** - Remove a game by ID or name\n\n"
                  "**`/updategame`** - Interactive menu to update game properties\n\n"
                  "**`/setgameemoji <game> <emoji>`** - Change a game's emoji",
            inline=False
        )
        
        # Results & Utilities
        embed.add_field(
            name="📊 Results & Utilities",
            value="**`/results`** - Show top 5 compatible games\n"
                  "• Filters games by player count compatibility\n"
                  "• Only counts available players (not marked unavailable)\n"
                  "• Shows scores based on available users' votes\n\n"
                  "**`/language <lang>`** - Set your preferred language\n"
                  "• Choose English (en) or Français (fr)\n"
                  "• All bot messages will appear in your language\n\n"
                  "**`/clearvotes`** - Manually clear all votes (saves backup)\n\n"
                  "**`/sync`** - Force sync commands (admin only)",
            inline=False
        )
        
        # Rating System
        embed.add_field(
            name="⭐ Rating System",
            value="**1 ⭐** - Don't want to play\n"
                  "**2 ⭐⭐** - Prefer not to\n"
                  "**3 ⭐⭐⭐** - Neutral/OK\n"
                  "**4 ⭐⭐⭐⭐** - Want to play\n"
                  "**5 ⭐⭐⭐⭐⭐** - Really want to play!",
            inline=False
        )
        
        # Tips & Notes
        embed.add_field(
            name="💡 Tips",
            value="• Use game IDs for easier management (shown in `/listgames`)\n"
                  "• Voting automatically marks you as available\n"
                  "• Use `/unavailable` to mark yourself unavailable (votes are preserved)\n"
                  "• Use `/available` to restore your votes when you're back\n"
                  "• Votes auto-reset every Wednesday at 11:59 PM\n"
                  "• Previous votes are backed up automatically\n"
                  "• Games must match player count to appear in results\n"
                  "• Each server has its own separate game list and votes\n"
                  "• Use `/language` to change your preferred language",
            inline=False
        )
        
        embed.set_footer(text="Need more help? Check the README or ask an admin!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Help command used by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
    
    @bot.tree.command(name="results", description="Show voting results and recommended game")
    async def results(interaction: discord.Interaction):
        """Show voting results and the most wanted game based on votes and player count."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
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
                title="📊 Voting Results",
                description=f"**Available Players:** {available_players}",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="⚠️ No Compatible Games",
                value=f"With {available_players} player(s), no games match the player count requirements.",
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
            title="📊 Voting Results",
            description=f"**Available Players:** {available_players}",
            color=discord.Color.gold()
        )
        
        # Show the winner
        best_emoji = best_game.get('emoji', '🎮')
        embed.add_field(
            name="🏆 Recommended Game",
            value=f"{best_emoji} **{best_game['name']}**\n"
                  f"Score: {best_score} points\n"
                  f"Players: {best_game['min_players']}-{best_game['max_players']} ✅",
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
        field_name = "Top 5 Compatible Games" if total_compatible > 5 else "All Compatible Games"
        if total_compatible > 5:
            field_name += f" (showing 5 of {total_compatible})"
        
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
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
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
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Sync to this specific guild for instant update
            bot.tree.copy_global_to(guild=interaction.guild)
            synced = await bot.tree.sync(guild=interaction.guild)
            
            await interaction.followup.send(
                f"✅ Successfully synced {len(synced)} command(s) to this server!\n"
                f"Commands should be available immediately.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to sync commands: {e}",
                ephemeral=True
            )

