from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    uploads = relationship("ImageUpload", back_populates="patient")

class ImageUpload(Base):
    __tablename__ = 'image_uploads'

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, ForeignKey('patients.id'))
    image_path = Column(String, nullable=False)
    image_type = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='pending')
    analysis_result = Column(JSON)
    
    patient = relationship("Patient", back_populates="uploads")

class TrainingMetrics(Base):
    __tablename__ = 'training_metrics'

    id = Column(Integer, primary_key=True)
    round = Column(Integer)
    client_id = Column(String)
    accuracy = Column(Float)
    loss = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metrics = Column(JSON)

class GlobalModel(Base):
    __tablename__ = 'global_models'

    id = Column(Integer, primary_key=True)
    round = Column(Integer)
    model_path = Column(String)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(db_url: str = 'sqlite:///medai.db'):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def get_db_session(db_url: str = 'sqlite:///medai.db'):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()