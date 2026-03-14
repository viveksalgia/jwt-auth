"""
Centralized configuration management using Pydantic Settings.
All environment variables are loaded from .env file.
"""

from __future__ import annotations

import logging
import os

from pwdlib import PasswordHash

from dotenv import load_dotenv

import mariadb

# Load Environment variables from .env file for local development
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class Settings:
    """ A Simple class to hold environment settings """

    def __init__(self):
        # logging configs
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_level: int = getattr(logging, log_level_str, logging.INFO)

        self.db_host: str | None = os.getenv("DB_HOST")
        self.db_port: int = int(os.getenv("DB_PORT", "3306"))
        self.db_user: str | None = os.getenv("DB_USER")
        self.db_pass: str | None = os.getenv("DB_PASS")
        self.database: str | None = os.getenv("DATABASE")
        self.secret_key: str | None = os.getenv("SECRET_KEY")
        self.hashing_algo: str | None = os.getenv("ALGORITHM")
        self.token_expiry: int | None = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        self.passwordhash = PasswordHash.recommended()


        
    def get_mariadb_cursor(self):
        try:
            conn = mariadb.connect(
                user=self.db_user,
                password=self.db_pass,
                host=self.db_host,  # e.g., "localhost" or an IP address
                port=self.db_port,             # Default MariaDB port
                database=self.database,
                # Disable SSL for local development; enable in production with proper certificates
                ssl=False
            )
            return conn
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return e
            

# Singleton instance for settings
settings = Settings()
