# Import libraries
from sqlmodel import create_engine

# Create SQLite database file
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)