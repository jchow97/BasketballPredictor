from collections import deque

from sqlalchemy.engine import Row

from common.constants import TEAM_ABBRV


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

        self.last10 = deque(maxlen=10)
        self.last10_pct = self.calculate_last10()

        self.features: list[float] = []
        self.set_features()

    def calculate_last10(self) -> float:
        """
        Calculates and returns the win/loss percentage of the last 10 games played.
        :return: float of win/loss% of the last 10 games.
        """
        wins, losses = 0, 0
        for g in self.last10:
            if g == "W":
                wins += 1
            else:
                losses += 1

        if wins == 0:
            return 0.0
        else:
            return float(wins / float(wins + losses))

    def calculate_win_loss_pct(self) -> None:
        """
        Updates win pct based on the current wins and losses.
        :return: None
        """
        if self.wins == 0:
            self.win_loss_pct = 0.0
        elif self.losses == 0:
            self.win_loss_pct = 1.0
        else:
            self.win_loss_pct = self.wins / (self.wins + self.losses)

    def update_features(self, team_log: Row, opp_team_log: Row) -> None:
        """
        Updates the team object's features with the team's stats for the game.
        :param team_log: Game Team Log data row
        :param opp_team_log: Opposing team's Game Team Log data row
        :return: None
        """

        self.games += 1

        if float(team_log.GameTeamLog.total_points) > float(opp_team_log.GameTeamLog.total_points):
            self.wins += 1
            self.calculate_win_loss_pct()
            self.update_last10("W")
        else:
            self.losses += 1
            self.calculate_win_loss_pct()
            self.update_last10("L")

        margin_of_victory = team_log.GameTeamLog.total_points - opp_team_log.GameTeamLog.total_points
        self.mov_total += margin_of_victory
        self.mov = self.mov_total / self.games

        self.off_rtg_total += float(team_log.GameTeamLog.offensive_rating)
        self.off_rtg = self.off_rtg_total / self.games

        self.tov_pct_total += float(team_log.GameTeamLog.turnover_pct)
        self.tov_pct = self.tov_pct_total / self.games

        self.off_reb_total += float(team_log.GameTeamLog.offensive_rebounds)
        self.off_reb = self.off_reb_total / self.games

        self.ts_pct_total += float(team_log.GameTeamLog.true_shooting_pct)
        self.ts_pct = self.ts_pct_total / self.games

        self.def_rtg_total += float(team_log.GameTeamLog.defensive_rating)
        self.def_rtg = self.def_rtg_total / self.games

        self.def_reb_total += float(team_log.GameTeamLog.defensive_rebounds)
        self.def_reb = self.def_reb_total / self.games

        self.opp_tov_pct_total += float(opp_team_log.GameTeamLog.turnover_pct)
        self.opp_tov_pct = self.opp_tov_pct_total / self.games

        self.pace_total += float(team_log.GameTeamLog.pace)
        self.pace = self.pace_total / self.games

        # Only need to recalculate because add_last10() was already called earlier
        self.last10_pct = self.calculate_last10()

        self.set_features()

        print(f"{self.team_name} features updated.")

    def set_features(self) -> None:
        """
        Updates the features array with the proper stats.
        :return:
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

    def update_last10(self, result: str) -> None:
        """
        Updates the last 10 record for the team with the new result.
        :param result:
        :return:
        """
        if len(self.last10) == 10:
            self.last10.popleft()

        self.last10.append(result)
