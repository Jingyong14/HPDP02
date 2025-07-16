from googleapiclient.discovery import build
import pandas as pd
import time
import os

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# === CONFIGURATION ===
API_KEY = os.getenv("YOUTUBE_API_KEY")  # Load from environment variable
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable not set. Please set your API key in the environment.")
KEYWORDS = ["malaysia obesity rise", "malaysia cancer", "malaysia lifestyle", "malaysia brawl case", "malaysia killing crime" ]
MAX_VIDEO_RESULTS = 20     # How many videos to fetch
MAX_COMMENTS_PER_VIDEO = 500  # Comments per video
CSV_FILE = "../data/youtube_comments2.csv"

# === YouTube API Client ===
youtube = build("youtube", "v3", developerKey=API_KEY)

def get_video_ids_by_keyword(query, max_results=20):
    print(f"🔍 Searching YouTube for: {query}")
    video_ids = []
    next_page_token = None

    while len(video_ids) < max_results:
        request = youtube.search().list(
            q=query,
            part="id",
            type="video",
            maxResults=min(50, max_results - len(video_ids)),
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            video_ids.append(item["id"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
        time.sleep(0.5)

    print(f"✅ Found {len(video_ids)} videos.")
    return video_ids

def get_comments(video_id, max_results=500):
    comments = []
    next_page_token = None

    while len(comments) < max_results:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_results - len(comments)),
            textFormat="plainText",
            pageToken=next_page_token
        ).execute()

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "video_id": video_id,
                "author": snippet.get("authorDisplayName", ""),
                "text": snippet.get("textDisplay", ""),
                "published_at": snippet.get("publishedAt", ""),
                "like_count": snippet.get("likeCount", 0)
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
        time.sleep(0.5)

    return comments

def is_english(text):
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False

# === Load existing data if available ===
if os.path.exists(CSV_FILE):
    existing_df = pd.read_csv(CSV_FILE)
else:
    existing_df = pd.DataFrame(columns=["video_id", "author", "text", "published_at", "like_count"])

# === Step 1: Get video IDs ===
video_ids = []
for keyword in KEYWORDS:
    ids = get_video_ids_by_keyword(keyword, max_results=MAX_VIDEO_RESULTS)
    video_ids.extend(ids)

video_ids = list(set(video_ids))

# === Step 2: Extract comments ===
all_comments = []
for vid in video_ids:
    print(f"📥 Extracting from video ID: {vid}")
    try:
        comments = get_comments(vid, max_results=MAX_COMMENTS_PER_VIDEO)
        all_comments.extend(comments)
    except Exception as e:
        print(f"⚠️ Error on video {vid}: {e}")
    time.sleep(1)

df = pd.DataFrame(all_comments)

# === Step 3: Filter English only ===
print("🌐 Filtering English comments...")
df["is_english"] = df["text"].apply(is_english)
df = df[df["is_english"]].drop(columns=["is_english"])

# === Step 4: Merge with existing & remove duplicates ===
combined_df = pd.concat([existing_df, df])
combined_df.drop_duplicates(subset=["video_id", "text"], inplace=True)

# === Step 5: Save ===
combined_df.to_csv(CSV_FILE, index=False, encoding="utf-8")
print(f"✅ Done. Total comments saved: {len(combined_df)}")

# Keyword Used
# "malaysia education system", "malaysia healthcare system", "malaysia medications", "malaysia technology", "malaysia semiconductor industry"
# "malaysia investment", "malaysia best hospital", "malaysia wild animal", "najib case in malaysia", "malaysia corruption",  
# "jho low", "1mdb scandal", "malaysia military", "malaysia economy class", "malaysia protest", "malaysia mh370 case"
# "rohingya in malaysia", "zahid hamidi case", "petronas station on fire", "malaysia unemployment", "malaysia debt"
# "lim guan eng", "malaysia scam crime", "kim jong nam malaysia", "malaysia road accident crisis", "malaysia tariff response"
# "asean summit in malaysia", "macc malaysia", "missing british backpacker in malaysia", "sze fei izzuddin men's pair", "dr. M malaysia"
# "malaysian homeless records", "singapore acquire malaysian owned land", "what happened to fashionvalet", "malaysia ghost town", "malaysian rider championship opener"
# "malaysia travel", "malaysia beach", "malaysia current affairs", "malaysia opinion", "malaysia analysis"
# "malaysia issues", "Breaking news Malaysia", "klang crime", "malaysian celebrate eid", "commando malaysian"
# "sabah invicible people", "lahad datu incident", "malaysia storm", "malaysia discrimination", "malaysia unity"
# "lpg enforcement malaysia", "malaysia heart disease", "malaysia diabetes"
