from common.constants import CURRENT_TEAMS
from models.nba_team import NbaTeam
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


class NbaPredictor:
    """
    This class is the predictor for NBA Games utilizing sklearn pipeline.
    """

    def __init__(self, years):
        """
        Constructor for Logistic Regression ML pipeline.
        :param years: Seasons for model training.
        """
        self.teams = self.create_teams(years)
        self.pipeline = Pipeline([
            # ("scale", StandardScaler()),
            ("model", LogisticRegression(random_state=True, solver='liblinear', max_iter=100))
        ])

    def train_model(self) -> None:
        """
        Trains the logistic regression model using the specified training years.
        :return: None
        """

    def run_prediction(self, year: int):
        """
        Predicts a season of the NBA using a trained model.
        :param year: Season year (2021-2022 is 2022).
        :return:
        """

    def check_prediction(self):
        """
        Checks prediction against odds data for prediction accuracy.
        :return: Prediction accuracy
        """

    def process_odds_data(self, year: int):
        """
        Process odds data from Excel spreadsheet.
        :param year: Season year (2021-2022 is 2022).
        :return: A dataframe of the odds data for use.
        """

    @staticmethod
    def create_teams(years) -> dict:
        """
        Creates a dictionary of all current teams, for each year.
        :param years: Seasons to create teams for.
        :return: Dictionary of NBA teams (season unique).
        """
        teams = dict()
        for year in years:
            for team in CURRENT_TEAMS:
                team_name = f"{team}_{year}"
                teams[team_name] = NbaTeam(team, year)
                print(f'{team_name} created.')
        return teams
