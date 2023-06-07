from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from common.constants import CURRENT_TEAMS, TEAM_ABBRV
from models.database import username, port, database, Base, Player, GameType, PlayerStatsType, TeamHomeAwayType, \
    TeamStatsType, Season, Team, TeamStats, TeamAdvancedStats, PlayerStats, Game, GameTeam, GameTeamLog, PlayerTeam, \
    GamePlayerLog
from scripts.Scraper import Scraper


def initialize_database() -> None:
    """
    Create the database and create the tables based on the mapped classes.
    :return: None
    """

    engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:{port}/{database}')

    # Create tables.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def populate_tables(session: Session, scraper: Scraper, year: int) -> None:
    """
    Populate empty database tables using the scraper.
    :param session: SQLAlchemy Session
    :param scraper: Scraper object
    :param year: Specifies the year (season) to scrape.
    :return: None
    """

    add_types(session)
    season, schedule_df = add_season(session, scraper, year)
    add_teams(session, season.id)

    for i in schedule_df.index:
        home_team = schedule_df['Home/Neutral'][i]
        away_team = schedule_df['Visitor/Neutral'][i]
        game = add_game(session, scraper, schedule_df, i, season)
        add_game_teams(session, scraper, game, home_team, away_team)
    session.commit()

    for player in session.query(Player).all():
        add_player_stats(session, scraper, player)
    session.commit()


def add_types(session: Session) -> None:
    """
    Populate the four type tables (game_type, player_stats_type, team_home_away_type, team_stats_type) with known types.
    :param session: SQLAlchemy Session
    :return: None
    """

    # Add Game Types
    # TODO: (#6) Differentiate between playoff games by their rounds in `game_type` table.
    game_types = ["Preseason", "Regular Season", "Play-In Game", "Playoffs"]
    for gt in game_types:
        gt_object = GameType(type=gt)
        session.add(gt_object)
        session.commit()

    # Add Player Types
    player_stats_types = ["Regular Season", "Regular Season Career", "Playoffs", "Playoffs Career"]
    for pst in player_stats_types:
        pst_object = PlayerStatsType(type=pst)
        session.add(pst_object)
        session.commit()

    # Add Team Home/Away Types
    team_home_away_types = ["Home", "Away"]
    for that in team_home_away_types:
        that_object = TeamHomeAwayType(type=that)
        session.add(that_object)
        session.commit()

    # Add Team Stats Types
    team_stats_types = ["Team", "Team/g", "Opponent", "Opponent/g"]
    for tst in team_stats_types:
        tst_object = TeamStatsType(type=tst)
        session.add(tst_object)
        session.commit()


def add_teams(session: Session, season_id) -> None:
    """
    Populate the team tables with the current season's teams initialize their related tables
    (team_stats, team_advanced_stats).
    Team tables: team, team_stats, team_advanced_stats
    :param session: SQLAlchemy Session
    :param season_id:
    :return: None
    """

    for team in CURRENT_TEAMS:
        season = session.query(Season.year).where(Season.id == season_id).one()[0]
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
        session.add(t)
        session.flush()

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
            session.add(ts)

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
        session.add(tas)


def add_season(session: Session, scraper: Scraper, year: int):
    """
    Adds season to the season db table.
    :param session: SQLAlchemy Session
    :param scraper: Scraper object
    :param year: Season to be added.
    :return: season, schedule_df - Season object and the schedule dataframe.
    """
    schedule_df = scraper.scrape_nba_season(year)

    season_start_date = scraper.to_postgres_date(schedule_df['Date'].iloc[0])
    season_end_date = None

    season = Season(
        year=f"{year}",
        friendly_name=f"NBA Season {year - 1}-{year}",
        season_start=season_start_date,
        season_end=season_end_date
    )

    session.add(season)
    session.flush()
    return season, schedule_df


