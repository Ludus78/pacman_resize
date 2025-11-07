"""Module de gestion des records globaux du jeu.

Ce module gère les meilleurs scores/temps/niveaux de tous les temps.
"""
import json
import os
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Record:
    """Représente un record."""
    player_name: str
    value: float  # Score, niveau ou temps
    total_score: int  # Pour départage en cas d'égalité


class RecordsManager:
    """Gère les records globaux du jeu."""
    
    SAVE_FILE = "game_data/records.json"
    
    def __init__(self):
        """Initialise le gestionnaire de records."""
        self.best_score: Optional[Record] = None
        self.best_level: Optional[Record] = None
        self.best_time_level1: Optional[Record] = None
        self.load()
    
    def update_from_tournament(self, tournament_data: List[Tuple[str, any, int]]) -> Dict[str, bool]:
        """Met à jour les records à partir des données du tournoi.
        
        Args:
            tournament_data: Liste de (nom, valeur, total_score)
            
        Returns:
            Dict indiquant quels records ont été battus
        """
        updated = {
            'score': False,
            'level': False,
            'time': False
        }
        
        return updated
    
    def check_and_update_score(self, player_name: str, score: int, total_score: int) -> bool:
        """Vérifie et met à jour le record de score.
        
        Args:
            player_name: Nom du joueur
            score: Score atteint
            total_score: Score total pour départage
            
        Returns:
            True si record battu
        """
        if self.best_score is None:
            self.best_score = Record(player_name, float(score), total_score)
            self.save()
            return True
        
        # Compare score, puis total_score pour départage
        if score > self.best_score.value or (score == self.best_score.value and total_score > self.best_score.total_score):
            self.best_score = Record(player_name, float(score), total_score)
            self.save()
            return True
        
        return False
    
    def check_and_update_level(self, player_name: str, level: int, total_score: int) -> bool:
        """Vérifie et met à jour le record de niveau.
        
        Args:
            player_name: Nom du joueur
            level: Niveau atteint
            total_score: Score total pour départage
            
        Returns:
            True si record battu
        """
        if self.best_level is None:
            self.best_level = Record(player_name, float(level), total_score)
            self.save()
            return True
        
        # Compare niveau, puis total_score pour départage
        if level > self.best_level.value or (level == self.best_level.value and total_score > self.best_level.total_score):
            self.best_level = Record(player_name, float(level), total_score)
            self.save()
            return True
        
        return False
    
    def check_and_update_time(self, player_name: str, time: float, total_score: int) -> bool:
        """Vérifie et met à jour le record de temps niveau 1.
        
        Args:
            player_name: Nom du joueur
            time: Temps en secondes
            total_score: Score total pour départage
            
        Returns:
            True si record battu
        """
        if self.best_time_level1 is None:
            self.best_time_level1 = Record(player_name, time, total_score)
            self.save()
            return True
        
        # Compare temps (plus petit est mieux), puis total_score pour départage
        if time < self.best_time_level1.value or (time == self.best_time_level1.value and total_score > self.best_time_level1.total_score):
            self.best_time_level1 = Record(player_name, time, total_score)
            self.save()
            return True
        
        return False
    
    def get_all_records(self) -> Dict[str, Optional[Record]]:
        """Retourne tous les records.
        
        Returns:
            Dictionnaire avec les 3 records
        """
        return {
            'best_score': self.best_score,
            'best_level': self.best_level,
            'best_time_level1': self.best_time_level1
        }
    
    def reset(self):
        """Réinitialise tous les records."""
        self.best_score = None
        self.best_level = None
        self.best_time_level1 = None
        self.save()
    
    def save(self):
        """Sauvegarde les records."""
        os.makedirs("game_data", exist_ok=True)
        
        data = {
            'best_score': asdict(self.best_score) if self.best_score else None,
            'best_level': asdict(self.best_level) if self.best_level else None,
            'best_time_level1': asdict(self.best_time_level1) if self.best_time_level1 else None
        }
        
        with open(self.SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load(self):
        """Charge les records."""
        if not os.path.exists(self.SAVE_FILE):
            return
        
        try:
            with open(self.SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.best_score = Record(**data['best_score']) if data.get('best_score') else None
            self.best_level = Record(**data['best_level']) if data.get('best_level') else None
            self.best_time_level1 = Record(**data['best_time_level1']) if data.get('best_time_level1') else None
        except Exception as e:
            print(f"Erreur lors du chargement des records: {e}")
            self.reset()


# Instance globale du gestionnaire de records
records_manager = RecordsManager()

