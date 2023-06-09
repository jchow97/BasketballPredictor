from common.constants import CURRENT_TEAMS
from models.nba_team import NbaTeam


class NbaPredictor:
    """
    This class is the predictor for NBA Games utilizing sklearn pipeline.
    """

    def __init__(self):
        pass

    def create_teams(self, years) -> None:
        """
        Creates a dictionary of all current teams.
        :param years:
        :return:
        """
        teams = dict()
        for year in years:
            for team in CURRENT_TEAMS:
                team_name = f"{team}_{year}"
                teams[team_name] = NbaTeam(team, year)
                print(f'{team_name} created.')
        return teams