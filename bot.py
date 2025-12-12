"""Main bot file - sets up and runs the Discord bot."""
import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from logger_config import setup_logging
from scheduler import setup_scheduler
from commands import game_commands, voting_commands, utility_commands

# Set up logging
logger = setup_logging()

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Scheduler for reminders
scheduler = AsyncIOScheduler()


@bot.event
async def on_ready():
    """Called when the bot connects to Discord."""
    logger.info(f'Bot logged in as {bot.user} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} server(s)')
    
    # Sync commands - choose one method to avoid duplicates
    # Option 1: Guild-specific sync (instant, but need to sync to each server)
    # Option 2: Global sync (works everywhere, but takes up to 1 hour to update)
    
    # Using guild-specific sync for instant updates
    try:
        synced_count = 0
        # Sync to each guild individually for instant updates
        for guild in bot.guilds:
            try:
                bot.tree.copy_global_to(guild=guild)
                synced = await bot.tree.sync(guild=guild)
                synced_count += len(synced)
                logger.info(f"Synced {len(synced)} command(s) to guild: {guild.name} (ID: {guild.id})")
            except Exception as e:
                logger.error(f"Failed to sync to {guild.name}: {e}", exc_info=True)
            
        if synced_count > 0:
            logger.info(f"Total: {synced_count} command(s) synced to guilds")
        else:
            # Fallback to global sync if no guilds
            try:
                synced_global = await bot.tree.sync()
                logger.info(f"Synced {len(synced_global)} global command(s)")
            except Exception as e:
                logger.error(f"Global sync failed: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}", exc_info=True)
    
    # Start the scheduler and set up scheduled tasks
    scheduler.start()
    setup_scheduler(scheduler, bot)
    logger.info("Scheduler started and tasks configured")


# Error handler
@bot.event
async def on_error(event, *args, **kwargs):
    """Log errors that occur in bot events."""
    logger.error(f"Error in event {event}", exc_info=True)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Log errors that occur in slash commands."""
    logger.error(f"Command error in {interaction.command.name if interaction.command else 'unknown'}: {error}", exc_info=True)
    if not interaction.response.is_done():
        try:
            await interaction.response.send_message(
                "❌ An error occurred while processing your command. Please try again.",
                ephemeral=True
            )
        except:
            pass

# Register all command groups
game_commands.setup_game_commands(bot)
voting_commands.setup_voting_commands(bot)
utility_commands.setup_utility_commands(bot)


# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        print("❌ DISCORD_TOKEN not found in environment variables!")
        print("Please set it or create a .env file with DISCORD_TOKEN=your_token")
    else:
        logger.info("Starting bot...")
        try:
            bot.run(token)
        except Exception as e:
            logger.critical(f"Bot crashed: {e}", exc_info=True)
            raise
