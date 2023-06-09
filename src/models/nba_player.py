class NbaPlayer:
    """
    NBA Season Object.
    """

    def __init__(self, name: str, player_code: str):
        """
        Constructor for player object used for model training and prediction.
        :param name: Name of the player.
        :param player_code: Unique player code that identifies a player.
        """
        self.__name = name
        self.__player_code: player_code

