import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///with_amendments.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY', 'default_key')
    ITEMS_PER_PAGE = 20