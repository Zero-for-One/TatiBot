"""Pagination view for results."""
import discord
from typing import List, Tuple


class ResultsPaginationView(discord.ui.View):
    """View for paginating through results."""
    
    def __init__(self, games_data: List[Tuple], available_players: int, guild_id: int, user_id: str, best_game_key: str = None, best_game_data: dict = None, best_score: int = None, voters: list = None):
        super().__init__(timeout=300)
        self.games_data = games_data  # List of (game_key, game, score) tuples
        self.available_players = available_players
        self.guild_id = guild_id
        self.user_id = user_id
        self.current_page = 0
        self.items_per_page = 10
        self.best_game_key = best_game_key
        self.best_game_data = best_game_data
        self.best_score = best_score
        self.voters = voters
        
    def get_total_pages(self) -> int:
        """Calculate total number of pages."""
        return max(1, (len(self.games_data) + self.items_per_page - 1) // self.items_per_page)
    
    def get_current_page_data(self) -> List[Tuple]:
        """Get games for current page."""
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        return self.games_data[start:end]
    
    def create_embed(self, best_game_key: str = None, best_game_data: dict = None, best_score: int = None, voters: list = None) -> discord.Embed:
        """Create embed for current page."""
        from core.translations import get_translation
        t = lambda k, **kw: get_translation(k, user_id=self.user_id, guild_id=self.guild_id, **kw)
        
        embed = discord.Embed(
            title=t("results_title"),
            description=t("results_available_players", count=self.available_players),
            color=discord.Color.gold()
        )
        
        # Show recommended game on first page
        if self.current_page == 0 and best_game_data and best_game_key:
            best_emoji = best_game_data.get('emoji', '🎮')
            embed.add_field(
                name=t("results_recommended"),
                value=f"{best_emoji} **{best_game_data['name']}**\n"
                      f"{t('results_recommended_score', score=best_score)}\n"
                      f"{t('results_recommended_players', min=best_game_data['min_players'], max=best_game_data['max_players'])}",
                inline=False
            )
        
        current_data = self.get_current_page_data()
        game_list = []
        
        for game_key, game, score in current_data:
            game_emoji = game.get('emoji', '🎮')
                marker = "•"
            line = f"{marker} {game_emoji} **{game['name']}** - {score} points (Players: {game['min_players']}-{game['max_players']})"
            # Add store links if available
            store_links = game.get("store_links", "")
            if store_links:
                line += f"\n   🔗 {store_links}"
            game_list.append(line)
        
        total_pages = self.get_total_pages()
        field_name = t("results_all_games")
        if total_pages > 1:
            field_name = f"{field_name} (Page {self.current_page + 1}/{total_pages})"
        
        embed.add_field(
            name=field_name,
            value="\n".join(game_list) if game_list else "None",
            inline=False
        )
        
        # Show voters on first page
        if self.current_page == 0 and voters:
            embed.add_field(
                name=t("results_voters"),
                value=", ".join(voters) if voters else "None",
                inline=False
            )
        
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
        
        embed = self.create_embed(self.best_game_key, self.best_game_data, self.best_score, self.voters)
        await interaction.response.edit_message(embed=embed, view=self)
