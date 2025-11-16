import os
import json
from contextlib import contextmanager
from google.cloud import bigquery
from google.oauth2 import service_account
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_engine = None
_session_maker = None

def get_engine():
    global _engine
    if _engine is None:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        
        if not credentials_path or not project_id:
            raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CLOUD_PROJECT_ID")
        
        with open(credentials_path, 'r') as f:
            credentials_info = json.load(f)
        
        connection_string = f"bigquery://{project_id}"
        
        _engine = create_engine(
            connection_string,
            credentials_info=credentials_info,
            echo=False
        )
    
    return _engine

@contextmanager
def get_session():
    global _session_maker
    if _session_maker is None:
        engine = get_engine()
        _session_maker = sessionmaker(bind=engine)
    
    session = _session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_bigquery_client():
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    
    if not credentials_path:
        raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS")
    
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    return bigquery.Client(credentials=credentials, project=project_id)
