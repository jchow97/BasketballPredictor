import numpy as np
import pandas as pd

from common.constants import CURRENT_TEAMS
from models.database import *
from models.nba_match import NbaMatch
from models.nba_player import NbaPlayer
from models.nba_season import NbaSeason
from models.nba_team import NbaTeam
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from service.database_service import DatabaseService


class NbaPredictor:
    """
    This class is the predictor for NBA Games utilizing sklearn pipeline.
    """

    def __init__(self, database_service: DatabaseService, seasons: list[int]):
        """
        Constructor for Logistic Regression ML pipeline.
        :param seasons: Years for model training.
        """
        self.training_seasons = seasons
        self.teams = self.create_teams(seasons)
        self.pipeline = Pipeline([
            # ("scale", StandardScaler()),
            ("model", LogisticRegression(random_state=True, solver='liblinear', max_iter=100))
        ])

        self.HOME_COURT_ADV = 1.0

        self.db = database_service

    def train_model(self) -> tuple[list[list[float]], list[float], list[list[NbaTeam]]]:
        """
        Trains the logistic regression model using the specified training years.
        :return: None
        """
        training_input_data = []
        training_output_data = []
        input_context = []

        # Query for seasons.
        seasons: list[Season] = self.db.get_seasons(self.training_seasons)

        # Create season and match objects.
        """
        Pseudocode:
        For each season:
            - Query for game, and related teams + team logs. (1 query, 2.5k rows)
            - Create match objects.
            - For each match:
                Query for player logs (2 queries, 1 for each team per match)
                
        """
        for season in seasons:
            matches: list[tuple[Game, GameTeam, GameTeamLog, Team]] = self.db.get_games_by_season_id(season.id)

            schedule: list[NbaMatch] = []
            for i in range(0, len(matches), 2):

                home_game_object, home_game_team_object, home_game_team_log_object, home_team_object = matches[i]
                home_players_bpm: int = self.db.get_player_log_scaled_bpm_avg_by_game_team_id(home_game_team_object.id)
                away_game_object, away_game_team_object, away_game_team_log_object, away_team_object = matches[i+1]
                away_players_bpm: int = self.db.get_player_log_scaled_bpm_avg_by_game_team_id(away_game_team_object.id)

                if home_game_object.game_code != away_game_object.game_code:
                    raise ValueError("Game codes do not match")

                home_team: NbaTeam = self.teams[home_team_object.friendly_name]
                away_team: NbaTeam = self.teams[away_team_object.friendly_name]

                new_match: NbaMatch = NbaMatch(home_game_object.game_code, home_team, away_team)
                new_match.add_team_logs(home_game_team_log_object, away_game_team_log_object,
                                        home_players_bpm, away_players_bpm)


                schedule.append(new_match)

            # new_season = NbaSeason(int(season.year), schedule)

        # TODO: Delete
        for season in seasons:
            for match in season.matches:

                away_team: NbaTeam = self.teams[f"{match.away_team}_{season}"]
                home_team: NbaTeam = self.teams[f"{match.home_team}_{season}"]

                # Get average box plus/minus for each team.
                away_avg_bpm: float = self.calculate_avg_bpm(match.away_box_score)
                home_avg_bpm: float = self.calculate_avg_bpm(match.home_box_score)

                # Calculate the differential between the average box plus/minus.
                bpm_diff = home_avg_bpm - away_avg_bpm

                pre_data: list[float] = self.generate_input_data(away_team, home_team)
                np.append(pre_data, [self.HOME_COURT_ADV, bpm_diff])

                # Calculate the point differential for each team.
                away_box_total = match.away_box_score.iloc[-1]
                away_pts = away_box_total["PTS"]
                home_box_total = match.home_box_score.iloc[-1]
                home_pts = home_box_total["PTS"]
                game_pt_diff = float(away_pts) - float(home_pts)  # Done this way to better reflect spreads.

                # Finalize return data.
                training_input_data.append(pre_data)
                training_output_data.append(game_pt_diff)
                # context/row identifiers [away, home]
                input_context.append([away_team, home_team])

                print(f'{match.game_code} input and output data added.')

                # Update team objects with new match data.
                print(f"Updating away team ({away_team}) features.")
                away_team.update_team_stats(match.away_box_score, match.home_box_score, match.game_summary)
                print(f"Updating home team ({home_team}) features.")
                home_team.update_team_stats(match.home_box_score, match.away_box_score, match.game_summary)

        return training_input_data, training_output_data, input_context

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
    def generate_input_data(away: NbaTeam, home: NbaTeam) -> list[float]:
        """
        Generate the differential between the features of the home team.
        :param away: Away team object.
        :param home: Home team object.
        :return: List of differences for each feature.
        """

        away_f: list[float] = away.features
        home_f: list[float] = home.features

        input_data = np.subtract(home_f, away_f)
        return input_data

    @staticmethod
    def create_teams(years: list[int]) -> dict:
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

    def calculate_avg_bpm(self, box_score: pd.DataFrame) -> float:
        """
        Calculates the average box plus/minus for the team's box score.
        :param box_score: Dataframe of the team's box score.
        :return: float of the average box plus/minus.
        """
        pre_bpm_sum = 0.0
        count = 0

        for i in box_score.index[:-1]:  # -1 to exclude team totals.
            player_name = box_score['Players'][i]
            print(f"Fetching {player_name}'s BPM.")
            player_code: str = self.db.scraper.get_player_code(player_name)
            player: NbaPlayer = self.db.get_player(player_code)
            pre_bpm_sum += float(player.bpm)
            count += 1

        return pre_bpm_sum / count
