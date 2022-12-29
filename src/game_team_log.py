class game_team_log:

    def __init__(self):
        id = None
        game_team_id = None

        # game summary stats
        total_points = None
        first_quarter_points = None
        second_quarter_points = None
        third_quarter_points = None
        fourth_quarter_points = None
        overtime_points = None # going to store a list of = Nones, then we can store infinite overtime_points

        # basic box score stats
        minutes_played = None
        field_goals = None
        field_goal_attempts = None
        field_goal_pct = None
        three_pointers = None
        three_point_attempts = None
        three_point_pct = None
        free_throws = None
        free_throw_attempts = None
        free_throw_pct = None
        offensive_rebounds = None
        defensive_rebounds = None
        total_rebounds = None
        assists = None
        steals = None
        blocks = None
        turnovers = None
        personal_fouls = None
        points = None
        plus_minus = None

        # Advanced box score stats
        true_shooting_pct = None
        effective_field_goal_pct = None
        three_point_attempt_rate = None
        free_throw_attempt_rate = None
        offensive_rebound_pct = None
        defensive_rebound_pct = None
        total_rebound_pct = None
        assist_pct = None
        steal_pct = None
        block_pct = None
        turnover_pct = None
        usage_pct = None
        offensive_rating = None
        defensive_rating = None
        box_plus_minus = None
        pace = None
        free_throws_per_field_goal_attempt = None