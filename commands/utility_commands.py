"""Utility commands (results, clear, sync)."""
import discord
from discord import app_commands
import logging
from data_manager import load_votes, load_games, save_old_votes, clear_votes

logger = logging.getLogger(__name__)


def setup_utility_commands(bot: discord.ext.commands.Bot):
    """Register utility commands."""
    
    @bot.tree.command(name="results", description="Show voting results and recommended game")
    async def results(interaction: discord.Interaction):
        """Show voting results and the most wanted game based on votes and player count."""
        votes = load_votes()
        games = load_games()
        
        if not votes:
            await interaction.response.send_message(
                "❌ No votes yet! Use `/vote` to start voting.",
                ephemeral=True
            )
            return
        
        # Count available players (people who voted)
        available_players = len(votes)
        
        # Calculate game scores (sum of ratings)
        # Games not voted on default to rating 0 per player
        game_scores = {}
        num_voters = len(votes)
        
        for game_key in games.keys():
            game_scores[game_key] = 0
        
        for user_data in votes.values():
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
        
        # Show who voted
        voters = [votes[uid]["username"] for uid in votes.keys()]
        embed.add_field(
            name="👥 Voters (Available)",
            value=", ".join(voters) if voters else "None",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    
    @bot.tree.command(name="clearvotes", description="Clear all votes (start fresh)")
    async def clearvotes(interaction: discord.Interaction):
        """Clear all votes. Use this to start a new voting period."""
        old_file = save_old_votes()
        clear_votes(save_backup=False)
        
        logger.info(f"Votes cleared manually by {interaction.user} (ID: {interaction.user.id})")
        if old_file:
            logger.info(f"Votes backed up to: {old_file}")
        
        message = "✅ All votes have been cleared! Ready for a new voting period."
        if old_file:
            message += f"\n📁 Previous votes saved to: `{old_file}`"
        
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

