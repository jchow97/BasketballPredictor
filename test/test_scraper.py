import unittest

from scripts.Scraper import Scraper


class TestScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.test_scraper = Scraper()
        self.arbitrary_season_year = '2000'

    def test_scrape_nba_match(self):
        self.test_scraper.scrape_nba_match('202204120BRK',
                                           'https://www.basketball-reference.com/boxscores/202204120BRK.html')

    def test_scrape_nba_player(self):
        self.test_scraper.scrape_nba_player('bambamo01',
                                            'https://www.basketball-reference.com/players/b/bambamo01.html')


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
