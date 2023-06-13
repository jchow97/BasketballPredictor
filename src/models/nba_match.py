import pandas as pd


class NbaMatch:
    """
    NBA Season Object.
    """

    def __init__(self, game_code, home_team: str, away_team: str):
        """
        Constructor for match object used for model training and prediction.
        :param game_code: Unique game code.
        """
        self.game_code = game_code
        self.home_team: str = home_team
        self.away_team: str = away_team
        # TODO: change home_team and away_team to NbaTeam types.
        self.home_box_score: pd.DataFrame = pd.DataFrame()
        self.away_box_score: pd.DataFrame = pd.DataFrame()
        self.game_summary = None
