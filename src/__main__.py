from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from DatabaseClasses import initialize_database, database, populate_tables
from scripts.Scraper import Scraper


def main():
    engine = create_engine(f'postgresql+psycopg2://jeffreychow:@localhost:5432/{database}')
    session = Session(engine)
    scraper = Scraper()

    initialize_database()
    populate_tables(2022, session, scraper)


if __name__ == "__main__":
    main()
