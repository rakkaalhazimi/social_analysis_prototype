# File Path
DATA_PATH = "src/csv/labeled.csv"
TWEET_TEMPLATE_PATH = "src/template/tweet.html"
TWEET_STYLE_PATH = "src/template/tweet_style.html"

# Twitter Parameters
METRIC_COLS = ["retweet_count", "reply_count", "like_count", "quote_count"]
COUNT_ANALYSIS_COLS = ["viral_count", "influencer_count", "sensitive_count"]
COUNT_SENTIMENT_COLS = ["positive_sentiment_count", "negative_sentiment_count"]
USER_INVOLVEMENT_COLS = ["interactions", "potential_users_reached"]
TWEET_COUNT_COL = "tweets_count"
DATE_COL = "created_at"
TEXT_COL = "full_text"
TEXT_CLEAN_COL = "full_text_cleaned"
USER_ID_COL = "user.id"
USER_FOLLOWERS_COL = "user.followers_count"
USERNAME_COL = "user.screen_name"
REPLY_COL = "reply_count"
LIKE_COL = "like_count"
RETWEET_COL = "retweet_count"
QUOTE_COL = "quote_count"
SENSITIVE_COL = "possibly_sensitive"
SENTIMENT_COL = "sentiment"


# Bokeh Plot Additional Column
COLOR_COL = "color"
CATEGORY_COL = "category"