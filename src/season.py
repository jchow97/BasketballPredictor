"""
Class for NBA Season object.
"""
class season:
    year = None
    friendly_name = None
    preseason_start = None
    preseason_end = None
    season_start = None
    season_end = None
    playoffs_start = None
    playoffs_end = None

    def __init__(self, year):
        self.year = year
        self.friendly_name = f"{year - 1}-{year} NBA Season"
        self.preseason_start = None
        self.preseason_end = None
        self.season_start = None
        self.season_end = None
        self.playoffs_start = None
        self.playoffs_end = None
