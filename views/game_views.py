"""Views and modals for game management (add, update, remove, list)."""
import discord
import logging
from core.data_manager import load_games, load_shared_games, add_game_to_shared, add_game_to_server, remove_game_from_server, get_next_game_id
from core.translations import get_translation

logger = logging.getLogger(__name__)


# ========== Game List Pagination ==========

class GameListPaginationView(discord.ui.View):
    """View for paginating through game list."""
    
    def __init__(self, games_data, guild_id: int, user_id: str):
        super().__init__(timeout=300)
        self.games_data = games_data  # List of (game_key, game_data) tuples
        self.guild_id = guild_id
        self.user_id = user_id
        self.current_page = 0
        self.items_per_page = 15  # Show 15 games per page
    
    def get_total_pages(self) -> int:
        """Calculate total number of pages."""
        return max(1, (len(self.games_data) + self.items_per_page - 1) // self.items_per_page)
    
    def get_current_page_data(self):
        """Get games for current page."""
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        return self.games_data[start:end]
    
    def create_embed(self) -> discord.Embed:
        """Create embed for current page."""
        from core.translations import get_translation
        t = lambda k, **kw: get_translation(k, user_id=self.user_id, guild_id=self.guild_id, **kw)
        
        current_data = self.get_current_page_data()
        game_list = []
        
        for game_key, game_data in current_data:
            emoji = game_data.get("emoji", "🎮")
            line = f"{emoji} **{game_data['name']}** - Players: {game_data['min_players']}-{game_data['max_players']}"
            store_links = game_data.get("store_links", "")
            if store_links:
                # Truncate long store links
                if len(store_links) > 50:
                    store_links = store_links[:47] + "..."
                line += f"\n   🔗 {store_links}"
            game_list.append(line)
        
        total_pages = self.get_total_pages()
        title = t("game_list_title")
        if total_pages > 1:
            title = f"{title} (Page {self.current_page + 1}/{total_pages})"
        
        embed = discord.Embed(
            title=title,
            description="\n".join(game_list) if game_list else t("error_no_games"),
            color=discord.Color.green()
        )
        
        embed.set_footer(text=f"Total games: {len(self.games_data)}")
        
        return embed
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page."""
        total_pages = self.get_total_pages()
        if self.current_page < total_pages - 1:
            self.current_page += 1
            await self.update_message(interaction)
    
    async def update_message(self, interaction: discord.Interaction):
        """Update the message with current page."""
        total_pages = self.get_total_pages()
        
        # Update button states
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page >= total_pages - 1)
        
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)


# ========== Game Update Modal and View ==========

class UpdateGameModal(discord.ui.Modal):
    """Modal for updating game properties."""
    
    def __init__(self, game_key, game_data, guild_id, user_id):
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        super().__init__(title=t("game_update_modal_title"))
        self.game_key = game_key
        self.game_data = game_data
        self.guild_id = guild_id
        self.user_id = user_id
        
        # Pre-fill with current values
        self.name_input = discord.ui.TextInput(
            label=t("game_update_name_label"),
            placeholder=t("game_update_name_placeholder"),
            default=game_data["name"],
            max_length=100,
            required=False
        )
        self.add_item(self.name_input)
        
        self.min_players_input = discord.ui.TextInput(
            label=t("game_update_min_label"),
            placeholder=t("game_update_min_placeholder"),
            default=str(game_data["min_players"]),
            max_length=3,
            required=False
        )
        self.add_item(self.min_players_input)
        
        self.max_players_input = discord.ui.TextInput(
            label=t("game_update_max_label"),
            placeholder=t("game_update_max_placeholder"),
            default=str(game_data["max_players"]),
            max_length=3,
            required=False
        )
        self.add_item(self.max_players_input)
        
        self.emoji_input = discord.ui.TextInput(
            label=t("game_update_emoji_label"),
            placeholder=t("game_update_emoji_placeholder"),
            default=game_data.get("emoji", "🎮"),
            max_length=10,
            required=False
        )
        self.add_item(self.emoji_input)
        
        # Store links (optional)
        self.store_links_input = discord.ui.TextInput(
            label=t("game_update_store_links_label"),
            placeholder=t("game_update_store_links_placeholder"),
            default=game_data.get("store_links", ""),
            max_length=500,
            required=False
        )
        self.add_item(self.store_links_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        games = load_games(self.guild_id)
        game = games[self.game_key]
        changes = []
        
        # Update name if changed
        new_name = self.name_input.value.strip() if self.name_input.value else None
        new_key = None
        if new_name and new_name != game["name"]:
            new_key = new_name.lower()
            if new_key != self.game_key and new_key in games:
                await interaction.response.send_message(
                    f"❌ A game with name '{new_name}' already exists!",
                    ephemeral=True
                )
                return
            
            old_name = game["name"]
            # If key changes, move the entry
            if new_key != self.game_key:
                games[new_key] = games[self.game_key].copy()
                del games[self.game_key]
                game = games[new_key]
                self.game_key = new_key
            
            game["name"] = new_name
            changes.append(f"Name: {old_name} → {new_name}")
        
        # Update min_players if changed
        min_players_str = self.min_players_input.value.strip() if self.min_players_input.value else None
        if min_players_str:
            try:
                min_players = int(min_players_str)
                if min_players < 1:
                    await interaction.response.send_message(
                        "❌ Invalid player count! Minimum must be at least 1.",
                        ephemeral=True
                    )
                    return
                
                if min_players != game["min_players"]:
                    old_min = game["min_players"]
                    game["min_players"] = min_players
                    changes.append(f"Min players: {old_min} → {min_players}")
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid number for min players!",
                    ephemeral=True
                )
                return
        
        # Update max_players if changed
        max_players_str = self.max_players_input.value.strip() if self.max_players_input.value else None
        if max_players_str:
            try:
                max_players = int(max_players_str)
                current_min = game["min_players"]
                if max_players < current_min:
                    await interaction.response.send_message(
                        f"❌ Invalid player count! Maximum ({max_players}) must be >= minimum ({current_min}).",
                        ephemeral=True
                    )
                    return
                
                if max_players != game["max_players"]:
                    old_max = game["max_players"]
                    game["max_players"] = max_players
                    changes.append(f"Max players: {old_max} → {max_players}")
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid number for max players!",
                    ephemeral=True
                )
                return
        
        # Update emoji if changed
        emoji = self.emoji_input.value.strip() if self.emoji_input.value else None
        if emoji and emoji != game.get("emoji", "🎮"):
            old_emoji = game.get("emoji", "🎮")
            game["emoji"] = emoji
            changes.append(f"Emoji: {old_emoji} → {emoji}")
        
        # Update store links if changed
        store_links = self.store_links_input.value.strip() if self.store_links_input.value else ""
        old_store_links = game.get("store_links", "")
        if store_links != old_store_links:
            if store_links:
                game["store_links"] = store_links
                if old_store_links:
                    changes.append(f"Store links: Updated")
                else:
                    changes.append(f"Store links: Added")
            else:
                if "store_links" in game:
                    del game["store_links"]
                if old_store_links:
                    changes.append(f"Store links: Removed")
        
        if not changes:
            await interaction.response.send_message(
                "ℹ️ No changes detected. All values are the same.",
                ephemeral=True
            )
            return
        
        # Update shared games with the changes
        # Handle name/key change (new_key was defined earlier if name changed)
        if new_name and new_name != game["name"] and new_key != self.game_key:
            # Remove old key from server list, add new key
            from core.data_manager import remove_game_from_server, add_game_to_server, save_shared_games
            remove_game_from_server(self.game_key, self.guild_id)
            add_game_to_server(new_key, self.guild_id)
            # Update shared games: remove old, add new
            shared_games = load_shared_games()
            if self.game_key in shared_games:
                del shared_games[self.game_key]
            shared_games[new_key] = game.copy()
            save_shared_games(shared_games)
        else:
            # Just update the shared game definition
            add_game_to_shared(self.game_key, game)
        
        logger.info(f"Game updated: '{game['name']}' by {interaction.user} (ID: {interaction.user.id}) in guild {self.guild_id} - Changes: {', '.join(changes)}")
        
        game_emoji = game.get("emoji", "🎮")
        response = f"✅ Updated {game_emoji} **{game['name']}**\n"
        response += "\n".join([f"• {change}" for change in changes])
        
        await interaction.response.send_message(response, ephemeral=True)


class UpdateGameView(discord.ui.View):
    """View for selecting a game to update."""
    
    def __init__(self, games, guild_id, user_id):
        super().__init__(timeout=300)
        self.games = games
        self.guild_id = guild_id
        self.user_id = user_id
        
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        
        # Create select menu with games (showing name only)
        self.game_select = discord.ui.Select(
            placeholder=t("game_update_select"),
            options=[
                discord.SelectOption(
                    label=game_data['name'],
                    description=t("vote_players_desc", min=game_data['min_players'], max=game_data['max_players']),
                    value=game_key,
                    emoji=game_data.get("emoji", "🎮")
                )
                for game_key, game_data in sorted(games.items(), key=lambda x: (x[1].get("id", 9999), x[1]["name"]))
            ]
        )
        self.game_select.callback = self.on_game_selected
        self.add_item(self.game_select)
    
    async def on_game_selected(self, interaction: discord.Interaction):
        """Handle game selection - show modal to update."""
        game_key = self.game_select.values[0]
        game_data = self.games[game_key]
        
        user_id = str(interaction.user.id)
        modal = UpdateGameModal(game_key, game_data, self.guild_id, user_id)
        await interaction.response.send_modal(modal)


# ========== Game Removal Modal and View ==========

class RemoveGameConfirmationModal(discord.ui.Modal):
    """Modal for confirming game removal."""
    
    def __init__(self, game_key, game_data, guild_id, user_id):
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        super().__init__(title=t("game_remove_confirm_title"))
        self.game_key = game_key
        self.game_data = game_data
        self.guild_id = guild_id
        self.user_id = user_id
        
        # Simple confirmation message (no input needed, but Discord requires at least one TextInput)
        # Truncate game name if too long for placeholder (Discord limit is 100 chars for placeholder)
        game_name_display = game_data['name']
        if len(game_name_display) > 80:
            game_name_display = game_name_display[:77] + "..."
        
        placeholder_text = t("game_remove_confirm_placeholder", game_name=game_name_display)
        if len(placeholder_text) > 100:
            placeholder_text = placeholder_text[:97] + "..."
        
        self.confirm_message = discord.ui.TextInput(
            label=t("game_remove_confirm_label"),
            placeholder=placeholder_text,
            default="",
            max_length=1,
            required=False
        )
        self.add_item(self.confirm_message)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle confirmation submission."""
        import logging
        logger = logging.getLogger(__name__)
        
        t = lambda k, **kw: get_translation(k, user_id=self.user_id, guild_id=self.guild_id, **kw)
        game_name = self.game_data["name"]
        game_id = self.game_data.get("id", "?")
        
        # Remove from server's game list (but keep in shared games)
        remove_game_from_server(self.game_key, self.guild_id)
        
        logger.info(f"Game removed from server: '{game_name}' (ID: {game_id}) by {interaction.user} (ID: {interaction.user.id}) in guild {self.guild_id}")
        
        await interaction.response.send_message(
            t("game_removed", game_name=game_name),
            ephemeral=True
        )


class RemoveGameView(discord.ui.View):
    """View for selecting a game to remove."""
    
    def __init__(self, games, guild_id, user_id):
        super().__init__(timeout=300)
        self.games = games
        self.guild_id = guild_id
        self.user_id = user_id
        
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        
        # Create select menu with games (showing name only)
        self.game_select = discord.ui.Select(
            placeholder=t("game_remove_select"),
            options=[
                discord.SelectOption(
                    label=game_data['name'],
                    description=t("vote_players_desc", min=game_data['min_players'], max=game_data['max_players']),
                    value=game_key,
                    emoji=game_data.get("emoji", "🎮")
                )
                for game_key, game_data in sorted(games.items(), key=lambda x: (x[1].get("id", 9999), x[1]["name"]))
            ]
        )
        self.game_select.callback = self.on_game_selected
        self.add_item(self.game_select)
    
    async def on_game_selected(self, interaction: discord.Interaction):
        """Handle game selection - show confirmation modal."""
        game_key = self.game_select.values[0]
        game_data = self.games[game_key]
        
        # Show confirmation modal
        modal = RemoveGameConfirmationModal(game_key, game_data, self.guild_id, self.user_id)
        await interaction.response.send_modal(modal)


# ========== Add Game Modal ==========

class AddGameModal(discord.ui.Modal):
    """Modal for adding a new game."""
    
    def __init__(self, guild_id, user_id):
        t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw)
        super().__init__(title=t("game_add_modal_title"))
        self.guild_id = guild_id
        self.user_id = user_id
        
        # Game name (required)
        self.name_input = discord.ui.TextInput(
            label=t("game_add_name_label"),
            placeholder=t("game_add_name_placeholder"),
            max_length=100,
            required=True
        )
        self.add_item(self.name_input)
        
        # Min players (optional, default 1)
        self.min_players_input = discord.ui.TextInput(
            label=t("game_add_min_label"),
            placeholder=t("game_add_min_placeholder"),
            default="1",
            max_length=3,
            required=False
        )
        self.add_item(self.min_players_input)
        
        # Max players (optional, default 10)
        self.max_players_input = discord.ui.TextInput(
            label=t("game_add_max_label"),
            placeholder=t("game_add_max_placeholder"),
            default="10",
            max_length=3,
            required=False
        )
        self.add_item(self.max_players_input)
        
        # Emoji (optional, default 🎮)
        self.emoji_input = discord.ui.TextInput(
            label=t("game_add_emoji_label"),
            placeholder=t("game_add_emoji_placeholder"),
            default="🎮",
            max_length=10,
            required=False
        )
        self.add_item(self.emoji_input)
        
        # Store links (optional)
        self.store_links_input = discord.ui.TextInput(
            label=t("game_add_store_links_label"),
            placeholder=t("game_add_store_links_placeholder"),
            default="",
            max_length=500,
            required=False
        )
        self.add_item(self.store_links_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        t = lambda k, **kw: get_translation(k, user_id=self.user_id, guild_id=self.guild_id, **kw)
        
        # Get values
        name = self.name_input.value.strip()
        if not name:
            await interaction.response.send_message(
                "❌ Game name cannot be empty!",
                ephemeral=True
            )
            return
        
        # Parse min players
        min_players_str = self.min_players_input.value.strip() if self.min_players_input.value else "1"
        try:
            min_players = int(min_players_str) if min_players_str else 1
        except ValueError:
            min_players = 1
        
        # Parse max players
        max_players_str = self.max_players_input.value.strip() if self.max_players_input.value else "10"
        try:
            max_players = int(max_players_str) if max_players_str else 10
        except ValueError:
            max_players = 10
        
        # Get emoji (default 🎮)
        emoji = self.emoji_input.value.strip() if self.emoji_input.value else "🎮"
        
        # Get store links (optional)
        store_links = self.store_links_input.value.strip() if self.store_links_input.value else ""
        
        # Validation
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
        
        # Check if game already exists in this server
        games = load_games(self.guild_id)
        game_key = name.lower()
        
        if game_key in games:
            await interaction.response.send_message(
                t("game_exists", name=name),
                ephemeral=True
            )
            return
        
        # Get next ID from shared games
        shared_games = load_shared_games()
        game_id = get_next_game_id(shared_games)
        
        # Create game data
        game_data = {
            "id": game_id,
            "name": name,
            "min_players": min_players,
            "max_players": max_players,
            "emoji": emoji
        }
        if store_links:
            game_data["store_links"] = store_links
        
        # Add to shared games database
        add_game_to_shared(game_key, game_data)
        
        # Add to server's game list
        add_game_to_server(game_key, self.guild_id)
        
        logger.info(f"Game added: '{name}' (Players: {min_players}-{max_players}, Emoji: {emoji}) by {interaction.user} (ID: {interaction.user.id}) in guild {self.guild_id}")
        
        await interaction.response.send_message(
            t("game_added", emoji=emoji, name=name, min_players=min_players, max_players=max_players),
            ephemeral=False
        )
