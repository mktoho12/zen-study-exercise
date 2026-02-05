"""Configuration management for ZEN Study scraper."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration for ZEN Study API access."""

    # Base URLs
    API_BASE_URL = "https://api.nnn.ed.nico"
    PAGE_BASE_URL = "https://www.nnn.ed.nico"

    # Session cookie name
    SESSION_COOKIE_NAME = "_zane_session"

    # Authority value
    AUTHORITY = "zen_univ_student"

    # Service name
    SERVICE = "zen_univ"

    # Content type
    CONTENT_TYPE = "zen_univ"

    # Output directory
    OUTPUT_DIR = "output"
    OUTPUT_FILE = "exercises.json"

    # Rate limiting
    REQUEST_DELAY = 0.1  # seconds between requests

    @classmethod
    def get_session_cookie(cls) -> str:
        """Get session cookie from environment variable.

        Returns:
            Session cookie value

        Raises:
            SystemExit: If ZANE_SESSION environment variable is not set
        """
        session = os.environ.get("ZANE_SESSION")
        if not session:
            print("エラー: 環境変数 ZANE_SESSION が設定されていません。")
            print("以下のいずれかの方法で設定してください:")
            print('  1. .env ファイルに記載: ZANE_SESSION="your_session_cookie_value"')
            print('  2. 環境変数で設定: export ZANE_SESSION="your_session_cookie_value"')
            sys.exit(1)
        return session

    @classmethod
    def get_cookie_header(cls) -> str:
        """Get formatted Cookie header value.

        Returns:
            Cookie header string
        """
        session = cls.get_session_cookie()
        return f"{cls.SESSION_COOKIE_NAME}={session}; authority={cls.AUTHORITY}"
