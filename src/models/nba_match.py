
class NbaMatch:
    """
    NBA Season Object.
    """

    def __init__(self, game_code):
        """
        Constructor for match object used for model training and prediction.
        :param game_code: Unique game code.
        """
        self.game_code = game_code
        self.away_team = None
        self.home_team = None
