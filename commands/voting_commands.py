"""Voting commands."""
import discord
from discord import app_commands
import logging
from core.data_manager import load_games, load_votes
from views.voting_view import VotingView, _generate_vote_table_fields
from core.translations import get_translation

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
        # Include emoji only (no ID)
        display_name = f"{emoji} {game_name}"
        if len(display_name) > 25:
            display_name = display_name[:22] + "..."
        
        if rating > 0:
            rating_display = f"{rating}/5"
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
        
        votes = load_votes(guild_id)
        user_votes_data = votes.get(user_id, {}).get("votes", {})
        
        # Create embed with table of games and ratings
        embed = discord.Embed(
            title=t("vote_title"),
            description=t("vote_description"),
            color=discord.Color.blue()
        )
        
        # Generate table fields using helper function
        table_fields = generate_vote_table_fields(games, user_votes_data)
        for field_name, field_value in table_fields:
            embed.add_field(name=field_name, value=field_value, inline=False)
        
        view = VotingView(games, votes, guild_id, user_id)
        view.embed = embed  # Store embed reference for updates
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    
    @bot.tree.command(name="myvotes", description="View your current votes")
    async def myvotes(interaction: discord.Interaction):
        """Show your current votes."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        votes = load_votes(guild_id)
        games = load_games(guild_id)
        
        if not games:
            await interaction.response.send_message(
                t("error_no_games"),
                ephemeral=True
            )
            return
        
        user_votes = votes.get(user_id, {}).get("votes", {}) if user_id in votes else {}
        is_unavailable = votes.get(user_id, {}).get("unavailable", False) if user_id in votes else False
        
        embed = discord.Embed(
            title=t("myvotes_title"),
            description=t("myvotes_description"),
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
                    f"{emoji} **{game_data['name']}** - {rating}/5 {rating_emoji}"
                )
            else:
                vote_list.append(
                    f"{emoji} **{game_data['name']}** - 0/5 {t('myvotes_not_voted')}"
                )
        
        embed.description = "\n".join(vote_list)
        
        # Show availability status
        if is_unavailable:
            embed.set_footer(text="❌ You are marked as unavailable (use /available to mark yourself available)")
        elif user_votes:
            embed.set_footer(text=t("myvotes_available"))
        else:
            embed.set_footer(text=t("myvotes_unavailable"))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    
    @bot.tree.command(name="unavailable", description="Mark yourself as unavailable (keeps your votes)")
    async def unavailable(interaction: discord.Interaction):
        """Mark yourself as unavailable while keeping your votes."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        votes = load_votes(guild_id)
        
        from core.data_manager import save_votes
        
        # Initialize user entry if it doesn't exist
        if user_id not in votes:
            votes[user_id] = {
                "username": str(interaction.user),
                "votes": {},
                "unavailable": True,
                "language": "en"
            }
        else:
            # Check if already unavailable
            if votes[user_id].get("unavailable", False):
                await interaction.response.send_message(
                    t("unavailable_already"),
                    ephemeral=True
                )
                return
            
            # Mark as unavailable but keep votes
            votes[user_id]["unavailable"] = True
            votes[user_id]["username"] = str(interaction.user)
        
        save_votes(votes, guild_id)
        
        logger.info(f"User marked as unavailable: {interaction.user} (ID: {user_id}) in guild {guild_id}")
        
        await interaction.response.send_message(
            t("unavailable_success"),
            ephemeral=True
        )
    
    @bot.tree.command(name="available", description="Mark yourself as available (restores your votes)")
    async def available(interaction: discord.Interaction):
        """Mark yourself as available again."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
            
        guild_id = interaction.guild.id
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        votes = load_votes(guild_id)
        
        from core.data_manager import save_votes
        
        # Initialize user entry if it doesn't exist
        if user_id not in votes:
            votes[user_id] = {
                "username": str(interaction.user),
                "votes": {},
                "unavailable": False,
                "language": "en"
            }
            save_votes(votes, guild_id)
            await interaction.response.send_message(
                t("available_no_votes"),
                ephemeral=True
            )
            return
        
        # Check if already available
        if not votes[user_id].get("unavailable", False):
            await interaction.response.send_message(
                t("available_already"),
                ephemeral=True
            )
            return
        
        # Mark as available (votes are already preserved)
        votes[user_id]["unavailable"] = False
        votes[user_id]["username"] = str(interaction.user)
        save_votes(votes, guild_id)
        
        logger.info(f"User marked as available: {interaction.user} (ID: {user_id}) in guild {guild_id}")
        
        await interaction.response.send_message(
            t("available_success"),
            ephemeral=True
        )

