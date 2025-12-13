"""Translation strings for the bot."""
from typing import Dict

# Translation dictionaries
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Common
        "error_no_games": "❌ No games in the list yet!",
        "error_game_not_found": "❌ Game '{game}' not found in the list!",
        "error_need_admin": "❌ You need administrator permissions to use this command.",
        "error_need_permission": "❌ You don't have permission to manage games. Ask an admin to configure game management roles.",
        
        # Game commands
        "game_added": "✅ Added {emoji} '{name}' (Players: {min_players}-{max_players})",
        "game_removed": "✅ Removed '[{game_id}] {game_name}' from the list",
        "game_exists": "❌ Game '{name}' is already in the list!",
        "game_invalid_min": "❌ Invalid player count! Minimum must be at least 1.",
        "game_invalid_max": "❌ Invalid player count! Maximum must be >= minimum.",
        "game_list_title": "🎮 Available Games",
        "game_update_title": "🔧 Update Game",
        "game_update_description": "Select a game from the dropdown below to update its properties.",
        "game_remove_title": "🗑️ Remove Game",
        "game_remove_description": "Select a game from the dropdown below to remove it.",
        "game_remove_select": "Choose a game to remove...",
        "game_update_modal_title": "🔧 Update Game",
        "game_update_name_label": "Game Name",
        "game_update_name_placeholder": "Enter the game name",
        "game_update_min_label": "Minimum Players",
        "game_update_min_placeholder": "e.g., 1",
        "game_update_max_label": "Maximum Players",
        "game_update_max_placeholder": "e.g., 10",
        "game_update_emoji_label": "Emoji",
        "game_update_emoji_placeholder": "e.g., 🎮",
        "game_update_select": "Choose a game to update...",
        "game_add_modal_title": "➕ Add New Game",
        "game_add_name_label": "Game Name",
        "game_add_name_placeholder": "Enter the game name",
        "game_add_min_label": "Minimum Players",
        "game_add_min_placeholder": "Default: 1",
        "game_add_max_label": "Maximum Players",
        "game_add_max_placeholder": "Default: 10",
        "game_add_emoji_label": "Emoji",
        "game_add_emoji_placeholder": "Default: 🎮",
        "game_add_store_links_label": "Store Links (optional)",
        "game_add_store_links_placeholder": "e.g., Steam: https://..., Epic: https://...",
        "game_update_store_links_label": "Store Links",
        "game_update_store_links_placeholder": "e.g., Steam: https://..., Epic: https://...",
        "gameroles_set": "✅ Game management roles set to: {roles}\nOnly admins and users with these roles can add/remove/update games.",
        "gameroles_cleared": "✅ Game management roles cleared. Only administrators can manage games now.",
        "gameroles_invalid": "❌ Could not find any valid roles. Please mention roles or use role names.",
        
        # Voting
        "vote_title": "🎮 Game Voting",
        "vote_description": "Select a game and rate it from 1-5 stars.\nGames not voted on default to rating 0.",
        "vote_modal_title": "⭐ Vote: {game}",
        "vote_modal_rating_label": "Rating (1-5)",
        "vote_modal_rating_placeholder": "Enter a rating from 1 to 5 (default: 5)",
        "vote_modal_invalid_rating": "❌ Invalid rating! Please enter a number from 1 to 5.",
        "vote_modal_success": "✅ Voted {rating}/5 {stars} for **{game}**!",
        "vote_table_title": "📊 Your Votes",
        "vote_table_continued": "📊 Your Votes (cont.)",
        "vote_select_game": "Choose a game to vote for...",
        "vote_select_rating": "Choose a rating...",
        "vote_rating_placeholder": "Choose rating (1-5)...",
        "vote_selected_game": "Selected: {game}",
        "vote_selected_rating": "Selected: {rating}/5 {stars}",
        "vote_players_desc": "Players: {min}-{max}",
        "vote_rating_5": "5 - Really want to play ⭐⭐⭐⭐⭐",
        "vote_rating_4": "4 - Want to play ⭐⭐⭐⭐",
        "vote_rating_3": "3 - Neutral ⭐⭐⭐",
        "vote_rating_2": "2 - Don't really want ⭐⭐",
        "vote_rating_1": "1 - Don't want to play ⭐",
        "vote_restore_button": "🔄 Restore Last Votes",
        "vote_restore_no_previous": "❌ No previous votes found to restore!",
        "vote_restore_no_user": "❌ You didn't have any votes in any previous period!",
        "vote_restore_success": "✅ Restored {count} of **your** vote(s) from {date}!\nThis only affects your votes - others' votes are unchanged.\nYou can still modify them using the dropdowns above.",
        "vote_restore_no_match": "❌ None of your previous votes match games in the current list!",
        "vote_need_game": "❌ Please select a game first!",
        "vote_saved": "Vote saved: {user} voted {rating}/5 for '{game}'",
        
        # My votes
        "myvotes_title": "Your Votes",
        "myvotes_description": "Games you haven't voted for default to rating 0.",
        "myvotes_available": "✅ You are marked as available for game night",
        "myvotes_unavailable": "❌ You are not marked as available (no votes)",
        "myvotes_not_voted": "(not voted)",
        
        # Unavailable/Available
        "unavailable_success": "✅ You've been marked as unavailable. Your votes are preserved and will be restored when you mark yourself available again.",
        "unavailable_already": "ℹ️ You're already marked as unavailable.",
        "available_success": "✅ You've been marked as available! Your previous votes have been restored.",
        "available_already": "ℹ️ You're already marked as available.",
        "available_no_votes": "✅ You've been marked as available! Use `/vote` to start voting.",
        
        # Results
        "results_no_votes": "❌ No votes yet! Use `/vote` to start voting.",
        "results_title": "📊 Voting Results",
        "results_available_players": "**Available Players:** {count}",
        "results_no_compatible": "⚠️ No Compatible Games",
        "results_no_compatible_desc": "With {count} player(s), no games match the player count requirements.",
        "results_recommended": "🏆 Recommended Game",
        "results_recommended_score": "Score: {score} points",
        "results_recommended_players": "Players: {min}-{max} ✅",
        "results_top_games": "Top 5 Compatible Games",
        "results_all_games": "All Compatible Games",
        "results_top_showing": "Top 5 Compatible Games (showing 5 of {total})",
        "results_voters": "👥 Voters (Available)",
        
        # Clear votes
        "clearvotes_success": "✅ All votes have been cleared! Ready for a new voting period.",
        "clearvotes_backup": "📁 Previous votes saved to: `{file}`",
        
        # Sync
        "sync_success": "✅ Successfully synced {count} command(s) to this server!\nCommands should be available immediately.",
        "sync_error": "❌ Failed to sync commands: {error}",
        
        # Language
        "language_current": "Your current language is: **{lang}**",
        "language_changed": "✅ Language changed to **{lang}**",
        "language_invalid": "❌ Invalid language! Available: {options}",
        "language_options": "English (en), Français (fr)",
        
        # Help
        "help_title": "🎮 TatiBot Help",
        "help_description": "A Discord bot for organizing game nights! Vote on games and find the perfect match for your group.\n\nEach server has its own game list and votes. Use `/language` to change your preferred language.",
        "help_how_it_works": "📖 How It Works",
        "help_how_it_works_value": "1. **Vote**: Use `/vote` to rate games from 1-5 stars\n"
                                   "2. **Availability**: Voting marks you as available for game night\n"
                                   "3. **Unavailable**: Use `/unavailable` to mark yourself unavailable (votes preserved)\n"
                                   "4. **Available**: Use `/available` to mark yourself available again (votes restored)\n"
                                   "5. **Results**: Use `/results` to see all compatible games with pagination\n"
                                   "6. **Auto Reset**: Votes reset every Wednesday at 11:59 PM\n"
                                   "7. **Reminders**: Bot reminds everyone to vote (configurable per server, default: Sunday 8 PM)",
        "help_voting_commands": "⭐ Voting Commands",
        "help_voting_commands_value": "**`/vote`** - Open interactive voting interface\n"
                                      "• Select games from dropdown and rate them 1-5\n"
                                      "• Default rating is 5 if not specified\n"
                                      "• Games not voted on = rating 0\n"
                                      "• Table updates automatically after each vote\n"
                                      "• Use 'Restore Last Votes' to restore previous week's votes\n"
                                      "• Voting automatically marks you as available\n\n"
                                      "**`/myvotes`** - View all your current votes and availability status\n\n"
                                      "**`/unavailable`** - Mark yourself unavailable (keeps your votes)\n\n"
                                      "**`/available`** - Mark yourself available again (restores your votes)",
        "help_game_management": "🎮 Game Management",
        "help_game_management_value": "**`/addgame`** - Add a new game using a form\n"
                                      "• Opens a form to enter game details\n"
                                      "• Defaults: min=1, max=10, emoji=🎮\n"
                                      "• Optional store links (Steam, Epic, etc.)\n"
                                      "• Games get unique IDs automatically\n"
                                      "• Requires game management permission\n\n"
                                      "**`/listgames`** - Show all games with IDs, player counts, and store links\n\n"
                                      "**`/removegame`** - Remove a game using a dropdown (requires permission)\n\n"
                                      "**`/updategame`** - Interactive menu to update game properties (requires permission)\n\n"
                                      "**`/setgameemoji <game> <emoji>`** - Change a game's emoji (requires permission)\n\n"
                                      "**`/setgameroles <roles>`** - Configure which roles can manage games (admin only)\n"
                                      "• Set roles that can add/remove/update games\n"
                                      "• Accepts role mentions or names (comma-separated)\n"
                                      "• Leave empty to allow only admins",
        "help_results_utilities": "📊 Results & Utilities",
        "help_results_utilities_value": "**`/results`** - Show all compatible games with pagination\n"
                                        "• Filters games by player count compatibility\n"
                                        "• Shows all games sorted by score (pagination if more than 10)\n"
                                        "• Displays store links for each game\n"
                                        "• Only counts available players (not marked unavailable)\n\n"
                                        "**`/language <lang>`** - Set your preferred language\n"
                                        "• Choose English (en) or Français (fr)\n"
                                        "• All bot messages will appear in your language\n\n"
                                        "**`/clearvotes`** - Manually clear all votes (saves backup)\n\n"
                                        "**`/sync`** - Force sync commands (admin only)",
        "help_scheduling": "📅 Scheduling",
        "help_scheduling_value": "**`/schedule <date> <time> [description]`** - Schedule a game night\n"
                                 "• Date format: YYYY-MM-DD (e.g., 2024-12-25)\n"
                                 "• Time format: HH:MM 24-hour (e.g., 20:00)\n"
                                 "• Optional description\n\n"
                                 "**`/schedules`** - List all upcoming scheduled game nights\n\n"
                                 "**`/configreminder <day> <hour> <minute>`** - Configure reminder schedule (admin only)\n"
                                 "• Set when voting reminders are sent per server\n"
                                 "• Default: Sunday at 20:00 (8 PM)\n\n"
                                 "**`/configgamenight <day> <hour> <minute>`** - Configure recurring game night (admin only)\n\n"
                                 "**`/config`** - View current server configuration",
        "help_rating_system": "⭐ Rating System",
        "help_rating_system_value": "**1 ⭐** - Don't want to play\n"
                                    "**2 ⭐⭐** - Prefer not to\n"
                                    "**3 ⭐⭐⭐** - Neutral/OK\n"
                                    "**4 ⭐⭐⭐⭐** - Want to play\n"
                                    "**5 ⭐⭐⭐⭐⭐** - Really want to play!",
        "help_tips": "💡 Tips",
        "help_tips_value": "• Use game IDs for easier management (shown in `/listgames`)\n"
                           "• Add store links (Steam, Epic, etc.) when creating/updating games\n"
                           "• Voting automatically marks you as available\n"
                           "• Use `/unavailable` to mark yourself unavailable (votes are preserved)\n"
                           "• Use `/available` to restore your votes when you're back\n"
                           "• Votes auto-reset every Wednesday at 11:59 PM\n"
                           "• Previous votes are backed up automatically\n"
                           "• Games must match player count to appear in results\n"
                           "• `/results` shows all games with pagination (not just top 5)\n"
                           "• Use `/setgameroles` to allow specific roles to manage games\n"
                           "• Use `/configreminder` to customize reminder schedule per server\n"
                           "• Use `/schedule` to schedule specific game nights\n"
                           "• Each server has its own separate game list and votes\n"
                           "• Use `/language` to change your preferred language",
        "help_footer": "Need more help? Check the README or ask an admin!",
        "error_server_only": "❌ This command can only be used in a server!",
        
        # Scheduling
        "schedule_invalid_date": "❌ Invalid date format! Please use YYYY-MM-DD (e.g., 2024-12-25).",
        "schedule_invalid_time": "❌ Invalid time format! Please use HH:MM in 24-hour format (e.g., 20:00 for 8 PM).",
        "schedule_past_date": "❌ Cannot schedule a game night in the past! Please choose a future date.",
        "schedule_success": "✅ Game night scheduled for **{date}** at **{time}**{description}!",
        "schedules_title": "📅 Upcoming Game Nights",
        "schedules_none": "📅 No upcoming game nights scheduled.",
        "schedules_more": "And {count} more...",
        "configreminder_success": "✅ Voting reminder schedule updated to **{day}** at **{hour:02d}:{minute}**!\nNote: The bot needs to be restarted for the new schedule to take effect.",
        "configgamenight_success": "✅ Recurring game night schedule set to **{day}** at **{hour:02d}:{minute}**!\nNote: The bot needs to be restarted for the new schedule to take effect.",
        "configgamenight_disabled": "✅ Recurring game night schedule disabled.",
        "configgamenight_missing_time": "❌ Please provide both hour and minute when setting a game night schedule.",
        "config_invalid_hour": "❌ Invalid hour! Please use a number between 0 and 23 (24-hour format).",
        "config_invalid_minute": "❌ Invalid minute! Please use a number between 0 and 59.",
        "config_title": "⚙️ Server Configuration",
        "config_reminder": "📢 Voting Reminder",
        "config_gamenight": "🎮 Recurring Game Night",
        "config_gamenight_none": "Not configured",
    },
    "fr": {
        # Common
        "error_no_games": "❌ Aucun jeu dans la liste pour le moment !",
        "error_game_not_found": "❌ Jeu '{game}' introuvable dans la liste !",
        "error_need_admin": "❌ Vous devez avoir les permissions d'administrateur pour utiliser cette commande.",
        "error_need_permission": "❌ Vous n'avez pas la permission de gérer les jeux. Demandez à un admin de configurer les rôles de gestion des jeux.",
        
        # Game commands
        "game_added": "✅ Ajouté {emoji} '{name}' (Joueurs : {min_players}-{max_players})",
        "game_removed": "✅ Supprimé '[{game_id}] {game_name}' de la liste",
        "game_exists": "❌ Le jeu '{name}' est déjà dans la liste !",
        "game_invalid_min": "❌ Nombre de joueurs invalide ! Le minimum doit être d'au moins 1.",
        "game_invalid_max": "❌ Nombre de joueurs invalide ! Le maximum doit être >= au minimum.",
        "game_list_title": "🎮 Jeux Disponibles",
        "game_update_title": "🔧 Modifier un Jeu",
        "game_update_description": "Sélectionnez un jeu dans le menu déroulant ci-dessous pour modifier ses propriétés.",
        "game_remove_title": "🗑️ Supprimer un Jeu",
        "game_remove_description": "Sélectionnez un jeu dans le menu déroulant ci-dessous pour le supprimer.",
        "game_remove_select": "Choisissez un jeu à supprimer...",
        "game_update_modal_title": "🔧 Modifier un Jeu",
        "game_update_name_label": "Nom du Jeu",
        "game_update_name_placeholder": "Entrez le nom du jeu",
        "game_update_min_label": "Joueurs Minimum",
        "game_update_min_placeholder": "ex: 1",
        "game_update_max_label": "Joueurs Maximum",
        "game_update_max_placeholder": "ex: 10",
        "game_update_emoji_label": "Emoji",
        "game_update_emoji_placeholder": "ex: 🎮",
        "game_update_select": "Choisissez un jeu à modifier...",
        "game_add_modal_title": "➕ Ajouter un Nouveau Jeu",
        "game_add_name_label": "Nom du Jeu",
        "game_add_name_placeholder": "Entrez le nom du jeu",
        "game_add_min_label": "Joueurs Minimum",
        "game_add_min_placeholder": "Par défaut : 1",
        "game_add_max_label": "Joueurs Maximum",
        "game_add_max_placeholder": "Par défaut : 10",
        "game_add_emoji_label": "Emoji",
        "game_add_emoji_placeholder": "Par défaut : 🎮",
        "game_add_store_links_label": "Liens de Magasin (optionnel)",
        "game_add_store_links_placeholder": "ex: Steam: https://..., Epic: https://...",
        "game_update_store_links_label": "Liens de Magasin",
        "game_update_store_links_placeholder": "ex: Steam: https://..., Epic: https://...",
        "gameroles_set": "✅ Rôles de gestion des jeux définis : {roles}\nSeuls les admins et les utilisateurs avec ces rôles peuvent ajouter/supprimer/modifier les jeux.",
        "gameroles_cleared": "✅ Rôles de gestion des jeux effacés. Seuls les administrateurs peuvent gérer les jeux maintenant.",
        "gameroles_invalid": "❌ Impossible de trouver des rôles valides. Veuillez mentionner les rôles ou utiliser les noms de rôles.",
        
        # Voting
        "vote_title": "🎮 Vote pour les Jeux",
        "vote_description": "Sélectionnez un jeu et notez-le de 1 à 5 étoiles.\nLes jeux non votés ont une note par défaut de 0.",
        "vote_table_title": "📊 Vos Votes",
        "vote_table_continued": "📊 Vos Votes (suite)",
        "vote_select_game": "Choisissez un jeu pour voter...",
        "vote_select_rating": "Choisissez une note...",
        "vote_modal_title": "⭐ Vote : {game}",
        "vote_modal_rating_label": "Note (1-5)",
        "vote_modal_rating_placeholder": "Entrez une note de 1 à 5 (par défaut : 5)",
        "vote_modal_invalid_rating": "❌ Note invalide ! Veuillez entrer un nombre de 1 à 5.",
        "vote_modal_success": "✅ Voté {rating}/5 {stars} pour **{game}** !",
        "vote_restore_button": "🔄 Restaurer les Derniers Votes",
        "vote_restore_no_previous": "❌ Aucun vote précédent trouvé à restaurer !",
        "vote_restore_no_user": "❌ Vous n'aviez aucun vote dans aucune période précédente !",
        "vote_restore_success": "✅ Restauré {count} de **vos** vote(s) du {date} !\nCela n'affecte que vos votes - les votes des autres ne changent pas.\nVous pouvez toujours les modifier avec les menus déroulants ci-dessus.",
        "vote_restore_no_match": "❌ Aucun de vos votes précédents ne correspond aux jeux de la liste actuelle !",
        "vote_need_game": "❌ Veuillez d'abord sélectionner un jeu !",
        "vote_saved": "Vote enregistré : {user} a voté {rating}/5 pour '{game}'",
        
        # My votes
        "myvotes_title": "Vos Votes",
        "myvotes_description": "Les jeux pour lesquels vous n'avez pas voté ont une note par défaut de 0.",
        "myvotes_available": "✅ Vous êtes marqué(e) comme disponible pour la soirée jeu",
        "myvotes_unavailable": "❌ Vous n'êtes pas marqué(e) comme disponible (pas de votes)",
        "myvotes_not_voted": "(non voté)",
        
        # Unavailable
        "unavailable_success": "✅ Vous avez été marqué(e) comme indisponible. Tous vos votes ont été supprimés.",
        "unavailable_no_votes": "❌ Vous n'avez aucun vote à supprimer.",
        
        # Results
        "results_no_votes": "❌ Aucun vote pour le moment ! Utilisez `/vote` pour commencer à voter.",
        "results_title": "📊 Résultats des Votes",
        "results_available_players": "**Joueurs Disponibles :** {count}",
        "results_no_compatible": "⚠️ Aucun Jeu Compatible",
        "results_no_compatible_desc": "Avec {count} joueur(s), aucun jeu ne correspond aux exigences de nombre de joueurs.",
        "results_recommended": "🏆 Jeu Recommandé",
        "results_recommended_score": "Score : {score} points",
        "results_recommended_players": "Joueurs : {min}-{max} ✅",
        "results_top_games": "Top 5 des Jeux Compatibles",
        "results_all_games": "Tous les Jeux Compatibles",
        "results_top_showing": "Top 5 des Jeux Compatibles (affichage de 5 sur {total})",
        "results_voters": "👥 Votants (Disponibles)",
        
        # Clear votes
        "clearvotes_success": "✅ Tous les votes ont été effacés ! Prêt pour une nouvelle période de vote.",
        "clearvotes_backup": "📁 Votes précédents sauvegardés dans : `{file}`",
        
        # Sync
        "sync_success": "✅ {count} commande(s) synchronisée(s) avec succès sur ce serveur !\nLes commandes devraient être disponibles immédiatement.",
        "sync_error": "❌ Échec de la synchronisation des commandes : {error}",
        
        # Language
        "language_current": "Votre langue actuelle est : **{lang}**",
        "language_changed": "✅ Langue changée en **{lang}**",
        "language_invalid": "❌ Langue invalide ! Disponibles : {options}",
        "language_options": "English (en), Français (fr)",
        
        # Help
        "help_title": "🎮 Aide TatiBot",
        "help_description": "Un bot Discord pour organiser des soirées jeux ! Votez pour les jeux et trouvez le match parfait pour votre groupe.\n\nChaque serveur a sa propre liste de jeux et ses votes. Utilisez `/language` pour changer votre langue préférée.",
        "help_how_it_works": "📖 Comment Ça Marche",
        "help_how_it_works_value": "1. **Votez** : Utilisez `/vote` pour noter les jeux de 1 à 5 étoiles\n"
                                   "2. **Disponibilité** : Voter vous marque comme disponible pour la soirée jeu\n"
                                   "3. **Indisponible** : Utilisez `/unavailable` pour vous marquer indisponible (votes préservés)\n"
                                   "4. **Disponible** : Utilisez `/available` pour vous marquer disponible à nouveau (votes restaurés)\n"
                                   "5. **Résultats** : Utilisez `/results` pour voir tous les jeux compatibles avec pagination\n"
                                   "6. **Réinitialisation Auto** : Les votes se réinitialisent chaque mercredi à 23h59\n"
                                   "7. **Rappels** : Le bot rappelle à tout le monde de voter (configurable par serveur, par défaut : dimanche 20h)",
        "help_voting_commands": "⭐ Commandes de Vote",
        "help_voting_commands_value": "**`/vote`** - Ouvrir l'interface de vote interactive\n"
                                      "• Sélectionnez des jeux dans le menu déroulant et notez-les de 1 à 5\n"
                                      "• La note par défaut est 5 si non spécifiée\n"
                                      "• Les jeux non votés = note 0\n"
                                      "• Le tableau se met à jour automatiquement après chaque vote\n"
                                      "• Utilisez 'Restaurer les Derniers Votes' pour restaurer les votes de la semaine précédente\n"
                                      "• Voter vous marque automatiquement comme disponible\n\n"
                                      "**`/myvotes`** - Voir tous vos votes actuels et votre statut de disponibilité\n\n"
                                      "**`/unavailable`** - Vous marquer indisponible (garde vos votes)\n\n"
                                      "**`/available`** - Vous marquer disponible à nouveau (restaure vos votes)",
        "help_game_management": "🎮 Gestion des Jeux",
        "help_game_management_value": "**`/addgame`** - Ajouter un nouveau jeu avec un formulaire\n"
                                      "• Ouvre un formulaire pour saisir les détails du jeu\n"
                                      "• Par défaut : min=1, max=10, emoji=🎮\n"
                                      "• Liens de magasin optionnels (Steam, Epic, etc.)\n"
                                      "• Les jeux obtiennent des ID uniques automatiquement\n"
                                      "• Nécessite la permission de gestion des jeux\n\n"
                                      "**`/listgames`** - Afficher tous les jeux avec ID, nombre de joueurs et liens de magasin\n\n"
                                      "**`/removegame`** - Supprimer un jeu avec un menu déroulant (nécessite permission)\n\n"
                                      "**`/updategame`** - Menu interactif pour modifier les propriétés d'un jeu (nécessite permission)\n\n"
                                      "**`/setgameemoji <game> <emoji>`** - Changer l'emoji d'un jeu (nécessite permission)\n\n"
                                      "**`/setgameroles <roles>`** - Configurer quels rôles peuvent gérer les jeux (admin uniquement)\n"
                                      "• Définir les rôles qui peuvent ajouter/supprimer/modifier les jeux\n"
                                      "• Accepte les mentions de rôles ou les noms (séparés par des virgules)\n"
                                      "• Laisser vide pour autoriser uniquement les admins",
        "help_results_utilities": "📊 Résultats et Utilitaires",
        "help_results_utilities_value": "**`/results`** - Afficher tous les jeux compatibles avec pagination\n"
                                        "• Filtre les jeux par compatibilité du nombre de joueurs\n"
                                        "• Affiche tous les jeux triés par score (pagination si plus de 10)\n"
                                        "• Affiche les liens de magasin pour chaque jeu\n"
                                        "• Ne compte que les joueurs disponibles (non marqués indisponibles)\n\n"
                                        "**`/language <lang>`** - Définir votre langue préférée\n"
                                        "• Choisissez English (en) ou Français (fr)\n"
                                        "• Tous les messages du bot apparaîtront dans votre langue\n\n"
                                        "**`/clearvotes`** - Effacer manuellement tous les votes (sauvegarde une copie)\n\n"
                                        "**`/sync`** - Forcer la synchronisation des commandes (admin uniquement)",
        "help_scheduling": "📅 Planification",
        "help_scheduling_value": "**`/schedule <date> <time> [description]`** - Planifier une soirée de jeu\n"
                                 "• Format de date : AAAA-MM-JJ (ex: 2024-12-25)\n"
                                 "• Format d'heure : HH:MM 24h (ex: 20:00)\n"
                                 "• Description optionnelle\n\n"
                                 "**`/schedules`** - Lister toutes les soirées de jeu planifiées à venir\n\n"
                                 "**`/configreminder <day> <hour> <minute>`** - Configurer le planning des rappels (admin uniquement)\n"
                                 "• Définir quand les rappels de vote sont envoyés par serveur\n"
                                 "• Par défaut : dimanche à 20:00 (20h)\n\n"
                                 "**`/configgamenight <day> <hour> <minute>`** - Configurer la soirée de jeu récurrente (admin uniquement)\n\n"
                                 "**`/config`** - Voir la configuration actuelle du serveur",
        "help_rating_system": "⭐ Système de Notation",
        "help_rating_system_value": "**1 ⭐** - Ne veut pas jouer\n"
                                    "**2 ⭐⭐** - Préfère ne pas\n"
                                    "**3 ⭐⭐⭐** - Neutre/OK\n"
                                    "**4 ⭐⭐⭐⭐** - Veut jouer\n"
                                    "**5 ⭐⭐⭐⭐⭐** - Veut vraiment jouer !",
        "help_tips": "💡 Conseils",
        "help_tips_value": "• Utilisez les ID de jeu pour une gestion plus facile (affichés dans `/listgames`)\n"
                           "• Ajoutez des liens de magasin (Steam, Epic, etc.) lors de la création/modification des jeux\n"
                           "• Voter vous marque automatiquement comme disponible\n"
                           "• Utilisez `/unavailable` pour vous marquer indisponible (votes préservés)\n"
                           "• Utilisez `/available` pour restaurer vos votes quand vous revenez\n"
                           "• Les votes se réinitialisent automatiquement chaque mercredi à 23h59\n"
                           "• Les votes précédents sont sauvegardés automatiquement\n"
                           "• Les jeux doivent correspondre au nombre de joueurs pour apparaître dans les résultats\n"
                           "• `/results` affiche tous les jeux avec pagination (pas seulement le top 5)\n"
                           "• Utilisez `/setgameroles` pour autoriser des rôles spécifiques à gérer les jeux\n"
                           "• Utilisez `/configreminder` pour personnaliser le planning des rappels par serveur\n"
                           "• Utilisez `/schedule` pour planifier des soirées de jeu spécifiques\n"
                           "• Chaque serveur a sa propre liste de jeux et ses votes séparés\n"
                           "• Utilisez `/language` pour changer votre langue préférée",
        "help_footer": "Besoin d'aide ? Consultez le README ou demandez à un admin !",
        "error_server_only": "❌ Cette commande ne peut être utilisée que dans un serveur !",
        
        # Scheduling
        "schedule_invalid_date": "❌ Format de date invalide ! Veuillez utiliser AAAA-MM-JJ (ex: 2024-12-25).",
        "schedule_invalid_time": "❌ Format d'heure invalide ! Veuillez utiliser HH:MM en format 24h (ex: 20:00 pour 20h).",
        "schedule_past_date": "❌ Impossible de planifier une soirée de jeu dans le passé ! Veuillez choisir une date future.",
        "schedule_success": "✅ Soirée de jeu planifiée pour le **{date}** à **{time}**{description} !",
        "schedules_title": "📅 Soirées de Jeu à Venir",
        "schedules_none": "📅 Aucune soirée de jeu planifiée.",
        "schedules_more": "Et {count} de plus...",
        "configreminder_success": "✅ Planification des rappels de vote mise à jour pour **{day}** à **{hour:02d}:{minute}** !\nNote : Le bot doit être redémarré pour que le nouveau planning prenne effet.",
        "configgamenight_success": "✅ Planification de soirée de jeu récurrente définie pour **{day}** à **{hour:02d}:{minute}** !\nNote : Le bot doit être redémarré pour que le nouveau planning prenne effet.",
        "configgamenight_disabled": "✅ Planification de soirée de jeu récurrente désactivée.",
        "configgamenight_missing_time": "❌ Veuillez fournir l'heure et la minute lors de la définition d'une planification de soirée de jeu.",
        "config_invalid_hour": "❌ Heure invalide ! Veuillez utiliser un nombre entre 0 et 23 (format 24h).",
        "config_invalid_minute": "❌ Minute invalide ! Veuillez utiliser un nombre entre 0 et 59.",
        "config_title": "⚙️ Configuration du Serveur",
        "config_reminder": "📢 Rappel de Vote",
        "config_gamenight": "🎮 Soirée de Jeu Récurrente",
        "config_gamenight_none": "Non configuré",
    }
}


