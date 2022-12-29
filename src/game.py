class game:
    id = None
    season_id = None
    type = None
    start_datetime = None

    def __init__(self, id, season_id, type, start_datetime):
        self.id = id
        self.season_id = season_id
        self.type = type
        self.start_datetime = start_datetime
