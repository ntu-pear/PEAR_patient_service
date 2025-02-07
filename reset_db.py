# reset_db.py
from app.database import SessionLocal, engine
from sqlalchemy.orm import close_all_sessions

print("Resetting SQLAlchemy sessions and engine...")

# Close all active SQLAlchemy sessions
close_all_sessions()

# Dispose the engine to clear cached connections
engine.dispose()

print("Database session and engine cache cleared.")
