import praw
import pandas as pd
import json
import time
from datetime import datetime, timezone
import os

# ---------- Reddit API Setup ----------
# Replace these with your own credentials from https://www.reddit.com/prefs/apps
reddit = praw.Reddit(
    client_id="7x4tjUc-GvE_Fu6ZyoPs5Q",
    client_secret="zigISzvDxbLcwlXoBSmgARGyAjY_ew",
    user_agent="AcademicResearchApp/0.1 by u/DrinkEuphoric5248"
)

# ---------- Keywords to Search ----------
# These are keywords related to harassment and workplace context
harassment_keywords = [
    "harassment", "harassed", "sexual harassment", "gender harassment",
    "sex-based harassment", "gender-based harassment",
    "sexism", "sexist", "gender discrimination", "discrimination",
    "inappropriate behavior", "inappropriate", "creepy", "creep", "uncomfortable",
    "predatory behavior", "predatory", "misconduct", "abuse", "abusive",
    "toxic", "bully", "bullying", "sexual jokes", "unwanted attention",
    "stalking", "hostile environment"
]

work_keywords = [
    "job", "work", "workplace", "boss", "supervisor",
    "coworker", "co-worker", "colleague", "manager", "team lead", "team leader",
    "shift supervisor", "employer", "employment", "company", "office", "human resources", "hr",
    "promotion", "performance review", "toxic workplace", "hostile work environment",
    "microaggressions", "managerial abuse", "job harassment", "sexual harassment at work",
    "gender discrimination at work"
]

# ---------- Subreddit to Scrape ----------
# Change this list to include the subreddits you want to analyze
subreddits = ['legaladvice']

# ---------- Date Filtering ----------
# Only include posts created after this date
cutoff_timestamp = datetime(2024, 4, 21, tzinfo=timezone.utc).timestamp()

# ---------- Output File ----------
# This is where the results will be stored
output_file = "legaladvice_with_comments.csv"

# ---------- Helper Structures ----------
post_data_list = []          # Master list to hold all valid posts
saved_post_ids = set()       # Set to track and avoid duplicates
counter = 1                  # Row number counter

# ---------- Main Scraping Logic ----------
for subreddit_name in subreddits:
    subreddit = reddit.subreddit(subreddit_name)  # connect to the subreddit
    for h_kw in harassment_keywords:
        print(f"\n Searching for '{h_kw}' in r/{subreddit_name}...")

        try:
            for post in subreddit.search(h_kw, sort='new', limit=100):
                if post.created_utc < cutoff_timestamp:
                    continue
                if post.id in saved_post_ids:
                    continue

                title = post.title.lower()
                body = post.selftext.lower()

                # Match post if it contains any work-related keyword
                if any(w_kw in title or w_kw in body for w_kw in work_keywords):
                    # Skip NSFW, deleted or removed posts
                    if post.selftext.lower() in ['[deleted]', '[removed]'] or post.over_18:
                        continue

                    # ---------- Fetch all comments ----------
                    post.comments.replace_more(limit=0)
                    comments_list = []
                    for comment in post.comments.list():
                        if comment.body.lower() not in ['[deleted]', '[removed]']:
                            comments_list.append({
                                "comment_author": str(comment.author),
                                "comment_body": comment.body,
                                "comment_score": comment.score,
                                "comment_created_utc": datetime.fromtimestamp(
                                    comment.created_utc, tz=timezone.utc
                                ).strftime('%Y-%m-%d %H:%M:%S')
                            })

                    # ---------- Save the post ----------
                    post_data = {
                        "id": counter,
                        "post_id": post.id,
                        "subreddit": subreddit_name,
                        "harassment_keyword": h_kw,
                        "title": post.title,
                        "text": post.selftext,
                        "author": str(post.author),
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "created_utc": datetime.fromtimestamp(
                            post.created_utc, tz=timezone.utc
                        ).strftime('%Y-%m-%d %H:%M:%S'),
                        "url": post.url,
                        "comments_json": json.dumps(comments_list, ensure_ascii=False)
                    }

                    post_data_list.append(post_data)
                    saved_post_ids.add(post.id)
                    counter += 1

            time.sleep(2)  # avoid hitting API too fast

        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

# ---------- Final Save to CSV ----------
df = pd.DataFrame(post_data_list)
df.to_csv(output_file, index=False)
print(f"\n DONE: {len(df)} unique posts saved to {output_file}")
