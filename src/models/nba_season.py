from models.nba_match import NbaMatch


class NbaSeason:
    """
    NBA Season Object.
    """

    def __init__(self, season: int):
        """
        Constructor for season object used for model training and prediction.
        :param season: Season year.
        """
        self.__season = season
        self.__matches = list()

    def get_game_schedule(self) -> list[NbaMatch]:
        """
        Iterates through an NBA season schedule to get a list of games.
        :return:
        """

