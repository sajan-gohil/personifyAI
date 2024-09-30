import os
import json
import praw
import dotenv
dotenv.load_dotenv()

def get_client():
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="testscript by u/me",
        username=os.getenv("REDDIT_USERNAME"),
    )
    return reddit

def fetch_subreddit(client, subreddit):
    results = []
    for submission in client.subreddit("SneakerheadsIndia").new(limit=20):
        results.append({
            "title": submission.title,
            "thumbnail": submission.thumbnail,
            "media": submission.media,
            "text": submission.selftext
        })
    return results

if __name__ == "__main__":
    subreddits = ["Sneakers", "SneakerheadsIndia", "footwear", "shoes"]
    client = get_client()
    results = []
    for i in subreddits:
        results.extend(fetch_subreddit(client, i))
    json.dump(results)