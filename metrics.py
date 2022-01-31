import re
from collections import defaultdict
from functools import partial

import numpy as np
import pandas as pd

import config
from utils import filter_tweet_count, replace_wspace


"""
==================================================================================
Tweet Timeline
==================================================================================

Get daily tweet count based on specific query

"""


def tweet_trends(period, queries, df):

    # Copy Dataframe
    df = df.copy()

    # Count tweets based on its query periodically
    trends = pd.concat([
        df.resample(period).agg({config.TEXT_COL: partial(filter_tweet_count, query=query)})
        for query in queries
    ], axis=1)

    # Change column names and index
    trends.columns = [replace_wspace(query) for query in queries]
    trends["date"] = [date for date in trends.index]

    return trends


"""
==================================================================================
Public Metrics
==================================================================================

Public Metrics is provided by twitter API, it is consist of:
- retweet_count
- reply_count
- like_count
- quote_count

"""

def query_metric(queries, df):
    analytics = {}
    for query in queries:
        filter = df[config.TEXT_COL].str.contains(query, flags=re.IGNORECASE)
        analytics[query] = df[filter][config.METRIC_COLS].sum(axis=0)

    return pd.DataFrame(analytics).T


"""
==================================================================================
Tweet Counts
==================================================================================

Count specifics aspect from all the tweets on every query:

- Tweet Count
  Tweet Count is the total of tweet by specific query

- Viral Count
  Viral Tweets is determined by any tweets that has more than 1000 `reply`, `like` or `retweet`

- User Followers Count
  User Followers Count is determined by the total followers of unique users.

- Influencer Count
  Influencer Counts is determined by the total of users who have more than 1000 followers

- Sensitive Count
  Sensitive Count is the total of potential harmfull tweet that marked as sensitive by twitter

"""

def count_tweet(df):
    return len(df)

def count_viral(df):
    return (df[config.METRIC_COLS] > 1000).any(axis=1).sum()

def count_sensitive(df):
    return df[config.SENSITIVE_COL].sum()

def count_followers(df):
    unique_user = df[[config.USER_ID_COL, config.USER_FOLLOWERS_COL]].drop_duplicates(subset=[config.USER_ID_COL])
    return unique_user[config.USER_FOLLOWERS_COL].sum()

def count_max_followers(df):
    unique_user = df[[config.USER_ID_COL, config.USER_FOLLOWERS_COL]].drop_duplicates(subset=[config.USER_ID_COL])
    return unique_user[config.USER_FOLLOWERS_COL].max()

def count_influencer(df):
    unique_user = df[[config.USER_ID_COL, config.USER_FOLLOWERS_COL]].drop_duplicates(subset=[config.USER_ID_COL])
    return (unique_user[config.USER_FOLLOWERS_COL] > 1000).sum()


COUNT_ITEMS = {
    "tweets_count": count_tweet,
    "viral_count": count_viral,
    "followers_count": count_followers,
    "influencer_count": count_influencer,
    "sensitive_count": count_sensitive,
    "max_follower_count": count_max_followers,
}


def all_counts(df, queries):

    # Copy Dataframe
    df = df.copy()

    # Initialize Dictionary
    analytics = defaultdict(list)

    for query in queries:
        # Filter tweet by query
        filter = df[config.TEXT_COL].str.contains(query, flags=re.IGNORECASE)
        filtered_df = df[filter]

        # Counts all the aspects
        for name, func in COUNT_ITEMS.items():
            analytics[query].append( func(filtered_df) )

    df_values = np.array(list(analytics.values()))
    return pd.DataFrame(df_values, columns=COUNT_ITEMS.keys(), index=analytics.keys())


"""
==================================================================================
User Involvement
==================================================================================

Make new variables from the existing counts, user Involvement made variables are consist of:

- Interaction
  Sum of reply count and retweet count

- Potential Users Reached
  Potential users reached is the sum of total followers of the author's and retweet.

"""

def user_involvement(metrics_df):
    metrics_df["interactions"] = metrics_df[config.REPLY_COL] + metrics_df[config.RETWEET_COL]
    metrics_df = metrics_df.rename(columns={"max_follower_count": "potential_users_reached"})
    return metrics_df