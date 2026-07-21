"""
Handles YouTube OAuth authentication and uploads a finished video
with title, description, and tags.
"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_FILE = "token.pickle"


def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secret_file = os.getenv("YOUTUBE_CLIENT_SECRET_FILE")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            # Runs a local server for one-time browser OAuth consent (do this once manually).
            # access_type=offline + prompt=consent ensures a refresh_token is issued so
            # this keeps working unattended in GitHub Actions without re-login.
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, title: str, description: str, tags: list,
                  category_id: str = "22", privacy_status: str = "public") -> str:
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Uploaded: https://youtube.com/watch?v={video_id}")
    return video_id


def set_thumbnail(video_id: str, thumbnail_path: str) -> bool:
    """
    Uploads a custom thumbnail for the given video.
    NOTE: This requires the YouTube channel to be phone-verified.
    If not verified, this will fail - the pipeline should catch that
    and continue without stopping the whole run.
    """
    youtube = get_authenticated_service()
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("Custom thumbnail set successfully.")
        return True
    except Exception as e:
        print(f"Could not set custom thumbnail (channel may need phone verification): {e}")
        return False


def post_engagement_comment(video_id: str, comment_text: str) -> bool:
    """
    Posts a comment on the video (e.g. an engaging question) to help
    kickstart the comment section. NOTE: Programmatically pinning a
    comment isn't reliably supported via the public API for all
    channels - go to YouTube Studio and manually pin this comment
    (it will be the newest one, posted by you) for best effect.
    """
    youtube = get_authenticated_service()
    try:
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {"textOriginal": comment_text}
                    }
                }
            }
        ).execute()
        print("Engagement comment posted (pin it manually in YouTube Studio for best effect).")
        return True
    except Exception as e:
        print(f"Could not post comment: {e}")
        return False
