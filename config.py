import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret") 

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "another-dev-secret")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False              
    JWT_COOKIE_CSRF_PROTECT = True         
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  
    JWT_COOKIE_SAMESITE = "Lax"