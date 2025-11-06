#!/usr/bin/env python3
"""Script de test pour le système de victoire.

Ce script teste que la victoire est correctement détectée quand
tous les points (dots + power_dots) ont été mangés.
"""
import sys
import os

# Ajoute le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState
from game.entities import Position, Pellet, PowerPellet


def test_victory_detection():
    """Teste la détection de victoire."""
    print("🧪 Test du système de victoire...")
    print()
    
    # Crée un état de jeu de test
    state = GameState(800, 600)
    
    # Test 1 : Pas de victoire si des dots restent
    print("Test 1 : Dots restants → Pas de victoire")
    state.dots = {(1, 1): Pellet(Position(1, 1), value=1)}
    state.power_dots = {}
    result = state.check_victory()
    assert not result, "❌ ÉCHEC : Victoire détectée alors qu'il reste des dots"
    print(f"   ✅ RÉUSSI : check_victory() = {result}")
    print()
    
    # Test 2 : Pas de victoire si des power_dots restent
    print("Test 2 : Power dots restants → Pas de victoire")
    state.dots = {}
    state.power_dots = {(2, 2): PowerPellet(Position(2, 2))}
    result = state.check_victory()
    assert not result, "❌ ÉCHEC : Victoire détectée alors qu'il reste des power dots"
    print(f"   ✅ RÉUSSI : check_victory() = {result}")
    print()
    
    # Test 3 : Pas de victoire si les deux types restent
    print("Test 3 : Dots ET power dots restants → Pas de victoire")
    state.dots = {(1, 1): Pellet(Position(1, 1), value=1)}
    state.power_dots = {(2, 2): PowerPellet(Position(2, 2))}
    result = state.check_victory()
    assert not result, "❌ ÉCHEC : Victoire détectée alors qu'il reste des points"
    print(f"   ✅ RÉUSSI : check_victory() = {result}")
    print()
    
    # Test 4 : VICTOIRE si tous les points sont mangés
    print("Test 4 : Aucun point restant → VICTOIRE !")
    state.dots = {}
    state.power_dots = {}
    result = state.check_victory()
    assert result, "❌ ÉCHEC : Victoire NON détectée alors que tous les points sont mangés"
    print(f"   ✅ RÉUSSI : check_victory() = {result}")
    print()
    
    print("=" * 60)
    print("🎉 TOUS LES TESTS RÉUSSIS !")
    print("=" * 60)
    print()
    print("Le système de victoire fonctionne correctement :")
    print("  ✅ Vérifie que TOUS les dots sont mangés")
    print("  ✅ Vérifie que TOUS les power_dots sont mangés")
    print("  ✅ Déclenche la victoire uniquement si les deux sont vides")
    print()


if __name__ == "__main__":
    try:
        test_victory_detection()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DU TEST : {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

