from dataclasses import dataclass
from ortools.sat.python import cp_model
from itertools import combinations
import math
import json
import sys
@dataclass
class TournamentConfig:
    # Paramètres de base
    num_players: int = 10
    num_courts: int = 2
    num_rounds: int = 8
    num_teams_per_court: int = 2
    players_per_team: int = 2
    saved_json: str = "planning.json"

    # === DRAPEAUX POUR TESTER FACILEMENT (ON/OFF) ===
    # Contraintes d'équilibre (Hard)
    use_strict_bye_spacing: bool = True
    use_games_fairness: bool = True
    use_court_fairness: bool = True
    use_partner_fairness: bool = True

    use_add_quadratic_progressive_penalty: bool = False
    use_zero_opponent_penalty: bool = False
    use_repetition_penalty: bool = False
    use_add_progressive_repeat_penalty: bool = False
    use_add_quadratic_progressive_penalty: bool = False
    use_add_opponent_encounters_bounds_constraint: bool = False
    use_opponent_encounters_bounds_constraint: bool = False

    weight_zero_opponent_penalty = 100
    weight_repetition_penalty = 100
    weight_progressive_repeat_penalty = 10000
    weight_quadratic_progressive_penalty = 1000
    weight_excessive_opponent = 100000

    
    


    @property
    def all_players(self): return range(self.num_players)
    @property
    def all_rounds(self): return range(self.num_rounds)
    @property
    def all_courts(self): return range(self.num_courts)
    @property
    def all_teams(self): return range(self.num_teams_per_court)
    @property
    def active_players_per_round(self): return self.num_courts * self.num_teams_per_court * self.players_per_team
    @property
    def num_byes_per_round(self): return self.num_players - self.active_players_per_round
    @property
    def total_players(self): return self.num_players
    @property
    def players_on_court(self): return self.active_players_per_round
    @property
    def total_byes_allowed(self): return self.num_byes_per_round * self.num_rounds

