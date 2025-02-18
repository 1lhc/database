# Description: This file contains the configuration for the application.
# It sets the database URI, API key, and the number of items per page.
import os

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "with_amendments.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLAlchemy engine options for connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 30,          # Number of persistent connections
    "max_overflow": 20,       # Additional temporary connections
    "pool_timeout": 60,       # Wait up to 60 seconds for a connection
    "pool_pre_ping": True     # Check connections for staleness
    }
    
    # API Key configuration
    API_KEY = os.environ.get('API_KEY', 'default_key')
    REQUIRE_API_KEY = os.environ.get('REQUIRE_API_KEY', 'False').lower() == 'true'
    
    # Pagination configuration
    ITEMS_PER_PAGE = 20