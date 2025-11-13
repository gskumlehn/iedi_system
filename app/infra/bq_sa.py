import os
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
        project_id = os.getenv("GCP_PROJECT_ID")
        
        if not credentials_path or not project_id:
            raise ValueError("Missing GCP credentials or project ID")
        
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        connection_string = f"bigquery://{project_id}"
        
        _engine = create_engine(
            connection_string,
            credentials_info=credentials,
            echo=False
        )
    
    return _engine

def get_session():
    global _session_maker
    if _session_maker is None:
        engine = get_engine()
        _session_maker = sessionmaker(bind=engine)
    
    return _session_maker()

def get_bigquery_client():
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    return bigquery.Client(credentials=credentials)
