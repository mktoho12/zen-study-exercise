"""HTTP client for ZEN Study API."""

import sys
import time
from typing import Any

import httpx

from .config import Config


class ZenStudyClient:
    """HTTP client for ZEN Study API and page requests."""

    def __init__(self):
        """Initialize the client."""
        self.session_cookie = Config.get_cookie_header()
        self.client = httpx.Client(
            headers={"Cookie": self.session_cookie},
            timeout=30.0,
            follow_redirects=True,
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.client.close()

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """Handle response and check for authentication errors.

        Args:
            response: HTTP response

        Returns:
            Response if successful

        Raises:
            SystemExit: If authentication fails
        """
        if response.status_code in (401, 403):
            print("\nエラー: 認証に失敗しました。")
            print("セッションCookieの有効期限が切れている可能性があります。")
            print("ブラウザのDevToolsから新しいセッションCookieを取得して、")
            print("環境変数 ZANE_SESSION を更新してください。")
            sys.exit(1)

        response.raise_for_status()
        return response

    def get_my_courses(self, limit: int = 20, offset: int = 0) -> dict[str, Any]:
        """Get list of courses the user is enrolled in.

        Args:
            limit: Number of courses to fetch
            offset: Offset for pagination

        Returns:
            API response as dictionary
        """
        url = f"{Config.API_BASE_URL}/v3/dashboard/my_courses"
        params = {"service": Config.SERVICE, "limit": limit, "offset": offset}

        response = self.client.get(url, params=params)
        self._handle_response(response)
        time.sleep(Config.REQUEST_DELAY)

        return response.json()

    def get_course_info(self, course_id: int) -> dict[str, Any]:
        """Get course information including chapter list.

        Args:
            course_id: Course ID

        Returns:
            API response as dictionary
        """
        url = f"{Config.API_BASE_URL}/v2/material/courses/{course_id}"
        params = {"revision": 1}

        response = self.client.get(url, params=params)
        self._handle_response(response)
        time.sleep(Config.REQUEST_DELAY)

        return response.json()

    def get_chapter_info(self, course_id: int, chapter_id: int) -> dict[str, Any]:
        """Get chapter information including section list.

        Args:
            course_id: Course ID
            chapter_id: Chapter ID

        Returns:
            API response as dictionary
        """
        url = f"{Config.API_BASE_URL}/v2/material/courses/{course_id}/chapters/{chapter_id}"
        params = {"revision": 1}

        response = self.client.get(url, params=params)
        self._handle_response(response)
        time.sleep(Config.REQUEST_DELAY)

        return response.json()

    def get_exercise_html(self, exercise_url: str) -> str:
        """Get exercise HTML page.

        Args:
            exercise_url: Exercise URL (with /result removed if present)

        Returns:
            HTML content as string
        """
        response = self.client.get(exercise_url)
        self._handle_response(response)
        time.sleep(Config.REQUEST_DELAY)

        return response.text
