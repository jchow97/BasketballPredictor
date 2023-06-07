from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.database_utils import initialize_database, populate_tables
from models.database import username, database
from scripts.Scraper import Scraper


def main():
    engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:5432/{database}')
    session = Session(engine)
    scraper = Scraper()

    initialize_database()
    populate_tables(session, scraper, 2022)


if __name__ == "__main__":
    main()
