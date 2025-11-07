"""Module de gestion du mode tournoi.

Ce module gère l'inscription des participants, le suivi de leurs performances
et le calcul des classements pour les différents prix.
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class PlayerAttempt:
    """Représente une tentative de jeu d'un joueur."""
    score: int
    level_reached: int
    time_level1: Optional[float]  # Temps pour finir le niveau 1 (None si pas fini)
    level1_completed: bool  # Si le joueur a complété le niveau 1


@dataclass
class TournamentPlayer:
    """Représente un joueur du tournoi."""
    name: str
    attempts: List[PlayerAttempt]
    current_attempt: int  # Index de la tentative en cours (0, 1, ou 2)
    
    def get_max_score(self) -> int:
        """Retourne le score maximum atteint."""
        if not self.attempts:
            return 0
        return max(attempt.score for attempt in self.attempts)
    
    def get_max_level(self) -> int:
        """Retourne le niveau maximum atteint."""
        if not self.attempts:
            return 0
        return max(attempt.level_reached for attempt in self.attempts)
    
    def get_best_level1_time(self) -> Optional[float]:
        """Retourne le meilleur temps pour le niveau 1."""
        times = [a.time_level1 for a in self.attempts if a.time_level1 is not None]
        if not times:
            return None
        return min(times)


class TournamentManager:
    """Gère le tournoi de Pac-Man."""
    
    SAVE_FILE = "game_data/tournament_data.json"
    
    def __init__(self):
        """Initialise le gestionnaire de tournoi."""
        self.players: List[TournamentPlayer] = []
        self.current_player_idx: int = 0
        self.is_active: bool = False
        self.tournament_started: bool = False
        self.load()
    
    def add_player(self, name: str) -> bool:
        """Ajoute un joueur au tournoi.
        
        Args:
            name: Nom du joueur
            
        Returns:
            True si ajouté avec succès, False si le nom existe déjà
        """
        # Vérifie si le nom existe déjà
        if any(p.name.lower() == name.lower() for p in self.players):
            return False
        
        player = TournamentPlayer(name=name, attempts=[], current_attempt=0)
        self.players.append(player)
        self.save()
        return True
    
    def remove_player(self, name: str) -> bool:
        """Retire un joueur du tournoi.
        
        Args:
            name: Nom du joueur à retirer
            
        Returns:
            True si retiré avec succès
        """
        initial_count = len(self.players)
        self.players = [p for p in self.players if p.name.lower() != name.lower()]
        if len(self.players) < initial_count:
            self.save()
            return True
        return False
    
    def start_tournament(self) -> bool:
        """Démarre le tournoi.
        
        Returns:
            True si démarré avec succès, False s'il n'y a pas assez de joueurs
        """
        if len(self.players) < 2:
            return False
        
        self.is_active = True
        self.tournament_started = True
        self.current_player_idx = 0
        self.save()
        return True
    
    def get_current_player(self) -> Optional[TournamentPlayer]:
        """Retourne le joueur en cours.
        
        Returns:
            Le joueur en cours ou None
        """
        if not self.is_active or not self.players:
            return None
        
        if 0 <= self.current_player_idx < len(self.players):
            return self.players[self.current_player_idx]
        
        return None
    
    def record_attempt(self, score: int, level: int, time_level1: Optional[float], level1_completed: bool):
        """Enregistre une tentative pour le joueur en cours.
        
        Args:
            score: Score atteint
            level: Niveau atteint
            time_level1: Temps pour finir le niveau 1 (None si pas fini)
            level1_completed: Si le niveau 1 a été complété
        """
        player = self.get_current_player()
        if not player:
            return
        
        attempt = PlayerAttempt(
            score=score,
            level_reached=level,
            time_level1=time_level1,
            level1_completed=level1_completed
        )
        player.attempts.append(attempt)
        player.current_attempt += 1
        
        self.save()
    
    def next_player_or_finish(self) -> Tuple[bool, bool]:
        """Passe au joueur suivant ou termine le tournoi.
        
        Returns:
            (has_next, tournament_finished)
            - has_next: True s'il y a un joueur suivant
            - tournament_finished: True si le tournoi est terminé
        """
        current = self.get_current_player()
        if not current:
            return False, True
        
        # Si le joueur actuel a encore des vies
        if current.current_attempt < 3:
            self.save()
            return True, False
        
        # Sinon, passe au joueur suivant
        self.current_player_idx += 1
        
        # Vérifie si on a terminé tous les joueurs
        if self.current_player_idx >= len(self.players):
            self.is_active = False
            self.save()
            return False, True
        
        self.save()
        return True, False
    
    def get_rankings(self) -> Dict[str, List[Tuple[str, any, int]]]:
        """Calcule les classements pour les 3 prix.
        
        Returns:
            Dictionnaire avec 3 classements:
            - 'max_score': Liste de (nom, score, total_points_tiebreak)
            - 'max_level': Liste de (nom, niveau, total_points_tiebreak)
            - 'fastest_level1': Liste de (nom, temps, total_points_tiebreak)
        """
        rankings = {
            'max_score': [],
            'max_level': [],
            'fastest_level1': []
        }
        
        for player in self.players:
            # Calcul du total de points pour départage
            total_points = sum(a.score for a in player.attempts)
            
            # Max score
            max_score = player.get_max_score()
            rankings['max_score'].append((player.name, max_score, total_points))
            
            # Max level
            max_level = player.get_max_level()
            rankings['max_level'].append((player.name, max_level, total_points))
            
            # Fastest level 1
            best_time = player.get_best_level1_time()
            if best_time is not None:
                rankings['fastest_level1'].append((player.name, best_time, total_points))
        
        # Tri des classements
        # Max score: décroissant par score, puis par total_points
        rankings['max_score'].sort(key=lambda x: (-x[1], -x[2]))
        
        # Max level: décroissant par niveau, puis par total_points
        rankings['max_level'].sort(key=lambda x: (-x[1], -x[2]))
        
        # Fastest level 1: croissant par temps, puis décroissant par total_points
        rankings['fastest_level1'].sort(key=lambda x: (x[1], -x[2]))
        
        return rankings
    
    def reset(self):
        """Réinitialise complètement le tournoi."""
        self.players = []
        self.current_player_idx = 0
        self.is_active = False
        self.tournament_started = False
        self.save()
    
    def save(self):
        """Sauvegarde les données du tournoi."""
        os.makedirs("game_data", exist_ok=True)
        
        data = {
            'players': [
                {
                    'name': p.name,
                    'attempts': [asdict(a) for a in p.attempts],
                    'current_attempt': p.current_attempt
                }
                for p in self.players
            ],
            'current_player_idx': self.current_player_idx,
            'is_active': self.is_active,
            'tournament_started': self.tournament_started
        }
        
        with open(self.SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load(self):
        """Charge les données du tournoi."""
        if not os.path.exists(self.SAVE_FILE):
            return
        
        try:
            with open(self.SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.players = [
                TournamentPlayer(
                    name=p['name'],
                    attempts=[PlayerAttempt(**a) for a in p['attempts']],
                    current_attempt=p['current_attempt']
                )
                for p in data.get('players', [])
            ]
            self.current_player_idx = data.get('current_player_idx', 0)
            self.is_active = data.get('is_active', False)
            self.tournament_started = data.get('tournament_started', False)
        except Exception as e:
            print(f"Erreur lors du chargement du tournoi: {e}")
            self.reset()


# Instance globale du gestionnaire de tournoi
tournament_manager = TournamentManager()

