from game.menu import main_menu

# Point d'entrée du jeu Pacman
def main() -> None:
    # Affiche le menu principal et attend un choix de l'utilisateur
    choix = main_menu()

    if choix == "JOUER":
        print("Démarrage du jeu... (à implémenter)")
        # TODO: appeler la boucle de jeu quand elle sera prête
    elif choix == "PARAMÈTRES":
        print("Ouverture des paramètres... (à implémenter)")
        # TODO: ouvrir un écran de paramètres
    else:
        print("Au revoir.")


if __name__ == "__main__":
    main()
