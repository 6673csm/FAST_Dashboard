"""
FAST Dashboard - FastAPI Backend
database.py: SQLAlchemy SQLite setup
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone

DATABASE_URL = "sqlite:///./fast_dashboard.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── ORM Models ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete")
    trained_models = relationship("TrainedModel", back_populates="owner", cascade="all, delete")


class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(200))
    data_json = Column(Text)       # CSV data stored as JSON string
    metadata_json = Column(Text)   # Metadata dict as JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="datasets")
    models = relationship("TrainedModel", back_populates="dataset", cascade="all, delete")


class TrainedModel(Base):
    __tablename__ = "trained_models"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    model_name = Column(String(100))
    target = Column(String(100))
    metrics_json = Column(Text)    # Evaluation metrics as JSON string
    model_path = Column(String(300))  # Path to saved joblib file
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="trained_models")
    dataset = relationship("Dataset", back_populates="models")


class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    forecast_json = Column(Text)   # Forecast results as JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_db():
    """Dependency injector for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
