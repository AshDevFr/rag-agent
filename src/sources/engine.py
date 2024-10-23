import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()

port = ""
if os.environ.get("POSTGRES_PORT") and os.environ.get("POSTGRES_PORT") != "":
    port = f":{os.environ.get('POSTGRES_PORT')}"

connection = f"postgresql+psycopg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}{port}/{os.environ.get("POSTGRES_DB")}"  # Uses psycopg3!
engine = create_engine(connection)


def get_new_session():
    return Session(engine)
