from kafka import KafkaProducer
from youtube_comment_downloader import YoutubeCommentDownloader
from yt_dlp import YoutubeDL
import json
import time

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# List of video IDs
VIDEO_IDS = [
    "1HRPIlg0QIk",
    "NeG9Ps0mS0Y",
    "JyzGus2bB08",
    "-Vot0XL0If8",
    "w8xPMD8ubOE",
    "g9fN4fSTS7o",
    "quaTx38WnZ8",
]

# Initialize downloader
downloader = YoutubeCommentDownloader()
sent_ids = set()  # avoid sending same comment again

# Function to fetch video info (title, publish date, views, likes)
def get_video_info(video_id):
    ydl_opts = {}
    url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", ""),
            "published_at": info.get("upload_date", ""),
            "view_count": info.get("view_count", 0),
            "like_count": info.get("like_count", 0),
        }

# Function to stream comments and send to Kafka
def stream_comments(video_id, video_info):
    comments = downloader.get_comments_from_url(f"https://www.youtube.com/watch?v={video_id}")
    for comment in comments:
        if comment["cid"] not in sent_ids:
            sent_ids.add(comment["cid"])
            data = {
                "video_id": video_id,
                "title": video_info["title"],
                "published_at": video_info["published_at"],
                "view_count": video_info["view_count"],
                "likes": video_info["like_count"],
                "comment_text": comment["text"]
            }
            print(f"📤 Sending to Kafka: {data}")
            producer.send("youtube-comments", value=data)
            time.sleep(1)  # wait a bit between sends

# Main loop
while True:
    for video_id in VIDEO_IDS:
        print(f"🔁 Fetching new comments from video: {video_id}")
        # Fetch video metadata
        video_info = get_video_info(video_id)
        # Stream comments
        stream_comments(video_id, video_info)
        time.sleep(10)  # wait 10 seconds between videos
