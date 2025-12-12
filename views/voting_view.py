"""Voting view for interactive game voting."""
import discord
import asyncio
import logging
from data_manager import load_votes, save_votes, get_latest_old_votes

logger = logging.getLogger(__name__)


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


class VotingView(discord.ui.View):
    """Interactive voting view with dropdowns for games and ratings."""
    
    def __init__(self, games, user_votes):
        super().__init__(timeout=300)  # 5 minute timeout
        self.games = games
        self.user_votes = user_votes
        self.user_id = None
        self.embed = None  # Will store the embed reference for updates
        
        # Add restore previous votes button FIRST (above dropdowns)
        self.restore_button = discord.ui.Button(
            label="🔄 Restore Last Votes",
            style=discord.ButtonStyle.secondary
        )
        self.restore_button.callback = self.on_restore_clicked
        self.add_item(self.restore_button)
        
        # Create select menu with games (showing ID and name)
        # Note: Discord Select menus preserve selected value - we'll update placeholder to show selection
        self.game_select = discord.ui.Select(
            placeholder="Choose a game to vote for...",
            options=[
                discord.SelectOption(
                    label=f"[{game_data.get('id', '?')}] {game_data['name']}",
                    description=f"Players: {game_data['min_players']}-{game_data['max_players']}",
                    value=game_key,
                    emoji=game_data.get("emoji", "🎮")
                )
                for game_key, game_data in sorted(games.items(), key=lambda x: (x[1].get("id", 9999), x[1]["name"]))
            ]
        )
        self.game_select.callback = self.on_game_selected
        self.add_item(self.game_select)
        
        # Create rating select menu (no default value - defaults set dynamically based on selections)
        self.rating_select = discord.ui.Select(
            placeholder="Choose rating (1-5)...",
            options=[
                discord.SelectOption(label="5 - Really want to play ⭐⭐⭐⭐⭐", value="5", emoji="⭐"),
                discord.SelectOption(label="4 - Want to play ⭐⭐⭐⭐", value="4", emoji="⭐"),
                discord.SelectOption(label="3 - Neutral ⭐⭐⭐", value="3", emoji="⭐"),
                discord.SelectOption(label="2 - Don't really want ⭐⭐", value="2", emoji="⭐"),
                discord.SelectOption(label="1 - Don't want to play ⭐", value="1", emoji="⭐"),
            ]
        )
        self.rating_select.callback = self.on_rating_selected
        self.add_item(self.rating_select)
        
        self.selected_game = None
        self.selected_rating = None
    
    async def on_restore_clicked(self, interaction: discord.Interaction):
        """Restore votes from the last voting period - PERSONAL ONLY (doesn't affect others)."""
        old_votes = get_latest_old_votes()
        # Get the current user's ID - this ensures only this user's votes are restored
        user_id = str(interaction.user.id)
        
        if not old_votes:
            await interaction.response.send_message(
                "❌ No previous votes found to restore!",
                ephemeral=True
            )
            return
        
        # Check if this specific user had votes in the old file
        if user_id not in old_votes:
            await interaction.response.send_message(
                "❌ You didn't vote in the previous period, so there's nothing to restore!",
                ephemeral=True
            )
            return
        
        # Get only this user's votes from the old file
        old_user_votes = old_votes[user_id].get("votes", {})
        if not old_user_votes:
            await interaction.response.send_message(
                "❌ You didn't have any votes in the previous period!",
                ephemeral=True
            )
            return
        
        # Restore only this user's votes - doesn't touch other users' votes
        votes = load_votes()
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
        save_votes(votes)
        self.user_votes[user_id] = votes[user_id]
        
        if restored_count > 0:
            await interaction.response.send_message(
                f"✅ Restored {restored_count} of **your** vote(s) from the previous voting period!\n"
                f"This only affects your votes - others' votes are unchanged.\n"
                f"You can still modify them using the dropdowns above.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ None of your previous votes match games in the current list!",
                ephemeral=True
            )
    
    async def _delete_after_delay(self, interaction: discord.Interaction, delay: int):
        """Delete the interaction response after a delay."""
        await asyncio.sleep(delay)
        try:
            await interaction.delete_original_response()
        except:
            pass  # Message might already be deleted or interaction expired
    
    
    def _update_select_placeholders(self):
        """Update select menu placeholders to show current selections."""
        # Update game select placeholder
        if self.selected_game:
            game_data = self.games[self.selected_game]
            game_name = game_data["name"]
            game_id = game_data.get("id", "?")
            emoji = game_data.get("emoji", "🎮")
            # Truncate if too long
            display_name = f"{emoji} [{game_id}] {game_name}"
            if len(display_name) > 100:
                display_name = display_name[:97] + "..."
            self.game_select.placeholder = f"Selected: {display_name}"
        else:
            self.game_select.placeholder = "Choose a game to vote for..."
        
        # Update rating select placeholder
        if self.selected_rating:
            stars = "⭐" * self.selected_rating
            self.rating_select.placeholder = f"Selected: {self.selected_rating}/5 {stars}"
        else:
            self.rating_select.placeholder = "Choose rating (1-5)..."
    
    async def _update_embed_table(self, interaction: discord.Interaction, user_id: str):
        """Helper method to update the embed table with current votes."""
        if self.embed is None:
            return
        
        try:
            # Load fresh votes to ensure we have the latest data
            votes = load_votes()
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
            
            # Update select placeholders to show current selections
            self._update_select_placeholders()
            
            # Edit the original message with updated embed
            await interaction.edit_original_response(embed=self.embed, view=self)
        except Exception as e:
            logger.warning(f"Failed to update embed table: {e}")
    
    async def on_game_selected(self, interaction: discord.Interaction):
        """Handle game selection - auto-save if rating is already selected."""
        self.selected_game = self.game_select.values[0]
        game_key = self.selected_game
        user_id = str(interaction.user.id)
        self.user_id = user_id
        
        # Load votes to check existing rating
        votes = load_votes()
        existing_rating = None
        
        if user_id in votes:
            existing_rating = votes[user_id].get("votes", {}).get(game_key)
        
        # If there's an existing rating, set it as selected
        if existing_rating:
            self.selected_rating = existing_rating
            # Update rating select to show current rating
            for option in self.rating_select.options:
                option.default = (option.value == str(existing_rating))
        else:
            # If rating was already selected (user selected rating first), keep it
            # Otherwise clear it
            if not self.selected_rating:
                # Reset rating select defaults
                for option in self.rating_select.options:
                    option.default = False
        
        # Update placeholders to show selections
        self._update_select_placeholders()
        
        # If both game and rating are now selected, auto-save the vote
        if self.selected_game and self.selected_rating:
            # Save the vote
            if user_id not in votes:
                votes[user_id] = {
                    "username": str(interaction.user),
                    "votes": {}
                }
            
            votes[user_id]["votes"][game_key] = self.selected_rating
            votes[user_id]["username"] = str(interaction.user)
            save_votes(votes)
            
            # Update local state
            self.user_votes[user_id] = votes[user_id]
            
            game_name = self.games[game_key]["name"]
            rating_emoji = "⭐" * self.selected_rating
            
            logger.info(f"Vote saved: {interaction.user} (ID: {user_id}) voted {self.selected_rating}/5 for '{game_name}'")
            
            # Update rating select defaults
            for option in self.rating_select.options:
                option.default = (option.value == str(self.selected_rating))
            
            # Defer to update embed
            await interaction.response.defer(ephemeral=True)
            
            # Update the embed table (this provides feedback via the updated table)
            try:
                await self._update_embed_table(interaction, user_id)
            except Exception as e:
                logger.warning(f"Failed to update embed after vote: {e}")
        else:
            # Defer silently - don't update the view to avoid resetting the dropdown
            await interaction.response.defer(ephemeral=True)
    
    async def on_rating_selected(self, interaction: discord.Interaction):
        """Handle rating selection - automatically save vote if game is already selected."""
        # Use currently selected game or first selected from dropdown
        if not self.selected_game:
            if self.game_select.values:
                self.selected_game = self.game_select.values[0]
            else:
                await interaction.response.send_message(
                    "❌ Please select a game first!",
                    ephemeral=True
                )
                return
        
        rating = int(self.rating_select.values[0])
        self.selected_rating = rating
        
        # Automatically save the vote since both game and rating are now selected
        game_key = self.selected_game
        user_id = str(interaction.user.id)
        self.user_id = user_id
        
        # Save the vote
        votes = load_votes()
        
        if user_id not in votes:
            votes[user_id] = {
                "username": str(interaction.user),
                "votes": {}
            }
        
        votes[user_id]["votes"][game_key] = rating
        votes[user_id]["username"] = str(interaction.user)
        save_votes(votes)
        
        # Update local state
        self.user_votes[user_id] = votes[user_id]
        
        game_name = self.games[game_key]["name"]
        rating_emoji = "⭐" * rating
        
        logger.info(f"Vote saved: {interaction.user} (ID: {user_id}) voted {rating}/5 for '{game_name}'")
        
        # Update rating select defaults to reflect selected rating
        for option in self.rating_select.options:
            option.default = (option.value == str(rating))
        
        # Update placeholders to show selections
        self._update_select_placeholders()
        
        # Defer the interaction first so we can update the embed
        await interaction.response.defer(ephemeral=True)
        
        # Update the embed table (this provides feedback via the updated table)
        try:
            await self._update_embed_table(interaction, user_id)
        except Exception as e:
            logger.warning(f"Failed to update embed after vote: {e}")
    

