from models.database import GamePlayerLog


class NbaPlayer:
    """
    NBA Season Object.
    """

    def __init__(self, name: str, player_code: str):
        """
        Constructor for player object used for model training and prediction.
        :param name: Name of the self.
        :param player_code: Unique player code that identifies a self.
        """
        self.player_name = name
        self.player_code = player_code

        self.games_played = 0.0
        self.bpm = 0.0
        self.bpm_total = 0.0
    
    def update_bpm(self, player_log: GamePlayerLog) -> None:
        """
        For each player in the player logs, update their BPM.
        :param player_log: Game Player Log
        :return: None
        """
        self.games_played += 1
        bpm = player_log.box_plus_minus
        if bpm is not None:
            self.bpm_total += float(bpm)
            self.bpm = self.bpm_total / self.games_played