def get_user_language(user_id: str, guild_id: int, votes: dict = None) -> str:
    """Get user's preferred language, defaulting to 'en'.
    
    Args:
        user_id: The user's ID as a string
        guild_id: The Discord guild (server) ID
        votes: Optional votes dict (will load if not provided)
    
    Returns:
        Language code ('en' or 'fr')
    """
    if votes is None:
        from data_manager import load_votes
        votes = load_votes(guild_id)
    
    user_data = votes.get(str(user_id), {})
    return user_data.get("language", "en")


def get_translation(key: str, user_id: str = None, guild_id: int = None, lang: str = None, votes: dict = None, **kwargs) -> str:
    """Get a translated string.
    
    Args:
        key: Translation key
        user_id: User ID to get language from (optional if lang is provided)
        guild_id: The Discord guild (server) ID (required if user_id is provided)
        lang: Language code directly (optional if user_id is provided)
        votes: Optional votes dict (will load if not provided)
        **kwargs: Variables to format into the string
    
    Returns:
        Translated and formatted string
    """
    if lang is None:
        if user_id is None:
            lang = "en"
        else:
            if guild_id is None:
                lang = "en"  # Default if guild_id not provided
            else:
                lang = get_user_language(user_id, guild_id, votes)
    
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    text = translations.get(key, TRANSLATIONS["en"].get(key, key))
    
    # Format the string with kwargs
    try:
        return text.format(**kwargs)
    except KeyError:
        # If formatting fails, return as-is
        return text


def set_user_language(user_id: str, lang: str, votes: dict = None) -> bool:
    """Set user's preferred language.
    
    Args:
        user_id: The user's ID as a string
        lang: Language code ('en' or 'fr')
        votes: Optional votes dict (will load if not provided)
    
    Returns:
        True if language is valid and set, False otherwise
    """
    if lang not in TRANSLATIONS:
        return False
    
    if votes is None:
        from data_manager import load_votes, save_votes
        votes = load_votes()
        should_save = True
    else:
        should_save = False
    
    user_id_str = str(user_id)
    if user_id_str not in votes:
        votes[user_id_str] = {
            "username": "",  # Will be set when user interacts
            "votes": {},
            "language": lang
        }
    else:
        votes[user_id_str]["language"] = lang
    
    if should_save:
        from data_manager import save_votes
        save_votes(votes)
    
    return True

