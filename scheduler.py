"""Scheduled tasks and reminders."""
import discord
import logging
from pathlib import Path
from datetime import datetime, timedelta
from apscheduler.triggers.cron import CronTrigger
from data_manager import save_old_votes, clear_votes
from config import DATA_DIR

logger = logging.getLogger(__name__)


async def send_sunday_reminder(bot):
    """Send reminder message to vote on all servers the bot is in."""
    logger.info("Sunday reminder triggered - sending vote reminders")
    embed = discord.Embed(
        title="🎮 Game Night Reminder!",
        description="It's time to vote for next week's game! Use `/vote` to rate games and show your availability.",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="How it works",
        value="1. Use `/vote` to open the interactive voting menu\n"
              "2. Select games and rate them (default is 5)\n"
              "3. Not voting for a game = rating 0\n"
              "4. Voting shows you're available for game night\n"
              "5. Use `/results` to see which game won!",
        inline=False
    )
    
    for guild in bot.guilds:
        # Try to find a general channel or first text channel
        channel = None
        for ch in guild.text_channels:
            if 'general' in ch.name.lower() or ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
        
        if channel:
            try:
                await channel.send(embed=embed)
                logger.info(f"Sunday reminder sent to {guild.name} (ID: {guild.id}) in channel {channel.name}")
            except Exception as e:
                logger.error(f"Failed to send reminder to {guild.name}: {e}", exc_info=True)


async def reset_votes_wednesday(bot):
    """Reset votes every Wednesday at 11:59 PM and save backup."""
    logger.info("Wednesday reset triggered - saving votes and clearing")
    old_file = save_old_votes()
    if old_file:
        logger.info(f"Votes backed up to: {old_file}")
    clear_votes(save_backup=False)
    logger.info("All votes cleared for new voting period")
    
    embed = discord.Embed(
        title="🔄 Votes Reset!",
        description="All votes have been reset for the new voting period.\n"
                   "Use `/vote` to start voting for next week's game night!",
        color=discord.Color.orange()
    )
    
    if old_file:
        embed.set_footer(text=f"Previous votes saved to: {old_file}")
    
    for guild in bot.guilds:
        # Try to find a general channel or first text channel
        channel = None
        for ch in guild.text_channels:
            if 'general' in ch.name.lower() or ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
        
        if channel:
            try:
                await channel.send(embed=embed)
                logger.info(f"Reset notification sent to {guild.name} (ID: {guild.id}) in channel {channel.name}")
            except Exception as e:
                logger.error(f"Failed to send reset message to {guild.name}: {e}", exc_info=True)


async def clean_old_votes(bot):
    """Clean vote backup files older than 30 days."""
    logger.info("Starting cleanup of old vote backup files (older than 30 days)")
    try:
        old_files = list(DATA_DIR.glob("votes.old.*.json"))
        cutoff_date = datetime.now() - timedelta(days=30)
        deleted_count = 0
        
        for old_file in old_files:
            try:
                # Extract date from filename: votes.old.YYYY-MM-DD.json
                date_str = old_file.stem.split('.')[-1]  # Get last part after splitting by '.'
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    old_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old vote backup: {old_file.name} (from {date_str})")
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse date from filename {old_file.name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error deleting {old_file.name}: {e}", exc_info=True)
        
        if deleted_count > 0:
            logger.info(f"Cleanup complete: Deleted {deleted_count} old vote backup file(s)")
        else:
            logger.info("Cleanup complete: No old vote backup files to delete")
    except Exception as e:
        logger.error(f"Error during vote cleanup: {e}", exc_info=True)


async def clean_old_logs(bot):
    """Clean log files older than 7 days."""
    logger.info("Starting cleanup of old log files (older than 7 days)")
    try:
        logs_dir = Path("logs")
        log_files = list(logs_dir.glob("*.log*"))
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = 0
        
        for log_file in log_files:
            try:
                # Get file modification time
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old log file: {log_file.name} (modified: {file_mtime.strftime('%Y-%m-%d')})")
            except Exception as e:
                logger.error(f"Error deleting {log_file.name}: {e}", exc_info=True)
        
        if deleted_count > 0:
            logger.info(f"Cleanup complete: Deleted {deleted_count} old log file(s)")
        else:
            logger.info("Cleanup complete: No old log files to delete")
    except Exception as e:
        logger.error(f"Error during log cleanup: {e}", exc_info=True)


def setup_scheduler(scheduler, bot):
    """Set up scheduled tasks."""
    # Schedule Sunday reminder at 8 PM (20:00)
    scheduler.add_job(
        send_sunday_reminder,
        CronTrigger(day_of_week='sun', hour=20, minute=0),
        args=[bot],
        id='sunday_reminder'
    )
    logger.info("Scheduled Sunday reminder for 8 PM")
    
    # Schedule Wednesday vote reset at 11:59 PM (23:59)
    scheduler.add_job(
        reset_votes_wednesday,
        CronTrigger(day_of_week='wed', hour=23, minute=59),
        args=[bot],
        id='wednesday_reset'
    )
    logger.info("Scheduled Wednesday vote reset for 11:59 PM")
    
    # Schedule daily cleanup of old vote backups (older than 30 days) at 2 AM
    scheduler.add_job(
        clean_old_votes,
        CronTrigger(hour=2, minute=0),
        args=[bot],
        id='cleanup_old_votes'
    )
    logger.info("Scheduled daily cleanup of vote backups (older than 30 days) at 2 AM")
    
    # Schedule daily cleanup of old logs (older than 7 days) at 2:05 AM
    scheduler.add_job(
        clean_old_logs,
        CronTrigger(hour=2, minute=5),
        args=[bot],
        id='cleanup_old_logs'
    )
    logger.info("Scheduled daily cleanup of log files (older than 7 days) at 2:05 AM")

