from common.constants import TEAM_ABBRV


class NbaTeam:
    """
    NBA Season Object.

    This class uses the per-game stats of each box-score. Thus, any given stat for the team will be split into
    per game and totals for the stat. Per game (labelled as the normal stat) is simply the cumulated total over
    the course of a season, divided by the number of games played. This may cause statistical differences
    compared to the basketball-reference data.
    """
    class Node:
        val = None
        next = None
        prev = None

        def __init__(self, val='N/A', next=None, prev=None):
            self.val = val
            self.next = next
            self.prev = prev

    def __init__(self, team: str, season:int):
        """
        Constructor for team object used for model training and prediction.
        :param team: Team name.
        :param season: Year (2021-2022 is 2022).
        """
        # Team Details
        self.__team_name = team
        self.__season = season
        self.__team_abbrv = TEAM_ABBRV[self.__team_name]

        # Features
        self.__win_loss_pct = 0.0
        self.__mov = 0.0
        self.__off_rtg = 0.0
        self.__tov_pct = 0.0
        self.__off_reb = 0.0
        self.__ts_pct = 0.0
        self.__def_rtg = 0.0
        self.__def_reb = 0.0
        self.__opp_tov_pct = 0.0
        self.__pace = 0.0
        # + Home Court Advantage

        # Supplementary fields
        self.__wins = 0.0
        self.__losses = 0.0
        self.__games = 0.0

        self.__mov_total = 0.0
        self.__off_rtg_total = 0.0
        self.__tov_pct_total = 0.0
        self.__off_reb_total = 0.0
        self.__ts_pct_total = 0.0
        self.__def_rtg_total = 0.0
        self.__def_reb_total = 0.0
        self.__opp_tov_pct_total = 0.0
        self.__pace_total = 0.0

        # Create last 10 linked list.
        count = 0
        self.__last10_head = self.Node()
        curr = self.__last10_head
        prev = None
        while count < 10:
            curr.next = self.Node()
            prev = curr
            curr = curr.next
            curr.prev = prev
            count += 1
        self.__last10_tail = curr
        self.__last10_pct = self.calculate_last10()

        self.__features = []

    def calculate_last10(self) -> float:
        pass
