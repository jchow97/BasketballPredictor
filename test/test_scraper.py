import unittest

import pandas as pd

from scripts.Scraper import Scraper


class TestScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.test_scraper = Scraper()
        self.arbitrary_season_year = '2000'


    def test_scrape_nba_season_success(self):
        pass
        # TODO: Fix and add unit tests.
        self.assertEqual(self.test_scraper.scrape_nba_season(self.arbitrary_season_year,
                                                             'resources/2021-22_nba_schedule.html'), pd.DataFrame([0]))


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
