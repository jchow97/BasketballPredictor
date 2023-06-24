import numpy as np
from sqlalchemy.engine import Row

from common.constants import CURRENT_TEAMS
from models.database import GamePlayerLog
from models.nba_player import NbaPlayer
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
        self.training_years = seasons
        self.pipeline = Pipeline([
            # ("scale", StandardScaler()),
            ("model", LogisticRegression(random_state=True, solver='liblinear', max_iter=100))
        ])

        self.HOME_COURT_ADV = 1.0

        self.db = database_service

    def train_model(self):
        """
        Trains the logistic regression model using the specified training years.
        :return: TODO (not sure what `pipeline.fit` returns.).
        """

        """
        Pseudocode: How model training works.
            1. 2d array of input (features) -> actual outcome
                [features] -> pt_differential (home - away)
            2. run pipeline.fit(training_input_data, training_output_data)
            
        """
        training_input_data, training_output_data = self.generate_training_data()
        # Train model
        self.pipeline.fit(training_input_data, training_output_data)

    def generate_training_data(self) -> tuple[list[list[float]], list[float]]:
        """
        Generates training data to train nba model.
        :return: Training input data (2d array) and training outcome data (array)
        """
        training_input_data = []
        training_outcome_data = []

        for year in self.training_years:
            season = self.db.get_season_by_year(year)
            schedule = self.db.get_games_by_season_id(season.id)
            teams = self.create_teams(year)
            players: dict[NbaPlayer] = {}
            for match in schedule:
                # Get team game logs from database.
                home_team_log, away_team_log = self.db.get_team_logs_by_game_id(match.id)

                # Get Team objects from memory.
                home_team_obj: NbaTeam = teams[f"{home_team_log.name}"]
                away_team_obj: NbaTeam = teams[f"{away_team_log.name}"]

                home_player_logs: list[GamePlayerLog] = self.db.get_player_logs_by_game_id_team_id(match.id,
                                                                                                   match.home_team_id)
                away_player_logs: list[GamePlayerLog] = self.db.get_player_logs_by_game_id_team_id(match.id,
                                                                                                   match.away_team_id)

                # Get features from team objects (before this game's stats).
                features: list[float] = self.generate_features_differential(home_team_obj, away_team_obj)

                # Add average BPM differential from player objects
                np.append(features, (self.calculate_avg_bpm(home_player_logs, players) -
                                     self.calculate_avg_bpm(away_player_logs, players)))

                # Calculate outcome data.
                total_points_differential: float = home_team_log.GameTeamLog.total_points - \
                                                   away_team_log.GameTeamLog.total_points

                training_input_data.append(features)
                training_outcome_data.append(total_points_differential)

                # Update team and player objects.
                self.update_team_features(home_team_obj, home_team_log, away_team_log)
                self.update_team_features(away_team_obj, away_team_log, home_team_log)

        return training_input_data, training_outcome_data

    def run_prediction(self, year: int):
        """
        Predicts a season of the NBA using a trained model.
        :param year: Season year (2021-2022 is 2022).
        :return:
        """
        raise NotImplementedError()

    def check_prediction(self):
        """
        Checks prediction against odds data for prediction accuracy.
        :return: Prediction accuracy
        """
        raise NotImplementedError()

    def process_odds_data(self, year: int):
        """
        Process odds data from Excel spreadsheet.
        :param year: Season year (2021-2022 is 2022).
        :return: A dataframe of the odds data for use.
        """
        raise NotImplementedError()

    @staticmethod
    def generate_features_differential(home: NbaTeam, away: NbaTeam) -> list[float]:
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
    def create_teams(year: int) -> dict:
        """
        Creates a dictionary of all current teams, for each year.
        :param year: Seasons to create teams for.
        :return: Dictionary of NBA teams (season unique).
        """
        teams = {}
        for team in CURRENT_TEAMS:
            teams[team] = NbaTeam(team, year)
            print(f'{team} created.')
        return teams

    def calculate_avg_bpm(self, player_logs, players: dict) -> float:
        """
        Calculates the average box plus/minus differential of the players between two teams in a match.
        :param players: Dictionary of NbaPlayer objects.
        :param player_logs: Team's player logs for the match.
        :return: float of the average box plus/minus.
        """
        pre_bpm_sum = 0.0
        count = 0

        # TODO: Add support to advanced stats in database.
        # TODO: Currently this uses a player dict, but make it so that we query instead to reduce our memory usage.
        for player_log in player_logs:
            if player_log.minutes_played is None:
                continue

            player = self.db.get_player_by_player_id(player_log.player_id)
            player_obj = players.get(player.unique_code)
            if not player_obj:
                players[player.unique_code] = NbaPlayer(player.friendly_name, player.unique_code)
                pre_bpm_sum += float(players[player.unique_code].bpm)
            else:
                pre_bpm_sum += float(player_obj.bpm)
            count += 1

            self.update_player_bpm(player_log, players[player.unique_code])
        if count == 0:
            return 0

        return pre_bpm_sum / count

    @staticmethod
    def update_team_features(team, team_log, opp_team_log) -> None:
        """
        Updates the team object's features with the team's stats for the game.
        :param team: Team Object
        :param team_log: Game Team Log data row
        :param opp_team_log: Opposing team's Game Team Log data row
        :return: None
        """
        team.games += 1

        if float(team_log.GameTeamLog.total_points) > float(opp_team_log.GameTeamLog.total_points):
            team.wins += 1
            team.calculate_win_loss_pct()
            team.last10.popleft()
            team.last10.append("W")
        else:
            team.losses += 1
            team.calculate_win_loss_pct()
            team.last10.popleft()
            team.last10.append("L")

        margin_of_victory = team_log.GameTeamLog.total_points - opp_team_log.GameTeamLog.total_points
        team.mov_total += margin_of_victory
        team.mov = team.mov_total / team.games

        team.off_rtg_total += float(team_log.GameTeamLog.offensive_rating)
        team.off_rtg = team.off_rtg_total / team.games

        team.tov_pct_total += float(team_log.GameTeamLog.turnover_pct)
        team.tov_pct = team.tov_pct_total / team.games

        team.off_reb_total += float(team_log.GameTeamLog.offensive_rebounds)
        team.off_reb = team.off_reb_total / team.games

        team.ts_pct_total += float(team_log.GameTeamLog.true_shooting_pct)
        team.ts_pct = team.ts_pct_total / team.games

        team.def_rtg_total += float(team_log.GameTeamLog.defensive_rating)
        team.def_rtg = team.def_rtg_total / team.games

        team.def_reb_total += float(team_log.GameTeamLog.defensive_rebounds)
        team.def_reb = team.def_reb_total / team.games

        team.opp_tov_pct_total += float(opp_team_log.GameTeamLog.turnover_pct)
        team.opp_tov_pct = team.opp_tov_pct_total / team.games

        team.pace_total += float(team_log.GameTeamLog.pace)
        team.pace = team.pace_total / team.games

        # Only need to recalculate because add_last10() was already called earlier
        team.last10_pct = team.calculate_last10()

        team.update_features()
        print(f"{team.team_name} features updated.")

    @staticmethod
    def update_player_bpm(player_log: GamePlayerLog, player: NbaPlayer) -> None:
        """
        For each player in the player logs, update their BPM.
        :param player: NbaPlayer Object
        :param player_log: Game Player Log
        :return: None
        """
        player.games_played += 1
        bpm = player_log.box_plus_minus
        if bpm is not None:
            player.bpm_total += float(bpm)
            player.bpm = player.bpm_total / player.games_played
