from dataclasses import dataclass
from ortools.sat.python import cp_model
from itertools import combinations
import math
import json
import sys
from TournamentConfig import TournamentConfig
@dataclass

class TournamentScheduler:
    def __init__(self, config: TournamentConfig, time_limit_seconds=15):
        self.config = config
        self.model = cp_model.CpModel()
        
        # Dictionnaires pour les variables
        self.is_bye = {}
        self.is_assigned = {}
        
        # Liste pour stocker les termes de pénalité (Fonction de coût)
        self.objective_terms = []
        self.time_limit_seconds = time_limit_seconds

    def _bool_and(self, var_a, var_b, name):
        """Fonction utilitaire pour créer un ET logique entre deux booléens."""
        prod = self.model.NewBoolVar(name)
        self.model.Add(prod <= var_a)
        self.model.Add(prod <= var_b)
        self.model.Add(prod >= var_a + var_b - 1)
        return prod

    # =========================================================================
    # VARIABLES CREATION
    # =========================================================================
    def _create_variables(self):
        for r in self.config.all_rounds:
            for p in self.config.all_players:
                self.is_bye[r, p] = self.model.NewBoolVar(f"bye_r{r}_p{p}")
                for c in self.config.all_courts:
                    for t in self.config.all_teams:
                        self.is_assigned[r, p, c, t] = self.model.NewBoolVar(f"assign_r{r}_p{p}_c{c}_t{t}")

    # =========================================================================
    # 1. CONTRAINTES STRUCTURELLES
    # =========================================================================
    def _add_structural_constraints(self):
        for r in self.config.all_rounds:
            for p in self.config.all_players:
                self.model.Add(
                    self.is_bye[r, p] + 
                    sum(self.is_assigned[r, p, c, t] for c in self.config.all_courts for t in self.config.all_teams) 
                    == 1
                )
                
            self.model.Add(
                sum(self.is_bye[r, p] for p in self.config.all_players) == self.config.num_byes_per_round
            )
            
            for c in self.config.all_courts:
                for t in self.config.all_teams:
                    self.model.Add(
                        sum(self.is_assigned[r, p, c, t] for p in self.config.all_players) 
                        == self.config.players_per_team
                    )

    # =========================================================================
    # 2. CONTRAINTES D'ÉQUILIBRE (HARD CONSTRAINTS)
    # =========================================================================
    def _add_strict_bye_spacing(self):
        if self.config.num_byes_per_round == 0: return

        ratio = self.config.active_players_per_round / self.config.num_byes_per_round
        min_games_between = math.floor(ratio)
        max_games_between = math.ceil(ratio)
        
        min_distance = min_games_between + 1
        max_distance = max_games_between + 1

        for p in self.config.all_players:
            for r1 in self.config.all_rounds:
                for r2 in range(r1 + 1, self.config.num_rounds):
                    actual_distance = r2 - r1
                    if actual_distance < min_distance or actual_distance > max_distance:
                        self.model.Add(self.is_bye[r1, p] + self.is_bye[r2, p] <= 1)

    def _add_games_fairness(self):
        games_played = {}
        for p in self.config.all_players:
            games_played[p] = self.model.NewIntVar(0, self.config.num_rounds, f"games_{p}")
            self.model.Add(games_played[p] == sum(1 - self.is_bye[r, p] for r in self.config.all_rounds))

        min_games = self.model.NewIntVar(0, self.config.num_rounds, "min_games")
        max_games = self.model.NewIntVar(0, self.config.num_rounds, "max_games")
        self.model.AddMinEquality(min_games, list(games_played.values()))
        self.model.AddMaxEquality(max_games, list(games_played.values()))
        self.model.Add(max_games - min_games <= 1)

    def _add_court_fairness(self):
        for p in self.config.all_players:
            c1_count = sum(self.is_assigned[r, p, 0, t] for r in self.config.all_rounds for t in self.config.all_teams)
            c2_count = sum(self.is_assigned[r, p, 1, t] for r in self.config.all_rounds for t in self.config.all_teams)
            
            diff = self.model.NewIntVar(0, self.config.num_rounds, f"diff_courts_p{p}")
            self.model.Add(diff >= c1_count - c2_count)
            self.model.Add(diff >= c2_count - c1_count)
            self.model.Add(diff <= 1)

    def _add_partner_fairness(self):
        avg_games = (self.config.active_players_per_round * self.config.num_rounds) / self.config.num_players
        max_games = math.ceil(avg_games)
        available_partners = self.config.num_players - 1
        max_partner_freq = math.ceil(max_games / available_partners)

        for p_a, p_b in combinations(self.config.all_players, 2):
            partner_events = []
            for r in self.config.all_rounds:
                for c in self.config.all_courts:
                    for t in self.config.all_teams:
                        prod_p = self._bool_and(
                            self.is_assigned[r, p_a, c, t],
                            self.is_assigned[r, p_b, c, t],
                            f"part_{p_a}_{p_b}_r{r}_c{c}_t{t}"
                        )
                        partner_events.append(prod_p)
            self.model.Add(sum(partner_events) <= max_partner_freq)

    def _add_zero_opponent_penalty(self):
        """Pénalise le modèle chaque fois que deux joueurs ne s'affrontent jamais."""
        # On peut définir un poids si on veut donner plus d'importance à cette pénalité
        weight_zero_opponent_penalty = self.config.weight_zero_opponent_penalty

        for p_a, p_b in combinations(self.config.all_players, 2):
            opp_events = []
            
            for r in self.config.all_rounds:
                for c in self.config.all_courts:
                    # Cas 1: p_a dans équipe 0, p_b dans équipe 1
                    pa_0_pb_1 = self._bool_and(
                        self.is_assigned[r, p_a, c, 0],
                        self.is_assigned[r, p_b, c, 1],
                        f"opp_{p_a}_{p_b}_r{r}_c{c}_01"
                    )
                    # Cas 2: p_a dans équipe 1, p_b dans équipe 0
                    pa_1_pb_0 = self._bool_and(
                        self.is_assigned[r, p_a, c, 1],
                        self.is_assigned[r, p_b, c, 0],
                        f"opp_{p_a}_{p_b}_r{r}_c{c}_10"
                    )
                    opp_events.extend([pa_0_pb_1, pa_1_pb_0])
            
            # # Somme du nombre de fois où la paire s'affronte
            # sum_encounters = sum(opp_events)
            
            # # Variable binaire qui vaut 1 si le nombre d'affrontements est 0
            # is_zero_encounters = self.model.NewBoolVar(f"zero_opp_{p_a}_{p_b}")
            
            # # Lier is_zero_encounters à la somme des affrontements avec OnlyEnforceIf
            # # Si is_zero_encounters == 1, alors la somme DOIT être 0
            # self.model.Add(sum_encounters == 0).OnlyEnforceIf(is_zero_encounters)
            # # Si is_zero_encounters == 0, alors ils s'affrontent au moins 1 fois
            # self.model.Add(sum_encounters >= 1).OnlyEnforceIf(is_zero_encounters.Not())
            
            # # Ajouter la pénalité à la fonction objectif
            # self.objective_terms.append(is_zero_encounters * weight_zero_opponent_penalty)

            # Contrainte stricte : au moins 1 affrontement garanti
            self.model.Add(sum(opp_events) >= 1)

    def _add_use_repetition_penalty(self):
        weight_repetition_penalty = self.config.weight_repetition_penalty

        """Pénalise fortement les répétitions de rencontres, avec un coût plus élevé au début."""
        for p_a, p_b in combinations(self.config.all_players, 2):
            meet_vars = []
            
            for r in self.config.all_rounds:
                meet_r = self.model.NewBoolVar(f"meet_{p_a}_{p_b}_r{r}")
                same_court_vars = []
                for c in self.config.all_courts:
                    p_a_on_c = self.model.NewBoolVar(f"pa_{p_a}_c{c}_r{r}")
                    self.model.Add(p_a_on_c == sum(self.is_assigned[r, p_a, c, t] for t in self.config.all_teams))
                    
                    p_b_on_c = self.model.NewBoolVar(f"pb_{p_b}_c{c}_r{r}")
                    self.model.Add(p_b_on_c == sum(self.is_assigned[r, p_b, c, t] for t in self.config.all_teams))
                    
                    both_on_c = self._bool_and(p_a_on_c, p_b_on_c, f"both_{p_a}_{p_b}_c{c}_r{r}")
                    same_court_vars.append(both_on_c)
                
                self.model.Add(meet_r == sum(same_court_vars))
                meet_vars.append(meet_r)
            
            for r1 in range(self.config.num_rounds):
                for r2 in range(r1 + 1, self.config.num_rounds):
                    repeat = self._bool_and(meet_vars[r1], meet_vars[r2], f"repeat_{p_a}_{p_b}_r{r1}_r{r2}")
                    
                    # Plus r2 est proche du début, plus le multiplicateur est élevé
                    urgency_multiplier = self.config.num_rounds - r2
                    penalty = weight_repetition_penalty * urgency_multiplier
                    
                    self.objective_terms.append(repeat * penalty)

    def _add_progressive_repeat_penalty(self):
        """Pénalise les répétitions de rencontres sociales (même terrain).
        La pénalité est fortement majorée si la re-rencontre a lieu dans les premiers tours.
        """
        weight_progressive_repeat_penalty = self.config.weight_progressive_repeat_penalty
        num_rounds = self.config.num_rounds

        for p_a, p_b in combinations(self.config.all_players, 2):
            meet_vars = []

            # 1. Variable booléenne de rencontre à chaque round
            for r in self.config.all_rounds:
                same_court_vars = []
                for c in self.config.all_courts:
                    p_a_on_c = sum(
                        self.is_assigned[r, p_a, c, t] for t in self.config.all_teams
                    )
                    p_b_on_c = sum(
                        self.is_assigned[r, p_b, c, t] for t in self.config.all_teams
                    )
                    both_on_c = self._bool_and(
                        p_a_on_c, p_b_on_c, f"both_{p_a}_{p_b}_r{r}_c{c}"
                    )
                    same_court_vars.append(both_on_c)

                meet_r = self.model.NewBoolVar(f"meet_{p_a}_{p_b}_r{r}")
                self.model.Add(meet_r == sum(same_court_vars))
                meet_vars.append(meet_r)

            # 2. Détection et pénalisation progressive des paires de répétition (r1 < r2)
            for r1 in range(num_rounds):
                for r2 in range(r1 + 1, num_rounds):
                    repeat = self._bool_and(
                        meet_vars[r1],
                        meet_vars[r2],
                        f"repeat_{p_a}_{p_b}_r{r1}_r{r2}",
                    )

                    # Multiplicateur décroissant avec le numéro du tour (r2)
                    # Plus la répétition a lieu tôt (ex: tour 1 vs tour 7), plus le multiplicateur est fort
                    urgency_multiplier = num_rounds - r2
                    penalty = weight_progressive_repeat_penalty * urgency_multiplier

                    self.objective_terms.append(repeat * penalty)

    def _add_quadratic_progressive_penalty(self):
        """Pénalise quadratiquement les répétitions survenues dans les premiers tours."""
        weight_quadratic_progressive_penalty = self.config.weight_quadratic_progressive_penalty
        num_rounds = self.config.num_rounds

        for p_a, p_b in combinations(self.config.all_players, 2):
            meet_vars = []

            for r in self.config.all_rounds:
                same_court_vars = []
                for c in self.config.all_courts:
                    p_a_on_c = sum(self.is_assigned[r, p_a, c, t] for t in self.config.all_teams)
                    p_b_on_c = sum(self.is_assigned[r, p_b, c, t] for t in self.config.all_teams)
                    both_on_c = self._bool_and(p_a_on_c, p_b_on_c, f"both_{p_a}_{p_b}_r{r}_c{c}")
                    same_court_vars.append(both_on_c)

                meet_r = self.model.NewBoolVar(f"meet_{p_a}_{p_b}_r{r}")
                self.model.Add(meet_r == sum(same_court_vars))
                meet_vars.append(meet_r)

            for r1 in range(num_rounds):
                for r2 in range(r1 + 1, num_rounds):
                    repeat = self._bool_and(meet_vars[r1], meet_vars[r2], f"repeat_{p_a}_{p_b}_r{r1}_r{r2}")

                    # Progression quadratique : l'urgence au début du tournoi est décuplée
                    urgency_multiplier = (num_rounds - r2) ** 2
                    penalty = weight_quadratic_progressive_penalty * urgency_multiplier

                    self.objective_terms.append(repeat * penalty)

    def _add_opponent_encounters_bounds_constraint(self):
        """Contrainte stricte optimisée : chaque paire d'adversaires s'affronte 1 ou 2 fois.
        Utilise AddMultiplicationEquality nativement pour accélérer le presolve.
        """
        for p_a, p_b in combinations(self.config.all_players, 2):
            opp_events = []

            for r in self.config.all_rounds:
                for c in self.config.all_courts:
                    # p_a équipe 0 ET p_b équipe 1
                    pa0_pb1 = self.model.NewBoolVar(f"opp01_{p_a}_{p_b}_r{r}_c{c}")
                    self.model.AddMultiplicationEquality(
                        pa0_pb1,
                        [
                            self.is_assigned[r, p_a, c, 0],
                            self.is_assigned[r, p_b, c, 1],
                        ],
                    )

                    # p_a équipe 1 ET p_b équipe 0
                    pa1_pb0 = self.model.NewBoolVar(f"opp10_{p_a}_{p_b}_r{r}_c{c}")
                    self.model.AddMultiplicationEquality(
                        pa1_pb0,
                        [
                            self.is_assigned[r, p_a, c, 1],
                            self.is_assigned[r, p_b, c, 0],
                        ],
                    )

                    opp_events.extend([pa0_pb1, pa1_pb0])

            # Borne stricte : 1 ou 2 affrontements sur tout le tournoi
            total_encounters = sum(opp_events)
            self.model.Add(total_encounters >= 1)
            self.model.Add(total_encounters <= 3)

    def _add_opponent_triple_penalty(self):
        """Pénalise fortement chaque paire d'ADVERSAIRES qui s'affronte 3 fois (ou plus)."""
        weight_opponent_3 = 1000

        for p_a, p_b in combinations(self.config.all_players, 2):
            opp_events = []

            for r in self.config.all_rounds:
                for c in self.config.all_courts:
                    # p_a dans l'équipe 0 ET p_b dans l'équipe 1
                    pa0_pb1 = self.model.NewBoolVar(
                        f"opp01_{p_a}_{p_b}_r{r}_c{c}"
                    )
                    self.model.AddMultiplicationEquality(
                        pa0_pb1,
                        [
                            self.is_assigned[r, p_a, c, 0],
                            self.is_assigned[r, p_b, c, 1],
                        ],
                    )

                    # p_a dans l'équipe 1 ET p_b dans l'équipe 0
                    pa1_pb0 = self.model.NewBoolVar(
                        f"opp10_{p_a}_{p_b}_r{r}_c{c}"
                    )
                    self.model.AddMultiplicationEquality(
                        pa1_pb0,
                        [
                            self.is_assigned[r, p_a, c, 1],
                            self.is_assigned[r, p_b, c, 0],
                        ],
                    )

                    opp_events.extend([pa0_pb1, pa1_pb0])

            total_encounters = sum(opp_events)

            # Actif uniquement si la paire s'affronte 3 fois ou plus
            is_opponent_3 = self.model.NewBoolVar(f"opp_3_{p_a}_{p_b}")
            self.model.Add(total_encounters >= 3).OnlyEnforceIf(is_opponent_3)
            self.model.Add(total_encounters < 3).OnlyEnforceIf(is_opponent_3.Not())

            self.objective_terms.append(is_opponent_3 * weight_opponent_3)
    # =========================================================================
    # ORCHESTRATION ET RÉSOLUTION
    # =========================================================================
    def build_model(self):
        self._create_variables()
        self._add_structural_constraints()
        
        # Hard constraints
        if self.config.use_games_fairness: self._add_games_fairness()
        if self.config.use_court_fairness: self._add_court_fairness()
        if self.config.use_strict_bye_spacing: self._add_strict_bye_spacing()
        if self.config.use_partner_fairness: self._add_partner_fairness()
        # Soft constraints (Pénalités)
        # if self.config.use_opponent_encounters_bounds_constraint: 
        #     self._add_opponent_encounters_bounds_constraint()
        #     self._add_opponent_triple_penalty()

        # self._add_zero_opponent_penalty()  # <--- AJOUT ICI
        # if self.config.use_repetition_penalty: self._add_use_repetition_penalty()  # <--- AJOUT ICI
        # if self.config.use_add_progressive_repeat_penalty: self._add_progressive_repeat_penalty
        # if self.config.use_add_quadratic_progressive_penalty: self._add_quadratic_progressive_penalty






        # Soft constraints (Pénalités)

        
        if self.objective_terms:
            self.model.Minimize(sum(self.objective_terms))

    def solve(self):
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = self.time_limit_seconds
            
            status = solver.Solve(self.model)
            
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                print(f"\n✅ Solution trouvée ! (Statut : {solver.StatusName(status)})")
                
                if self.objective_terms:
                    print(f"Score de pénalité total (plus bas = mieux) : {solver.ObjectiveValue()}")
                    
                # Appels uniques aux méthodes d'affichage et d'export
                self.display_solution(solver)
                self.print_encounter_matrix(solver)
                self.export_json(solver)
                
            else:
                print(f"\n❌ Aucune solution trouvée en moins de {self.time_limit_seconds}s.")
                
            return solver, status

    def display_solution(self, solver):
        """Affiche le tournoi et le tableau des statistiques de diversité."""
        print("-" * 50)
        for r in self.config.all_rounds:
            print(f"--- TOUR {r + 1} ---")
            
            for c in self.config.all_courts:
                teams = [[], []]
                for t in self.config.all_teams:
                    for p in self.config.all_players:
                        if solver.Value(self.is_assigned[r, p, c, t]):
                            teams[t].append(f"J{p}")
                
                print(f"  Terrain {c + 1} : {teams[0][0]} & {teams[0][1]}  CONTRE  {teams[1][0]} & {teams[1][1]}")
            
            byes = [f"J{p}" for p in self.config.all_players if solver.Value(self.is_bye[r, p])]
            print(f"  Repos     : {', '.join(byes)}\n")
        print("-" * 50)

        # Tableau des statistiques
        print("\n" + "="*85)
        print(" SUIVI JOUEUR : Diversité cumulée (et Terrain assigné) ".center(85, "="))
        print("="*85 + "\n")
        print("Légende : Chiffre = Nb total de joueurs différents croisés | R = Repos | C1, C2 = Terrains\n")

        header_div = f"| {'Tour':^6} |"
        for p in self.config.all_players:
            header_div += f" P{p:<5} |"
        print(header_div)
        print("-" * len(header_div))

        players_met_so_far = {p: set() for p in self.config.all_players}

        for round_idx in self.config.all_rounds:
            player_court_this_round = {}
            for court in self.config.all_courts:
                team0 = [p for p in self.config.all_players if solver.Value(self.is_assigned[round_idx, p, court, 0]) == 1]
                team1 = [p for p in self.config.all_players if solver.Value(self.is_assigned[round_idx, p, court, 1]) == 1]
                all_on_court = team0 + team1
                
                for p in all_on_court:
                    player_court_this_round[p] = f"C{court+1}"
                    mates = [other for other in all_on_court if other != p]
                    players_met_so_far[p].update(mates)

            for p in self.config.all_players:
                if p not in player_court_this_round:
                    player_court_this_round[p] = "R"

            row_str = f"| {round_idx + 1:^6} |"
            for p in self.config.all_players:
                count = len(players_met_so_far[p])
                pos = player_court_this_round[p]
                cell_content = f"{count}({pos})"
                row_str += f" {cell_content:<5} |"
            print(row_str)

        print("-" * len(header_div))

    def print_encounter_matrix(self, solver):
            """Affiche une matrice des rencontres (qui a rencontré qui et combien de fois)."""
            num_p = self.config.num_players
            
            # 1. Initialiser une matrice de zéros (10x10)
            matrix = [[0 for _ in range(num_p)] for _ in range(num_p)]
            
            # 2. Parcourir tous les tours et terrains pour compter les rencontres
            for r in self.config.all_rounds:
                for c in self.config.all_courts:
                    # Récupérer les joueurs sur ce terrain à ce tour
                    court_players = []
                    for t in self.config.all_teams:
                        for p in self.config.all_players:
                            if solver.Value(self.is_assigned[r, p, c, t]):
                                court_players.append(p)
                    
                    # Tous ceux qui sont sur ce même terrain se rencontrent
                    for i in range(len(court_players)):
                        for j in range(i + 1, len(court_players)):
                            p1 = court_players[i]
                            p2 = court_players[j]
                            matrix[p1][p2] += 1
                            matrix[p2][p1] += 1

            # 3. Affichage de la matrice
            print("\n" + "="*70)
            print(" MATRICE DE FRÉQUENCE DES RENCONTRES (Qui rencontre qui ?) ".center(70, "="))
            print("="*70 + "\n")
            
            # En-tête des colonnes
            header = "      " + " ".join([f"P{i:<3}" for i in self.config.all_players])
            print(header)
            print("    " + "-" * (len(header) - 4))
            
            # Lignes
            for i in self.config.all_players:
                row_str = f"P{i:<2} | "
                for j in self.config.all_players:
                    if i == j:
                        row_str += " -  "  # Un joueur ne se rencontre pas lui-même
                    else:
                        row_str += f" {matrix[i][j]:<3} "
                print(row_str)
            print("-" * (len(header) - 4))
            

    def export_json(self, solver):
                tournament_data = {
                    "num_rounds": self.config.num_rounds,
                    "num_courts": self.config.num_courts,
                    "num_players": self.config.num_players,
                    "rounds": []
                }

                for round_idx in self.config.all_rounds:
                    round_info = {"round_number": round_idx + 1, "courts": [], "byes": []}
                    
                    for court in self.config.all_courts:
                        team0 = []
                        team1 = []
                        for player in self.config.all_players:
                            # Utilisation correcte de self.is_assigned
                            if solver.Value(self.is_assigned[round_idx, player, court, 0]) == 1:
                                team0.append(int(player))
                            if solver.Value(self.is_assigned[round_idx, player, court, 1]) == 1:
                                team1.append(int(player))
                                
                        round_info["courts"].append({
                            "court_number": court + 1, 
                            "team_1": team0, 
                            "team_2": team1
                        })
                        
                    byes = [int(player) for player in self.config.all_players if solver.Value(self.is_bye[round_idx, player]) == 1]
                    round_info["byes"] = byes
                    tournament_data["rounds"].append(round_info)

                # Écriture propre du fichier JSON
                with open(self.config.saved_json, "w", encoding="utf-8") as f:
                    json.dump(tournament_data, f, ensure_ascii=False, indent=4)
                    
                print(f"✅ [Succès] Le planning a bien été sauvegardé dans {self.config.saved_json}.")

