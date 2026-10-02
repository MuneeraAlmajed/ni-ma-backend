from sqlalchemy.orm import sessionmaker, Session
from data.user_data import user_list
from config.environment import DATABASE_URL
from sqlalchemy import create_engine
from models.base import Base

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

try:
    print("Recreating database...")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("seeding the database...")

    db = SessionLocal()

    db.add_all(user_list)
    db.commit()

    db.close()

    print("Database seeding complete! 👋")
except Exception as e:
    print("An error occurred:", e)