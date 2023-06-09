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
        self.player_code: player_code

        self.games_played = 0.0
        self.bpm = 0.0
        self.bpm_total = 0.0

    def update_bpm(self, box_score: pd.DataFrame) -> None:
        """
        Updates the box plus/minus field.
        :param box_score:
        :return: None.
        """
        self.__games_played += 1
        print(self.__player_name)
        bpm = box_score.loc[box_score['Players'] == self.__player_name]['BPM']
        if bpm.any():
            self.__bpm_total += float(bpm)
            self.__bpm = self.__bpm_total / self.__games_played
