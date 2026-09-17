from app.database import SessionLocal, Base, engine
from app import crud


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        crud.create_seed_users(db)
        crud.create_seed_data(db)
        print("Seed ejecutado correctamente")
    finally:
        db.close()
