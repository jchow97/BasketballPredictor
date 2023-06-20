from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from common.constants import CURRENT_TEAMS, TEAM_ABBRV
from models.database import Base, Player, GameType, PlayerStatsType, TeamHomeAwayType, \
    TeamStatsType, Season, Team, TeamStats, TeamAdvancedStats, PlayerStats, Game, GameTeam, GameTeamLog, PlayerTeam, \
    GamePlayerLog
from models.nba_match import NbaMatch
from models.nba_player import NbaPlayer
from models.nba_season import NbaSeason
from models.nba_team import NbaTeam
from scripts.Scraper import Scraper


class DatabaseService:
    def __init__(self, session: Session, scraper: Scraper):
        self.session = session
        self.scraper = scraper
        self.__username = 'jeffreychow'
        self.__database = 'nba_dev'
        self.__port = '5432'

    def initialize_database(self) -> None:
        """
        Create the database and create the tables based on the mapped classes.
        :return: None
        """

        engine = create_engine(f'postgresql+psycopg2://{self.__username}:@localhost:{self.__port}/{self.__database}')

        # Create tables.
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def populate_tables(self, year: int) -> None:
        """
        Populate empty database tables using the scraper.
        :param year: Specifies the year (season) to scrape.
        :return: None
        """

        self.add_types()
        season, schedule_df = self.add_season(year)
        self.add_teams(season.id)

        for i in schedule_df.index:
            home_team = schedule_df['Home/Neutral'][i]
            away_team = schedule_df['Visitor/Neutral'][i]
            game = self.add_game(schedule_df, i, season)
            self.add_game_teams(game, home_team, away_team)
        self.session.commit()

        for player in self.session.query(Player).all():
            self.add_player_stats(player)
        self.session.commit()

    def add_types(self) -> None:
        """
        Populate the four type tables (game_type, player_stats_type, team_home_away_type, team_stats_type) with known
        types.
        :return: None
        """

        # Add Game Types
        # TODO: (#6) Differentiate between playoff games by their rounds in `game_type` table.
        game_types = ["Preseason", "Regular Season", "Play-In Game", "Playoffs"]
        for gt in game_types:
            gt_object = GameType(type=gt)
            self.session.add(gt_object)
            self.session.commit()

        # Add Player Types
        player_stats_types = ["Regular Season", "Regular Season Career", "Playoffs", "Playoffs Career"]
        for pst in player_stats_types:
            pst_object = PlayerStatsType(type=pst)
            self.session.add(pst_object)
            self.session.commit()

        # Add Team Home/Away Types
        team_home_away_types = ["Home", "Away"]
        for that in team_home_away_types:
            that_object = TeamHomeAwayType(type=that)
            self.session.add(that_object)
            self.session.commit()

        # Add Team Stats Types
        team_stats_types = ["Team", "Team/g", "Opponent", "Opponent/g"]
        for tst in team_stats_types:
            tst_object = TeamStatsType(type=tst)
            self.session.add(tst_object)
            self.session.commit()

    def add_teams(self, season_id: int) -> None:
        """
        Populate the team tables with the current season's teams initialize their related tables
        (team_stats, team_advanced_stats).
        Team tables: team, team_stats, team_advanced_stats
        :param season_id:
        :return: None
        """

        for team in CURRENT_TEAMS:
            season = self.session.query(Season.year).where(Season.id == season_id).one()[0]
            prev_year = str(int(season) - 1)
            t = Team(
                season_id=season_id,
                name=team,
                abbreviation=TEAM_ABBRV[team],
                friendly_name=f"{prev_year}-{season} {team}",

                wins=0,
                losses=0,
                home_wins=0,
                home_losses=0,
                away_wins=0,
                away_losses=0,
                streak=0,
                last_ten_wins=0,
                last_ten_losses=0,

                ats_wins=0,
                ats_losses=0,
                ats_ties=0,
                ats_home_wins=0,
                ats_home_losses=0,
                ats_home_ties=0,
                ats_away_wins=0,
                ats_away_losses=0,
                ats_away_ties=0
            )
            self.session.add(t)
            self.session.flush()

            for i in range(4):
                ts = TeamStats(
                    team_id=t.id,
                    type=i + 1,
                    minutes_played="",
                    field_goals=0,
                    field_goal_attempts=0,
                    three_pointers=0,
                    three_point_attempts=0,
                    three_point_pct=0,
                    two_pointers=0,
                    two_point_attempts=0,
                    two_point_pct=0,
                    free_throws=0,
                    free_throw_attempts=0,
                    free_throw_pct=0,
                    offensive_rebounds=0,
                    defensive_rebounds=0,
                    total_rebounds=0,
                    assists=0,
                    steals=0,
                    blocks=0,
                    turnovers=0,
                    personal_fouls=0,
                    points=0
                )
                self.session.add(ts)

            tas = TeamAdvancedStats(
                team_id=t.id,
                wins=0,
                losses=0,
                pythagorean_wins=0,
                pythagorean_losses=0,
                margin_of_victory=0,
                strength_of_schedule=0,
                simple_rating_system=0,
                offensive_rating=0,
                defensive_rating=0,
                pace=0,
                free_throw_attempt_rate=0,
                three_point_attempt_rate=0,
                effective_field_goal_pct=0,
                turnover_pct=0,
                offensive_rebound_pct=0,
                free_throws_per_field_goal_attempt=0,
                opponent_effective_field_goal_pct=0,
                opponent_turnover_pct=0,
                defensive_rebound_pct=0,
                defensive_free_throws_per_field_goal_attempt=0,
            )
            self.session.add(tas)

    # noinspection PyTypeChecker
    def add_season(self, year: int):
        """
        Adds season to the season db table.
        :param year: Season to be added.
        :return: season, schedule_df - Season object and the schedule dataframe.
        """
        schedule_df = self.scraper.scrape_nba_season(year)

        season_start_date = self.scraper.to_postgres_date(schedule_df['Date'].iloc[0])

        season = Season(
            year=f"{year}",
            friendly_name=f"NBA Season {year - 1}-{year}",
            season_start=season_start_date,
        )

        self.session.add(season)
        self.session.flush()
        return season, schedule_df

    def add_player_stats(self, player: Player) -> None:
        """
        Add a player's season and career statistics to the player_stats database table.
        :param player: Related Player object.
        :return: None
        """

        # TODO: (#5) Add advanced analytics tables from player page to PlayerStats
        player_stats_df = self.scraper.scrape_nba_player(player.unique_code)

        if player_stats_df is None:
            return None

        for i in player_stats_df.index[:-1]:
            if player_stats_df['Season'][i] != '':
                player_stats = PlayerStats(
                    player_id=player.id,
                    type=2 if player_stats_df['Season'][i] == 'Career' else 1,  # for Regular Season
                    season=player_stats_df['Season'][i] if (player_stats_df['Season'][i] != 'DNP') and (
                            player_stats_df['Season'][i] != '') else None,
                    games_played=player_stats_df['G'][i] if (player_stats_df['G'][i] != 'DNP') and (
                            player_stats_df['G'][i] != '') else None,
                    games_started=player_stats_df['GS'][i] if (player_stats_df['GS'][i] != 'DNP') and (
                            player_stats_df['GS'][i] != '') else None,
                    minutes_played=player_stats_df['MP'][i] if (player_stats_df['MP'][i] != 'DNP') and (
                            player_stats_df['MP'][i] != '') else None,
                    field_goals=player_stats_df['FG'][i] if (player_stats_df['FG'][i] != 'DNP') and (
                            player_stats_df['FG'][i] != '') else None,
                    field_goal_attempts=player_stats_df['FGA'][i] if (player_stats_df['FGA'][i] != 'DNP') and (
                            player_stats_df['FGA'][i] != '') else None,
                    field_goal_pct=player_stats_df['FG%'][i] if (player_stats_df['FG%'][i] != 'DNP') and (
                            player_stats_df['FG%'][i] != '') else None,
                    three_pointers=player_stats_df['3P'][i] if (player_stats_df['3P'][i] != 'DNP') and (
                            player_stats_df['3P'][i] != '') else None,
                    three_point_attempts=player_stats_df['3PA'][i] if (player_stats_df['3PA'][i] != 'DNP') and (
                            player_stats_df['3PA'][i] != '') else None,
                    three_point_pct=player_stats_df['3P%'][i] if (player_stats_df['3P%'][i] != 'DNP') and (
                            player_stats_df['3P%'][i] != '') else None,
                    two_pointers=player_stats_df['2P'][i] if (player_stats_df['2P'][i] != 'DNP') and (
                            player_stats_df['2P'][i] != '') else None,
                    two_point_attempts=player_stats_df['2PA'][i] if (player_stats_df['2PA'][i] != 'DNP') and (
                            player_stats_df['2PA'][i] != '') else None,
                    two_point_pct=player_stats_df['2P%'][i] if (player_stats_df['2P%'][i] != 'DNP') and (
                            player_stats_df['2P%'][i] != '') else None,
                    effective_field_goal_pct=player_stats_df['eFG%'][i] if (player_stats_df['eFG%'][i] != 'DNP') and (
                            player_stats_df['eFG%'][
                                i] != '') else None,
                    free_throws=player_stats_df['FT'][i] if (player_stats_df['FT'][i] != 'DNP') and (
                            player_stats_df['FT'][i] != '') else None,
                    free_throw_attempts=player_stats_df['FTA'][i] if (player_stats_df['FTA'][i] != 'DNP') and (
                            player_stats_df['FTA'][i] != '') else None,
                    free_throw_pct=player_stats_df['FT%'][i] if (player_stats_df['FT%'][i] != 'DNP') and (
                            player_stats_df['FT%'][i] != '') else None,
                    offensive_rebounds=player_stats_df['ORB'][i] if (player_stats_df['ORB'][i] != 'DNP') and (
                            player_stats_df['ORB'][i] != '') else None,
                    defensive_rebounds=player_stats_df['DRB'][i] if (player_stats_df['DRB'][i] != 'DNP') and (
                            player_stats_df['DRB'][i] != '') else None,
                    total_rebounds=player_stats_df['TRB'][i] if (player_stats_df['TRB'][i] != 'DNP') and (
                            player_stats_df['TRB'][i] != '') else None,
                    assists=player_stats_df['AST'][i] if (player_stats_df['AST'][i] != 'DNP') and (
                            player_stats_df['AST'][i] != '') else None,
                    steals=player_stats_df['STL'][i] if (player_stats_df['STL'][i] != 'DNP') and (
                            player_stats_df['STL'][i] != '') else None,
                    blocks=player_stats_df['BLK'][i] if (player_stats_df['BLK'][i] != 'DNP') and (
                            player_stats_df['BLK'][i] != '') else None,
                    turnovers=player_stats_df['TOV'][i] if (player_stats_df['TOV'][i] != 'DNP') and (
                            player_stats_df['TOV'][i] != '') else None,
                    personal_fouls=player_stats_df['PF'][i] if (player_stats_df['PF'][i] != 'DNP') and (
                            player_stats_df['PF'][i] != '') else None,
                    points=player_stats_df['PTS'][i] if (player_stats_df['PTS'][i] != 'DNP') and (
                            player_stats_df['PTS'][i] != '') else None
                )
                self.session.add(player_stats)

    # noinspection DuplicatedCode
    def add_game_teams(self, game: Game, home_team: str, away_team: str) -> None:
        """
        Adds the away and home team's game data to game_team database table.
        :param game: Related game
        :param home_team: Home team of the game.
        :param away_team: Away team of the game
        :return: None
        """
        game_summary, home_box, away_box = self.scraper.scrape_nba_match(game.game_code)
        # Game Summary headers: Team | 1 | 2 | 3 | 4 | (OT) | T | Pace | eFG% | TOV% | ORB% | FT/FGA | ORtg

        home_box_team_stats = home_box.iloc[-1]
        home_team_game_summary = game_summary.iloc[1]
        away_box_team_stats = away_box.iloc[-1]
        away_team_game_summary = game_summary.iloc[0]

        game_home_team = GameTeam(
            game_id=game.id,
            team_id=self.session.query(Team.id).filter(Team.name == home_team).scalar_subquery(),
            team_home_away_type=1
        )

        self.session.add(game_home_team)
        self.session.flush()

        self.add_game_team_log(game_home_team, home_team_game_summary, home_box_team_stats)

        for i in home_box.index[:-1]:
            player_name = home_box['Players'][i]
            player_code = home_box['Player Code'][i]
            player = self.session.query(Player).filter(
                Player.unique_code == player_code and Player.friendly_name == player_name).one_or_none()

            if player is None:
                player = self.add_player(player_name, player_code)
                self.add_player_team(player, game_home_team)

            self.add_game_player_log(home_box, i, player, game_home_team)

        game_away_team = GameTeam(
            game_id=game.id,
            team_id=self.session.query(Team.id).filter(Team.name == away_team).scalar_subquery(),
            team_home_away_type=2
        )
        self.session.add(game_away_team)
        self.session.flush()

        self.add_game_team_log(game_away_team, away_team_game_summary, away_box_team_stats)

        for i in away_box.index[:-1]:
            player_name = away_box['Players'][i]
            player_code = away_box['Player Code'][i]
            player = self.session.query(Player).filter(
                Player.unique_code == player_code and Player.friendly_name == player_name).one_or_none()

            if player is None:
                player = self.add_player(player_name, player_code)
                self.add_player_team(player, game_away_team)

            self.add_game_player_log(away_box, i, player, game_away_team)

    def add_game_team_log(self, game_team: GameTeam, game_summary: pd.DataFrame, team_box_stats: pd.DataFrame):
        """
        Adds a team's game log to the game_team_log database table.
        :param game_team: Related GameTeam object
        :param game_summary: Team's statistics dataframe.
        :param team_box_stats: Team's box score dataframe.
        :return:
        """
        # noinspection PyTypeChecker
        gtl = GameTeamLog(
            game_team_id=game_team.id,

            total_points=game_summary['T'],
            first_quarter_points=game_summary['1'],
            second_quarter_points=game_summary['2'],
            third_quarter_points=game_summary['3'],
            fourth_quarter_points=game_summary['4'],
            overtime_points=None,  # TODO: Configure OT calculation.

            minutes_played=team_box_stats['MP'],
            field_goals=team_box_stats['FG'],
            field_goal_attempts=team_box_stats['FGA'],
            field_goal_pct=team_box_stats['FG%'],
            three_pointers=team_box_stats['3P'],
            three_point_attempts=team_box_stats['3PA'],
            three_point_pct=team_box_stats['3P%'],
            free_throws=team_box_stats['FT'],
            free_throw_attempts=team_box_stats['FTA'],
            free_throw_pct=team_box_stats['FT%'],
            offensive_rebounds=team_box_stats['ORB'],
            defensive_rebounds=team_box_stats['DRB'],
            total_rebounds=team_box_stats['TRB'],
            assists=team_box_stats['AST'],
            steals=team_box_stats['STL'],
            blocks=team_box_stats['BLK'],
            turnovers=team_box_stats['TOV'],
            personal_fouls=team_box_stats['PF'],
            points=team_box_stats['PTS'],
            plus_minus=None,

            true_shooting_pct=team_box_stats['TS%'],
            effective_field_goal_pct=team_box_stats['eFG%'],
            three_point_attempt_rate=team_box_stats['3PAr'],
            free_throw_attempt_rate=team_box_stats['FTr'],
            offensive_rebound_pct=team_box_stats['ORB%'],
            defensive_rebound_pct=team_box_stats['DRB%'],
            total_rebound_pct=team_box_stats['TRB%'],
            assist_pct=team_box_stats['AST%'],
            steal_pct=team_box_stats['STL%'],
            block_pct=team_box_stats['BLK%'],
            turnover_pct=team_box_stats['TOV%'],
            usage_pct=team_box_stats['USG%'],
            offensive_rating=team_box_stats['ORtg'],
            defensive_rating=team_box_stats['DRtg'],
            box_plus_minus=None,
            pace=game_summary['Pace'],
            free_throws_per_field_goal_attempt=game_summary['FT/FGA'],
        )
        self.session.add(gtl)

    def add_player(self, player_name: str, player_code: str) -> Player:
        """
        Add a player to the player database table.
        :param player_name: Player's name.
        :param player_code: Player's unique identifier.
        :return: Newly created Player object.
        """
        player = Player(
            unique_code=player_code,
            first_name=player_name.split()[0],
            last_name=player_name.split()[1],
            friendly_name=player_name
        )

        self.session.add(player)
        self.session.flush()

        return player

    def add_player_team(self, player: Player, game_team) -> None:
        """
        Add a player-team relationship to the player_team database table.
        :param player: Related Player object.
        :param game_team: The player's team
        :return: None
        """
        player_team = PlayerTeam(
            player_id=player.id,
            team_id=game_team.team_id,
            # TODO: Replace datetime.now to actual date.
            start_date=datetime.now()
        )
        self.session.add(player_team)

    def add_game_player_log(self, box_df: pd.DataFrame, i: int, player: Player, game_team: GameTeam) -> None:
        """
        Add a player's game log to the game_player_log database table.
        :param box_df: Game's box score dataframe
        :param i: index of the box score to look at
        :param player: Related Player object.
        :param game_team: Related GameTeam object.
        :return: None
        """
        if ("Did Not" in box_df['MP'][i]) or ("Not With" in box_df['MP'][i]):
            game_player_log = GamePlayerLog(
                player_id=player.id,
                game_team_id=game_team.id
            )
        else:
            game_player_log = GamePlayerLog(
                player_id=player.id,
                game_team_id=game_team.id,

                minutes_played=box_df['MP'][i] if (box_df['MP'][i] != '') else None,
                field_goals=box_df['FG'][i] if (box_df['FG'][i] != '') else None,
                field_goal_attempts=box_df['FGA'][i] if (box_df['FGA'][i] != '') else None,
                field_goal_pct=box_df['FG%'][i] if (box_df['FG%'][i] != '') else None,
                three_pointers=box_df['3P'][i] if (box_df['3P'][i] != '') else None,
                three_point_attempts=box_df['3PA'][i] if (box_df['3PA'][i] != '') else None,
                three_point_pct=box_df['3P%'][i] if (box_df['3P%'][i] != '') else None,
                free_throws=box_df['FT'][i] if (box_df['FT'][i] != '') else None,
                free_throw_attempts=box_df['FTA'][i] if (box_df['FTA'][i] != '') else None,
                free_throw_pct=box_df['FT%'][i] if (box_df['FT%'][i] != '') else None,
                offensive_rebounds=box_df['ORB'][i] if (box_df['ORB'][i] != '') else None,
                defensive_rebounds=box_df['DRB'][i] if (box_df['DRB'][i] != '') else None,
                total_rebounds=box_df['TRB'][i] if (box_df['TRB'][i] != '') else None,
                assists=box_df['AST'][i] if (box_df['AST'][i] != '') else None,
                steals=box_df['STL'][i] if (box_df['STL'][i] != '') else None,
                blocks=box_df['BLK'][i] if (box_df['BLK'][i] != '') else None,
                turnovers=box_df['TOV'][i] if (box_df['TOV'][i] != '') else None,
                personal_fouls=box_df['PF'][i] if (box_df['PF'][i] != '') else None,
                points=box_df['PTS'][i] if (box_df['PTS'][i] != '') else None,
                plus_minus=box_df['+/-'][i] if (box_df['+/-'][i] != '') else None,

                true_shooting_pct=box_df['TS%'][i] if (box_df['TS%'][i] != '') else None,
                effective_field_goal_pct=box_df['eFG%'][i] if (box_df['eFG%'][i] != '') else None,
                three_point_attempt_rate=box_df['3PAr'][i] if (box_df['3PAr'][i] != '') else None,
                free_throw_attempt_rate=box_df['FTr'][i] if (box_df['FTr'][i] != '') else None,
                offensive_rebound_pct=box_df['ORB%'][i] if (box_df['ORB%'][i] != '') else None,
                defensive_rebound_pct=box_df['DRB%'][i] if (box_df['DRB%'][i] != '') else None,
                total_rebound_pct=box_df['TRB%'][i] if (box_df['TRB%'][i] != '') else None,
                assist_pct=box_df['AST%'][i] if (box_df['AST%'][i] != '') else None,
                steal_pct=box_df['STL%'][i] if (box_df['STL%'][i] != '') else None,
                block_pct=box_df['BLK%'][i] if (box_df['BLK%'][i] != '') else None,
                turnover_pct=box_df['TOV%'][i] if (box_df['TOV%'][i] != '') else None,
                usage_pct=box_df['USG%'][i] if (box_df['USG%'][i] != '') else None,
                offensive_rating=box_df['ORtg'][i] if (box_df['ORtg'][i] != '') else None,
                defensive_rating=box_df['DRtg'][i] if (box_df['DRtg'][i] != '') else None,
                box_plus_minus=box_df['BPM'][i] if (box_df['BPM'][i] != '') else None
            )
        self.session.add(game_player_log)

    # noinspection PyTypeChecker
    def add_game(self, schedule: pd.DataFrame, i: int, season: Season) -> Game:
        """
        Add a game to the game database table.
        :param schedule: Schedule dataframe.
        :param i: Index to look at
        :param season: Related Season object.
        :return: Newly created Game object.
        """
        # Create game object
        game_datetime = self.scraper.to_postgres_datetime(schedule['Date'][i], schedule['Start (ET)'][i])
        home_team = schedule['Home/Neutral'][i]
        # away_team = schedule['Visitor/Neutral'][i]
        game_code = self.scraper.get_game_code(schedule['Date'][i], home_team)

        # TODO: (#3) Correct assignment of game types.
        game = Game(
            season_id=season.id,
            type=2,  # 2: regular season
            start_datetime=game_datetime,
            game_code=game_code
        )
        self.session.add(game)
        self.session.flush()
        return game

    def get_seasons(self, seasons: list[int]) -> list[NbaSeason]:
        """
        Combines various season schedules from the database and returns as one giant schedule, ordered by game time.
        :param seasons:
        :return: A big schedule.
        """
        result: list[NbaSeason] = []

        for season in seasons:
            result.append(self.get_season(season))

        return result

    def get_season(self, year: int) -> NbaSeason:
        """
        Retrieves a season's schedule from the database.
        :param year: NBA Season to retrieve (e.g. 2021-2022 season would be 2022).
        :return: A dataframe of the NBA season schedule.
        """
        season = self.session.query(Season).where(Season.year == str(year)).one_or_none()

        if season is None:
            raise NotImplementedError()

        # TODO: Create match objects from schedule and assign to NbaSeason.matches.
        # matches = self.session.query(Game).where(Game.season_id == season_query.Season.id).all()

        return NbaSeason(int(season.year))

    def get_game(self, game_code: str) -> NbaMatch:
        """
        Retrieves a game from the database.
        :param game_code: Unique game code
        :return: TODO
        """
        query = self.session\
            .query(Game, GameTeam, GameTeamLog, Team)\
            .where(Game.game_code == game_code)\
            .where(GameTeam.game_id == Game.id)\
            .where(GameTeamLog.game_team_id == GameTeam.id)\
            .where(Team.id == GameTeam.team_id)\
            .all()

        if query is None:
            raise NotImplementedError()

        return NbaMatch(query[0].Game.game_code, query[0].Team.name, query[1].Team.name)

    def get_team(self, team: str, season: int) -> NbaTeam:
        """
        Retrieves a team for a specific season from the database with their statistics.
        :param team: Team name.
        :param season: year (e.g. 2021-2022 is 2022).
        :return: NbaTeam object
        """
        query = self.session\
            .query(Team, Season)\
            .where(Season.id == Team.season_id)\
            .where(Team.name == team)\
            .where(Season.year == str(season))\
            .one_or_none()

        if query is None:
            # TODO: Handle none case.
            raise NotImplementedError()

        team = NbaTeam(query.Team.name, query.Season.year)
        team.update_features(query.Team)

        return team

    def get_player(self, player_code: str) -> NbaPlayer:
        """
        Retrieves a player from the database with their most recently-played season stats (this may change).
        :param player_code: Unique player code.
        :return: NbaPlayer object
        """
        query = self.session\
            .query(Player, PlayerStats)\
            .where(Player.id == PlayerStats.player_id)\
            .where(Player.unique_code == player_code)\
            .order_by(PlayerStats.season.desc())\
            .first()

        player = NbaPlayer(query.Player.friendly_name, query.Player.unique_code)
        return player
