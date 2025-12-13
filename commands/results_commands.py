"""Results command."""
import discord
from data_manager import load_votes, load_games
from helpers import require_guild, send_guild_only_error

def setup_results_commands(bot: discord.ext.commands.Bot):
    """Register results command."""
    
    @bot.tree.command(name="results", description="Show voting results and recommended game")
    async def results(interaction: discord.Interaction):
        """Show voting results and the most wanted game based on votes and player count."""
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        votes = load_votes(guild_id)
        games = load_games(guild_id)
        
        if not votes:
            await interaction.response.send_message(t("results_no_votes"), ephemeral=True)
            return
        
        # Count available players
        available_users = {
            uid: user_data for uid, user_data in votes.items()
            if not user_data.get("unavailable", False)
        }
        available_players = len(available_users)
        
        # Calculate game scores
        game_scores = {}
        for game_key in games.keys():
            game_scores[game_key] = 0
        
        for user_data in available_users.values():
            user_game_votes = user_data.get("votes", {})
            for game_key in games.keys():
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
        
        # Show all compatible games sorted by score with pagination
        sorted_games = sorted(compatible_games.items(), key=lambda x: x[1], reverse=True)
        games_data = [(game_key, games[game_key], score) for game_key, score in sorted_games]
        
        # Show who voted
        voters = [available_users[uid]["username"] for uid in available_users.keys()]
        embed.add_field(
            name=t("results_voters"),
            value=", ".join(voters) if voters else "None",
            inline=False
        )
        
        # Use pagination view if there are many games
        if len(games_data) > 10:
            from views.results_view import ResultsPaginationView
            view = ResultsPaginationView(games_data, available_players, guild_id, user_id, best_game_key, best_game, best_score, voters)
            first_page_embed = view.create_embed(best_game_key, best_game, best_score, voters)
            await interaction.response.send_message(embed=first_page_embed, view=view)
        else:
            # Show all games if 10 or fewer
            game_list = []
            for game_key, game, score in games_data:
                game_emoji = game.get('emoji', '🎮')
                marker = "🏆" if game_key == best_game_key else "•"
                line = f"{marker} {game_emoji} **{game['name']}** - {score} points (Players: {game['min_players']}-{game['max_players']})"
                store_links = game.get("store_links", "")
                if store_links:
                    line += f"\n   🔗 {store_links}"
                game_list.append(line)
            
            embed.add_field(
                name=t("results_all_games"),
                value="\n".join(game_list) if game_list else "None",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
