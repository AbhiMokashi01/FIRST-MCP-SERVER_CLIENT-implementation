import os
import requests

from dotenv import load_dotenv
from tavily import TavilyClient

from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Read-only access to calendar events
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.readonly"
]


def tavily_search(query:str)->list[dict]:
    """Searchs and provides results on the query"""
    if not query.strip():
        raise ValueError("query cannot be empty")

    tavily_search_api_key=os.getenv("TAVILY_API_KEY")

    if not tavily_search_api_key:
        raise ValueError("API KEY IS NOT PASSED")

    client=TavilyClient(api_key=tavily_search_api_key)

    response=client.search(query=query,max_results=3)

    results = []
    

    for item in response.get("results", []):
        results.append({
            "title": item["title"],
            "summary": item["content"],
            "url": item["url"]
        })

    return results


def find_tutorials(query:str)->list[dict]:
    if not query.strip():
        raise ValueError("query cannoty be empty")

    yt_api_key=os.getenv("YOUTUBE_API_KEY")

    if not yt_api_key:
        raise ValueError("YOUTUBE API KEY NOT FOUND")

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 3,
        "key": yt_api_key
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    tutorials = []

    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")

        if not video_id:
            continue

        tutorials.append({
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })

    return tutorials



BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_calendar_credentials():
    """Retrun calender authentication"""
    creds = None

    # 1. Load previously authorized credentials
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    # 2. Refresh or request authorization
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # 3. Save credentials for future runs
        TOKEN_FILE.write_text(
            creds.to_json(),
            encoding="utf-8"
        )

    return creds


def list_upcoming_events() -> list[dict]:
    """Return the next 5 events from the primary Google Calendar."""

    creds = get_calendar_credentials()

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    now = datetime.now(timezone.utc).isoformat()

    try:
        response = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=5,
                singleEvents=True,
                orderBy="startTime"
            )
            .execute()
        )
    except HttpError as error:
        raise RuntimeError(
            f"Google Calendar API error: HTTP {error.resp.status}"
        ) from error

    events = response.get("items", [])

    results = []

    for event in events:
        start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        results.append({
            "title": event.get("summary", "Untitled event"),
            "start": start
        })

    return results




if __name__ == "__main__":

    print("Testing Tavily Search")
    results = tavily_search("Python decorators")

    for result in results:
        print(result)

    print("\nTesting YouTube API")
    videos = find_tutorials("Python decorators tutorial")

    for video in videos:
        print(video)