"""Admin-only commands."""
import discord
import logging
from data_manager import save_old_votes, clear_votes
from helpers import require_admin, send_guild_only_error, send_admin_error

logger = logging.getLogger(__name__)


def setup_admin_commands(bot: discord.ext.commands.Bot):
    """Register admin commands."""
    
    @bot.tree.command(name="clearvotes", description="Clear all votes (start fresh)")
    async def clearvotes(interaction: discord.Interaction):
        """Clear all votes. Use this to start a new voting period."""
        result = require_guild(interaction)
        if result is None:
            await send_guild_only_error(interaction)
            return
        
        guild_id, user_id, t = result
        
        old_file = save_old_votes(guild_id)
        clear_votes(guild_id, save_backup=False)
        
        logger.info(f"Votes cleared manually by {interaction.user} (ID: {interaction.user.id}) in guild {guild_id}")
        if old_file:
            logger.info(f"Votes backed up to: {old_file}")
        
        message = t("clearvotes_success")
        if old_file:
            message += f"\n{t('clearvotes_backup', file=old_file.split('/')[-1])}"
        
        await interaction.response.send_message(message)
    
    
    @bot.tree.command(name="sync", description="Force sync commands (admin only - for instant updates)")
    async def sync(interaction: discord.Interaction):
        """Force sync commands to this server for instant updates."""
        result = require_admin(interaction)
        if result is None:
            if not interaction.guild:
                await send_guild_only_error(interaction)
            else:
                await send_admin_error(interaction, interaction.guild.id, str(interaction.user.id))
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id, user_id, t = result
            bot.tree.copy_global_to(guild=interaction.guild)
            synced = await bot.tree.sync(guild=interaction.guild)
            
            await interaction.followup.send(
                t("sync_success", count=len(synced)),
                ephemeral=True
            )
        except Exception as e:
            guild_id = interaction.guild.id if interaction.guild else None
            user_id = str(interaction.user.id)
            from translations import get_translation
            t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw) if guild_id else get_translation(k, lang="en", **kw)
            await interaction.followup.send(
                t("sync_error", error=str(e)),
                ephemeral=True
            )
