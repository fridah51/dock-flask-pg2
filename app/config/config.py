import os


class Development():
    # SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///alchemy.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    SECRET_KEY = '11ae8fcaceff9710e238b932'
    DEBUG = os.getenv("DEBUG")
    FLASK_APP = os.getenv("FLASK_APP")
    FLASK_ENV = os.getenv("FLASK_ENV")
    SECURITY_PASSWORD_SALT = 'my_precious_two'

  
 