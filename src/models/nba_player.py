import pandas as pd


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
        self.player_name = name
        self.player_code = player_code

        self.games_played = 0.0
        self.bpm = 0.0
        self.bpm_total = 0.0
