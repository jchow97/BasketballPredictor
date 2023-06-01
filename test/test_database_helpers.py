import unittest

from DatabaseClasses import to_postgres_timestamp


class TestDatabaseHelpers(unittest.TestCase):

    def test_to_postgres_timestamp(self):
        test_date_string = 'Tue, Oct 19, 2021'
        assert(to_postgres_timestamp(test_date_string), '2021-10-19 00:00:00')


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
