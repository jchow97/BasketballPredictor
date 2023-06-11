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
        self.away_box_score = None
        self.game_summary = None
