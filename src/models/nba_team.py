import pandas as pd

from common.constants import TEAM_ABBRV
from models.database import Team


class NbaTeam:
    """
    NBA Season Object.

    This class uses the per-game stats of each box-score. Thus, any given stat for the team will be split into
    per game and totals for the stat. Per game (labelled as the normal stat) is simply the cumulated total over
    the course of a season, divided by the number of games played. This may cause statistical differences
    compared to the basketball-reference data.
    """
    class Node:
        def __init__(self, val='N/A', next=None, prev=None):
            self.val = val
            self.next = next
            self.prev = prev

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
        count = 0
        self.last10_head = self.Node()
        curr = self.last10_head
        prev = None
        while count < 10:
            curr.next = self.Node()
            prev = curr
            curr = curr.next
            curr.prev = prev
            count += 1
        self.last10_tail = curr
        self.last10_pct = self.calculate_last10()

        self.features: list[float] = []

    def calculate_last10(self) -> float:
        """
        Calculates and returns the win/loss percentage of the last 10 games played.
        :return: float of win/loss% of the last 10 games.
        """
        pass

    def calculate_win_loss_pct(self) -> float:
        """
        Calculates win pct based on the current wins and losses.
        :return: float of the win/loss percentage of the team.
        """
        pass

    def update_team_stats(self, team_box_score: pd.DataFrame, opponent_box_score: pd.DataFrame,
                          game_summary: pd.DataFrame) -> None:
        """
        Updates all features and fields for the team after a game.
        :param team_box_score: Dataframe of basic and advanced box score for the team.
        :param opponent_box_score: Dataframe of basic and advanced box score for the opposing team.
        :param game_summary: Game summary dataframe.
        :return: None
        """

        pass

    def update_features(self, database_team: Team):
        """
        Updates the feature properties using database Team object's properties. Useful for data persistence.
        :param database_team:
        :return:
        """
        pass

