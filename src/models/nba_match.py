import pandas as pd

from models.nba_team import NbaTeam


class NbaMatch:
    """
    NBA Season Object.
    """

    def __init__(self, game_code, home_team: NbaTeam, away_team: NbaTeam):
        """
        Constructor for match object used for model training and prediction.
        :param game_code: Unique game code.
        """
        self.game_code = game_code
        self.home_team: NbaTeam = home_team
        self.away_team: NbaTeam = away_team

        self.home_box_score = None
        self.home_players_bpm = 0.0
        self.away_box_score = None
        self.away_players_bpm = 0.0

        self.game_summary = None

    def add_team_logs(self, home_team_game_log, away_team_game_log, home_players_bpm, away_players_bpm):
        """
        Adds relevant box score data (including player BPMs) into properties.
        :param home_team_game_log: GameTeamLog for the home team
        :param away_team_game_log: GameTeamLog for the away team
        :param home_players_bpm: Sum of home players' BPMs.
        :param away_players_bpm:
        :return:
        """

        raise NotImplementedError

    def add_odds_data(self):
        raise NotImplementedError
    