def add_player_stats(session: Session, scraper: Scraper, player: Player) -> None:
    """
    Add a player's season and career statistics to the player_stats database table.
    :param session: SQLAlchemy Session
    :param scraper: Scraper object
    :param player: Related Player object.
    :return: None
    """

    # TODO: (#5) Add advanced analytics tables from player page to PlayerStats
    player_stats_df = scraper.scrape_nba_player(player.unique_code)

    if player_stats_df is None:
        return None

    for i in player_stats_df.index[:-1]:
        if player_stats_df['Season'][i] != '':
            player_stats = PlayerStats(
                player_id=player.id,
                type=2 if player_stats_df['Season'][i] == 'Career' else 1,  # for Regular Season
                season=player_stats_df['Season'][i] if (player_stats_df['Season'][i] != 'DNP')
                                                       and (player_stats_df['Season'][i] != '') else None,
                games_played=player_stats_df['G'][i] if (player_stats_df['G'][i] != 'DNP')
                                                        and (player_stats_df['G'][i] != '') else None,
                games_started=player_stats_df['GS'][i] if (player_stats_df['GS'][i] != 'DNP')
                                                          and (player_stats_df['GS'][i] != '') else None,
                minutes_played=player_stats_df['MP'][i] if (player_stats_df['MP'][i] != 'DNP')
                                                           and (player_stats_df['MP'][i] != '') else None,
                field_goals=player_stats_df['FG'][i] if (player_stats_df['FG'][i] != 'DNP')
                                                        and (player_stats_df['FG'][i] != '') else None,
                field_goal_attempts=player_stats_df['FGA'][i] if (player_stats_df['FGA'][i] != 'DNP')
                                                                 and (player_stats_df['FGA'][i] != '') else None,
                field_goal_pct=player_stats_df['FG%'][i] if (player_stats_df['FG%'][i] != 'DNP')
                                                            and (player_stats_df['FG%'][i] != '') else None,
                three_pointers=player_stats_df['3P'][i] if (player_stats_df['3P'][i] != 'DNP')
                                                           and (player_stats_df['3P'][i] != '') else None,
                three_point_attempts=player_stats_df['3PA'][i] if (player_stats_df['3PA'][i] != 'DNP')
                                                                  and (player_stats_df['3PA'][i] != '') else None,
                three_point_pct=player_stats_df['3P%'][i] if (player_stats_df['3P%'][i] != 'DNP')
                                                             and (player_stats_df['3P%'][i] != '') else None,
                two_pointers=player_stats_df['2P'][i] if (player_stats_df['2P'][i] != 'DNP')
                                                         and (player_stats_df['2P'][i] != '') else None,
                two_point_attempts=player_stats_df['2PA'][i] if (player_stats_df['2PA'][i] != 'DNP')
                                                                and (player_stats_df['2PA'][i] != '') else None,
                two_point_pct=player_stats_df['2P%'][i] if (player_stats_df['2P%'][i] != 'DNP')
                                                           and (player_stats_df['2P%'][i] != '') else None,
                effective_field_goal_pct=player_stats_df['eFG%'][i] if (player_stats_df['eFG%'][i] != 'DNP')
                                                                       and (player_stats_df['eFG%'][
                                                                                i] != '') else None,
                free_throws=player_stats_df['FT'][i] if (player_stats_df['FT'][i] != 'DNP')
                                                        and (player_stats_df['FT'][i] != '') else None,
                free_throw_attempts=player_stats_df['FTA'][i] if (player_stats_df['FTA'][i] != 'DNP')
                                                                 and (player_stats_df['FTA'][i] != '') else None,
                free_throw_pct=player_stats_df['FT%'][i] if (player_stats_df['FT%'][i] != 'DNP')
                                                            and (player_stats_df['FT%'][i] != '') else None,
                offensive_rebounds=player_stats_df['ORB'][i] if (player_stats_df['ORB'][i] != 'DNP')
                                                                and (player_stats_df['ORB'][i] != '') else None,
                defensive_rebounds=player_stats_df['DRB'][i] if (player_stats_df['DRB'][i] != 'DNP')
                                                                and (player_stats_df['DRB'][i] != '') else None,
                total_rebounds=player_stats_df['TRB'][i] if (player_stats_df['TRB'][i] != 'DNP')
                                                            and (player_stats_df['TRB'][i] != '') else None,
                assists=player_stats_df['AST'][i] if (player_stats_df['AST'][i] != 'DNP')
                                                     and (player_stats_df['AST'][i] != '') else None,
                steals=player_stats_df['STL'][i] if (player_stats_df['STL'][i] != 'DNP')
                                                    and (player_stats_df['STL'][i] != '') else None,
                blocks=player_stats_df['BLK'][i] if (player_stats_df['BLK'][i] != 'DNP')
                                                    and (player_stats_df['BLK'][i] != '') else None,
                turnovers=player_stats_df['TOV'][i] if (player_stats_df['TOV'][i] != 'DNP')
                                                       and (player_stats_df['TOV'][i] != '') else None,
                personal_fouls=player_stats_df['PF'][i] if (player_stats_df['PF'][i] != 'DNP')
                                                           and (player_stats_df['PF'][i] != '') else None,
                points=player_stats_df['PTS'][i] if (player_stats_df['PTS'][i] != 'DNP')
                                                    and (player_stats_df['PTS'][i] != '') else None
            )
            session.add(player_stats)


