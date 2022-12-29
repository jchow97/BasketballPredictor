class team:

    def __init__(self):
        id = None
        season_id = None
        team_stats_id = None
        team_advanced_stats_id = None
        team_name = None
        friendly_name = None
        
        # records
        wins = None
        losses = None
        home_wins = None
        home_losses = None
        away_wins = None
        away_losses = None
        streak = None
        last_ten_wins = None
        last_ten_losses = None
        
        # more betting-related info (nullable, for future use)
        ats_wins = None
        ats_losses = None
        ats_ties = None
        ats_home_wins = None
        ats_home_losses = None
        ats_home_ties = None
        ats_away_wins = None
        ats_away_losses = None
        ats_away_ties = None