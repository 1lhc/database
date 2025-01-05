# Description: This file contains the configuration for the application. 
# It sets the database URI, API key, and the number of items per page.
import os

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "with_amendments.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY', 'default_key')
    REQUIRE_API_KEY = os.environ.get('REQUIRE_API_KEY', 'False').lower() == 'true'
    ITEMS_PER_PAGE = 20