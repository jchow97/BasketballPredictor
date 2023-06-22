from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, DECIMAL
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Game(Base):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("season.id", name='fk_game_season_id'))
    type = Column(Integer, ForeignKey("game_type.id", name='fk_game_game_type_id'))
    start_datetime = Column(DateTime)
    game_code = Column(String)
    home_team_id = Column(Integer, ForeignKey("team.id", name='fk_game_home_team_id'))
    away_team_id = Column(Integer, ForeignKey("team.id", name='fk_game_away_team_id'))
    spread = Column(DECIMAL)
    odds = Column(DECIMAL)
    money_line_odds = Column(DECIMAL)
    over_under_odds = Column(DECIMAL)


class GamePlayerLog(Base):
    __tablename__ = "game_player_log"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id", name='fk_game_player_player_id'))
    game_id = Column(Integer, ForeignKey("game.id", name='fk_game_player_game_id'))

    minutes_played = Column(String, default=None)
    field_goals = Column(Integer, default=None)
    field_goal_attempts = Column(Integer, default=None)
    field_goal_pct = Column(DECIMAL, default=None)
    three_pointers = Column(Integer, default=None)
    three_point_attempts = Column(Integer, default=None)
    three_point_pct = Column(DECIMAL, default=None)
    free_throws = Column(Integer, default=None)
    free_throw_attempts = Column(Integer, default=None)
    free_throw_pct = Column(DECIMAL, default=None)
    offensive_rebounds = Column(Integer, default=None)
    defensive_rebounds = Column(Integer, default=None)
    total_rebounds = Column(Integer, default=None)
    assists = Column(Integer, default=None)
    steals = Column(Integer, default=None)
    blocks = Column(Integer, default=None)
    turnovers = Column(Integer, default=None)
    personal_fouls = Column(Integer, default=None)
    points = Column(Integer, default=None)
    plus_minus = Column(Integer, default=None)
    true_shooting_pct = Column(DECIMAL, default=None)
    effective_field_goal_pct = Column(DECIMAL, default=None)
    three_point_attempt_rate = Column(DECIMAL, default=None)
    free_throw_attempt_rate = Column(DECIMAL, default=None)
    offensive_rebound_pct = Column(DECIMAL, default=None)
    defensive_rebound_pct = Column(DECIMAL, default=None)
    total_rebound_pct = Column(DECIMAL, default=None)
    assist_pct = Column(DECIMAL, default=None)
    steal_pct = Column(DECIMAL, default=None)
    block_pct = Column(DECIMAL, default=None)
    turnover_pct = Column(DECIMAL, default=None)
    usage_pct = Column(DECIMAL, default=None)
    offensive_rating = Column(DECIMAL, default=None)
    defensive_rating = Column(DECIMAL, default=None)
    box_plus_minus = Column(DECIMAL, default=None)


class GameTeamLog(Base):
    __tablename__ = "game_team_log"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("game.id", name='fk_game_team_log_game_id'))
    team_id = Column(Integer, ForeignKey("team.id", name='fk_game_team_log_team_id'))

    total_points = Column(Integer)
    first_quarter_points = Column(Integer)
    second_quarter_points = Column(Integer)
    third_quarter_points = Column(Integer)
    fourth_quarter_points = Column(Integer)
    overtime_points = Column(
        String)  # going to store a list of = Column(Integer)s, then we can store infinite overtime_points

    minutes_played = Column(String(6))
    field_goals = Column(Integer)
    field_goal_attempts = Column(Integer)
    field_goal_pct = Column(DECIMAL)
    three_pointers = Column(Integer)
    three_point_attempts = Column(Integer)
    three_point_pct = Column(DECIMAL)
    free_throws = Column(Integer)
    free_throw_attempts = Column(Integer)
    free_throw_pct = Column(DECIMAL)
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)
    total_rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    personal_fouls = Column(Integer)
    points = Column(Integer)
    plus_minus = Column(Integer)

    true_shooting_pct = Column(DECIMAL)
    effective_field_goal_pct = Column(DECIMAL)
    three_point_attempt_rate = Column(DECIMAL)
    free_throw_attempt_rate = Column(DECIMAL)
    offensive_rebound_pct = Column(DECIMAL)
    defensive_rebound_pct = Column(DECIMAL)
    total_rebound_pct = Column(DECIMAL)
    assist_pct = Column(DECIMAL)
    steal_pct = Column(DECIMAL)
    block_pct = Column(DECIMAL)
    turnover_pct = Column(DECIMAL)
    usage_pct = Column(DECIMAL)
    offensive_rating = Column(DECIMAL)
    defensive_rating = Column(DECIMAL)
    box_plus_minus = Column(DECIMAL)
    pace = Column(DECIMAL)
    free_throws_per_field_goal_attempt = Column(DECIMAL)


class GameType(Base):
    __tablename__ = "game_type"

    id = Column(Integer, primary_key=True)
    type = Column(String)


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    unique_code = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    friendly_name = Column(String)
    birth_date = Column(DateTime)


