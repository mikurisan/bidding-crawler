from sqlmodel import create_engine, Session
from typing import Optional

import os

class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls, database_url: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, database_url: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        db_url = os.getenv('DATABASE_URL') or database_url
        if db_url is None:
            raise ValueError(
                "Database URL must be provided either through DATABASE_URL "
                "environment variable or database_url parameter"
            )
            
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self._initialized = True
    
    def create_session(self) -> Session:
        return Session(self.engine)

db_manager = DatabaseManager("mysql+pymysql://root:Jaka2022!@172.30.1.196:3306/test?charset=utf8mb4")