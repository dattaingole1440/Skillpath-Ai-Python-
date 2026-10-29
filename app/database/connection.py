import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Determine runtime directory for persistent SQLite database
if getattr(sys, 'frozen', False):
    DB_DIR = os.path.dirname(sys.executable)
    env_in_exe = os.path.join(DB_DIR, ".env")
    if os.path.exists(env_in_exe):
        load_dotenv(env_in_exe)
else:
    DB_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sqlite_file = os.path.join(DB_DIR, "skillpath_ai.db").replace("\\", "/")
default_sqlite_url = f"sqlite:///{sqlite_file}"

# Use configured DATABASE_URL (MySQL/PostgreSQL) if set; automatically falls back to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", default_sqlite_url)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to database with retry mechanism (ensures MySQL is ready after computer/server restart)
MAX_RETRIES = 5
RETRY_DELAY = 2

engine = None
connected = False

for attempt in range(1, MAX_RETRIES + 1):
    try:
        masked_url = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL
        logger.info(f"[DATABASE] Connecting to database (attempt {attempt}/{MAX_RETRIES}): {masked_url}")
        test_engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {"connect_timeout": 10},
            **({"pool_size": 10, "max_overflow": 20} if not DATABASE_URL.startswith("sqlite") else {})
        )
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        connected = True
        logger.info(f"[DATABASE] Connected successfully to {'MySQL (Single Source of Truth)' if 'mysql' in DATABASE_URL else 'Database'}")
        break
    except Exception as e:
        logger.warning(f"[DATABASE] Connection attempt {attempt} failed: {e}")
        if attempt < MAX_RETRIES:
            import time
            time.sleep(RETRY_DELAY)

if not connected:
    if DATABASE_URL != default_sqlite_url:
        logger.error("[DATABASE] Could not connect to primary MySQL after retries. Falling back to SQLite.")
        DATABASE_URL = default_sqlite_url
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        raise RuntimeError("Could not connect to database.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def sync_db_schema(bind_engine, base):
    """
    Ensures existing database tables are synchronized with SQLAlchemy models
    by automatically adding any missing columns without dropping data.
    """
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(bind_engine)
        existing_tables = set(inspector.get_table_names())
        
        with bind_engine.connect() as conn:
            for table_name, table in base.metadata.tables.items():
                if table_name in existing_tables:
                    existing_cols = {c['name'] for c in inspector.get_columns(table_name)}
                    for col in table.columns:
                        if col.name not in existing_cols:
                            col_type = str(col.type.compile(bind_engine.dialect))
                            nullable = 'NULL' if col.nullable else 'NOT NULL'
                            sql = f'ALTER TABLE `{table_name}` ADD COLUMN `{col.name}` {col_type} {nullable}'
                            try:
                                conn.execute(text(sql))
                                conn.commit()
                                logger.info(f"Successfully added missing column '{col.name}' to '{table_name}'.")
                            except Exception as ex:
                                logger.warning(f"Could not auto-add column '{col.name}' to '{table_name}': {ex}")

            # Ensure any NULL is_deleted flags default to 0 (active)
            for tbl in ["careers", "roadmaps", "topics", "videos", "quizzes", "questions", "coding_challenges"]:
                if tbl in existing_tables:
                    try:
                        conn.execute(text(f"UPDATE `{tbl}` SET `is_deleted` = 0 WHERE `is_deleted` IS NULL"))
                        conn.commit()
                    except Exception:
                        pass
    except Exception as e:
        logger.warning(f"Database schema sync warning: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


