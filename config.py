import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///with_amendments.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY', 'default_key')
    REQUIRE_API_KEY = os.environ.get('REQUIRE_API_KEY', 'False').lower() == 'true'
    ITEMS_PER_PAGE = 20