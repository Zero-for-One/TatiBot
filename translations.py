"""Translation strings for the bot."""
from typing import Dict

# Translation dictionaries
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Common
        "error_no_games": "❌ No games in the list yet!",
        "error_game_not_found": "❌ Game '{game}' not found in the list!",
        "error_need_admin": "❌ You need administrator permissions to use this command.",
        
        # Game commands
        "game_added": "✅ Added {emoji} '{name}' (Players: {min_players}-{max_players})",
        "game_removed": "✅ Removed '[{game_id}] {game_name}' from the list",
        "game_exists": "❌ Game '{name}' is already in the list!",
        "game_invalid_min": "❌ Invalid player count! Minimum must be at least 1.",
        "game_invalid_max": "❌ Invalid player count! Maximum must be >= minimum.",
        "game_list_title": "🎮 Available Games",
        "game_update_title": "🔧 Update Game",
        "game_update_description": "Select a game from the dropdown below to update its properties.",
        
        # Voting
        "vote_title": "🎮 Game Voting",
        "vote_description": "Select a game and rate it from 1-5 stars.\nGames not voted on default to rating 0.",
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
    },
    "fr": {
        # Common
        "error_no_games": "❌ Aucun jeu dans la liste pour le moment !",
        "error_game_not_found": "❌ Jeu '{game}' introuvable dans la liste !",
        "error_need_admin": "❌ Vous devez avoir les permissions d'administrateur pour utiliser cette commande.",
        
        # Game commands
        "game_added": "✅ Ajouté {emoji} '{name}' (Joueurs : {min_players}-{max_players})",
        "game_removed": "✅ Supprimé '[{game_id}] {game_name}' de la liste",
        "game_exists": "❌ Le jeu '{name}' est déjà dans la liste !",
        "game_invalid_min": "❌ Nombre de joueurs invalide ! Le minimum doit être d'au moins 1.",
        "game_invalid_max": "❌ Nombre de joueurs invalide ! Le maximum doit être >= au minimum.",
        "game_list_title": "🎮 Jeux Disponibles",
        "game_update_title": "🔧 Modifier un Jeu",
        "game_update_description": "Sélectionnez un jeu dans le menu déroulant ci-dessous pour modifier ses propriétés.",
        "game_update_select": "Choisissez un jeu à modifier...",
        
        # Voting
        "vote_title": "🎮 Vote pour les Jeux",
        "vote_description": "Sélectionnez un jeu et notez-le de 1 à 5 étoiles.\nLes jeux non votés ont une note par défaut de 0.",
        "vote_table_title": "📊 Vos Votes",
        "vote_table_continued": "📊 Vos Votes (suite)",
        "vote_select_game": "Choisissez un jeu pour voter...",
        "vote_select_rating": "Choisissez une note...",
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