def add_game_teams(session: Session, scraper: Scraper, game: Game, home_team: str, away_team: str) -> None:
    """
    Adds the away and home team's game data to game_team database table.
    :param session: SQLAlchemy Session
    :param scraper: Scraper Object
    :param game: Related game
    :param home_team: Home team of the game.
    :param away_team: Away team of the game
    :return: None
    """
    game_summary, home_box, away_box = scraper.scrape_nba_match(game.game_code)
    # Game Summary headers: Team | 1 | 2 | 3 | 4 | (OT) | T | Pace | eFG% | TOV% | ORB% | FT/FGA | ORtg

    home_box_team_stats = home_box.iloc[-1]
    home_team_game_summary = game_summary.iloc[1]
    away_box_team_stats = away_box.iloc[-1]
    away_team_game_summary = game_summary.iloc[0]

    game_home_team = GameTeam(
        game_id=game.id,
        team_id=session.query(Team.id).filter(Team.name == home_team).scalar_subquery(),
        team_home_away_type=1
    )

    session.add(game_home_team)
    session.flush()

    add_game_team_log(session, game_home_team, home_team_game_summary, home_box_team_stats)

    for i in home_box.index[:-1]:
        player_name = home_box['Players'][i]
        player_code = home_box['Player Code'][i]
        player = session.query(Player).filter(
            Player.unique_code == player_code and Player.friendly_name == player_name).one_or_none()

        if player is None:
            player = add_player(session, player_name, player_code)
            add_player_team(session, player, game_home_team)

        add_game_player_log(session, home_box, i, player, game_home_team)

    game_away_team = GameTeam(
        game_id=game.id,
        team_id=session.query(Team.id).filter(Team.name == away_team).scalar_subquery(),
        team_home_away_type=2
    )
    session.add(game_away_team)
    session.flush()

    add_game_team_log(session, game_away_team, away_team_game_summary, away_box_team_stats)

    for i in away_box.index[:-1]:
        player_name = away_box['Players'][i]
        player_code = away_box['Player Code'][i]
        player = session.query(Player).filter(
            Player.unique_code == player_code and Player.friendly_name == player_name).one_or_none()

        if player is None:
            player = add_player(session, player_name, player_code)
            add_player_team(session, player, game_away_team)

        add_game_player_log(session, away_box, i, player, game_away_team)


def add_game_team_log(session: Session, game_team: GameTeam, game_summary: pd.DataFrame, team_box_stats: pd.DataFrame):
    """
    Adds a team's game log to the game_team_log database table.
    :param session: SQLAlchemy Session
    :param game_team: Related GameTeam object
    :param game_summary: Team's statistics dataframe.
    :param team_box_stats: Team's box score dataframe.
    :return:
    """
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
    session.add(gtl)


def add_player(session: Session, player_name: str, player_code: str) -> Player:
    """
    Add a player to the player database table.
    :param session: SQLAlchemy Session.
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

    session.add(player)
    session.flush()

    return player


def add_player_team(session: Session, player: Player, game_team) -> None:
    """
    Add a player-team relationship to the player_team database table.
    :param session: SQLAlchemy Session
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
    session.add(player_team)


def add_game_player_log(session: Session, box_df: pd.DataFrame, i: int, player: Player, game_team: GameTeam) -> None:
    """
    Add a player's game log to the game_player_log database table.
    :param session: SQLAlchemy Session
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
    session.add(game_player_log)


def add_game(session: Session, scraper: Scraper, schedule: pd.DataFrame, i: int, season: Season) -> Game:
    """
    Add a game to the game database table.
    :param session: SQLAlchemy Session
    :param scraper: Scraper object
    :param schedule: Schedule dataframe.
    :param i: Index to look at
    :param season: Related Season object.
    :return: Newly created Game object.
    """
    # Create game object
    game_datetime = scraper.to_postgres_datetime(schedule['Date'][i], schedule['Start (ET)'][i])
    home_team = schedule['Home/Neutral'][i]
    away_team = schedule['Visitor/Neutral'][i]
    game_code = scraper.get_game_code(schedule['Date'][i], home_team)

    # TODO: (#3) Correct assignment of game types.
    game = Game(
        season_id=season.id,
        type=2,  # 2: regular season
        start_datetime=game_datetime,
        game_code=game_code
    )
    session.add(game)
    session.flush()
    return game


def to_postgres_timestamp(date_string: str) -> str:
    """
    Convert a date_string to the postgres date.
    :param date_string: Python datetime object.
    :return: string in Postgres format.
    """
    # Convert the input string to a datetime object
    date_obj = datetime.strptime(date_string, '%a, %b %d, %Y')

    # Convert the datetime object to the PostgreSQL timestamp format
    postgres_timestamp = date_obj.strftime('%Y-%m-%d %H:%M:%S')

    return postgres_timestamp
