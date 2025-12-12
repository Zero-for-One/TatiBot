"""Views and modals for updating games."""
import discord
import logging
from data_manager import load_games, save_games

logger = logging.getLogger(__name__)


class UpdateGameModal(discord.ui.Modal, title="Update Game"):
    """Modal for updating game properties."""
    
    def __init__(self, game_key, game_data):
        super().__init__()
        self.game_key = game_key
        self.game_data = game_data
        
        # Pre-fill with current values
        self.name_input = discord.ui.TextInput(
            label="Game Name",
            placeholder="Enter new name (or keep current)",
            default=game_data["name"],
            max_length=100,
            required=False
        )
        self.add_item(self.name_input)
        
        self.min_players_input = discord.ui.TextInput(
            label="Min Players",
            placeholder="Minimum number of players",
            default=str(game_data["min_players"]),
            max_length=3,
            required=False
        )
        self.add_item(self.min_players_input)
        
        self.max_players_input = discord.ui.TextInput(
            label="Max Players",
            placeholder="Maximum number of players",
            default=str(game_data["max_players"]),
            max_length=3,
            required=False
        )
        self.add_item(self.max_players_input)
        
        self.emoji_input = discord.ui.TextInput(
            label="Emoji",
            placeholder="Emoji/emote for the game",
            default=game_data.get("emoji", "🎮"),
            max_length=10,
            required=False
        )
        self.add_item(self.emoji_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        games = load_games()
        game = games[self.game_key]
        changes = []
        
        # Update name if changed
        new_name = self.name_input.value.strip() if self.name_input.value else None
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
        
        if not changes:
            await interaction.response.send_message(
                "ℹ️ No changes detected. All values are the same.",
                ephemeral=True
            )
            return
        
        save_games(games)
        
        logger.info(f"Game updated: '{game['name']}' by {interaction.user} (ID: {interaction.user.id}) - Changes: {', '.join(changes)}")
        
        game_emoji = game.get("emoji", "🎮")
        response = f"✅ Updated {game_emoji} **{game['name']}**\n"
        response += "\n".join([f"• {change}" for change in changes])
        
        await interaction.response.send_message(response, ephemeral=True)


class UpdateGameView(discord.ui.View):
    """View for selecting a game to update."""
    
    def __init__(self, games):
        super().__init__(timeout=300)
        self.games = games
        
        # Create select menu with games (showing ID and name)
        self.game_select = discord.ui.Select(
            placeholder="Choose a game to update...",
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
    
    async def on_game_selected(self, interaction: discord.Interaction):
        """Handle game selection - show modal to update."""
        game_key = self.game_select.values[0]
        game_data = self.games[game_key]
        
        modal = UpdateGameModal(game_key, game_data)
        await interaction.response.send_modal(modal)

