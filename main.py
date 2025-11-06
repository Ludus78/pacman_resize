"""Point d'entrée principal du jeu Pacman.

Ce module lance le menu principal et démarre la partie de jeu.
"""
from game.menu import main_menu
from game.game_loop import GameLoop


def main() -> None:
    """Point d'entrée du jeu Pacman.
    
    Affiche le menu principal et lance le jeu selon le choix de l'utilisateur.
    """
    # Affiche le menu principal et attend un choix de l'utilisateur
    choix = main_menu()
    
    if choix == "JOUER":
        # Lance la boucle de jeu
        game_loop = GameLoop()
        game_loop.run()
    elif choix == "PARAMÈTRES":
        print("Ouverture des paramètres... (à implémenter)")
        # TODO: ouvrir un écran de paramètres
    else:
        print("Au revoir.")


if __name__ == "__main__":
    main()
