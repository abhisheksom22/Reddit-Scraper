# Reddit Harassment & Work-Related Scraper (PRAW-based)

This project uses Reddit's API through the PRAW library to collect Reddit posts that mention **harassment** and **workplace**-related keywords across various subreddits. It stores structured information, including post metadata and full comment threads, into a CSV file for academic research.

---

## Step-by-Step Setup Instructions

### 1. Create a Reddit Application (to get credentials)

1. Go to: https://www.reddit.com/prefs/apps
2. Scroll to the bottom and click on **"Create App"**
3. Fill out the form:
   - **Name**: AcademicResearchApp
   - **App type**: Script
   - **Redirect URI**: http://localhost:8080 (or any dummy URI)
4. After creating the app, note down:
   - **Client ID** (under the app name)
   - **Client Secret**
   - Your Reddit **username**
5. You’ll use these in your script like so:
```python
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="AcademicResearchApp/0.1 by u/YOUR_USERNAME"
)
```

---

### 2. Set Up Python Environment

Open a terminal and run:

```bash
python3 -m venv venv
source venv/bin/activate
pip install praw pandas
```

---

### 3. How the Script Works

The script loops through:

- A set of **harassment-related keywords**
- A set of **work-related keywords**
- A list of **target subreddits**

For each harassment keyword, it searches the subreddit and checks if the post also includes a work-related term.

Only posts from **after April 21, 2024** are included  
**NSFW, deleted or removed posts** are ignored  
All **comments** are collected and stored in a nested JSON column

---

### 4. How to Customize

#### Change Subreddits:
```python
subreddits = ['work', 'legaladvice', 'advice']
```

#### Change Harassment Keywords:
Edit the list at the top of the script:
```python
harassment_keywords = ["harassment", "sexism", "abuse", ...]
```

#### Change Work Keywords:
Also at the top:
```python
work_keywords = ["job", "boss", "coworker", "hr", "promotion", ...]
```

#### Change the Cutoff Date:
Update this line in the script:
```python
cutoff_timestamp = datetime(2024, 4, 21, tzinfo=timezone.utc).timestamp()
```

---

### 5. Run the Script

After filling in your credentials and editing the keywords/subreddits if needed, just run:

```bash
python reddit2_kappy.py
```

You’ll see log messages like:
```
🔍 Searching for 'harassment' in r/work...
 Saved post abc123 from r/work
```

When done, your CSV (e.g. `legaladvice_with_comments.csv`) will be ready.

---

## Output CSV Structure

| Column | Description |
|--------|-------------|
| id | Row number |
| post_id | Reddit post ID |
| subreddit | Subreddit name |
| harassment_keyword | Keyword matched in post |
| title | Post title |
| text | Full post body |
| author | Reddit username |
| score | Reddit post score |
| num_comments | Number of comments |
| created_utc | Post creation timestamp |
| url | Reddit post URL |
| comments_json | List of comments in JSON format |

---

## Important Notes

- This script respects Reddit’s API rate limits using `time.sleep(2)` between queries (for free tier it is 60 requests per minuite).
- Posts are **not duplicated** thanks to an internal ID tracker.
- Comments are captured in full (excluding `[deleted]` or `[removed]` ones).

---

## Libraries Used

- `praw`: Python Reddit API Wrapper
- `pandas`: Dataframe and CSV handling
- `json`: To store comments as JSON inside a column


