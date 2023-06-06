from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from DatabaseClasses import initialize_database, database, populate_tables


def main():
    engine = create_engine(f'postgresql+psycopg2://jeffreychow:@localhost:5432/{database}')
    session = Session(engine)
    initialize_database()
    populate_tables(2022, session)


if __name__ == "__main__":
    main()
