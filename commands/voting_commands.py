"""Voting commands."""
import discord
from discord import app_commands
import logging
from data_manager import load_games, load_votes
from views.voting_view import VotingView, _generate_vote_table_fields

logger = logging.getLogger(__name__)


def generate_vote_table_fields(games, user_votes_data):
    """Generate embed table fields for the voting table. Re-exported from views."""
    return _generate_vote_table_fields(games, user_votes_data)
    """Generate embed table fields for the voting table.
    
    Args:
        games: Dictionary of games
        user_votes_data: Dictionary of user's votes {game_key: rating}
    
    Returns:
        List of tuples (field_name, field_value) for embed.add_field()
    """
    sorted_games = sorted(games.items(), key=lambda x: (x[1].get("id", 9999), x[1]["name"]))
    MAX_FIELD_LENGTH = 1000  # Leave some buffer under 1024
    
    # Build compact table format
    table_chunks = []
    current_chunk = []
    current_length = 0
    
    # Add header
    header = "```\nGame" + " " * 25 + "Rating  Players\n" + "─" * 50 + "\n"
    current_chunk.append(header)
    current_length = len(header)
    
    for game_key, game_data in sorted_games:
        game_name = game_data["name"]
        game_id = game_data.get("id", "?")
        emoji = game_data.get("emoji", "🎮")
        rating = user_votes_data.get(game_key, 0)
        players = f"{game_data['min_players']}-{game_data['max_players']}"
        
        # More compact format - shorter game names, simpler rating
        # Include emoji and ID in the display
        display_name = f"{emoji} [{game_id}] {game_name}"
        if len(display_name) > 22:
            display_name = display_name[:19] + "..."
        
        if rating > 0:
            rating_display = f"{rating}/5 {'⭐' * rating}"
        else:
            rating_display = "0/5"
        
        line = f"{display_name:<25} {rating_display:<8} {players}\n"
        
        # Check if adding this line would exceed the limit
        if current_length + len(line) + 3 > MAX_FIELD_LENGTH:  # +3 for closing ```
            # Close current chunk and start new one
            current_chunk.append("```")
            table_chunks.append("".join(current_chunk))
            current_chunk = [header]  # Start new chunk with header
            current_length = len(header)
        
        current_chunk.append(line)
        current_length += len(line)
    
    # Close the last chunk
    if current_chunk:
        current_chunk.append("```")
        table_chunks.append("".join(current_chunk))
    
    # Return list of (field_name, field_value) tuples
    fields = []
    for i, chunk in enumerate(table_chunks):
        field_name = "📊 Your Votes" if i == 0 else f"📊 Your Votes (cont.)"
        fields.append((field_name, chunk))
    
    return fields


def setup_voting_commands(bot: discord.ext.commands.Bot):
    """Register voting commands."""
    
    @bot.tree.command(name="vote", description="Vote for games using an interactive menu")
    async def vote(interaction: discord.Interaction):
        """Interactive voting interface with dropdown menus."""
        games = load_games()
        
        if not games:
            await interaction.response.send_message(
                "❌ No games in the list yet! Use `/addgame` to add some games first.",
                ephemeral=True
            )
            return
        
        votes = load_votes()
        user_id = str(interaction.user.id)
        user_votes_data = votes.get(user_id, {}).get("votes", {})
        
        # Create embed with table of games and ratings
        embed = discord.Embed(
            title="🎮 Game Voting",
            description="1. Select a game from the dropdown\n"
                       "2. Select a rating (1-5)\n"
                       "Vote is automatically saved when both are selected.\n\n"
                       "Not voting for a game means rating 0 (don't want to play).",
            color=discord.Color.blue()
        )
        
        # Generate table fields using helper function
        table_fields = generate_vote_table_fields(games, user_votes_data)
        for field_name, field_value in table_fields:
            embed.add_field(name=field_name, value=field_value, inline=False)
        
        view = VotingView(games, votes)
        view.embed = embed  # Store embed reference for updates
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    
    @bot.tree.command(name="myvotes", description="View your current votes")
    async def myvotes(interaction: discord.Interaction):
        """Show your current votes."""
        votes = load_votes()
        user_id = str(interaction.user.id)
        games = load_games()
        
        if not games:
            await interaction.response.send_message(
                "❌ No games in the list yet!",
                ephemeral=True
            )
            return
        
        user_votes = votes.get(user_id, {}).get("votes", {}) if user_id in votes else {}
        
        embed = discord.Embed(
            title="Your Votes",
            description="Games you haven't voted for default to rating 0.",
            color=discord.Color.blue()
        )
        
        vote_list = []
        for game_key, game_data in sorted(games.items(), key=lambda x: (x[1].get("id", 9999), x[1]["name"])):
            emoji = game_data.get("emoji", "🎮")
            game_id = game_data.get("id", "?")
            rating = user_votes.get(game_key, 0)
            if rating > 0:
                rating_emoji = "⭐" * rating
                vote_list.append(
                    f"{emoji} **[{game_id}] {game_data['name']}** - {rating}/5 {rating_emoji}"
                )
            else:
                vote_list.append(
                    f"{emoji} **[{game_id}] {game_data['name']}** - 0/5 (not voted)"
                )
        
        embed.description = "\n".join(vote_list)
        
        # Show availability status
        if user_votes:
            embed.set_footer(text="✅ You are marked as available for game night")
        else:
            embed.set_footer(text="❌ You are not marked as available (no votes)")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    
    @bot.tree.command(name="unavailable", description="Mark yourself as unavailable (removes your votes)")
    async def unavailable(interaction: discord.Interaction):
        """Remove your votes to mark yourself as unavailable."""
        votes = load_votes()
        user_id = str(interaction.user.id)
        
        from data_manager import save_votes
        
        if user_id in votes:
            del votes[user_id]
            save_votes(votes)
            await interaction.response.send_message(
                "✅ You've been marked as unavailable. Your votes have been removed."
            )
        else:
            await interaction.response.send_message(
                "ℹ️ You weren't marked as available (no votes to remove).",
                ephemeral=True
            )

