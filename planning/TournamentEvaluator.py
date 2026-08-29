from dataclasses import dataclass
from ortools.sat.python import cp_model
from itertools import combinations
import math
import json
import sys
from TournamentConfig import TournamentConfig

@dataclass


class TournamentEvaluator:

    def __init__(self, schedule_dict, name="Planning"):
        self.schedule_data = schedule_dict.get('rounds', [])
        self.num_players = schedule_dict.get('num_players', 0)

        self.all_players = list(range(self.num_players))
        self.num_rounds = schedule_dict.get('num_rounds', 0)

        self.name = name

    def evaluate_schedule(self):
        schedule_stats = self.compute_stats()
        def get_first_last(stats_dict):
            """Returns the first and last (key, value) pairs from a dictionary."""
            items = list(stats_dict.items())
            return items[0], items[-1]

        # Unpack directly into your variables
        (partner_pairs_min, partner_pairs_min_count), (partner_pairs_max, partner_pairs_max_count) = get_first_last(schedule_stats['partner_pairs_stats'])
        (opponent_pairs_min, opponent_pairs_min_count), (opponent_pairs_max, opponent_pairs_max_count) = get_first_last(schedule_stats['opponent_pairs_stats'])
        (social_pairs_min, social_pairs_min_count), (social_pairs_max, social_pairs_max_count) = get_first_last(schedule_stats['social_pairs_stats'])






        print(
            f"\n================ RAPPORT D'ÉVALUATION : {self.name} ({len(self.schedule_data)} rounds) ================"
        )
        print(
            f"🔹 Total repos par joueur (Min-Max)   : {schedule_stats['min_byes']} à {schedule_stats['max_byes']} repos"
            f" {'✅' if schedule_stats['min_byes'] == schedule_stats['max_byes'] else '⚠️'}"
        )
        print(
            f"🔹 Parties jouées entre 2 repos       : Min = {schedule_stats['min_games_between']} | Max = {schedule_stats['max_games_between']} parties"
        )
        print(
            f"🔹 Partenaires (Même équipe)          : Min = {partner_pairs_min} | Max = { partner_pairs_max} fois (1 seule fois: {schedule_stats['partner_pairs_stats'][1]} paires)"
            )
        print(
            f"🔹 Adversaires (Équipe adverse)       : Min = {opponent_pairs_min} | Max = {opponent_pairs_max} fois (0 fois: {schedule_stats['opponent_pairs_stats'][0]} paires)"
        )
        print(
            f"🔹 Rencontres totales (Sur terrain)   : Min = {social_pairs_min} | Max = {social_pairs_max} fois 0 fois: {schedule_stats['social_pairs_stats'][0]} paires)"
        )
        print(f"   👉 Paires croisées 1 SEULE FOIS    : {schedule_stats['social_pairs_stats'][1]}  paires")
        print(f"   👉 Paires jamais croisées (0)     : {schedule_stats['social_pairs_stats'][0]} paires")
        print(f"🔹 Alternance des terrains            :")
        print(
            f"   👉 Taux d'alternance              : {schedule_stats['alternation_rate']:.1f}% ({schedule_stats['court_switches']}/{schedule_stats['total_transitions']} changements)"
        )
        print(f"   👉 Répétitions consécutives       : {schedule_stats['same_court_consecutive']} fois")
        print(
            f"   👉 Série max sur un même terrain  : {schedule_stats['max_same_court_streak']} matchs d'affilée"
        )
        print(f"🔹 Min. de joueurs croisés par tour   :")
        print(f"   👉 {schedule_stats['rounds_div_str']}")
        print("================================================================")

        




    def display_solution(self):
        
        """Affiche le tournoi et le tableau des statistiques de diversité depuis des données de planning."""
        print("\n" + "="*85)
        print(f" DÉROULEMENT DU TOURNOI : {self.name} ".center(85, "="))
        print("="*85 + "\n")
        
        for r_info in self.schedule_data:
            r = r_info["round_number"]
            print(f"--- TOUR {r} ---")
            
            for court in r_info["courts"]:
                c_num = court["court_number"]
                t1 = [f"J{p}" for p in court["team_1"]]
                t2 = [f"J{p}" for p in court["team_2"]]
                print(f"  Terrain {c_num} : {t1[0]} & {t1[1]}  CONTRE  {t2[0]} & {t2[1]}")
            
            byes = [f"J{p}" for p in r_info["byes"]]
            print(f"  Repos     : {', '.join(byes)}\n")
        print("-" * 50)

    def display_solution_diversity(self):
        
        # Tableau des statistiques
        print("\n" + "="*85)
        print(f" SUIVI JOUEUR ({self.name}) : Diversité cumulée (et Terrain assigné) ".center(85, "="))
        print("="*85 + "\n")
        print("Légende : Chiffre = Nb total de joueurs différents croisés | R = Repos | C1, C2 = Terrains\n")

        header_div = f"| {'Tour':^6} |"
        for p in self.all_players:
            header_div += f" P{p:<5} |"
        print(header_div)
        print("-" * len(header_div))

        players_met_so_far = {p: set() for p in self.all_players}

        for r_info in self.schedule_data:
            round_idx = r_info["round_number"]
            player_court_this_round = {}
            
            for court in r_info["courts"]:
                c_num = court["court_number"]
                team0 = court["team_1"]
                team1 = court["team_2"]
                all_on_court = team0 + team1
                
                for p in all_on_court:
                    player_court_this_round[p] = f"C{c_num}"
                    mates = [other for other in all_on_court if other != p]
                    players_met_so_far[p].update(mates)

            for p in self.all_players:
                if p not in player_court_this_round:
                    player_court_this_round[p] = "R"

            row_str = f"| {round_idx:^6} |"
            for p in self.all_players:
                count = len(players_met_so_far[p])
                pos = player_court_this_round[p]
                cell_content = f"{count}({pos})"
                row_str += f" {cell_content:<5} |"
            print(row_str)

        print("-" * len(header_div))

    def print_encounter_matrix(self):
        """Affiche la matrice des rencontres depuis des données de planning."""
        num_p = self.num_players
        matrix = [[0 for _ in range(num_p)] for _ in range(num_p)]
        
        for r_info in self.schedule_data:
            for court in r_info["courts"]:
                court_players = court["team_1"] + court["team_2"]
                for i in range(len(court_players)):
                    for j in range(i + 1, len(court_players)):
                        p1 = court_players[i]
                        p2 = court_players[j]
                        matrix[p1][p2] += 1
                        matrix[p2][p1] += 1

        print("\n" + "="*70)
        print(f" MATRICE DE FRÉQUENCE DES RENCONTRES : {self.name} ".center(70, "="))
        print("="*70 + "\n")
        
        header = "      " + " ".join([f"P{i:<3}" for i in self.all_players])
        print(header)
        print("    " + "-" * (len(header) - 4))
        
        for i in self.all_players:
            row_str = f"P{i:<2} | "
            for j in self.all_players:
                if i == j:
                    row_str += " -  "
                else:
                    row_str += f" {matrix[i][j]:<3} "
            print(row_str)
        print("-" * (len(header) - 4))
        
        all_vals = [matrix[i][j] for i in range(num_p) for j in range(num_p) if i != j]
        if all_vals:
            min_m, max_m, avg_m = min(all_vals), max(all_vals), sum(all_vals) / len(all_vals)
            print(f"📊 Statistiques des rencontres : Min = {min_m} fois | Max = {max_m} fois | Moyenne = {avg_m:.2f} fois par pair.")
        print("="*70 + "\n")

    def compute_stats(self):
        schedule_data = self.schedule_data[: self.num_rounds]

        partner_counts = {
            (p1, p2): 0
            for p1 in self.all_players
            for p2 in self.all_players
            if p1 < p2
        }
        opponent_counts = {
            (p1, p2): 0
            for p1 in self.all_players
            for p2 in self.all_players
            if p1 < p2
        }
        total_encounters = {
            (p1, p2): 0
            for p1 in self.all_players
            for p2 in self.all_players
            if p1 < p2
        }

        player_games = {p: 0 for p in self.all_players}
        player_byes = {p: 0 for p in self.all_players}
        bye_rounds = {p: [] for p in self.all_players}
        court_history = {p: [] for p in self.all_players}

        players_met_so_far = {p: set() for p in self.all_players}
        min_unique_met_per_round = []

        for r_idx, round_info in enumerate(schedule_data):
            round_num = r_idx + 1
            byes = round_info["byes"]

            for p in self.all_players:
                if p in byes:
                    player_byes[p] += 1
                    bye_rounds[p].append(round_num)
                    court_history[p].append(None)
                else:
                    player_games[p] += 1

            for court in round_info["courts"]:
                c_num = court["court_number"]
                team1 = court["team_1"]
                team2 = court["team_2"]
                all_on_court = team1 + team2

                for p in all_on_court:
                    court_history[p].append(c_num)
                    mates = [other for other in all_on_court if other != p]
                    players_met_so_far[p].update(mates)

                if len(team1) == 2:
                    p1, p2 = sorted(team1)
                    partner_counts[(p1, p2)] += 1

                if len(team2) == 2:
                    p1, p2 = sorted(team2)
                    partner_counts[(p1, p2)] += 1

                for t1 in team1:
                    for t2 in team2:
                        p1, p2 = sorted([t1, t2])
                        opponent_counts[(p1, p2)] += 1

            min_met_this_round = min(
                len(players_met_so_far[p]) for p in self.all_players
            )
            min_unique_met_per_round.append(min_met_this_round)

        for pair in total_encounters:
            total_encounters[pair] = (
                partner_counts[pair] + opponent_counts[pair]
            )

        # Calcul des espaces entre repos
        games_between_byes = []
        for p, r_list in bye_rounds.items():
            if len(r_list) > 1:
                for i in range(len(r_list) - 1):
                    games_count = r_list[i + 1] - r_list[i] - 1
                    games_between_byes.append(games_count)

        min_games_between = (
            min(games_between_byes) if games_between_byes else "N/A"
        )
        max_games_between = (
            max(games_between_byes) if games_between_byes else "N/A"
        )

        # --- MESURE DE L'ALTERNANCE DES TERRAINS ---
        total_transitions = 0
        court_switches = 0
        same_court_consecutive = 0
        max_same_court_streak = 1

        for p, history in court_history.items():
            # Filtre uniquement les matchs réellement joués (exclut les repos)
            active_courts = [c for c in history if c is not None]

            current_streak = 1
            for i in range(len(active_courts) - 1):
                total_transitions += 1
                if active_courts[i] != active_courts[i + 1]:
                    court_switches += 1
                    current_streak = 1
                else:
                    same_court_consecutive += 1
                    current_streak += 1
                    if current_streak > max_same_court_streak:
                        max_same_court_streak = current_streak

        alternation_rate = (
            (court_switches / total_transitions * 100)
            if total_transitions > 0
            else 0
        )

        min_byes, max_byes = min(player_byes.values()), max(
            player_byes.values()
        )
        p_vals = list(partner_counts.values())
        o_vals = list(opponent_counts.values())
        t_vals = list(total_encounters.values())

        ones_total = t_vals.count(1)
        zeros_total = t_vals.count(0)

        rounds_div_str = " | ".join(
            [f"T{i+1}: {v}" for i, v in enumerate(min_unique_met_per_round)]
        )



        social_pairs_stats = {p: 0 for p in range(max(t_vals) + 1)}
        partner_pairs_stats = {p: 0 for p in range(max(p_vals) + 1)}
        opponent_pairs_stats = {p: 0 for p in range(max(o_vals) + 1)}


        for i in range(max(t_vals)+ 1):
            social_pairs_stats[i] = t_vals.count(i)
        for i in range(max(p_vals)+ 1):
            partner_pairs_stats[i] = p_vals.count(i)
        for i in range(max(o_vals) + 1):
            opponent_pairs_stats[i] = o_vals.count(i)



        return { "min_byes" : min_byes, "max_byes" : max_byes, 
                "min_games_between" : min_games_between, "max_games_between" : max_games_between,
                "partner_pairs_stats" : partner_pairs_stats,

                "possible_pairs": len(p_vals),
    
                "partner_pairs_diff_more_one" : p_vals.count(max(p_vals) -2),

                "social_pairs_stats" : social_pairs_stats,
                "opponent_pairs_stats" : opponent_pairs_stats,
                "same_court_consecutive": same_court_consecutive,
                "alternation_rate" : alternation_rate,
                "court_switches" : court_switches,
                "total_transitions" : total_transitions,
                "max_same_court_streak" : max_same_court_streak,
                "rounds_div_str" : rounds_div_str
        }


# SCRIPT D'EXÉCUTION PRINCIPAL
# =========================================================================
