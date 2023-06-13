from collections import deque
import pandas as pd

from common.constants import TEAM_ABBRV
from models.database import Team, TeamStats, TeamAdvancedStats


class NbaTeam:
    """
    NBA Season Object.

    This class uses the per-game stats of each box-score. Thus, any given stat for the team will be split into
    per game and totals for the stat. Per game (labelled as the normal stat) is simply the cumulated total over
    the course of a season, divided by the number of games played. This may cause statistical differences
    compared to the basketball-reference data.
    """
    def __init__(self, team: str, season: int):
        """
        Constructor for team object used for model training and prediction.
        :param team: Team name.
        :param season: Year (2021-2022 is 2022).
        """
        # Team Details
        self.team_name = team
        self.season = season
        self.team_abbrv = TEAM_ABBRV[self.team_name]

        # Features
        self.win_loss_pct = 0.0
        self.mov = 0.0
        self.off_rtg = 0.0
        self.tov_pct = 0.0
        self.off_reb = 0.0
        self.ts_pct = 0.0
        self.def_rtg = 0.0
        self.def_reb = 0.0
        self.opp_tov_pct = 0.0
        self.pace = 0.0
        # + Home Court Advantage

        # Supplementary fields
        self.wins = 0.0
        self.losses = 0.0
        self.games = 0.0

        self.mov_total = 0.0
        self.off_rtg_total = 0.0
        self.tov_pct_total = 0.0
        self.off_reb_total = 0.0
        self.ts_pct_total = 0.0
        self.def_rtg_total = 0.0
        self.def_reb_total = 0.0
        self.opp_tov_pct_total = 0.0
        self.pace_total = 0.0

        # Create last 10 linked list.
        self.last10 = deque(maxlen=10)
        self.last10_pct = self.calculate_last10()

        self.features: list[float] = []

    def update_team_stats(self, team_box_score: pd.DataFrame, opponent_box_score: pd.DataFrame,
                          game_summary: pd.DataFrame) -> None:
        """
        Updates all features and fields for the team after a game.
        :param team_box_score: Dataframe of basic and advanced box score for the team.
        :param opponent_box_score: Dataframe of basic and advanced box score for the opposing team.
        :param game_summary: Game summary dataframe.
        :return: None
        """

        team_totals = team_box_score.iloc[-1]
        opp_totals = opponent_box_score.iloc[-1]

        self.games += 1

        # Win-Loss Pct
        if float(team_totals['PTS']) > float(opp_totals['PTS']):
            # team won the match
            self.wins += 1
            self.win_loss_pct = self.calculate_win_loss_pct()
            self.add_last10("W")
        else:
            # team lost
            self.losses += 1
            self.calculate_win_loss_pct()
            self.add_last10("L")

        mov = float(team_totals['PTS']) - float(opp_totals['PTS'])
        self.mov_total += mov
        self.mov = self.mov_total / self.games

        self.off_rtg_total += float(team_totals['ORtg'])
        self.off_rtg = self.off_rtg_total / self.games

        self.tov_pct_total += float(team_totals['TOV_pct'])
        self.tov_pct = self.tov_pct_total / self.games

        self.off_reb_total += float(team_totals['ORB'])
        self.off_reb = self.off_reb_total / self.games

        self.ts_pct_total += float(team_totals['TS_pct'])
        self.ts_pct = self.ts_pct_total / self.games

        self.def_rtg_total += float(team_totals['DRtg'])
        self.def_rtg = self.def_rtg_total / self.games

        self.def_reb_total += float(team_totals['DRB'])
        self.def_reb = self.def_reb_total / self.games

        self.opp_tov_pct_total += float(opp_totals['TOV_pct'])
        self.opp_tov_pct = self.opp_tov_pct_total / self.games

        self.pace_total += float(game_summary.iloc[0]['Pace'])
        self.pace = self.pace_total / self.games

        # Only need to recalculate because add_last10() was already called earlier
        self.last10_pct = self.calculate_last10()

        self.update_features()
        print(f"{self.team_name} features updated.")

    def calculate_last10(self) -> float:
        """
        Calculates and returns the win/loss percentage of the last 10 games played.
        :return: float of win/loss% of the last 10 games.
        """
        wins, losses = self.count_last10_wl()
        if wins == 0:
            return 0.0
        elif losses == 0:
            return 0.0
        else:
            return float(wins) / float(wins + losses)

    def calculate_win_loss_pct(self) -> float:
        """
        Calculates win pct based on the current wins and losses.
        :return: float of the win/loss percentage of the team.
        """
        if self.wins == 0:
            return 0.0
        elif self.losses == 0:
            return 1.0
        else:
            return self.wins / self.losses

    def add_last10(self, outcome) -> None:
        """
        Adds game to last 10 record.
        :param outcome: Game outcome "W" or "L" of the game added.
        :return: None
        """
        if len(self.last10) == 10:
            self.last10.popleft()
            self.last10.append(outcome)

    def count_last10_wl(self) -> tuple[int, int]:
        """
        Counts and returns the number of wins and losses in the Last 10 record.
        :return: Tuple of the [wins, losses].
        """
        wins, losses = 0, 0
        for game in self.last10:
            if game == "W":
                wins += 1
            elif game == "L":
                losses += 1
        return wins, losses

    def update_features(self) -> list[float]:
        """
        Returns an array of the team's feature inputs.
        :return: list[float] - the team's feature inputs as a list.
              [w/l%, mov, ortg, tov%, oreb, ts%, drtg, dreb, o_tov%, pace, last10%]
        """
        self.features.clear()
        self.features.append(self.win_loss_pct)
        self.features.append(self.mov)
        self.features.append(self.off_rtg)
        self.features.append(self.tov_pct)
        self.features.append(self.off_reb)
        self.features.append(self.ts_pct)
        self.features.append(self.def_rtg)
        self.features.append(self.def_reb)
        self.features.append(self.opp_tov_pct)
        self.features.append(self.pace)
        self.features.append(self.last10_pct)

        print(self.features)
        return self.features

    def update_features_from_database(self, db_team: Team, db_team_basic_stats: TeamStats,
                                      db_team_adv_stats: TeamAdvancedStats) -> list[float]:
        """
        Updates the feature properties using database Team object's properties. Useful for data persistence.
        :param db_team: Team object from database.
        :param db_team_basic_stats: Team's basic stats object.
        :param db_team_adv_stats: Team's advanced stats object.
        :return:the team's feature inputs as a list.
              [w/l%, mov, ortg, tov%, oreb, ts%, drtg, dreb, o_tov%, pace, last10%]
        """

        self.wins = db_team.wins
        self.losses = db_team.losses
        self.win_loss_pct = self.calculate_win_loss_pct()

        self.mov = db_team_adv_stats.margin_of_victory
        self.off_rtg = db_team_adv_stats.offensive_rating
        self.tov_pct = db_team_adv_stats.turnover_pct
        self.off_reb = db_team_basic_stats.offensive_rebounds
        self.def_rtg = db_team_adv_stats.defensive_rating
        self.def_reb = db_team_basic_stats.defensive_rebounds
        self.opp_tov_pct = db_team_adv_stats.opponent_turnover_pct
        self.pace = db_team_adv_stats.pace

        # TODO: Fix this because db doesn't track last 10 in order.
        self.last10_pct = db_team.last_ten_wins / db_team.last_ten_losses

        return self.update_features()

