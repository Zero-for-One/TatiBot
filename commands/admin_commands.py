"""Admin-only commands."""
import discord
from discord import app_commands
import logging
import json
import io
from datetime import datetime
from core.data_manager import save_old_votes, clear_votes, export_guild_data, import_guild_data
from core.helpers import require_admin, require_guild, send_guild_only_error, send_admin_error

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
            from core.translations import get_translation
            t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw) if guild_id else get_translation(k, lang="en", **kw)
            await interaction.followup.send(
                t("sync_error", error=str(e)),
                ephemeral=True
            )
    
    
    @bot.tree.command(name="exportdata", description="Export all server data (games, votes, config, schedules)")
    async def exportdata(interaction: discord.Interaction):
        """Export all server data as a JSON file."""
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
            
            # Export all data
            export_data = export_guild_data(guild_id)
            
            # Create JSON file in memory
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            
            # Create file-like object
            file_obj = io.BytesIO(json_bytes)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tatiBot_export_{guild_id}_{timestamp}.json"
            
            # Send as file attachment
            file = discord.File(file_obj, filename=filename)
            
            await interaction.followup.send(
                t("export_success", filename=filename),
                file=file,
                ephemeral=True
            )
            
            logger.info(f"Data exported by {interaction.user} (ID: {user_id}) in guild {guild_id}")
            
        except Exception as e:
            guild_id = interaction.guild.id if interaction.guild else None
            user_id = str(interaction.user.id)
            from core.translations import get_translation
            t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw) if guild_id else get_translation(k, lang="en", **kw)
            await interaction.followup.send(
                t("export_error", error=str(e)),
                ephemeral=True
            )
            logger.error(f"Export error: {e}", exc_info=True)
    
    
    @bot.tree.command(name="importdata", description="Import server data from a JSON file")
    @app_commands.describe(
        file="The JSON export file to import",
        overwrite="If true, completely replace existing data. If false, merge with existing data."
    )
    async def importdata(interaction: discord.Interaction, file: discord.Attachment, overwrite: bool = False):
        """Import server data from an exported JSON file."""
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
            
            # Check file type
            if not file.filename.endswith('.json'):
                await interaction.followup.send(
                    t("import_error_invalid_file"),
                    ephemeral=True
                )
                return
            
            # Download and parse JSON
            file_content = await file.read()
            try:
                data = json.loads(file_content.decode('utf-8'))
            except json.JSONDecodeError as e:
                await interaction.followup.send(
                    t("import_error_invalid_json", error=str(e)),
                    ephemeral=True
                )
                return
            
            # Validate data structure
            if not isinstance(data, dict):
                await interaction.followup.send(
                    t("import_error_invalid_format"),
                    ephemeral=True
                )
                return
            
            # Import data
            results = import_guild_data(guild_id, data, overwrite=overwrite)
            
            # Build result message
            mode = t("import_mode_overwrite") if overwrite else t("import_mode_merge")
            message_parts = [
                t("import_success", mode=mode),
                f"• {t('import_games', count=results['games'])}",
                f"• {t('import_votes', count=results['votes'])}",
                f"• {t('import_config', success='✅' if results['config'] else '❌')}",
                f"• {t('import_schedules', count=results['schedules'])}"
            ]
            
            if results["errors"]:
                message_parts.append(f"\n⚠️ {t('import_warnings', count=len(results['errors']))}")
                for error in results["errors"]:
                    message_parts.append(f"  • {error}")
            
            await interaction.followup.send(
                "\n".join(message_parts),
                ephemeral=True
            )
            
            logger.info(f"Data imported by {interaction.user} (ID: {user_id}) in guild {guild_id} (overwrite={overwrite})")
            
        except Exception as e:
            guild_id = interaction.guild.id if interaction.guild else None
            user_id = str(interaction.user.id)
            from core.translations import get_translation
            t = lambda k, **kw: get_translation(k, user_id=user_id, guild_id=guild_id, **kw) if guild_id else get_translation(k, lang="en", **kw)
            await interaction.followup.send(
                t("import_error", error=str(e)),
                ephemeral=True
            )
            logger.error(f"Import error: {e}", exc_info=True)
