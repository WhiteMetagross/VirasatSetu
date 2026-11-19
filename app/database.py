import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

db_url = settings.DATABASE_URL

# Check if running in a serverless environment like Vercel or read only filesystem
is_serverless = bool(
    os.environ.get("VERCEL")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    or not os.access(".", os.W_OK)
)

if is_serverless and db_url.startswith("sqlite"):
    tmp_db_path = "/tmp/virasat_setu.db"
    if not os.path.exists(tmp_db_path):
        # Look for pre-seeded database bundle candidates
        candidates = [
            os.path.join(os.getcwd(), "virasat_setu.db"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "virasat_setu.db"),
            "/var/task/virasat_setu.db",
        ]
        for candidate in candidates:
            if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
                try:
                    shutil.copy2(candidate, tmp_db_path)
                    break
                except Exception:
                    pass
    db_url = f"sqlite:///{tmp_db_path}"

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()

