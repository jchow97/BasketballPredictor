from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.database_utils import DatabaseService
from scripts.Scraper import Scraper

username = 'jeffreychow'
port = '5432'
database = 'nba_dev'


def main():
    engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:{port}/{database}')
    session = Session(engine)
    scraper = Scraper()
    db_service = DatabaseService(session, scraper)

    db_service.initialize_database()
    db_service.populate_tables(2022)


if __name__ == "__main__":
    main()
