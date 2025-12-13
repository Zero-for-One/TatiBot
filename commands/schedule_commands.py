"""Commands for scheduling game nights."""
import discord
from discord import app_commands
import logging
from datetime import datetime
from data_manager import add_schedule, load_schedules
from helpers import require_guild, send_guild_only_error

logger = logging.getLogger(__name__)


def setup_schedule_commands(bot: discord.ext.commands.Bot):
    """Register schedule commands."""
    
    @bot.tree.command(name="schedule", description="Schedule a game night with date and time")
    @app_commands.describe(
        date="Date in YYYY-MM-DD format (e.g., 2024-12-25)",
        time="Time in HH:MM format (24-hour, e.g., 20:00 for 8 PM)",
        description="Optional description for this game night"
    )
    async def schedule(interaction: discord.Interaction, date: str, time: str, description: str = None):
        """Schedule a game night with date and time."""
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        
        # Parse date
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            await interaction.response.send_message(t("schedule_invalid_date"), ephemeral=True)
            return
        
        # Parse time
        try:
            time_parts = time.split(":")
            if len(time_parts) != 2:
                raise ValueError
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except (ValueError, IndexError):
            await interaction.response.send_message(t("schedule_invalid_time"), ephemeral=True)
            return
        
        # Combine date and time
        schedule_datetime = datetime.combine(date_obj, datetime.min.time().replace(hour=hour, minute=minute))
        
        # Check if date is in the past
        if schedule_datetime < datetime.now():
            await interaction.response.send_message(t("schedule_past_date"), ephemeral=True)
            return
        
        # Add the schedule
        schedule_id = add_schedule(guild_id, schedule_datetime, description)
        
        logger.info(f"Game night scheduled: {schedule_datetime} by {interaction.user} (ID: {user_id}) in guild {guild_id}")
        
        await interaction.response.send_message(
            t("schedule_success", 
              date=date_obj.strftime("%Y-%m-%d"),
              time=time,
              description=f"\n{description}" if description else ""),
            ephemeral=True
        )
    
    
    @bot.tree.command(name="schedules", description="List all upcoming scheduled game nights")
    async def schedules(interaction: discord.Interaction):
        """List all upcoming scheduled game nights."""
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        all_schedules = load_schedules(guild_id)
        now = datetime.now()
        
        # Filter to only upcoming schedules
        upcoming = [
            s for s in all_schedules
            if datetime.fromisoformat(s["datetime"]) > now
        ]
        
        if not upcoming:
            await interaction.response.send_message(t("schedules_none"), ephemeral=True)
            return
        
        embed = discord.Embed(title=t("schedules_title"), color=discord.Color.blue())
        
        schedule_list = []
        for schedule in upcoming[:10]:  # Limit to 10 upcoming
            schedule_dt = datetime.fromisoformat(schedule["datetime"])
            desc = schedule.get("description", "")
            if desc:
                desc = f" - {desc}"
            schedule_list.append(f"📅 **{schedule_dt.strftime('%Y-%m-%d %H:%M')}**{desc}")
        
        embed.description = "\n".join(schedule_list) if schedule_list else t("schedules_none")
        
        if len(upcoming) > 10:
            embed.set_footer(text=t("schedules_more", count=len(upcoming) - 10))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