class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id", name='fk_player_stats_player_id'))
    type = Column(Integer, ForeignKey("player_stats_type.id", name='fk_player_stats_player_stats_type_id'))
    season = Column(String)
    age = Column(Integer, default=None)

    games_played = Column(Integer, default=None)
    games_started = Column(Integer, default=None)
    minutes_played = Column(String, default=None)
    field_goals = Column(DECIMAL, default=None)
    field_goal_attempts = Column(DECIMAL, default=None)
    field_goal_pct = Column(DECIMAL, default=None)
    three_pointers = Column(DECIMAL, default=None)
    three_point_attempts = Column(DECIMAL, default=None)
    three_point_pct = Column(DECIMAL, default=None)
    two_pointers = Column(DECIMAL, default=None)
    two_point_attempts = Column(DECIMAL, default=None)
    two_point_pct = Column(DECIMAL, default=None)
    effective_field_goal_pct = Column(DECIMAL, default=None)
    free_throws = Column(DECIMAL, default=None)
    free_throw_attempts = Column(DECIMAL, default=None)
    free_throw_pct = Column(DECIMAL, default=None)
    offensive_rebounds = Column(DECIMAL, default=None)
    defensive_rebounds = Column(DECIMAL, default=None)
    total_rebounds = Column(DECIMAL, default=None)
    assists = Column(DECIMAL, default=None)
    steals = Column(DECIMAL, default=None)
    blocks = Column(DECIMAL, default=None)
    turnovers = Column(DECIMAL, default=None)
    personal_fouls = Column(DECIMAL, default=None)
    points = Column(DECIMAL, default=None)


class PlayerStatsType(Base):
    __tablename__ = "player_stats_type"

    id = Column(Integer, primary_key=True)
    type = Column(String)


class PlayerTeam(Base):
    __tablename__ = "player_team"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id", name='fk_player_team_player_id'))
    team_id = Column(Integer, ForeignKey("team.id", name='fk_player_team_team_id'))
    start_date = Column(DateTime)
    end_date = Column(DateTime)


class Season(Base):
    __tablename__ = "season"

    id = Column(Integer, primary_key=True)
    year = Column(String(4))
    friendly_name = Column(String)
    preseason_start = Column(DateTime)
    preseason_end = Column(DateTime)
    season_start = Column(DateTime)
    season_end = Column(DateTime)
    playoffs_start = Column(DateTime)
    playoffs_end = Column(DateTime)


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("season.id", name='fk_team_season_id'))
    team_stats_id = Column(Integer, ForeignKey("team_stats.id", name='fk_team_team_stats_id'))
    team_advanced_stats_id = Column(Integer, ForeignKey("team_advanced_stats.id",
                                                        name='fk_team_team_advanced_stats_id'))
    name = Column(String)
    abbreviation = Column(String(3))
    friendly_name = Column(String)

    wins = Column(Integer)
    losses = Column(Integer)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    streak = Column(Integer)
    last_ten_wins = Column(Integer)
    last_ten_losses = Column(Integer)

    ats_wins = Column(Integer)
    ats_losses = Column(Integer)
    ats_ties = Column(Integer)
    ats_home_wins = Column(Integer)
    ats_home_losses = Column(Integer)
    ats_home_ties = Column(Integer)
    ats_away_wins = Column(Integer)
    ats_away_losses = Column(Integer)
    ats_away_ties = Column(Integer)


class TeamStats(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id", name='fk_team_stats_team_id'))
    type = Column(Integer, ForeignKey("team_stats_type.id", name='fk_team_stats_team_stats_type_id'))
    minutes_played = Column(String(6))
    field_goals = Column(DECIMAL)
    field_goal_attempts = Column(DECIMAL)
    three_pointers = Column(DECIMAL)
    three_point_attempts = Column(DECIMAL)
    three_point_pct = Column(DECIMAL)
    two_pointers = Column(DECIMAL)
    two_point_attempts = Column(DECIMAL)
    two_point_pct = Column(DECIMAL)
    free_throws = Column(DECIMAL)
    free_throw_attempts = Column(DECIMAL)
    free_throw_pct = Column(DECIMAL)
    offensive_rebounds = Column(DECIMAL)
    defensive_rebounds = Column(DECIMAL)
    total_rebounds = Column(DECIMAL)
    assists = Column(DECIMAL)
    steals = Column(DECIMAL)
    blocks = Column(DECIMAL)
    turnovers = Column(DECIMAL)
    personal_fouls = Column(DECIMAL)
    points = Column(DECIMAL)


class TeamStatsType(Base):
    __tablename__ = "team_stats_type"

    id = Column(Integer, primary_key=True)
    type = Column(String)


class TeamAdvancedStats(Base):
    __tablename__ = "team_advanced_stats"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id", name='fk_team_advanced_stats_team_id'))
    wins = Column(Integer)
    losses = Column(Integer)
    pythagorean_wins = Column(Integer)
    pythagorean_losses = Column(Integer)
    margin_of_victory = Column(DECIMAL)
    strength_of_schedule = Column(DECIMAL)
    simple_rating_system = Column(DECIMAL)
    offensive_rating = Column(DECIMAL)
    defensive_rating = Column(DECIMAL)
    pace = Column(DECIMAL)
    free_throw_attempt_rate = Column(DECIMAL)
    three_point_attempt_rate = Column(DECIMAL)
    effective_field_goal_pct = Column(DECIMAL)
    turnover_pct = Column(DECIMAL)
    offensive_rebound_pct = Column(DECIMAL)
    free_throws_per_field_goal_attempt = Column(DECIMAL)
    opponent_effective_field_goal_pct = Column(DECIMAL)
    opponent_turnover_pct = Column(DECIMAL)
    defensive_rebound_pct = Column(DECIMAL)
    defensive_free_throws_per_field_goal_attempt = Column(DECIMAL)
    arena = Column(String)
    attendance = Column(String)
