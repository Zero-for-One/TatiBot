"""Server configuration commands."""
import discord
from discord import app_commands
import logging
from data_manager import load_server_config, save_server_config
from helpers import require_admin, send_guild_only_error, send_admin_error, require_guild

logger = logging.getLogger(__name__)

# Day choices for commands
DAY_CHOICES = [
    app_commands.Choice(name="Monday", value="mon"),
    app_commands.Choice(name="Tuesday", value="tue"),
    app_commands.Choice(name="Wednesday", value="wed"),
    app_commands.Choice(name="Thursday", value="thu"),
    app_commands.Choice(name="Friday", value="fri"),
    app_commands.Choice(name="Saturday", value="sat"),
    app_commands.Choice(name="Sunday", value="sun")
]

DAY_NAMES = {
    "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday",
    "thu": "Thursday", "fri": "Friday", "sat": "Saturday", "sun": "Sunday"
}


def setup_config_commands(bot: discord.ext.commands.Bot):
    """Register configuration commands."""
    
    @bot.tree.command(name="configreminder", description="Configure when voting reminders are sent (admin only)")
    @app_commands.describe(
        day="Day of the week",
        hour="Hour (0-23, 24-hour format)",
        minute="Minute (0-59)"
    )
    @app_commands.choices(day=DAY_CHOICES)
    async def configreminder(interaction: discord.Interaction, day: str, hour: int, minute: int):
        """Configure when voting reminders are sent."""
        result = require_admin(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_admin_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        guild_id, user_id, t = result
        
        # Validate hour and minute
        if not (0 <= hour <= 23):
            await interaction.response.send_message(t("config_invalid_hour"), ephemeral=True)
            return
        
        if not (0 <= minute <= 59):
            await interaction.response.send_message(t("config_invalid_minute"), ephemeral=True)
            return
        
        # Update config
        config = load_server_config(guild_id)
        config["reminder_day"] = day
        config["reminder_hour"] = hour
        config["reminder_minute"] = minute
        save_server_config(config, guild_id)
        
        logger.info(f"Reminder schedule updated: {day} {hour:02d}:{minute:02d} by {interaction.user} (ID: {user_id}) in guild {guild_id}")
        
        await interaction.response.send_message(
            t("configreminder_success",
              day=DAY_NAMES.get(day, day),
              hour=hour,
              minute=f"{minute:02d}"),
            ephemeral=True
        )
    
    
    @bot.tree.command(name="configgamenight", description="Configure default recurring game night schedule (admin only)")
    @app_commands.describe(
        day="Day of the week (or 'none' to disable)",
        hour="Hour (0-23, 24-hour format)",
        minute="Minute (0-59)"
    )
    @app_commands.choices(day=[
        app_commands.Choice(name="None (disable)", value="none"),
        *DAY_CHOICES
    ])
    async def configgamenight(interaction: discord.Interaction, day: str, hour: int = None, minute: int = None):
        """Configure default recurring game night schedule."""
        result = require_admin(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_admin_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        guild_id, user_id, t = result
        config = load_server_config(guild_id)
        
        if day == "none":
            config["game_night_day"] = None
            config["game_night_hour"] = None
            config["game_night_minute"] = None
            save_server_config(config, guild_id)
            
            logger.info(f"Recurring game night disabled by {interaction.user} (ID: {user_id}) in guild {guild_id}")
            await interaction.response.send_message(t("configgamenight_disabled"), ephemeral=True)
            return
        
        # Validate hour and minute if provided
        if hour is None or minute is None:
            await interaction.response.send_message(t("configgamenight_missing_time"), ephemeral=True)
            return
        
        if not (0 <= hour <= 23):
            await interaction.response.send_message(t("config_invalid_hour"), ephemeral=True)
            return
        
        if not (0 <= minute <= 59):
            await interaction.response.send_message(t("config_invalid_minute"), ephemeral=True)
            return
        
        # Update config
        config["game_night_day"] = day
        config["game_night_hour"] = hour
        config["game_night_minute"] = minute
        save_server_config(config, guild_id)
        
        logger.info(f"Game night schedule updated: {day} {hour:02d}:{minute:02d} by {interaction.user} (ID: {user_id}) in guild {guild_id}")
        
        await interaction.response.send_message(
            t("configgamenight_success",
              day=DAY_NAMES.get(day, day),
              hour=hour,
              minute=f"{minute:02d}"),
            ephemeral=True
        )
    
    
    @bot.tree.command(name="config", description="View current server configuration")
    async def config(interaction: discord.Interaction):
        """View current server configuration."""
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        config = load_server_config(guild_id)
        
        embed = discord.Embed(title=t("config_title"), color=discord.Color.blue())
        
        # Reminder schedule
        reminder_day = DAY_NAMES.get(config.get("reminder_day", "sun"), "Sunday")
        reminder_hour = config.get("reminder_hour", 20)
        reminder_minute = config.get("reminder_minute", 0)
        embed.add_field(
            name=t("config_reminder"),
            value=f"{reminder_day} at {reminder_hour:02d}:{reminder_minute:02d}",
            inline=False
        )
        
        # Game night schedule
        game_night_day = config.get("game_night_day")
        if game_night_day:
            game_night_hour = config.get("game_night_hour", 20)
            game_night_minute = config.get("game_night_minute", 0)
            game_night_day_name = DAY_NAMES.get(game_night_day, game_night_day)
            embed.add_field(
                name=t("config_gamenight"),
                value=f"{game_night_day_name} at {game_night_hour:02d}:{game_night_minute:02d}",
                inline=False
            )
        else:
            embed.add_field(
                name=t("config_gamenight"),
                value=t("config_gamenight_none"),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
