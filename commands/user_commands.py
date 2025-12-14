"""User commands (language, help)."""
import discord
from discord import app_commands
import logging
from core.data_manager import set_user_language, get_user_language
from core.helpers import require_guild, send_guild_only_error

logger = logging.getLogger(__name__)


def setup_user_commands(bot: discord.ext.commands.Bot):
    """Register user commands."""
    
    @bot.tree.command(name="language", description="Set your preferred language (English/Français)")
    @app_commands.describe(lang="Language code: 'en' for English, 'fr' for Français")
    @app_commands.choices(lang=[
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Français", value="fr")
    ])
    async def language(interaction: discord.Interaction, lang: str):
        """Set user's preferred language."""
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        
        if lang not in ["en", "fr"]:
            await interaction.response.send_message(
                t("language_invalid").format(options=t("language_options")),
                ephemeral=True
            )
            return
        
        success = set_user_language(user_id, lang, guild_id)
        
        if success:
            lang_names = {"en": "English", "fr": "Français"}
            from core.translations import get_translation
            t = lambda k: get_translation(k, lang=lang)
            await interaction.response.send_message(
                t("language_changed").format(lang=lang_names[lang]),
                ephemeral=True
            )
            logger.info(f"Language changed to {lang} for user {interaction.user} (ID: {user_id}) in guild {guild_id}")
        else:
            await interaction.response.send_message(
                t("language_invalid").format(options=t("language_options")),
                ephemeral=True
            )
    
    @bot.tree.command(name="help", description="Show how to use the bot and all available commands")
    async def help_command(interaction: discord.Interaction):
        """Display help information about the bot and its commands."""
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        
        embed = discord.Embed(
            title=t("help_title"),
            description=t("help_description"),
            color=discord.Color.blue()
        )
        
        embed.add_field(name=t("help_how_it_works"), value=t("help_how_it_works_value"), inline=False)
        embed.add_field(name=t("help_voting_commands"), value=t("help_voting_commands_value"), inline=False)
        embed.add_field(name=t("help_game_management"), value=t("help_game_management_value"), inline=False)
        embed.add_field(name=t("help_results_utilities"), value=t("help_results_utilities_value"), inline=False)
        embed.add_field(name=t("help_scheduling"), value=t("help_scheduling_value"), inline=False)
        embed.add_field(name=t("help_rating_system"), value=t("help_rating_system_value"), inline=False)
        embed.add_field(name=t("help_tips"), value=t("help_tips_value"), inline=False)
        embed.set_footer(text=t("help_footer"))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Help command used by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
