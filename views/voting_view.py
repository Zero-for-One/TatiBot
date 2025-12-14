"""Voting view for interactive game voting."""
import discord
import asyncio
import logging
from core.data_manager import load_votes, save_votes, find_user_votes_in_old_files
from core.translations import get_translation

logger = logging.getLogger(__name__)


class VoteRatingModal(discord.ui.Modal):
    """Modal for entering a rating for a selected game."""
    
    def __init__(self, game_key, game_data, games, guild_id, user_id, embed, view):
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        game_name = game_data["name"]
        game_emoji = game_data.get("emoji", "🎮")
        
        # Modal title with game name (truncate if too long for Discord's 45 char limit)
        title_text = f"{game_emoji} {game_name}"
        if len(title_text) > 45:
            title_text = title_text[:42] + "..."
        super().__init__(title=t("vote_modal_title", game=title_text))
        self.game_key = game_key
        self.game_data = game_data
        self.games = games
        self.guild_id = guild_id
        self.user_id = user_id
        self.embed = embed
        self.view = view
        
        # Check for existing rating
        votes = load_votes(guild_id)
        existing_rating = None
        if user_id in votes:
            existing_rating = votes[user_id].get("votes", {}).get(game_key)
        
        # Rating input (1-5)
        self.rating_input = discord.ui.TextInput(
            label=t("vote_modal_rating_label"),
            placeholder=t("vote_modal_rating_placeholder"),
            default=str(existing_rating) if existing_rating else "5",
            max_length=1,
            required=True
        )
        self.add_item(self.rating_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        t = lambda k, **kw: get_translation(k, user_id=self.user_id, guild_id=self.guild_id, **kw)
        user_id = str(interaction.user.id)
        
        # Parse rating
        rating_str = self.rating_input.value.strip()
        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                raise ValueError("Rating out of range")
        except ValueError:
            await interaction.response.send_message(
                t("vote_modal_invalid_rating"),
                ephemeral=True
            )
            return
        
        # Save the vote
        votes = load_votes(self.guild_id)
        
        from core.translations import get_user_language
        
        if user_id not in votes:
            votes[user_id] = {
                "username": str(interaction.user),
                "votes": {},
                "language": get_user_language(user_id, self.guild_id)
            }
        
        votes[user_id]["votes"][self.game_key] = rating
        votes[user_id]["username"] = str(interaction.user)
        # Mark as available when voting (remove unavailable flag)
        votes[user_id]["unavailable"] = False
        save_votes(votes, self.guild_id)
        
        logger.info(f"Vote saved: {interaction.user} (ID: {user_id}) voted {rating}/5 for '{self.game_data['name']}' in guild {self.guild_id}")
        
        # Update the embed table
        await interaction.response.defer(ephemeral=True)
        
        # Update the view's user_votes to reflect the change
        self.view.user_votes[user_id] = votes[user_id]
        
        # Update embed table
        await self.view._update_embed_table(interaction, user_id)
        
        # Send confirmation (ephemeral message - user will see it briefly)
        await interaction.followup.send(
            t("vote_modal_success", game=self.game_data['name'], rating=rating, stars=""),
            ephemeral=True
        )


def _generate_vote_table_fields(games, user_votes_data):
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


class VotingView(discord.ui.View):
    """Interactive voting view with dropdown for game selection (opens modal for rating)."""
    
    def __init__(self, games, user_votes, guild_id, user_id):
        super().__init__(timeout=300)  # 5 minute timeout
        self.games = games
        self.user_votes = user_votes
        self.guild_id = guild_id
        self.user_id = user_id
        self.embed = None  # Will store the embed reference for updates
        
        # Get translation function for this user
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        
        # Add restore previous votes button FIRST (above dropdowns)
        self.restore_button = discord.ui.Button(
            label=t("vote_restore_button"),
            style=discord.ButtonStyle.secondary
        )
        self.restore_button.callback = self.on_restore_clicked
        self.add_item(self.restore_button)
        
        # Create select menus with games (Discord limits: 25 options per menu, 5 action rows per message)
        # Split games into chunks of 25
        sorted_games = sorted(games.items(), key=lambda x: (x[1].get("id", 9999), x[1]["name"]))
        MAX_OPTIONS_PER_MENU = 25
        MAX_ACTION_ROWS = 5  # Discord limit: 5 action rows per message
        
        # Calculate chunks
        game_chunks = [sorted_games[i:i + MAX_OPTIONS_PER_MENU] for i in range(0, len(sorted_games), MAX_OPTIONS_PER_MENU)]
        
        # Filter out empty chunks (shouldn't happen, but safety check)
        game_chunks = [chunk for chunk in game_chunks if chunk]
        
        # Limit to MAX_ACTION_ROWS - 1 (reserve 1 for the restore button)
        # If we have more chunks than allowed, we'll only show the first N chunks
        max_chunks = MAX_ACTION_ROWS - 1
        if len(game_chunks) > max_chunks:
            logger.warning(f"Too many games ({len(sorted_games)}) for voting view. Showing first {max_chunks * MAX_OPTIONS_PER_MENU} games.")
            game_chunks = game_chunks[:max_chunks]
        
        logger.debug(f"Creating {len(game_chunks)} select menus for {len(sorted_games)} games. Chunk sizes: {[len(c) for c in game_chunks]}")
        
        # Store select menus for callback handling
        self.game_selects = []
        
        for chunk_idx, chunk in enumerate(game_chunks):
            # Skip empty chunks
            if not chunk:
                continue
            
            # Ensure chunk doesn't exceed limit (safety check)
            chunk = chunk[:MAX_OPTIONS_PER_MENU]
            
            # Create placeholder text
            if len(game_chunks) > 1:
                placeholder = t('vote_select_game')
            else:
                placeholder = t("vote_select_game")
            
            # Create options list
            options = []
            for game_key, game_data in chunk:
                options.append(
                    discord.SelectOption(
                        label=game_data['name'],
                        description=t("vote_players_desc", min=game_data['min_players'], max=game_data['max_players']),
                        value=game_key,
                        emoji=game_data.get("emoji", "🎮")
                    )
                )
            
            # Safety check: ensure we have at least 1 option and at most 25
            if not options:
                continue
            if len(options) > MAX_OPTIONS_PER_MENU:
                options = options[:MAX_OPTIONS_PER_MENU]
            
            game_select = discord.ui.Select(
                placeholder=placeholder,
                options=options
            )
            # Create a callback that captures this specific select
            def make_callback(select_menu):
                async def callback(interaction: discord.Interaction):
                    await self.on_game_selected(interaction, select_menu)
                return callback
            game_select.callback = make_callback(game_select)
            self.game_selects.append(game_select)
            self.add_item(game_select)
    
    async def on_restore_clicked(self, interaction: discord.Interaction):
        """Restore votes from the last voting period - PERSONAL ONLY (doesn't affect others).
        Searches through all old vote files to find user's most recent votes."""
        # Get the current user's ID - this ensures only this user's votes are restored
        user_id = str(interaction.user.id)
        t = lambda k, **kw: get_translation(k, user_id=user_id, **kw)
        
        # Search through all old vote files to find this user's votes
        old_votes, found_file = find_user_votes_in_old_files(user_id, self.guild_id)
        
        if not old_votes or user_id not in old_votes:
            await interaction.response.send_message(
                t("vote_restore_no_previous"),
                ephemeral=True
            )
            return
        
        # Get only this user's votes from the old file
        old_user_votes = old_votes[user_id].get("votes", {})
        if not old_user_votes:
            await interaction.response.send_message(
                t("vote_restore_no_user"),
                ephemeral=True
            )
            return
        
        # Restore only this user's votes - doesn't touch other users' votes
        votes = load_votes(self.guild_id)
        if user_id not in votes:
            votes[user_id] = {
                "username": str(interaction.user),
                "votes": {}
            }
        
        # Only restore votes for games that still exist
        # Only modifies votes[user_id] - this user's personal entry
        restored_count = 0
        for game_key, rating in old_user_votes.items():
            if game_key in self.games:
                votes[user_id]["votes"][game_key] = rating
                restored_count += 1
        
        votes[user_id]["username"] = str(interaction.user)
        save_votes(votes, self.guild_id)
        self.user_votes[user_id] = votes[user_id]
        
        if restored_count > 0:
            # Extract date from filename for display
            file_date = found_file.split('.')[-2] if found_file else "previous period"
            
            # Update the embed table to show restored votes
            await interaction.response.defer(ephemeral=True)
            try:
                await self._update_embed_table(interaction, user_id)
            except Exception as e:
                logger.warning(f"Failed to update embed after restoring votes: {e}")
            
            await interaction.followup.send(
                t("vote_restore_success", count=restored_count, date=file_date),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                t("vote_restore_no_match"),
                ephemeral=True
            )
    
    async def _delete_after_delay(self, interaction: discord.Interaction, delay: int):
        """Delete the interaction response after a delay."""
        await asyncio.sleep(delay)
        try:
            await interaction.delete_original_response()
        except:
            pass  # Message might already be deleted or interaction expired
    
    
    
    async def _update_embed_table(self, interaction: discord.Interaction, user_id: str):
        """Helper method to update the embed table with current votes."""
        if self.embed is None:
            return
        
        try:
            # Load fresh votes to ensure we have the latest data
            votes = load_votes(self.guild_id)
            updated_user_votes = votes.get(user_id, {}).get("votes", {})
            
            # Regenerate table fields with updated votes
            table_fields = _generate_vote_table_fields(self.games, updated_user_votes)
            
            # Clear existing table fields (remove fields that start with "📊 Your Votes")
            fields_to_remove = [i for i, field in enumerate(self.embed.fields) if field.name.startswith("📊 Your Votes")]
            for i in reversed(fields_to_remove):
                self.embed.remove_field(i)
            
            # Add updated fields
            for field_name, field_value in table_fields:
                self.embed.add_field(name=field_name, value=field_value, inline=False)
            
            # Edit the original message with updated embed
            await interaction.edit_original_response(embed=self.embed, view=self)
        except Exception as e:
            logger.warning(f"Failed to update embed table: {e}")
    
    async def on_game_selected(self, interaction: discord.Interaction, select: discord.ui.Select = None):
        """Handle game selection - open modal for rating."""
        # Get the selected game key from the select menu
        if select is None:
            # Fallback: find the select that has values
            for s in self.game_selects:
                if s.values:
                    select = s
                    break
        
        if not select or not select.values:
            t = lambda k, **kw: get_translation(k, user_id=str(interaction.user.id), guild_id=self.guild_id, **kw)
            await interaction.response.send_message(
                "❌ Could not determine selected game. Please try again.",
                ephemeral=True
            )
            return
        
        game_key = select.values[0]
        
        if game_key not in self.games:
            t = lambda k, **kw: get_translation(k, user_id=str(interaction.user.id), guild_id=self.guild_id, **kw)
            await interaction.response.send_message(
                t("error_game_not_found", game=game_key),
                ephemeral=True
            )
            return
        
        game_data = self.games[game_key]
        user_id = str(interaction.user.id)
        self.user_id = user_id
        
        # Open modal for rating
        modal = VoteRatingModal(game_key, game_data, self.games, self.guild_id, user_id, self.embed, self)
        await interaction.response.send_modal(modal)
    

