from models.nba_match import NbaMatch


class NbaSeason:
    """
    NBA Season Object.
    """

    def __init__(self, season: int, schedule: list[NbaMatch]):
        """
        Constructor for season object used for model training and prediction.
        :param season: Season year.
        """
        self.season = season
        self.matches: list = schedule
