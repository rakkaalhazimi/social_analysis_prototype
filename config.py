# File Path
DATA_PATH = "src/csv/labeled.csv"
TWEET_TEMPLATE_PATH = "src/template/tweet.html"
TWEET_STYLE_PATH = "src/template/tweet_style.html"

# Twitter Parameters
METRIC_COLS = ["retweet_count", "reply_count", "like_count", "quote_count"]
COUNT_COLS = ["tweets_count", "viral_count", "influencer_count", "sensitive_count"]
DATE_COL = "created_at"
TEXT_COL = "full_text"
USER_ID_COL = "user.id"
USER_FOLLOWERS_COL = "user.followers_count"
USERNAME_COL = "user.screen_name"
REPLY_COL = "reply_count"
LIKE_COL = "like_count"
RETWEET_COL = "retweet_count"
SENSITIVE_COL = "possibly_sensitive"


# Bokeh Plot Additional Column
COLOR_COL = "color"
CATEGORY_COL = "category"